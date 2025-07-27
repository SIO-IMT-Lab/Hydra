# This process waits for and time-stamps a rising edge on on of the
# Raspberry Pi GPIO pins. The purpose is to calibrate the on-board clock using
# the 1 pulse per second (1pps) output from a GPS.
# see: https://roboticsbackend.com/raspberry-pi-gpio-interrupts-tutorial/
# gbd 9/27/20

import time as time
import signal
import sys
import RPi.GPIO as GPIO
BUTTON_GPIO = 16
def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
def button_pressed_callback(channel):
    print("GPIO 16 rising edge detected. at %.8f" % time.time())
    
if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.RISING, 
            callback=button_pressed_callback)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()