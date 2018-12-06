# -*- coding: utf-8 -*-
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser
cfg = ConfigParser()


class Mongodb(object):

    def get_setting(self):
        try:
            cfg.read('DBConn_config.ini')
            self.host = cfg.get('Mongo_db', 'Host')
            self.user = cfg.get('Mongo_db', 'User')
            self.password = cfg.get('Mongo_db', 'Password')
            self.dbname = cfg.get('Mongo_db', 'DBname')
            self.replicaset = cfg.get('Mongo_db', 'ReplicaSet')
        except:
            print('Local database config file not found or broken. Please fill the config information correctly.')

    def __init__(self):
        self.get_setting()
        self._conn = None
        self._connect()
        self.db = self._conn[self.dbname]

    def _connect(self):
        try:
            if self.replicaset:
                conn_str = 'mongodb://%s:%s@%s/%s?replicaSet=%s' % (self.user, self.password, self.host, self.dbname, self.replicaset)
            else:
                conn_str = 'mongodb://%s:%s@%s/%s' % (self.user, self.password, self.host, self.dbname)
            self._conn = MongoClient(conn_str)
            print('Mongodb database: %s connected successfully.' % self.dbname)
        except:
            print("Mongodb connection error!")

    def get_collection(self, collection):
        try:
            handler = self.db[collection]
            #print(u'''Method: 'get_collection' executed. Current collection: '%s'. Handler 'coll' returned. ''' % collection)
            return handler
        except:
            print('Error: cannot fetch collection!')

    def insert_data(self, collection, data):
        try:
            col = self.db[collection]
            col.insert(data)
            print('Insert complete.')
        except:
            print('Insert error!')

    def clear_data(self, collection):
        col = self.db[collection]
        col.remove()

    def close(self):
        self._conn.close()
        print('Mongodb database connection closed.')


class Oracle(object):

    def get_setting(self):
        try:
            cfg.read('DBConn_config.ini')
            self.host = cfg.get('Oracle_db', 'host')
            self.user = cfg.get('Oracle_db', 'user')
            self.password = cfg.get('Oracle_db', 'password')
            self.port = cfg.get('Oracle_db', 'port')
            self.sid = cfg.get('Oracle_db', 'sid')
        except:
            print('Local database config file not found or broken. Please fill the config information correctly.')

    def __init__(self):
        self.get_setting()
        self._engine = None
        self._conn = None
        self._connect()

    def _connect(self):
        conn_str = 'oracle+cx_oracle://%s:%s@%s:%s/%s' % (self.user, self.password, self.host, self.port, self.sid)
        try:
            self._engine = create_engine(conn_str, encoding='utf-8', echo=False)
            db_session = sessionmaker(bind=self._engine)
            self._conn = db_session()
            print('Oracle database: %s connected successfully.' % self.sid)
        except:
            print('Oracle connection error!')

    def query(self, op):
        query_catch = self._conn.execute(op)
        return query_catch

    def close(self):
        self._conn.close()
        self._engine.dispose()
        print('Oracle database connection closed.')
