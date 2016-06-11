#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
#import RPi.GPIO as GPIO
import RPIO

RPIO.setmode(RPIO.BCM)

"""
ngpio=17
GPIO.setup(ngpio, GPIO.OUT)     #конфигурируем GPIO 7 как выход
GPIO.output(ngpio, True)               #выводим на GPIO 7 логическую "1" (3.3 V)
sleep(1)
GPIO.output(ngpio, False)              #выводим на GPIO 7 логический "0"
sleep(2)
GPIO.output(ngpio, True)               #выводим на GPIO 7 логическую "1" (3.3 V)
"""

def gpio_callback(gpio_id, val):
    print("gpio %s: %s" % (gpio_id, val))

ngpio=14

RPIO.setup(ngpio, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
RPIO.add_interrupt_callback(ngpio, gpio_callback, edge='rising', debounce_timeout_ms=100, pull_up_down=RPIO.PUD_DOWN)
#        , threaded_callback=True)

RPIO.wait_for_interrupts(threaded=True)

n = 0
while True:
    sleep(1)
    n += 1
    print n

RPIO.cleanup() 
