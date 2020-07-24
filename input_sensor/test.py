import RPi.GPIO as GPIO
import time
import datetime

# set GPIO 0 as pin
MagPIN = 14
#Co2PIN = 

#setup function for some setup---custom function
def setup():
    GPIO.setwarnings(False)
    #set the gpio modes to BCM numbering
    GPIO.setmode(GPIO.BCM)
    #set LEDPIN's mode to output,and initial level to LOW(0V
#set LEDPIN's mode to output,and initial level to LOW(0V)
    GPIO.setup(MagPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#main function
def main():
   #print info
    print('start')
    mag_status_next = 0
    time_Previous = datetime.datetime.now()
    while True:
        mag_status = GPIO.input(MagPIN)
        time_Later = datetime.datetime.now() - time_Previous
        if mag_status != mag_status_next:
           if mag_status < mag_status_next:
             time_Previous = datetime.datetime.now()
           else:
             print(str(time_Later))
        if time_Later.seconds >= 3600:
           time_Previous = datetime.datetime.now()
           print('1 hour over') 
        mag_status_next = mag_status
        time.sleep(0.5)

#define a destroy function for clean up everything after the script finished
def destroy():
    #release resource
    GPIO.cleanup()

# if run this script directly ,do:
if __name__ == '__main__':
    setup()
    try:
            main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        destroy()
