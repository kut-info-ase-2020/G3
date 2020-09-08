import socket
import json
import os, sys
import requests
# AF = IPv4 という意味
# TCP/IP の場合は、SOCK_STREAM を使う
url="https://script.google.com/macros/s/AKfycbzTu4MasOfwmuYoIvxCvXpV4cMOCF_vLgyf4SmsjUPz7UN7sjt7/exec"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # IPアドレスとポートを指定
    s.bind(('192.168.0.14', 50007))
    # 1 接続
    s.listen(1)
    # connection するまで待つ
    while True:
        # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
        conn, addr = s.accept()
        print('conect')
        child_pid = os.fork()
        if child_pid == 0:
          with conn:
             try:
                 while True:
                    # データを受け取る
                    data = conn.recv(1024)
                    if not data:
                        break

                    print('data : {}, addr: {}'.format(data, addr))
                    print(os.getpid())
                    # クライアントにデータを返す(b -> byte でないといけない)
                    date = data.decode()
                    json_dict = json.loads(date)
                    
                    if json_dict.get('id') <= 1:
                        strdata = json.dumps(json_data)
                        bindata = strdata.encode()
                        conn.sendall(bindata)
                    else:
                        response = requests.post(url, data=json_dict)
                        print('raspons ok')
                        conn.sendall(b'ok')
             except KeyboardInterrupt:
                conn.close()
                s.close()
          conn.close()

