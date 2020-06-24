#!/usr/bin/env python

import time
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

hallpin = 18
ledpin = 3

gpio.setup( hallpin, gpio.IN)
#gpio.setup(ledpin, gpio.OUT)
#gpio.output(ledpin, False)

found = 0
not_found = 0
while True:
    if(gpio.input(hallpin) == False):
        found += 1
        not_found = 0
        #gpio.output(ledpin, True)
        #print("magnet detected")
    else:
        not_found += 1
        found = 0
        #gpio.output(ledpin, False)
        #print("magnetic field not detected")
    #time.sleep(1)
    print('F={}, N={}'.format(found, not_found))
