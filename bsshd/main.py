#!/usr/local/python279/bin/python
#-*- coding: UTF-8 -*-

import os
import socket
import sys
import threading
import traceback
import subprocess
import paramiko
import logging
import daemon
import time
import re

from signal import SIGTERM 
from multiprocessing import Process
from globals import GenePidFile
from globals import SetParamLog
from globals import GlobalVar
from server import Server
from getinput import GetInput
from infomationhub import InfoHub
from checkmachine import CheckHost
from conf import ReadConf
from logger import CreateLogger


''' 配置根（root）日志参数 '''
CreateLogger.create_logger()
host_key = GlobalVar.set_host_key()
''' 加载配置文件 '''
config = ReadConf.config_dict()
'''
### Open the independent log file of the paramiko module
SetParamLog.param_log()
'''

''' 创建子日志 '''
log = logging.getLogger(os.path.basename(__file__))



class bsshd(object):
    ''' ssh 服务端程序
    '''
    pidfile = config['SERVER_PID_FILE']

    @classmethod
    def _create_conn(cls, client, addr):
        ''' 根据链接请求，创建链接

            Args:
                通过socket.accept()函数获得
                client: 套接字对象
                addr: 客户端地址
            Returns:
                无返回值，出错退出
        '''
        try:
            #t = paramiko.Transport(client, gss_kex=DoGSSAPIKeyExchange)
            t = paramiko.Transport(client)
            try:
                t.load_server_moduli()
            except:
                log.error('(Failed to load moduli -- gex will be unsupported.)')
                raise
            t.add_server_key(host_key)
            server = Server()
            try:
                t.start_server(server=server)
            except paramiko.SSHException:
                log.error('*** SSH negotiation failed.')
                sys.exit(1)
        
            # wait for auth
            chan = t.accept(120)
            if chan is None:
                log.warning('Gets the channel timeout')
                t.close()
                sys.exit(1)
            log.info('Authenticated!')
        
            server.event.wait(10)
            if not server.event.is_set():
                log.warn('*** Client never asked for a shell.')
                sys.exit(1)
        
            username = server.get_loginname()
            welcome='''
            \r\n*********************************************************************************
            \r\n**********                 Welcome To The Magic Gate                   **********
            \r\n*********************************************************************************
            '''

            usage='''
            \r    Instructions for use are as follows:
            \r    1. Login server.
            \r       ssh server_ip
            \r    2. Logout system.[q|Q]

            '''
            chan.send(welcome)
            chan.send('\r\nHI %s!\r\n'%username.upper())
            chan.send(usage)

            
            getdb = CheckHost(username)
            passwd_count = 0
            passwd_input = False
            while True:
                passwd = None
                search_content = None
                gi = GetInput(chan, username)
                cmd = gi.get_input()
                if cmd.startswith('ssh'):
                    IH = InfoHub(chan)
                    hostinfo = cmd.strip(' ').split(' ')[1]
                    if hostinfo.find('@') >= 0:
                        user = hostinfo.split('@')[0]
                        host = hostinfo.split('@')[1]
                    else:
                        user = username
                        host = hostinfo
                    infotupl = getdb.check_user_by_ip(host)
                    if infotupl:
                        admin, userlist = infotupl[0]
                        if int(admin.find(username)) >= 0:
                            passwd_input = True
                        elif int(userlist.find(username)) >= 0:
                            passwd_input = True
                        else:
                            chan.send('\r\nWARNING: You are not allowed to log in. Please contact the administrator.')
                            chan.send('\r\nADMIN: %s'%(admin,))
                            continue
                    else:
                        chan.send('\r\nHost does not exist')
                        continue
                    pw = GetInput(chan, username)
                    while passwd_input:
                        passwd = pw.get_input("%s@%s's password: "%(user, host))
                        if passwd:
                            if IH.info_hub(host=host, user=user, passwd=passwd):
                                chan.send('\r\n[ERROR] Permission denied, please try again.'%host)
                                log.error('Permission denied, please try again.[%s]'%host)
                                passwd_count+=1
                                
                                if passwd_count > 2:
                                    break
                            else:
                                break
                    
                elif cmd.startswith('/'):
                    search_content = cmd.split('/')[1]
                    host_re = re.complie(r'^10\.1[3,4,5]\d\.((?:(2[0-4]\d)|(25[0-5])|([01]?\d\d?))\.)')
                    domain_re = re.complie(r'^\w')
                    if host_re.match(search_content):
                        query_host(search_content, 0)
                    elif domain_re.match(search_content):
                        query_host(search_content, 1)

                elif cmd in ['h', 'help']:
                    chan.send('\r\n%s'%usage)

                elif cmd in ['q', 'Q']:
                    break

            chan.send('\r\n')
            chan.close()
        
        except Exception as e:
            log.error('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))
            traceback.print_exc()
            try:
                t.close()
            except:
                pass
            sys.exit(1)
    
    
    @classmethod
    def run(cls):
        ''' 启动服务，绑定端口、IP，接收链接请求
        '''
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((config['SERVER_BIND_HOST'], config['SERVER_BIND_PORT']))
        except Exception as e:
            log.error('*** Bind failed: %s:%s'%((config['SERVER_BIND_HOST'], config['SERVER_BIND_PORT'])) + str(e))
            traceback.print_exc()
            sys.exit(1)
        
        try:
            sock.listen(config['SERVER_LISTEN_BACKLOG'])
            log.info('Listening for connection ...')
        except Exception as e:
            log.error('*** Listen/accept failed: ' + str(e))
            traceback.print_exc()
            sys.exit(1)
        while True:
            log.info('------------------------')
            client, addr = sock.accept()
            log.info('Got a connection!')
            thread = threading.Thread(target=cls._create_conn, args=(client, addr))
            thread.daemon = True
            thread.start()
    
if __name__ == '__main__':
    daemon.daemonize(bsshd.pidfile)
    bsshd.run()
