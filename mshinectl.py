#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from pushbullet import Pushbullet
import time
import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
import RPIO_wrap.RPIO as RPIO
import cooker
import valve
import heads_sensor
import collections
import tsensor

# one_plus_one = pb.get_device('OnePlus One')
# Title, Message_body
# to device
# push = one_plus_one.push_note("Процесс", "Тело.")
# push = pb.push_note("Hello world!",
#                     "We're using the api.",
#                     device=one_plus_one)
# to channel
# c.push_note("Hello "+ c.name, "Hello My Channel")


class pb_wrap(Pushbullet):

    def __init__(self, api_key, emu_mode=False):
        self.emu_mode = emu_mode
        if emu_mode:
            self.channels = []
        else:
            super(pb_wrap, self).__init__(api_key)

    def get_channel(self, channel_name=u"Billy's moonshine"):
        if self.emu_mode:
            return pb_channel_emu()
        else:
            return [x for x in self.channels if x.name == channel_name][0]


class pb_channel_emu(object):

    def push_note(self, subject, body):
        pass


class Moonshine_controller(object):

    def __init__(self, emu_mode=False):
        self.Tcmd_prev = 'before start'
        self.Tcmd_last = 'before start'
        self.alarm_limit = 1
        self.downcount_limit = 5
        self.csv_write_period = 3
        self.alarm_cnt = 0
        self.T_sleep = 1
        self.sensor = tsensor.Tsensor(emu_mode)
        self.log = open('sensor-' + ('emu-' if self.sensor.emu_mode else '')
                        + time.strftime("%Y-%m-%d-%H-%M")
                        + '.csv', 'w', 0)  # 0 - unbuffered write
        self.T_prev = self.sensor.get_temperature()
        self.loop_flag = True
        self.cooker = cooker.Cooker(gpio_on_off=17, gpio_up=22, gpio_down=27)
        self.valve = valve.DoubleValve(gpio_v1=23, gpio_v2=24)
        self.heads_sensor = heads_sensor.Heads_sensor(gpio_heads_start=25,
                                                      gpio_heads_stop=14,
                                                      timeout=2000)
        self.pb = pb_wrap('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP', emu_mode)
        self.pb_channel = self.pb.get_channel()

    def load_config(self, conf_file_name):
        conf = open(conf_file_name, 'r')
        self.Tsteps = collections.OrderedDict(sorted(eval(conf.read()).items(),
                                              key=lambda t: t[0]))
        conf.close()
        self.set_Tsteps()

    def set_Tsteps(self):
        self.Tkeys = self.Tsteps.keys()
        self.Talarm = self.Tkeys.pop(0)
        self.Tcmd = self.Tsteps.pop(self.Talarm)
        # print(self.Tsteps)

    def release(self):
        self.cooker.release()
        self.valve.release()
        self.heads_sensor.release()
        RPIO.cleanup()

    def temperature_loop(self):
        downcount = 0
        csv_delay = 0
        # T_increase = 0
        print_str = []
        while self.loop_flag:
            self.temperature_in_celsius = self.sensor.get_temperature()
            # слежение за снижением температуры
            if self.T_prev > self.temperature_in_celsius:
                downcount += 1
                if downcount >= self.downcount_limit:
                    self.pb_channel.push_note("Снижение температуры", "Включаю нагрев")
                    self.cooker.set_power_600()
                    downcount = 0
            elif self.T_prev < self.temperature_in_celsius:
                downcount = 0
                # T_increase = self.temperature_in_celsius
            self.T_prev = self.temperature_in_celsius

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
                    else:
                        self.Tcmd = self.Tsteps.pop(self.Talarm)

            print_str.append(time.strftime("%H:%M:%S"))
            print_str.append(str(self.temperature_in_celsius))
            if self.Tcmd_last != self.Tcmd_prev:
                print_str.append(self.Tcmd_last)
                self.Tcmd_prev = self.Tcmd_last
                print(','.join(print_str), file=self.log)
            if csv_delay >= self.csv_write_period:
                csv_delay = 0
                print(','.join(print_str), file=self.log)

            print_str = []
            csv_delay += self.T_sleep
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

    def stop_process(self):
        self.loop_flag = False
        time.sleep(self.T_sleep+0.5)

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
        self.valve.way_2()
        self.heads_sensor.ignore_stop(),

    def start_watch_heads(self):
        self.valve.way_1()
        self.heads_sensor.watch_start(self.heads_started)

    def wait4body(self):
        self.cooker.switch_on()
        self.valve.way_2()

    def stop_body_power_on(self):
        self.stop_body()

    def stop_body(self):
        self.valve.way_3()
        self.pb_channel.push_note("Закончилось тело",
                                  "Клапан выключен")

    def finish(self):
        self.release()
