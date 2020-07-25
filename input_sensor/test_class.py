import RPi.GPIO as GPIO
import time
import datetime


class Sensor ():

    # GPIOのPIN
    MagPIN = 14
    LED = 23
    RLED = 17
    YLED = 22
    GLED = 27
    #基準値
    hourTime = 3600
    min5Time = 300
    ppmOk = 800
    ppmNo = 1000
    #Co2PIN = 

    #セットアップ
    def __init__(self):
        # GPIOのセットアップ
        self.GPIO.setwarnings(False)
        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setup(MagPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.GPIO.setup(LED,GPIO.OUT,initial=GPIO.LOW)
        self.GPIO.setup(RLED,GPIO.OUT,initial=GPIO.LOW)
        self.GPIO.setup(YLED,GPIO.OUT,initial=GPIO.LOW)
        self.GPIO.setup(GLED,GPIO.OUT,initial=GPIO.LOW)
        #  シリアス通信のセットアップ
        #　出力データのセットアップ
        self.mag_status_next = 1
        self.PreviousTime = datetime.datetime.now()
        self.nowTime = self.PreviousTime

    #　現在、窓の開閉
    def getMagstatus(self):
        return GPIO.input(MagPIN)

    #　前回の換気時刻と時刻更新有無
    def getPreviousOpenWindow(self, magstatus):
        #　窓が開いた場合
        if self.mag_status_next < magstatus:
            self.nowTime = datetime.datetime.now()
        #　窓が閉じた場合
        elif self.mag_status_next > magstatus:
            # 5分以上開いてた場合, 換気時刻更新
            if self.getBetweenTime(self.nowTime) >= self.min5Time:
                self.PreviousTime = datetime.datetime.now()
        #　今回の窓の開閉を記録
        self.mag_status_next = magstatus
        return self.PreviousTime

    #　換気推奨時間超過の有無
    def getOpenWindow(self, NnmTime):
        # 現在の換気推奨時間を超えていた場合,
        result = self.getBetweenTime(self.PreviousTime) >= (self.hourTime/NumTime)
        if result: 
                self.setOpenLED(self.LED)
        else:
                self.setCloseLED(self.LED)
        return result
        
    #　現在時刻までの秒単位時間経過
    def getBetweenTime(self, laterTime):
        td = datetime.datetime.now() - laterTime
        return td.seconds

    # 現在のppm
    def getCO2Status(self):
        ppm = random.uniform(600, 1200)
        print(ppm)
        return ppm

    # ppmの基準値超過の有無
    def getCO2over(self, ppmstatus)
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

    #　LEDを光らす
    def setOpenLED(self, LED_PIN):
        self.GPIO.output(LED_PIN,GPIO.HIGH)
    
    #　LEDを消す
    def setCloseLED(self,LED_PIN):
         self.GPIO.output(LED_PIN,GPIO.LOW)

    #define a destroy function for clean up everything after the script finished
    def close(self):
        self.GPIO.output(LED,GPIO.LOW)
        self.GPIO.output(RLED,GPIO.LOW)
        self.GPIO.output(YLED,GPIO.LOW)
        self.GPIO.output(GLED,GPIO.LOW)
        self.GPIO.cleanup()

# if run this script directly ,do:
if __name__ == '__main__':
    s = Sensor()
    try:
        while True:
            print(s.getMagstatus())
            print(s.getOpenWindow(s.getMagstatus()))
            print(s.getPreviousOpenWindow(2))
            print(s.getCO2over(s.getCO2Status))
            time.sleep(0.5)
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        s.close()
