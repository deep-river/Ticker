# -*- coding: utf-8 -*-
import DBConn
from datetime import datetime
from QueryMath import minus
from QueryMath import positive_num
from SendNotification import SendMail


def fetch_queries():
    Targetdb = DBConn.Mongodb()
    cursor = Targetdb.get_collection('Query_list')
    results = cursor.find({}, {'_id': 0})
    Targetdb.close()
    return results


def execute_queries(op):
    data = {}
    Sourcedb = DBConn.Oracle()
    for query in op:
        result = Sourcedb.query(op[query])
        data[query] = {}
        for id_s in result:
            data[query][id_s[0]] = float(id_s[1])
    Sourcedb.close()
    return data


def process_data(op):
    op['G'] = minus(op, 'C', 'E')
    op['J'] = minus(op, 'A', 'D')
    op['J'] = minus(op, 'J', 'I')
    op['F'] = positive_num(op, 'J')
    return op


def jsonify(op):
    temp_dict = {}
    for items in list(op):
        if op[items]:
            for n in list(op[items]):
                string = str(n)
                op[items][string] = op[items][n]
                del op[items][n]
            temp_dict[items] = op[items]
        else:
            op[items] = {}
    updatetime = datetime.now().replace(microsecond=0)
    op['last_updated'] = updatetime
    return op


def insert_data(op):
    Targetdb = DBConn.Mongodb()
    Targetdb.insert_data('Records', op)
    Targetdb.close()


def main_func():
    queries = fetch_queries()
    dict_query = {}
    for temp in queries:
        dict_query.update(temp)
    data = execute_queries(dict_query)
    data = process_data(data)
    data = jsonify(data)
    insert_data(data)
    notification = SendMail()
    notification.send()
    print(str(datetime.now().replace(microsecond=0))+': process completed.')


if __name__ == '__main__':
    main_func()
