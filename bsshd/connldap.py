#!/usr/bin/env /usr/local/python279/bin/python
#-*- coding: UTF-8 -*-

import os
import sys
import ldap
import logging

from conf import ReadConf
from logger import CreateLogger

log = logging.getLogger(os.path.basename(__file__))
config = ReadConf.config_dict()

class AuthLdap(object):
    ''' 连接LDAP服务，并验证用户输入的密码是否正确
    '''

    uri = "%s:%s"%(config['LDAP_SERVER'], config['LDAP_PORT'])

    @classmethod
    def _find_user(cls, username):
        '''
            查找登陆用户是否在LDAP服务中

            Args：
                username： 用户登陆的用户名

            Returns：
                LDAP中找到username，返回distinguishedName
                LDAP中未找到useranme，返回None
        '''
        try:
            base_dn = config['LDAP_BASE_DN']
            bind_dn= config['LDAP_BIND_DN']
            bind_passwd= config['LDAP_BIND_PASSWD']
            search_scope = ldap.SCOPE_SUBTREE

            ''' 字符串拼接的几种规范方法
            search_filter = "%s=%s"%(config['LDAP_SEARCH_ATTR'],username)
            search_filter = "({}={})".format(config['LDAP_SEARCH_ATTR'],username)
            '''
            search_filter = "({}={})".format(config['LDAP_SEARCH_ATTR'],username)
            retrieve_attributes = None


            log.info('Start validating ldap users')
            conn = ldap.initialize(cls.uri)

            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.protocol_version = ldap.VERSION3

            conn.simple_bind_s(bind_dn, bind_passwd)
            log.info('ldap connect successfully')


            ldap_result_id = conn.search(base_dn, search_scope, search_filter, retrieve_attributes)  
            result_set = []  

            while True:
                result_type, result_data = conn.result(ldap_result_id, 0)  
                if(result_data == []):  
                    break  
                else:  
                    if result_type == ldap.RES_SEARCH_ENTRY:  
                        result_set.append(result_data) 

            Name,Attrs = result_set[0][0]
            if hasattr(Attrs, 'has_key') and Attrs.has_key('name'):
                distinguishedName = Attrs['distinguishedName'][0]  
                return distinguishedName  
  
            else:  
                log.error("LDAP search result error")  
                return None 
            
        except ldap.LDAPError, e:
            log.error('LDAP ERROR [%s]'%e)
            return None

        except IndexError, e:
            log.error('Auth result ERROR [%s]'%e)
            return None

    @classmethod
    def login(cls, username, password):
        ''' 验证用户密码
            
            Args：
                username：登陆的用户
                password：登陆的密码

            Returns：
                获取到distinguishedName时，进行密码验证，密码正确返回True，不正确返回None
        '''
        distinguishedName = cls._find_user(username)
        if distinguishedName:
            try:
                conn = ldap.initialize(cls.uri)
                conn.simple_bind_s(distinguishedName, password)
                log.info('ldap auth successfully')
                return True
            except ldap.LDAPError,e:
                log.error('ldap auth fail')
                return None
