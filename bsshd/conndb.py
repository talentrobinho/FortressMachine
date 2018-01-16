#!/usr/bin/env /usr/local/python279/bin/python
#-*- coding: UTF-8 -*-

import os
import logging
import MySQLdb
from conf import ReadConf

config = ReadConf.config_dict()
log = logging.getLogger(os.path.basename(__file__))

CONNERR = None
QUERYERR = None

class Machine(object):

    def __init__(self):
        self.mysql_host = config['MYSQL_HOST']
        self.mysql_user = config['MYSQL_USER']
        self.mysql_passwd = config['MYSQL_PASSWD']
        self.mysql_db = config['MYSQL_DB']
        self.mysql_feild = config['MYSQL_FIELD']
        self.mysql_charset = config['MYSQL_CHARSET']
        self.conn = None
        self.db = None
        self.op_cur = None
        self.result = None



    def __conndb(self):
        try:
            self.conn = MySQLdb.connect(host=self.mysql_host,
                                user=self.mysql_user,
                                passwd=self.mysql_passwd,
                                db=self.mysql_db,
                                charset=self.mysql_charset)
        except Exception:
            log.error('*************')
            return CONNERR


        return self.conn

    def __colse_db(self, db=None):
        try:
            db.close()
        except AttributeError, e:
            log.error('Close the database error[%s]'%e)

    def query_data(self, sql=None):
        log.info("======: %s"%sql)
        self.db = self.__conndb()
        if not self.db is None:
            self.op_cur = self.db.cursor()
        else:
            return CONNERR

        try:
            if self.op_cur.execute(sql) == 0:
                self.result = []
            else:
                self.result = self.op_cur.fetchall()
        except Exception, e:
            log.error('Query data exception[%s]'%e)
            return QUERYERR
        finally:
            self.__colse_db(self.conn)

        return self.result


