#!/usr/bin/env python

import time
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

gpio_hs = 18

def hall_callback(arg):
    global field
    field = gpio.input(arg)
    #print('inside arg={}, field={}'.format(arg, bool(field)))
    print('inside arg={}, field={}, prev={}'.format(arg, field, prev))
    
gpio.setup(gpio_hs, gpio.IN, pull_up_down=gpio.PUD_UP)
#
#GPIO.remove_event_detect(gpio_hs)
#gpio.add_event_detect(gpio_hs, gpio.RISING)
#gpio.add_event_detect(gpio_hs, gpio.FALLING)

print('start input={}'.format(gpio.input(gpio_hs)))
field = gpio.input(gpio_hs)
prev = field
#print('start field={}'.format(bool(field)))
print('start field={}'.format(field))
gpio.add_event_detect(gpio_hs, gpio.BOTH)
gpio.add_event_callback(gpio_hs, callback=hall_callback)
while True:
    print('loop field={}, prev={}'.format(bool(field), bool(prev) ))
    time.sleep(1)
    if field != prev:
        print('CHANGED field={}, prev={}'.format(bool(field), bool(prev) ))
        prev = field
    #print('inside arg={}'.format(arg))

"""
found = 0
not_found = 0
while True:
    if gpio.input(gpio_hs):
        found += 1
        not_found = 0
        #gpio.output(ledpin, True)
        #print("magnet detected")
        print('{}^{}^{}'.format(time.strftime('%s'), found, not_found))
    else:
        not_found += 1
        found = 0
        #print("magnetic field not detected")
    #time.sleep(1)

    #print('{}^{}^{}'.format(time.strftime('%s'), found, not_found))
"""
