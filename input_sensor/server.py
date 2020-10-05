# -*- coding: utf-8 -*-
# python -ver 3.7.0

import socket
import json
import os, sys
import requests
import datetime
import time
import ast
### add pack signal ###
import signal
import time
from multiprocessing import Process, Queue, Event, Pipe

#pid_list=[]

### signal ###
def receive_signal(signum, stack):
    print('receive', signum)

### process ###
def connect_to_process(conn, addr):
    with conn:
        while True:
            data = conn.recv(1024)
            
            if not data:
                break
            print('data: {}, addr: {}'.format(data, addr))
            #print(os.getpid())
            conn.sendall(b'ok') # returned client for 'data'
    #print("pid list is %s ." % pid_list)  
    print('closed')

### sound ###

### change file bin -> json ###
def append_json_to_file(data: dict, path_file: str) -> bool:
    with open(path_file, 'ab+') as f:
        f.seek(0,2)
        if f.tell() == 0:
            f.write(json.dumps([data]).encode())
        else:
            f.seek(-1,2)
            f.truncate()
            f.write(' , '.encode())
            f.write(json.dumps(data).encode())
            f.write(']'.encode())
    return f.close()

signal.signal(signal.SIGCHLD, receive_signal)
signal.signal(signal.SIGTERM, receive_signal)

### main ###
if __name__ == '__main__' :

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 50007)) # IPaddr = server address. 
        s.listen(1)

        # socket loop
        while True:
            print('wait connection...')
            conn, addr = s.accept()
            print('connect')
            ## if connect is "true", do process method.
            p = Process(target=connect_to_process, args=(conn, addr))
            p.start()
            p.join()
