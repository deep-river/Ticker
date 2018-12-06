# -*- coding: utf-8 -*-
from Main import main_func
from flask import Flask, jsonify, render_template, request, make_response
import json
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta
from flask_apscheduler import APScheduler
from configparser import ConfigParser
cfg = ConfigParser()

app = Flask(__name__)


def connect_db():
    cfg.read('DBConn_config.ini')
    host = cfg.get('Mongo_db', 'Host')
    user = cfg.get('Mongo_db', 'User')
    password = cfg.get('Mongo_db', 'Password')
    dbname = cfg.get('Mongo_db', 'DBname')
    replicaset = cfg.get('Mongo_db', 'ReplicaSet')
    global conn
    conn = None
    try:
        conn = MongoClient('mongodb://%s:%s@%s/%s?replicaSet=%s' % (user, password, host, dbname, replicaset))
        db = conn[dbname]
        return db
    except:
        print('connection error.')


def remove_outdated_data(connection):
    querytime = datetime.now() - timedelta(days=60)
    deletetime = datetime.now() - timedelta(days=180)
    db = connection
    col = db['Records']
    result = col.find({'last_updated': {'$lte': querytime}}, {'_id': 0})
    for raw_data in result:
        db['Old_records'].insert(raw_data)
    col.remove({'last_updated': {'$lte': querytime}})
    db['Old_records'].remove({'last_updated': {'$lte': deletetime}})


def query_for_raw(connection, operand, queryrange=30):
    querytime = datetime.now() - timedelta(days=queryrange)
    db = connection
    col = db['Records']
    if operand == 'all':
        result = col.find({'last_updated': {'$gte': querytime}}, {'_id': 0})
    else:
        result = col.find({operand: {'$exists': True},'last_updated': {'$gte': querytime}}, {operand: 1, 'last_updated': 1, '_id': 0})

    result_list = []
    for raw_data in result:
        raw_data['last_updated'] = str(raw_data['last_updated'])
        result_list.append(raw_data)
    return result_list


def query_by_date_raw(connection, qdatefrom, qdateto, operand):
    db = connection
    col = db['Records']
    if operand == 'all':
        result = col.find({'last_updated': {'$gte': qdatefrom, '$lte': qdateto}}, {'_id': 0})
    else:
        result = col.find({operand: {'$exists': True}, 'last_updated': {'$gte': qdatefrom, '$lte': qdateto}},{operand: 1, 'last_updated': 1, '_id': 0})

    result_list = []
    for raw_data in result:
        raw_data['last_updated'] = str(raw_data['last_updated'])
        result_list.append(raw_data)
    return result_list


def query_for_formatted(connection, operand, queryrange=30):
    querytime = datetime.now() - timedelta(days=queryrange)
    db = connection
    col = db['Records']

    if operand == 'all':
        data = col.find({'last_updated': {'$gte': querytime}}, {'last_updated': 0, '_id': 0})
        index_list = list(data[0])

        result_list = []
        for result in data:
            result_list.append(result)

        value_dict = {}
        for index in index_list:
            temp_dict = {}
            for data in result_list:
                if data[index]:
                    values = data[index]
                    for id in values:
                        if id not in temp_dict:
                            temp_dict[id] = []
                        temp_dict[id].append(values[id])
            value_dict[index] = temp_dict

    else:
        data = col.find({'last_updated': {'$gte': querytime}}, {operand: 1, '_id': 0})
        index_list = [operand]
        result_list = []
        for result in data:
            result_list.append(result)

        value_dict = {}
        for index in index_list:
            temp_dict = {}
            for data in result_list:
                if data[index]:
                    values = data[index]
                    for id in values:
                        if id not in temp_dict:
                            temp_dict[id] = []
                        temp_dict[id].append(values[id])
            value_dict[index] = temp_dict

    dbtime = col.find({'last_updated': {'$gte': querytime}}, {'last_updated': 1, '_id': 0})
    time_list = []
    for ti in dbtime:
        time_list.append(str(ti['last_updated']))

    return index_list, time_list, value_dict


class Config(object):
    JOBS = [
        {
            'id':'scheduled_job',
            'func': '__main__:main_func',
            'args': None,
            'trigger': 'interval',
            'minutes': 30
        }
    ]


def scheduled_job():
    main_func()


@app.route('/')
def index():
    return render_template('Ticker-view.html')


@app.route("/chart_data", methods=["GET"])
def chart():
    if request.method == "GET":
        cursor = connect_db()
        remove_outdated_data(cursor)
        order_list, time_list, value_dict = query_for_formatted(cursor, 'all', 30)
        conn.close()
        pack = {"query_order": order_list, "time": time_list, "value": value_dict}
        data = json.dumps(pack, ensure_ascii=False)
        return data


@app.route("/api/v1.0/data/<string:query>/all/", methods=["GET"])
def get_data(query):
    cursor = connect_db()
    data_list = query_for_raw(cursor, query)
    conn.close()
    if data_list:
        data_str = {}
        data_str['Query_time'] = str(datetime.now().replace(microsecond=0))
        data_str['Count'] = len(data_list)
        data_str['Records'] = []
        num = 0
        for data in data_list:
            num += 1
            data['No.'] = num
            data_str['Records'].append(data)
        data = json.dumps(data_str, ensure_ascii=False)
        return data
    else:
        return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/api/v1.0/data/<string:query>/<int:numlimit>/", methods=["GET"])
def get_data_by_num(query, numlimit):
    cursor = connect_db()
    data_list = query_for_raw(cursor, query)
    conn.close()
    boundary = len(data_list)
    if data_list:
        if numlimit <= boundary:
            data_str = {}
            data_str['Query_time'] = str(datetime.now().replace(microsecond=0))
            data_str['Count'] = numlimit
            data_str['Records'] = []
            seq = 0
            for num in range(boundary - numlimit, boundary):
                seq += 1
                data_list[num]['No.'] = seq
                data_str['Records'].append(data_list[num])
            data = json.dumps(data_str, ensure_ascii=False)
            return data
        else:
            return make_response(jsonify({'error': 'Number out of range'}), 404)
    else:
        return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/api/v1.0/data/<string:datefrom>/<string:dateto>/<string:query>/all/", methods=["GET"])
def get_data_by_date(datefrom, dateto, query):
    datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
    dateto = datetime.strptime(dateto, '%Y-%m-%d')
    cursor = connect_db()
    data_list = query_by_date_raw(cursor, datefrom, dateto, query)
    conn.close()
    if data_list:
        data_str = {}
        data_str['Query_time'] = str(datetime.now().replace(microsecond=0))
        data_str['Count'] = len(data_list)
        data_str['Records'] = []
        num = 0
        for data in data_list:
            num += 1
            data['No.'] = num
            data_str['Records'].append(data)
        data = json.dumps(data_str, ensure_ascii=False)
        return data
    else:
        return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':

    app.config.from_object(Config())
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run()
