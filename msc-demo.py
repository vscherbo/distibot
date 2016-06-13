#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from time import sleep
import signal 
import sys
import time

class emu_cooker:
    powers = (120, 300, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000)
    max_power_index = len(powers)-1
    power_max = powers[-1]
    power_min = powers[0]
    def __init__(self):
        self.power_index = 6 # 1400W
        self.state_on = False
    def switch_on(self):
        if not self.state_on:
            print("   on")
            self.state_on = True
    def switch_off(self):
        if self.state_on:
            print("   off")
            self.state_on = False
    def power_up(self):
        if self.power_index < self.max_power_index:
            self.power_index += 1
            return True
        else:
            return False
    def power_down(self):
        if self.power_index > 0:
            self.power_index -= 1
            return True
        else:
            return False
    def current_power(self):
        return self.powers[self.power_index]
    def switch_on_600(self):
        self.switch_on()
        while self.current_power() > 600:
            self.power_down():
            print("   ", self.current_power())
    def set_1400(self):
        while self.current_power() < 1400:
            self.power_up()
            print("   ", self.current_power())


def signal_handler(signal, frame):
    global loop_flag
    loop_flag = False
    # log.close()
    # sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Talarms = [25.0, 25.5, 25.9, 999.9] # debug
Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9] # 1st production
T = [75, 76, 77.1, 77.2, 78, 79.1, 83, 84, 85.1, 86, 87, 88.1, 93, 94, 94.6, 97, 98, 98.6]
# Talarms = [94.5, 98.7, 999.9] # tails

def get_temperature():
    global loop_flag
    try:
        Tres = T.pop(0)
    except Exception as exp:
        Tres = 999.0
        loop_flag = False
    return Tres


def watch_heads():
    print("watch_heads")

def start_body(ck):
    print("start_body")

def stop_body():
    print("stop_body")

# log = open('sensor-'+time.strftime("%Y-%m-%d-%H-%M") +'.csv','w', 0) # 0 - unbuffered write
log = open('sensor.csv','w', 0) # 0 - unbuffered write
Talarm = Talarms.pop(0)
alarm_cnt = 0
loop_flag = True
ck = emu_cooker()
ck.switch_on()
Tactions = [ck.switch_off, ck.switch_on_min, watch_heads, ck.set_1400, stop_body, ck.switch_off, ck.switch_off]
while loop_flag:
    temperature_in_celsius = get_temperature()
    print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius), file=log)
    # print(time.strftime("%H:%M:%S")+ ","+ str(temperature_in_celsius))
    if temperature_in_celsius > Talarm:
        Talarm = Talarms.pop(0)
        Taction = Tactions.pop(0)
        print("name=", Taction.__name__)
        Taction()
    sleep(1)

log.close()
sys.exit(0)
