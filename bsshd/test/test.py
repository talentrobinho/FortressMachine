#!/usr/bin/env /usr/local/python279/bin/python



from multiprocessing import Process
import time
import os
import socket

def f(name):
    while True:
        print "hello %s"%name
        time.sleep(1)


def mf(name):
    p = Process(target=f, args=(name,))
    p.start()
    p.join() 
