#!/usr/bin/env /usr/local/python279/bin/python



from multiprocessing import Process
import time
import os
import socket
from test import mf
import traceback
import sys

def sss():
    # now connect
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 11111))
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

    try:
        sock.listen(100)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
    #while True:
    for n in ['aaa', 'bbb', 'ccc']:
        mf(n)

sss()
