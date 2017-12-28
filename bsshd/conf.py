#!/usr/bin/env /usr/local/python279/bin/python
#-*- coding: UTF-8 -*-
import ConfigParser, os



class ReadConf(object):

    ''' 读取配置文件
    '''
    conf_path = os.path.join(os.path.dirname(os.path.abspath('.')), 'bsshd.cfg')
    default_conf= os.path.join(os.path.dirname(os.path.abspath('.')), 'default.cfg')

    ''' 
        配置文件的value推荐使用双引号引起，也可以不用
        以下是配置文件格式样例：

        默认配置文件名：bsshd.cfg
        默认配置文件内容：
            [server]
            server_ip= 0.0.0.0
            server_port= 22
            pid_file = /tmp/bsshd.pid
            log_file= log_path
            log_level= debug
            listen_backlog= 100

            [ldap]
            server = "ldap://xxxx.com"
            port = 389
            base_dn = "DC=sogou-inc,DC=com"
            search_attribute = "sAMAccountName"
            search_dn = "reader@xxxx.com"
            bind_dn = "CN=reader,OU=aaa,OU=bbb,OU=ccc,DC=xxxx,DC=com"
            bind_passwd = "123456"


            [mysql]
            host=""
            user=""
            passwd=""
            db=""
    '''

    @classmethod
    def _read_conf(cls, conf_file=conf_path):
        config = ConfigParser.ConfigParser()

        if os.path.exists(conf_file):
            config.read(conf_file)
        else:
            config.read(cls.default_conf)
        return config

    @staticmethod
    def drop_quotes(str):
        return str.strip('"')

    @classmethod
    def config_dict(cls, conf_file=conf_path):
        '''
            将配置文件选项映射到自定义key的字典
            如果在配置文件中添加配置项，需要在此处添加对应的key，在程序中引用自定义key即可

            Args:
                conf_file: 是配置文件的绝对路径
                           不指定时，默认是../conf/bsshd.cfg, 当找不到bsshd.cfg时，会使用../conf/default.cfg

            Returns:
                返回配置文件的对应项的字典
        '''
        config_content = cls._read_conf(conf_file)
        return {
                    'SERVER_BIND_HOST': cls.drop_quotes(config_content.get('server', 'server_ip')),
                    'SERVER_BIND_PORT': int(cls.drop_quotes(config_content.get('server', 'server_port'))),
                    'SERVER_PID_FILE': cls.drop_quotes(config_content.get('server', 'pid_file')),
                    'SERVER_LISTEN_BACKLOG': int(cls.drop_quotes(config_content.get('server', 'listen_backlog'))),
                    'SERVER_LOGFILE': cls.drop_quotes(config_content.get('server', 'log_file')),
                    'SERVER_LOGLEVEL': cls.drop_quotes(config_content.get('server', 'log_level')),
                    'LDAP_SERVER': cls.drop_quotes(config_content.get('ldap', 'server')),
                    'LDAP_PORT': int(cls.drop_quotes(config_content.get('ldap', 'port'))),
                    'LDAP_BASE_DN': cls.drop_quotes(config_content.get('ldap', 'base_dn')),
                    'LDAP_SEARCH_DN': cls.drop_quotes(config_content.get('ldap', 'search_dn')),
                    'LDAP_SEARCH_ATTR': cls.drop_quotes(config_content.get('ldap', 'search_attribute')),
                    'LDAP_BIND_DN': cls.drop_quotes(config_content.get('ldap', 'bind_dn')),
                    'LDAP_BIND_PASSWD': cls.drop_quotes(config_content.get('ldap', 'bind_passwd')),

               }
