import RPi.GPIO as GPIO
import time as t
import datetime
import serial
import socket
import json

class Sensor():

    # GPIOのPIN
    MagPIN = 24
    LED = 23
    RLED = 17
    YLED = 22
    GLED = 27
    #基準値
    hourTime = 3600
    min5Time = 10
    ppmOk = 800
    ppmNo = 1000
    #シリアル送信信号
    PACKET = [0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]
    ZERO = [0xff, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78]

    #セットアップ
    def __init__(self):
        # GPIOのセットアップ
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.MagPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.LED,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.RLED,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.YLED,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.GLED,GPIO.OUT,initial=GPIO.LOW)
        #  シリアル通信のセットアップ
        self.s = serial.Serial("/dev/serial0", 9600, timeout=1)
        #　出力データのセットアップ
        self.mag_status_next = 1
        self.PreviousTime = datetime.datetime.now()
        self.nowTime = self.PreviousTime
        t.sleep(2)
    #　現在、窓の開閉
    def getMagstatus(self):
        return GPIO.input(self.MagPIN)

    #　前回の換気時刻と時刻更新有無
    def getPreviousOpenWindow(self, magstatus):
        #　窓が開いた場合
        if self.mag_status_next > magstatus:
            #窓が開いた時刻記録
            self.nowTime = datetime.datetime.now()
            print(self.nowTime)
        #　窓が閉じた場合
        elif self.mag_status_next < magstatus:
            # 5分以上開いてた場合, 換気時刻更新
            if self.getBetweenTime(self.nowTime) >= self.min5Time:
                self.PreviousTime = datetime.datetime.now()
            #窓が閉まった時刻記録
            self.nowTime = datetime.datetime.now()
        #　今回の窓の開閉を記録
        self.mag_status_next = magstatus
        
        return self.nowTime

    #　換気推奨時間超過の有無
    def getOpenWindow(self, NumTime):
        # 現在の換気推奨時間を超えていた場合,
        oktime = self.hourTime/NumTime
        result = self.getBetweenTime(self.PreviousTime) >= oktime and self.mag_status_next
        if result:
                self.setOpenLED(self.LED)
        else:
                self.setCloseLED(self.LED)
        return oktime

    #　現在時刻までの秒単位時間経過
    def getBetweenTime(self, laterTime):
        td = datetime.datetime.now() - laterTime
        return td.seconds

    # 現在のppm
    def getCO2Status(self):
        self.s.write(bytearray(self.PACKET))
        res = bytearray(self.s.read(9))
        checksum = 0xff & (~(res[1] + res[2] + res[3] + res[4] + res[5] + res[6] + res[7]) + 0x01)
        if res[8] == checksum:
            return (res[2] << 8) | res[3]
        else:
            raise Exception("checksum: " + hex(checksum))

    # ppmの基準値超過の有無
    def getCO2over(self, ppmstatus):
        if ppmstatus < self.ppmOk:
            self.setOpenLED(self.GLED)
            self.setCloseLED(self.YLED)
            self.setCloseLED(self.RLED)
        elif ppmstatus > self.ppmNo :
            self.setCloseLED(self.GLED)
            self.setCloseLED(self.YLED)
            self.setOpenLED(self.RLED)
        else:
            self.setCloseLED(self.GLED)
            self.setOpenLED(self.YLED)
            self.setCloseLED(self.RLED)
            
    #CO2キャリブレーション
    def getCO2zero(self):
        self.s.write(bytearray(self.ZERO))

    #　LEDを光らす
    def setOpenLED(self, LED_PIN):
        GPIO.output(LED_PIN,GPIO.HIGH)
    
    #　LEDを消す
    def setCloseLED(self,LED_PIN):
         GPIO.output(LED_PIN,GPIO.LOW)

    #define a destroy function for clean up everything after the script finished
    def close(self):
        GPIO.output(self.LED,GPIO.LOW)
        GPIO.output(self.RLED,GPIO.LOW)
        GPIO.output(self.YLED,GPIO.LOW)
        GPIO.output(self.GLED,GPIO.LOW)
        GPIO.cleanup()
        self.s.close()

class Conect():
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


# if run this script directly ,do:
if __name__ == '__main__':
    s = Sensor()
    c = Conect()
    try:
        s.getCO2zero()
        while True:
            #CO2
            co2_status = s.getCO2Status()
            s.getCO2over(s.getCO2Status())
            
            #データ
            data = {
                "id":2,
                "CO2": co2_status,
            }
            print(data)
            
            c.setsenddata(data)
            send_status = c.getrecvdata()
            print(send_status)
            t.sleep(10)
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        s.close()
        c.close()
