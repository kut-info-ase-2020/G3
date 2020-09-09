# coding:utf-8
import pygame.mixer
import time
import socket
import json

class Connect():
    def __init__(self):
       self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.s.connect(('192.168.0.8', 50007))
       
    def setsenddata(self, data):
        strdata = json.dumps(data)
        bindata = strdata.encode()
        # サーバにメッセージを送る
        self.s.sendall(bindata)
        
    def getrecvdata(self):
        # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
        data = self.s.recv(1024)
        return data
    
    def close(self):
        self.s.close()


if __name__=='__main__':
    c = Connect()
    try:
      pygame.mixer.init()
      while True:
        c.setsenddata({"id":1})
        
        status = c.getrecvdata()
        
        if status == '1':
          
          pygame.mixer.music.load("alarm.mp3")

          pygame.mixer.music.play(-1)

        else:
          pygame.mixer.music.stop()
          
        time.sleep(60)
    except KeyboardInterrupt:
      c.close()
    
    
