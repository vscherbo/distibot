#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from w1thermsensor import W1ThermSensor
from pushbullet import Pushbullet
import time
import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
import RPIO
import cooker
import valve
import heads_sensor
import collections

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

    def __init__(self):
        self.Tcmd_prev = 'before start'
        self.Tcmd_last = 'before start'
        self.alarm_limit = 3
        self.alarm_cnt = 0
        self.T_sleep = 5
        self.log = open('sensor-'
                        + time.strftime("%Y-%m-%d-%H-%M")
                        + '.csv', 'w', 0)  # 0 - unbuffered write
        self.sensor = W1ThermSensor()
        self.temperature_in_celsius = 0
        self.T_prev = 0
        self.T_curr = 0
        self.loop_flag = True
        self.cooker = cooker.Cooker(gpio_on_off=17, gpio_up=22, gpio_down=27)
        self.valve = valve.Valve(gpio_1_2=23)
        self.valve.default_way()
        self.heads_sensor = heads_sensor.Heads_sensor(gpio_heads_start=25,
                                                      gpio_heads_stop=14,
                                                      timeout=2000)
        self.pb = Pushbullet('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP')
        self.pb_channel = [x for x in self.pb.channels
                           if x.name == u"Billy's moonshine"][0]

    def load_config(self, conf_file_name): 
        conf = open(conf_file_name, 'r')
        Tsteps = collections.OrderedDict(sorted(eval(conf.read()).items(), key=lambda t: t[0]))
        conf.close()
        self.set_Tsteps(Tsteps)

    def set_Tsteps(self, Tsteps):
        self.Tkeys = Tsteps.keys()
        self.Talarm = self.Tkeys.pop(0)
        self.Tcmd = Tsteps.pop(self.Talarm)

    def release(self):
        self.cooker.release()
        self.valve.release()
        self.heads_sensor.release()
        RPIO.cleanup()

    def temperature_loop(self):
        downcount = 0
        while self.loop_flag:
            self.temperature_in_celsius = self.sensor.get_temperature()
            if self.T_prev > self.temperature_in_celsius:
                downcount += 1
                if downcount >= 3:
                    self.pb_channel.push_note("Снижение температуры", "Включаю плитку") 
                    self.cooker.set_power_600()
                    downcount = 0
            else:
                self.T_prev = self.temperature_in_celsius
                downcount = 0

            if self.temperature_in_celsius > self.Talarm:
                self.Tcmd_last = self.Tcmd.__name__
                self.pb_channel.push_note("Превысили " + str(self.Talarm),
                                          str(self.temperature_in_celsius)
                                          + ", Tcmd=" + str(self.Tcmd.__name__))

                self.Tcmd()
                self.alarm_cnt += 1
                if self.alarm_cnt >= self.alarm_limit:
                    self.alarm_cnt = 0
                    try:
                        self.Talarm = self.Tkeys.pop(0)
                    except IndexError:
                        self.Talarm = 999.0
                        self.Tcmd = self.do_nothing

            csv_prefix = time.strftime("%H:%M:%S") + "," + str(self.temperature_in_celsius)
            if self.Tcmd_last == self.Tcmd_prev:
                print(csv_prefix, file=self.log)
            else:
                print(csv_prefix + "," + self.Tcmd_last, file=self.log)
                self.Tcmd_prev = self.Tcmd_last
            time.sleep(self.T_sleep)

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
        self.heads_sensor.watch_stop(self.heads_finished)
        # including heads_sensor.ignore_start()

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
        # self.cooker.switch_off()
        # self.valve.default_way()
        self.release()
