#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from w1thermsensor import W1ThermSensor
from pushbullet import Pushbullet
import time
import RPIO
import cooker
import valve
import heads_sensor

# one_plus_one = pb.get_device('OnePlus One')
# Title, Message_body
# to device
# push = one_plus_one.push_note("Процесс", "Тело.")
# push = pb.push_note("Hello world!",
#                     "We're using the api.",
#                     device=one_plus_one)
# to channel
# c.push_note("Hello "+ c.name, "Hello My Channel")


class Moonshine_controller(object):

    def __init__(self, log):
        self.log = log
        self.sensor = W1ThermSensor()
        self.cooker = cooker.Cooker(gpio_on_off=17, gpio_up=22, gpio_down=27)
        self.valve = valve.Valve(gpio_1_2=23)
        self.valve.default_way()
        self.heads_sensor = heads_sensor.Heads_sensor(gpio_heads_start=25,
                                                      gpio_heads_stop=14,
                                                      timeout=2000)
        self.pb = Pushbullet('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP')
        self.pb_channel = [x for x in self.pb.channels
                           if x.name == u"Billy's moonshine"][0]

    def release(self):
        self.cooker.release()
        self.valve.release()
        self.heads_sensor.release()
        RPIO.cleanup()

    def do_nothing(self, gpio_id=-1, value="-1"):
        print("do_nothing "
              + time.strftime("%H:%M:%S")
              + ", gpio_id=" + str(gpio_id)
              + ", value=" + str(value), file=self.log)
        pass

    def start_process(self):
        self.cooker.switch_on()
        self.cooker.set_power_max()

    def heads_started(self, gpio_id, value):
        try:
            int(value)
        except ValueError:
            print("heads_started BAD value="+str(value))
            value = -1
        self.pb_channel.push_note("Стартовали головы",
                                  "gpio_id=" + str(gpio_id)
                                  + ", value=" + str(value))
        self.heads_sensor.ignore_start()

    def heads_finished(self, gpio_id, value):
        try:
            int(value)
        except ValueError:
            print("heads_finished BAD value="+str(value))
            value = -1
        self.pb_channel.push_note("Закончились головы",
                                  "gpio_id=" + str(gpio_id)
                                  + ", value=" + str(value))
        self.valve.default_way()
        self.heads_sensor.ignore_stop(),

    def start_watch_heads(self):
        self.valve.power_on_way()
        self.heads_sensor.watch_start(self.heads_started)
        self.heads_sensor.watch_stop(self.heads_finished)

    def wait4body(self):
        self.cooker.switch_on()
        self.valve.power_on_way()

    def stop_body_power_on(self):
        self.valve.power_on_way()
        self.pb_channel.push_note("Закончилось тело",
                                  "Клапан включён")

    def stop_body(self):
        self.valve.default_way()
        self.pb_channel.push_note("Закончилось тело",
                                  "Клапан выключен")

    def finish(self):
        #self.cooker.switch_off()
        #self.valve.default_way()
        self.release()
