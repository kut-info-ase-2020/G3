import RPi.GPIO as GPIO
import time

# set GPIO 0 as Mag pin
MagPIN = 14

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
    while True:
        print(GPIO.input(MagPIN))
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
