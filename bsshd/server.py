#!/usr/local/python279/bin/python

import base64
import os
import threading
import paramiko
from binascii import hexlify
from paramiko.py3compat import b, u, decodebytes
from connldap import AuthLdap

class Server (paramiko.ServerInterface):
    # 'data' is the output of base64.b64encode(key)
    # (using the "user_rsa_key" files)
    data = (b'AAAAB3NzaC1yc2EAAAABIwAAAQEAnXvb8NwUWtWjPdNSV5b74QcyKwKXyf6eNBZn025x+AF9W4Mt1WCU5XdzfjGtn4NkLaPUuY7wsXvYt1y7xfOWYnpyTYJ70bSGnpSwI2nlePbW5xNIQYUn8/MoMbDAjcRw6YO69FBYgjUl2HqmSiejaNPbLDUS/JaDTFvKO1kp+VtT5beAaXzisIFJNNlgr7LQcyi5ttaj4pj0csPhwH5ALaG9YLhniBlOyXrdigaK2SgMkasEFmD9VqPfmyT1JcwUs7ns/E01PF4Iq9NLXaREhmV+AyC3Sgf3DuYfIaBwIsbUHPTQIHP6u9GsHaj7GW6BvDeAxT1G3vKpVOUUYbCUJw== root@djt_14_91')
    good_pub_key = paramiko.RSAKey(data=decodebytes(data))

    def __init__(self):
        self.event = threading.Event()
        self.mythreading = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if AuthLdap.login(username, password):
            self.username = username
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        '''
        print('Auth attempt with key: ' + u(hexlify(key.get_fingerprint())))
        if (username == 'robey') and (key == self.good_pub_key):
            return paramiko.AUTH_SUCCESSFUL
        '''
        return paramiko.AUTH_FAILED
    
    def check_auth_gssapi_with_mic(self, username,
                                   gss_authenticated=paramiko.AUTH_FAILED,
                                   cc_file=None):
        """
        .. note::
            We are just checking in `AuthHandler` that the given user is a
            valid krb5 principal! We don't check if the krb5 principal is
            allowed to log in on the server, because there is no way to do that
            in python. So if you develop your own SSH server with paramiko for
            a certain platform like Linux, you should call ``krb5_kuserok()`` in
            your local kerberos library to make sure that the krb5_principal
            has an account on the server and is allowed to log in as a user.
        .. seealso::
            `krb5_kuserok() man page
            <http://www.unix.com/man-page/all/3/krb5_kuserok/>`_
        """
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(self, username,
                                gss_authenticated=paramiko.AUTH_FAILED,
                                cc_file=None):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def enable_auth_gssapi(self):
        return True

    def get_allowed_auths(self, username):
        return 'gssapi-keyex,gssapi-with-mic,password,publickey'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_window_change_request(self, channel, width, height, pixelwidth, pixelheigh):
        channel.win_width = width
        channel.win_height = height
        channel.event = self.mythreading
        channel.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth,
                                  pixelheight, modes):
        channel.win_width = width
        channel.win_height = height
        return True

    def check_channel_exec_request(self, channel, command):
        return True

    def get_loginname(self):
        return self.username

    def get_banner(self):
        return (None, None)
