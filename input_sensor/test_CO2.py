import serial
import RPi.GPIO as GPIO
import time
import datetime

s = None
def setup():
    global s
    #シリアル通信の設定
    s = serial.Serial('/dev/serial0',baudrate=9600,bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=1.0)
    print ("start setup")
    time.sleep(60)
    print ("end setup")


def readdata():
    #データをとる日付記述
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    #MH-Z14Aデータ受け取りコマンド送信
    b = bytearray([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
    s.write(b)
    time.sleep(5)
    #データを受け取る
    result = s.read(9)
    #サムチェックを行う
    checksum = (0xFF - ((ord(result[1])+ord(result[2])+ord(result[3])+ord(result[4])+ord(result[5])+ord(result[6])+ord(result[7]))% 256))+ 0x01
    checksumok = 'FAIL'
    if checksum == ord(result[8]):
        checksumok = 'PASS'
    #日付 ＋ pmm ＋ チェックサムクリアの有無
    pmm = (ord(result[2])*256)+ord(result[3])
    data = now + "," + str(pmm) + "pmm ," + checksumok+"\n"
    print (data)


if __name__ == '__main__':
    setup()
    while True:
        readdata()

