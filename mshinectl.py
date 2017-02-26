#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
from pushbullet import Pushbullet
import time
import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
# import RPIO_wrap.RPIO as RPIO
import RPIO
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
        self.downcount = 0
        self.downcount_limit = 5  # количество шагов подряд с неожидаемым снижением температуры
        self.csv_write_period = 3
        self.stage = 'start'
        self.temperature_in_celsius = 0
        self.current_ts = time.localtime()
        self.pause_start_ts = 0
        self.pause_limit = 180
        self.T_sleep = 1
        self.csv_delay = 0
        self.print_str = []
        self.sensor = tsensor.Tsensor(emu_mode)
        self.log = open('sensor-' + ('emu-' if self.sensor.emu_mode else '')
                        + time.strftime("%Y-%m-%d-%H-%M")
                        + '.csv', 'w', 0)  # 0 - unbuffered write
        self.T_prev = self.sensor.get_temperature()
        self.loop_flag = True
        self.cooker = cooker.Cooker(gpio_on_off=17, gpio_up=22, gpio_down=27, gpio_fry=15)
        self.valve = valve.DoubleValve(gpio_v1=23, gpio_v2=24)
        self.heads_sensor = heads_sensor.Heads_sensor(gpio_heads_start=25,
                                                      gpio_heads_stop=14,
                                                      timeout=2000)
        self.pb = pb_wrap('XmJ61j9LVdjbPyKcSOUYv1k053raCeJP', emu_mode)
        self.pb_channel = self.pb.get_channel()
        self.coord_time = []
        self.coord_temp = []

    def load_config(self, conf_file_name):
        conf = open(conf_file_name, 'r')
        self.Tsteps = collections.OrderedDict(sorted(eval(conf.read()).items(),
                                              key=lambda t: t[0]))
        conf.close()
        self.set_Tsteps()

    def set_Tsteps(self):
        self.Tkeys = self.Tsteps.keys()
        self.Tstage = self.Tkeys.pop(0)
        self.Tcmd = self.Tsteps.pop(self.Tstage)
        # print(self.Tsteps)

    def release(self):
        self.cooker.release()
        self.valve.release()
        self.heads_sensor.release()
        try:
            RPIO.cleanup()
        except BaseException as e:
            print('Exception while RPIO.cleanup ' + str(e))

    def pause_monitor(self):
        """ слежение за длительностью паузы
        """
        if 'pause' == self.stage:
            if time.time()-self.pause_start_ts > self.pause_limit:
                self.pb_channel.push_note("Пауза превысила {}".format(self.pause_limit), "Включаю нагрев")
                self.heat_for_heads()

    def decrease_monitor(self):
        """ слежение за снижением температуры
        TODO: сейчас включение нагрева срабатывает только для фазы отличной от "нагрев".
        Если было защитное выключение плитки, то фаза остаётся "нагрев", монитор срабатывает,
        но включение не происходит.
        """
        if self.T_prev > self.temperature_in_celsius:
            self.downcount += 1
            if self.downcount >= self.downcount_limit:
                self.pb_channel.push_note("Снижение температуры", "Включаю нагрев")
                self.heat_for_heads()
                self.downcount = 0
        elif self.T_prev < self.temperature_in_celsius:
            self.downcount = 0
        self.T_prev = self.temperature_in_celsius

    def csv_write(self):
        self.print_str.append(time.strftime("%H:%M:%S", self.current_ts))
        self.print_str.append(str(self.temperature_in_celsius))
        if self.csv_delay >= self.csv_write_period:
            self.csv_delay = 0
            print(','.join(self.print_str), file=self.log)
        elif self.Tcmd_last != self.Tcmd_prev:
            self.print_str.append(self.Tcmd_last)
            self.Tcmd_prev = self.Tcmd_last
            print(','.join(self.print_str), file=self.log)

        self.print_str = []
        self.csv_delay += self.T_sleep

    def do_cmd(self):
        self.Tcmd_last = self.Tcmd.__name__
        self.pb_channel.push_note("Превысили " + str(self.Tstage),
                                  str(self.temperature_in_celsius)
                                  + ", Tcmd=" + str(self.Tcmd.__name__))

        self.Tcmd()
        try:
            self.Tstage = self.Tkeys.pop(0)
        except IndexError:
            self.Tstage = 999.0
            self.Tcmd = self.do_nothing
        else:
            self.Tcmd = self.Tsteps.pop(self.Tstage)

    def temperature_loop(self):
        over_cnt = 0
        t_failed_cnt = 0
        while self.loop_flag:
            try:
                self.temperature_in_celsius = self.sensor.get_temperature()
                t_failed_cnt = 0
            except:
                t_failed_cnt += 1

            if t_failed_cnt > 3:
                t_failed_cnt = 0
                self.pb_channel.push_note("Сбой получения температуры", "Требуется вмешательство")

            if abs((self.temperature_in_celsius - self.T_prev) / self.T_prev) > 0.3:
                self.temperature_in_celsius = self.T_prev
                logging.info('Over 30% difference T_prev={}, T_curr={}'.format(self.T_prev, self.temperature_in_celsius))

            self.current_ts = time.localtime()
            self.coord_time.append(time.strftime("%H:%M:%S", self.current_ts))
            self.coord_temp.append(self.temperature_in_celsius)

            self.pause_monitor()
            self.decrease_monitor()

            if self.temperature_in_celsius > self.Tstage:
                over_cnt += 1

            if over_cnt > 3:
                over_cnt = 0
                self.do_cmd()

            self.csv_write()
            time.sleep(self.T_sleep)

    def do_nothing(self, gpio_id=-1, value="-1"):
        print("do_nothing "
              + time.strftime("%H:%M:%S")
              + ", gpio_id=" + str(gpio_id)
              + ", value=" + str(value), file=self.log)
        pass

    def start_process(self):
        self.cooker.switch_on()
        # self.cooker.set_power_max()
        self.cooker.set_fry()
        self.stage = 'heat'

    def heat_4_low_wine(self):
        self.cooker.switch_on()
        self.stage = 'heat'

    def stop_process(self):
        self.loop_flag = False
        time.sleep(self.T_sleep+0.5)
        self.cooker.switch_off()
        self.stage = 'finish'

    def heat_on_pause(self):
        self.cooker.switch_off()
        self.pause_start_ts = time.time()
        self.stage = 'pause'

    def heat_for_heads(self):
        if 'heat' != self.stage:  # если и так фаза нагрева, выходим
            self.cooker.set_power_600()
            self.stage = 'heat'

    def heads_started(self, gpio_id, value):
        if 'heads' == self.stage:
            pass
        else:
            self.stage = 'heads'
            self.Tcmd_last = 'heads_started'
            try:
                int(value)
            except ValueError:
                print("heads_started BAD value="+str(value))
                value = -1
            self.pb_channel.push_note("Стартовали головы",
                                      "gpio_id=" + str(gpio_id)
                                      + ", value=" + str(value))
            self.heads_sensor.watch_stop(self.heads_finished)  # including heads_sensor.ignore_start()

    def heads_finished(self, gpio_id, value):
        if 'body' == self.stage:
            pass
        else:
            self.stage = 'body'
            self.Tcmd_last = 'heads_finished'
            try:
                int(value)
            except ValueError:
                print("heads_finished BAD value="+str(value))
                value = -1
            self.pb_channel.push_note("Закончились головы",
                                      "gpio_id=" + str(gpio_id)
                                      + ", value=" + str(value))
            self.valve.way_2()
            self.cooker.switch_off()
            self.cooker.switch_on()  # set power 1400
            self.heads_sensor.ignore_stop(),

    def start_watch_heads(self):
        self.valve.way_1()
        self.heads_sensor.watch_start(self.heads_started)
        self.cooker.set_power(300)

    def wait4body(self):
        self.cooker.switch_on()
        self.valve.way_2()
        self.stage = 'heat'

#    def stop_body_power_on(self):
#        self.stop_body()

    def stop_body(self):
        self.stage = 'tail'
        self.valve.way_3()
        self.pb_channel.push_note("Закончилось тело",
                                  "Клапан выключен")

    def finish(self):
        self.stop_process()
