#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from w1thermsensor import W1ThermSensor
from time import sleep
from pushbullet import Pushbullet
import signal
import sys
import time
import thread


def signal_handler(signal, frame):
    global loop_flag
    loop_flag = False
    # log.close()
    # sys.exit(0)


def temperature_loop(Talarms):
    global loop_flag
    global log
    global temperature_in_celsius
    Talarm = Talarms.pop(0)
    alarm_cnt = 0
    while loop_flag:
        temperature_in_celsius = sensor.get_temperature()
        print("%s%s", time.strftime("%H:%M:%S"), temperature_in_celsius,
              sep=',', file=log)
        if temperature_in_celsius > Talarm:
            c.push_note("Превысили "+str(Talarm), str(temperature_in_celsius))
            alarm_cnt += 1
            if alarm_cnt >= alarm_limit:
                alarm_cnt = 0
                Talarm = Talarms.pop(0)
        sleep(5)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Talarms = [25.0, 25.5, 25.9, 999.9]  # debug
# Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9]  # 1st production
Talarms = [94.5, 98.7, 999.9]  # tails
alarm_limit = 3

pb = Pushbullet('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP')
c = [x for x in pb.channels if x.name == u"Billy's moonshine"][0]

print("Create sensor")
sensor = W1ThermSensor()
print("Sensor is created")
# 0 - unbuffered write
log = open('sensor-' + time.strftime("%Y-%m-%d-%H-%M") + '.csv', 'w', 0)
loop_flag = True
temperature_in_celsius = 0

try:
    thread.start_new_thread(temperature_loop, (Talarms,))
except Exception, exc:
    print("Error: unable to start thread, exception=%s" % str(exc))

demo_cnt = 0
while demo_cnt < 5:
    sleep(5)
    demo_cnt += 1
    # print("demo loop %s" % demo_cnt)
    print("T=%s" % temperature_in_celsius)

log.close()
sys.exit(0)

# sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
# ll /sys/bus/w1/devices/
