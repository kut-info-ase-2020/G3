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
from multiprocessing import Process, Queue, Event, Pipe, Manager

#pid_list=[]
#サーバープログラムver4、ファイルを生成し、まとめて送れる様になった。
url="https://script.google.com/macros/s/AKfycbzTu4MasOfwmuYoIvxCvXpV4cMOCF_vLgyf4SmsjUPz7UN7sjt7/exec"
file_send_time = 60
#start_time = 0

### signal ###
def receive_signal(signum, stack):
    p.join()
    print('------ receive signum is :', signum)

### time ###
#def time_measure():
#    time.time()

### process ###
def connect_to_process(conn, addr, d):
    with conn:
        while True:
            try:
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

                    if(time.time() - d.get('time') ) > file_send_time:
                        with open(file_name,'r') as f:
                            json_list = json.load(f)
                        #jsonファイル内のデータを送信
                        response = requests.post(url, data=json.dumps(json_list))
                        #Google sheetsからのレスポンス確認
                        print('raspons ' + response.text)
                        #ファイル削除によってログデータリセット
                        os.remove(file_name)
                        #再度、時間計測
                        d['time'] = time.time()
                    
                    #送られたデータ保管
                    if json_dict.get('id') == 3:
                        d['metre_NG'] = json_dict.get('metre_NG')
                        d['num'] = json_dict.get('num')
                        print(d.get('metre_NG'))
                        print(d.get('num'))
                    
                    #室内の人数を送り返し
                    if json_dict.get('id') == 4:
                        strnum = json.dumps(d.get('num'))
                        bindata = strnum.encode()
                        conn.sendall(bindata)
                    else:
                        #通信相手に処理の終了を知らせる
                        conn.sendall(b'ok')# returned client for 'data' 
            except Exception as e: 
                print('closed')
                conn.close()
                p.kill()
    #print("pid list is %s ." % pid_list)  
    print('closed')
    conn.close()




### sound ### 
def alarm_sound(json_dict): 
    strnum = json.dumps(d.get('metre_NG'))
    bindata = strnum.encode()
    conn.sendall(bindata)

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
p = 0
### main ###
if __name__ == '__main__' :
    ### socket set ###
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 50007)) # IPaddr = server address. 
        s.listen(1)
        #共有メモリ
        with Manager() as manager:
            # マネージャーから辞書型を生成します.
            d = manager.dict()
            d['metre_NG'] = 0
            d['num'] = 1
            d['time'] = time.time()
            
            while True:
                print('wait connection...')
                conn, addr = s.accept()
                print('connect')
                ## if connect is "true", do process method.
                p = Process(target=connect_to_process, args=(conn, addr, d))
                p.start()

