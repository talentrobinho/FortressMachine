#!/usr/local/python279/bin/python

import os
import sys
import threading
import paramiko
import selectors2 as selectors
import logging
from paramiko.py3compat import b, u 


log = logging.getLogger(os.path.basename(__file__))


class InfoHub(object):
    '''
        前端channel与后端channel数据交换
    '''

    def __init__(self, fchan):
        self.fchan = fchan
        self.bchan = None
        self.is_first_input = True
        self.in_input_state = False
        self.ENTER_CHAR = ('\r', '\n', '\r\n')
        self.sel = selectors.DefaultSelector()


    def info_hub(self, user, host, passwd='123'):
        ''' 连接后端服务器 '''
        try:
            log.info('connect host ...')
            ssh=paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=22, username=user, password=passwd, compress=True)
            self.bchan=ssh.invoke_shell(term='vt100', width=self.fchan.win_width, height=self.fchan.win_height)
            self.fchan.send('\r\n')
        except paramiko.ssh_exception.BadHostKeyException:
            log.error(u"The server's host key could not be verified")
            return 1
        except paramiko.ssh_exception.AuthenticationException:
            log.error(u"Authentication failed")
            return 1
        except paramiko.ssh_exception.SSHException:
            log.error(u"Other error connecting or establishing an SSH session")
            return 1
        except Exception:
            log.error(u"A socket error occurred while connecting")
            return 1

        if self.bchan is None:
            return 1

        ''' 注册前端channel和后端channel到事件驱动 '''
        self.sel.register(self.fchan, selectors.EVENT_READ)
        self.sel.register(self.bchan, selectors.EVENT_READ)
        while True:
            events = self.sel.select()
            ''' 
                self.fchan.event is set in server.py 

                通过线程事件监控用户窗口是否变化，变化则重绘窗口
            '''
            if self.fchan.event.is_set():
                self.fchan.event.clear()
                width = self.fchan.win_width
                height = self.fchan.win_height
                self.bchan.resize_pty(width, height)
 
            ''' 监听channel '''
            if self.fchan in [t[0].fileobj for t in events]:
                try:
                    x = u(self.fchan.recv(1024))
                    if len(x) == 0:
                        self.fchan.send('\r\n*** Welcome next time ***\r\n\r\n')
                        break
                    self.bchan.send(x)
                except Exception:
                    log.error('fchan error')
            if self.bchan in [t[0].fileobj for t in events]:
                try:
                    x = u(self.bchan.recv(1024))
                    if len(x) == 0:
                        self.fchan.send('Connection to %s closed.'%host)
                        break
                    self.fchan.send(x)
                except Exception:
                    log.error('bchan error')
