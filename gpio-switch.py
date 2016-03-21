#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

ngpio=17
#GPIO.cleanup() 
GPIO.setup(ngpio, GPIO.OUT)     #конфигурируем GPIO 7 как выход
GPIO.output(ngpio, True)               #выводим на GPIO 7 логическую "1" (3.3 V)
sleep(3)
GPIO.output(ngpio, False)              #выводим на GPIO 7 логический "0"
sleep(2)
GPIO.output(ngpio, True)               #выводим на GPIO 7 логическую "1" (3.3 V)
GPIO.cleanup() 
