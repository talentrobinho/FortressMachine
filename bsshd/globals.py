#!/usr/bin/env /usr/local/python279/bin/python
#-*- coding: UTF-8 -*-


import os
import paramiko
from functools import partial
from werkzeug.local import LocalStack, LocalProxy




class GenePidFile(object):
    ''' 
        Generate pid file
    '''

    fpid = None
    @classmethod
    def gen_pid(cls, pid_file='/tmp/sshdd.pid'):
        cls.fpid = open(pid_file, 'w')
        cls.fpid.write('%s'%os.getpid())
        cls.fpid.close()

class SetParamLog(object):

    @staticmethod
    def param_log(log_name='demo_server11.log'):
        paramiko.util.log_to_file(log_name)

class GlobalVar(object):

    host_key = None
    _path = None
    _file_name = None

    @classmethod
    def set_host_key(cls, filename='id_rsa'):
        #cls._path = os.path.join(os.path.dirname(os.getcwd()), 'conf')
        cls._path = os.path.join(os.getcwd(), '')
        cls._file_name = filename
        cls.host_key = paramiko.RSAKey(filename=os.path.join(cls._path, cls._file_name))
        return cls.host_key
        
