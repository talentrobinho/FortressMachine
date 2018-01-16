#!/usr/bin/env /usr/local/python279/bin/python
#-*- coding: UTF-8 -*-

import os
import logging
from conndb import Machine

''' 创建子日志 '''
log = logging.getLogger(os.path.basename(__file__))

class CheckHost(object):
    
    def __init__(self, username=None):
        self.username = username
        self.db = Machine()
        self.sql_by_name = None
        self.sql_by_host = None


    def get_machine_by_name(self, user=None):
        self.sql_by_name = 'select ip from machine where manager like "%{}%" or user like %{}%'.format(user, user)
        log.info(self.sql_by_name)
        log.info(self.db.query_data(self.sql_by_name))
        return None

    def check_user_by_ip(self, ip=None):
        self.sql_by_host = 'select manager,user from machine where ip="{}"'.format(ip)
        log.info(self.sql_by_host)
        log.info(self.db.query_data(self.sql_by_host))
        #admin, userlist = self.db.query_data(self.sql_by_host)[0]
        if len(self.db.query_data(self.sql_by_host)) > 0:
            return self.db.query_data(self.sql_by_host)
        return None
