# Toggle GPIO12 to test logeventtime.py
# gbd 9/27/20

from gpiozero import LED
from time import sleep

led = LED(12)

while True:
    led.on()
    sleep(0.001)
    led.off()
    sleep(0.9978)