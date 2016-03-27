#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from w1thermsensor import W1ThermSensor
from time import sleep
from pushbullet import Pushbullet
import signal 
import sys
import time
import cooker

def signal_handler(signal, frame):
    global loop_flag
    loop_flag = False
    # log.close()
    # sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Talarms = [25.0, 25.5, 25.9, 999.9] # debug
Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9] # 1st production
# Talarms = [94.5, 98.7, 999.9] # tails
alarm_limit = 3

print("Create sensor")
sensor = W1ThermSensor()
print("Sensor is created")

pb = Pushbullet('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP')
# one_plus_one = pb.get_device('OnePlus One')
c = [x for x in pb.channels if x.name == u"Billy's moonshine"][0]


# Title, Message_body
# to device
# push = one_plus_one.push_note("Процесс", "Тело.")
# push = pb.push_note("Hello world!", "We're using the api.", device=one_plus_one)
# to channel
# c.push_note("Hello "+ c.name, "Hello My Channel")

log = open('sensor-'+time.strftime("%Y-%m-%d-%H-%M") +'.csv','w', 0) # 0 - unbuffered write
Talarm = Talarms.pop(0)
alarm_cnt = 0
loop_flag = True
while loop_flag:
    temperature_in_celsius = sensor.get_temperature()
    print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius), file=log)
    # print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius))
    if temperature_in_celsius > Talarm:
        c.push_note("Превысили "+str(Talarm), str(temperature_in_celsius))
        alarm_cnt += 1
        if alarm_cnt >= alarm_limit:
            alarm_cnt = 0
            Talarm = Talarms.pop(0)
    # debug 
    # print("alarm_cnt="+str(alarm_cnt) + " Talarm=" + str(Talarm))
    sleep(5)

log.close()
sys.exit(0)

# sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
# ll /sys/bus/w1/devices/
