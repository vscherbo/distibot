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

# one_plus_one = pb.get_device('OnePlus One')
# Title, Message_body
# to device
# push = one_plus_one.push_note("Процесс", "Тело.")
# push = pb.push_note("Hello world!", "We're using the api.", device=one_plus_one)
# to channel
# c.push_note("Hello "+ c.name, "Hello My Channel")

class Moonshine_controller:
    def __init__(self):
        self.sensor = W1ThermSensor()
        self.cooker = cooker.Cooker(gpio_on_off= 17, gpio_up = 22, gpio_down = 27)
        self.valve = valve.Valve(ways = 2, gpio_1_2 = 23)
        self.heads_sensor = heads_sensor.Heads_sensor(gpio_heads_start = 25, gpio_heads_stop = 14)
        self.pb = Pushbullet('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP')
        self.pb_channel = [x for x in self.pb.channels if x.name == u"Billy's moonshine"][0]
    def __del__(self):
        RPIO.cleanup()
    def start_process(self):
        self.cooker.switch_on()
        self.cooker.power_max()
    def heads_started(self, gpio_id, value):
        self.pb_channel.push_note("Стартовали головы", "gpio_id="+str(gpio_id)+ ", value="+str(value))

    def start_watch_heads(self):
        self.valve.way_1()
        self.heads_sensor.watch_start(self.heads_started), 
        self.heads_sensor.watch_stop(self.valve.way_2), 
    def stop_body(self):
        self.valve.way_3()
    def finish(self):
        self.cooker.switch_off()
