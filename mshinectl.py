#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from w1thermsensor import W1ThermSensor
from time import sleep
from pushbullet import Pushbullet
import signal 
import sys
import time
import RPIO
import cooker
import valve
import heads_sensor

def signal_handler(signal, frame):
    global loop_flag
    loop_flag = False
    # log.close()
    # sys.exit(0)

def do_cmd(Tcmd):



signal.signal(signal.SIGINT, signal_handler)

RPIO.cleanup()

alarm_limit = 3


# one_plus_one = pb.get_device('OnePlus One')
# Title, Message_body
# to device
# push = one_plus_one.push_note("Процесс", "Тело.")
# push = pb.push_note("Hello world!", "We're using the api.", device=one_plus_one)
# to channel
# c.push_note("Hello "+ c.name, "Hello My Channel")

#cooker = Cooker(gpio_on_off= 22, gpio_up = 27, gpio_down = 17)
#valve = Valve(ways = 2, gpio_1_2 = 23)
#heads_sensor = Heads_sensor(gpio_heads_start = 25, gpio_heads_stop = 14)

class Moonshine_controller:
    def __init__(self):
        RPIO.cleanup()
        self.sensor = W1ThermSensor()
        self.cooker = Cooker(gpio_on_off= 22, gpio_up = 27, gpio_down = 17)
        self.valve = Valve(ways = 2, gpio_1_2 = 23)
        self.heads_sensor = Heads_sensor(gpio_heads_start = 25, gpio_heads_stop = 14)
        self.pb = Pushbullet('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP')
        self.pb_channel = [x for x in pb.channels if x.name == u"Billy's moonshine"][0]
    def __del__(self):
        RPIO.cleanup()
    def start_process(self):
        self.cooker.switch_on()
        self.cooker.power_max()
    def heads_started():
        self.pb_channel.push_note("Стартовали головы"+str(Talarm), str(temperature_in_celsius))

    def start_watch_heads():
        self.valve.way_1()
        self.heads_sensor.watch_start(self.heads_started), 
        self.heads_sensor.watch_stop(self.valve.way_2), 
    def stop_body():
        self.valve.way_3()
    def finish():
        self.cooker.switch_off()

def do_nothing():
    pass

mshinectl = Moonshine_controller()

#Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9] # 1st production
Tprocess = {'stop_cooker': 77.0, 
           'start_cooker': 79.0, 
           'watch_heads': 85.0, 
           'body_stop': 94.5, 
           'finish': 98.5, 
           'fake_last': 999.9] # 1st production
Talarms = Tprocess.values()
Tcmds = Tprocess.keys()

Tsteps = {0.0 : mshinectl.start_process
          77.0: mshinectl.cooker.switch_off, 
          79.0: mshinectl.cooker.set_power_600, 
          85.0: mshinectl.start_watch_heads, 
          94.5, mshinectl.stop_body,
          98.5, mshinectl.finish,
          999.9: do_nothing] # 1st production


# Talarms = [94.5, 98.7, 999.9] # tails

log = open('sensor-'+time.strftime("%Y-%m-%d-%H-%M") +'.csv','w', 0) # 0 - unbuffered write
(Talarm, Tcmd) = Tprocess.popitem(0)
alarm_cnt = 0
loop_flag = True
while loop_flag:
    temperature_in_celsius = mshinectl.sensor.get_temperature()
    print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius), file=log)
    # print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius))
    if temperature_in_celsius > Talarm:
        c.push_note("Превысили "+str(Talarm), str(temperature_in_celsius))
        Tcmd
        alarm_cnt += 1
        if alarm_cnt >= alarm_limit:
            alarm_cnt = 0
            (Talarm, Tcmd) = Tprocess.popitem(0)
    # debug 
    # print("alarm_cnt="+str(alarm_cnt) + " Talarm=" + str(Talarm))
    sleep(5)

log.close()
sys.exit(0)

# sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
# ll /sys/bus/w1/devices/
