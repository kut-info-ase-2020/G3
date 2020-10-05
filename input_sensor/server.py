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
from multiprocessing import Process, Queue, Event, Pipe

#pid_list=[]
#サーバープログラムver4、ファイルを生成し、まとめて送れる様になった。
url="https://script.google.com/macros/s/AKfycbzTu4MasOfwmuYoIvxCvXpV4cMOCF_vLgyf4SmsjUPz7UN7sjt7/exec"
file_send_time = 30
#start_time = 0

### signal ###
def receive_signal(signum, stack):
    print('------ receive signum is :', signum)

### time ###
#def time_measure():
#    time.time()

### process ###
def connect_to_process(conn, addr):
    with conn:
        start_time = time.time()
        while True:
            data = conn.recv(1024)  
            if not data:
                break
            print('data: {}, addr: {}'.format(data, addr))
            # change .bin -> .json
            data = data.decode()
            json_dict = json.loads(data)

            if json_dict.get('id') == 1:
                alarm_sound(json_dict)
            else:
                json_dict["Day"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
                file_name = 'test' + str(json_dict.get('id')) + '.json'
                append_json_to_file(json_dict, file_name)

                if(time.time() - start_time ) > file_send_time:
                    with open(file_name,'r') as f:
                        json_list = json.load(f)
                    #jsonファイル内のデータを送信
                    response = requests.post(url, data=json.dumps(json_list))
                    #Google sheetsからのレスポンス確認
                    print('raspons ' + response.text)
                    #ファイル削除によってログデータリセット
                    os.remove(file_name)
                    #再度、時間計測
                    start_time = time.time()
            conn.sendall(b'ok') # returned client for 'data'
    #print("pid list is %s ." % pid_list)  
    print('closed')
    conn.close()


### sound ### 
def alarm_sound(json_dict): 
    with open("./sample.json", "r") as f:
        flg_data = json.load(f)
        strnum = json.dumps(flg_data)
        bindata = strnum.encode()

### add writing to json file ###
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
    ### socket set ###
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 50007)) # IPaddr = server address. 
        s.listen(1)

        while True:
            print('wait connection...')
            conn, addr = s.accept()
            print('connect')
            ## if connect is "true", do process method.
            p = Process(target=connect_to_process, args=(conn, addr))
            p.start()
            p.join()
