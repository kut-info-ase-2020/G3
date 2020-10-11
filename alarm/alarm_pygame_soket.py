# coding:utf-8
import pygame.mixer
import time
import socket
import json

class Connect():
    def __init__(self):
       self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.s.connect(('192.168.0.35', 50007))
       
    def setsenddata(self, data):
        strdata = json.dumps(data)
        bindata = strdata.encode()
        # サーバにメッセージを送る
        self.s.sendall(bindata)
        
    def getrecvdata(self):
        #ネットワークのバッファサイズは1024。サーバからの文字列を取得する
        data = self.s.recv(1024)
        return data
    
    def close(self):
        self.s.close()


if __name__=='__main__':
    c = Connect()
    try:
      pygame.mixer.init()
      pygame.mixer.music.load("Warning-Alarm.mp3")
      p_ststus = 0
      while True:
        c.setsenddata({"id":1})
        status = int(c.getrecvdata())
        print(status)
        
        if status > p_ststus:
          pygame.mixer.music.play(-1)

        elif status < p_ststus:
          pygame.mixer.music.stop()
          
        p_ststus = status
          
        time.sleep(10)
    except KeyboardInterrupt:
      c.close()
    
    
