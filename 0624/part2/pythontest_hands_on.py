#!/usr/bin/python

###########################################################################
#Filename      :pythontest.py
#Description   :blink LED
#Author        :alan
#Website       :www.osoyoo.com
#Update        :2017/06/20
############################################################################

import RPi.GPIO as GPIO
import time

# set GPIO 0 as LED pin
LEDPIN = 17
LEDPIN_2 = 27

#print message at the begining ---custom function
def print_message():
    print ('|********************************|')
    print ('|            blink LED           |')
    print ('|      ------------------------- |')
    print ('|        LED connect to GPIO0    |')
    print ('|                                |')
    print ('|        LED will blink at 500ms |')
    print ('|      ------------------------- |')
    print ('|                                |')
    print ('|                          OSOYOO|')
    print ('|********************************|\n')
    print ('Program is running...')
    print ('Please press Ctrl+C to end the program...')

#setup function for some setup---custom function
def setup():
    GPIO.setwarnings(False)
    #set the gpio modes to BCM numbering
    GPIO.setmode(GPIO.BCM)
    #set LEDPIN's mode to output,and initial level to LOW(0V)
    GPIO.setup(LEDPIN,GPIO.OUT,initial=GPIO.LOW)

    GPIO.setup(LEDPIN_2,GPIO.OUT,initial=GPIO.LOW)

#main function
def main():
    #print info
    print_message()
    while True:
       GPIO.output(LEDPIN,GPIO.HIGH)
       GPIO.output(LEDPIN_2,GPIO.HIGH)
       print('...LED ON\n')
       time.sleep(0.5)
       
       GPIO.output(LEDPIN,GPIO.LOW)
       GPIO.output(LEDPIN_2,GPIO.LOW)
       print('LED OFF...\n')
       time.sleep(0.5)
       pass
    pass

#define a destroy function for clean up everything after the script finished
def destroy():
    #turn off LED
    GPIO.output(LEDPIN,GPIO.LOW)
    GPIO.output(LEDPIN_2,GPIO.LOW)
    #release resource
    GPIO.cleanup()
#
# if run this script directly ,do:
if __name__ == '__main__':
    setup()
    try:
            main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        destroy()

   
