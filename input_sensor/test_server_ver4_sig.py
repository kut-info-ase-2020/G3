# -*- coding: utf-8 -*-

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
from multiprocessing import Process, Queue, Event


#サーバープログラムver4、ファイルを生成し、まとめて送れる様になった。
url="https://script.google.com/macros/s/AKfycbzTu4MasOfwmuYoIvxCvXpV4cMOCF_vLgyf4SmsjUPz7UN7sjt7/exec"
#ファイル送信時間
time_file = 30

#jsonファイルの追加書き込み
def append_json_to_file(data: dict, path_file: str) -> bool:
  with open(path_file, 'ab+') as f:#ファイルを開く
    f.seek(0,2)#ファイルの末尾（2）に移動（フォフセット0）
    if f.tell() == 0 :#ファイルが空かチェック
        f.write(json.dumps([data]).encode())#空の場合は JSON 配列を書き込む
    else :
        f.seek(-1,2)#ファイルの末尾（2）から -1 文字移動
        f.truncate()#最後の文字を削除し、JSON 配列を開ける（]の削除）
        f.write(' , '.encode())#配列のセパレーターを書き込む
        f.write(json.dumps(data).encode())#辞書をJSON形式でダンプ書き込み
        f.write(']'.encode())#JSON配列を閉じる
  return f.close() #連続で追加する場合は都度 Open,Closeしない方がいいかも

#signal
def receive_signal(signum, stack):
    print("receive signal")
    child_pid.join()

#ソケットの設定開始
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # IPアドレスとポートを指定
    s.bind(('192.168.11.12', 50007))
    # 1 接続
    s.listen(1)
    # connection するまで待つ

    ### signal setting
    signal.signal(signal.SIGCHLD, receive_signal)
    signal.signal(signal.SIGTERM, receive_signal)

    while True:
        # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
        conn, addr = s.accept()
        print('conect')
        
        #プロセス作成
        child_pid = os.fork()
        
        #子プロセス処理
        if child_pid == 0:
          with conn:
             #時間計測開始
             start_time = time.time()
             while True:
                # データを受け取る
                data = conn.recv(1024)
                if not data:
                    break
                #送信データ確認用
                print('data : {}, addr: {}'.format(data, addr))
                print(os.getpid())
                # バイナリデータをstr→dictデータに変換
                date = data.decode()
                json_dict = json.loads(date)
                
                #id=1のみ、音を鳴らす処理のみなので隔離
                if json_dict.get('id') == 1:
                    with open("./sample.json", "r") as f:
                       flg_data = json.load(f)
                    strnum = json.dumps(flg_data)
                    bindata = strnum.encode()
                    
                    
                else:
                    #記録時刻書き込み
                    json_dict["Day"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
                    #jsonファイルをidごとに区分け
                    #->IDごとに分けないファイル内でごちゃ混ぜをしたい
                    #その場合、時間になると、送信する専用のプロセスを生成する様にしたい（id=1のプロセスを利用する）
                    file_name = 'test' + str(json_dict.get('id')) + '.json'
                    #jsonファイルへの書き込み
                    append_json_to_file(json_dict, file_name)
                    
                    #経過時間まで実行されない
                    if (time.time()-start_time) > time_file :
                        #jsonファイル読み込み
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
                    #通信相手に処理の終了を知らせる
                    conn.sendall(b'ok')
          print('close')
          conn.close()
