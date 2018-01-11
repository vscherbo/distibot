#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import collections
import ConfigParser
import io
import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)

from pushbullet import Pushbullet

import cooker
import valve
import heads_sensor_el
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


class Distibot(object):

    def __init__(self, conf_filename='distibot.conf'):
        self.parse_conf(conf_filename)
        self.outdir = 'output/'  # TODO config
        self.Tcmd_prev = 'before start'
        self.Tcmd_last = 'before start'
        self.downcount = 0
        self.downcount_limit = 5  # количество шагов подряд с неожидаемым снижением температуры
        self.csv_write_period = 3
        self.temperature_error_limit = 3
        self.temperature_over_limit = 3
        self.temperature_delta_limit = 0.3  # 30%
        self.stage = 'start'
        self.current_ts = time.localtime()
        self.pause_start_ts = 0
        self.pause_limit = 180
        self.T_sleep = 1
        self.csv_delay = 0
        self.print_str = []
        self.dt_string = time.strftime("%Y-%m-%d-%H-%M")

        if self.config.has_option('gpio_ts'):
            pass
            # TODO switch gpio to INPUT
            # self.ts_gpio = tsensor.Tsensor( ...
        if self.config.has_option('tsensor_boiler_id'):
            self.sensor_boiler = tsensor.Tsensor(sensor_id=self.config.get('tsensors', 'ts_boiler_id'))
        if self.config.has_option('tsensor_condenser_id'):
            self.sensor_condenser = tsensor.Tsensor(sensor_id=self.config.get('tsensors', 'ts_condenser_id'))
        self.temperature_boiler = self.sensor_boiler.get_temperature()
        self.temperature_condenser = self.sensor_condenser.get_temperature()
        self.T_prev = self.temperature_boiler

        self.loop_flag = True
        self.cooker = cooker.Cooker(gpio_on_off=self.config.get('cooker', 'gpio_cooker_on_off'),
                                    gpio_up=self.config.get('cooker', 'gpio_cooker_up'),
                                    gpio_down=self.config.get('cooker', 'gpio_cooker_down'),
                                    gpio_special=self.config.get('cooker', 'gpio_cooker_special'),
                                    powers=self.config.get('cooker', 'cooker_powers'),
                                    init_power=self.config.get('cooker', 'cooker_init_power'),
                                    )
        self.valve3way = valve.DoubleValve(gpio_v1=self.config.get('dbl_valve', 'gpio_dbl_valve_1'),
                                           gpio_v2=self.config.get('dbl_valve', 'gpio_dbl_valve_2'))
        self.heads_sensor = heads_sensor_el.Heads_sensor(gpio_heads_start=self.config.get('heads_sensor', 'gpio_hs_start'),
                                                         gpio_heads_stop=self.config.get('heads_sensor', 'gpio_hs_stop'),
                                                         timeout=2000)
        self.pb = pb_wrap(self.config.get('pushbullet', 'api_key'))
        self.pb_channel = self.pb.get_channel()
        self.coord_time = []
        self.coord_temp = []
        self.log = open(self.outdir + 'sensor-'  # + ('emu-' if emu_mode else '')
                        + self.dt_string
                        + '.csv', 'w', 0)  # 0 - unbuffered write

    def parse_conf(self, conf_file_name):
        # Load and parse the conf file
        with open(conf_file_name) as f:
            dib_config = f.read()
            self.config = ConfigParser.RawConfigParser(allow_no_value=True)
            self.config.readfp(io.BytesIO(dib_config))

        # this_sec='cooker'
        # for option in config.options(this_sec):
        #    print "option={0}, value={1}".format(option, config.get(this_sec, option))

    def load_script(self, play_file_name):
        script = open(play_file_name, 'r')
        self.Tsteps = collections.OrderedDict(sorted(eval(script.read()).items(),
                                              key=lambda t: t[0]))
        script.close()
        self.set_Tsteps()

    def set_Tsteps(self):
        self.Tkeys = self.Tsteps.keys()
        self.Tstage = self.Tkeys.pop(0)
        self.Tcmd = self.Tsteps.pop(self.Tstage)
        # print(self.Tsteps)

    def release(self):
        save_coord = open(self.outdir + self.dt_string+'.dat', 'w')
        for i_time, i_temp in zip(self.coord_time, self.coord_temp):
            save_str = '{}^{}\n'.format(i_time, i_temp)
            save_coord.write(save_str)
        save_coord.close()
        self.cooker.release()
        self.valve3way.release()
        self.heads_sensor.release()

    def pause_monitor(self):
        """ слежение за длительностью паузы
        """
        if 'pause' == self.stage:
            if time.time()-self.pause_start_ts > self.pause_limit:
                self.pb_channel.push_note("Пауза превысила {}".format(self.pause_limit), "Включаю нагрев")
                self.heat_for_heads()

    def decrease_monitor(self):
        """ слежение за снижением температуры
        TODO: сейчас включение нагрева срабатывает только для фазы "pause".
        Если было защитное выключение плитки, то фаза остаётся "нагрев", монитор срабатывает,
        но включение не происходит.
        """
        if 'pause' == self.stage:
            if self.T_prev > self.temperature_boiler:
                self.downcount += 1
                if self.downcount >= self.downcount_limit:
                    self.pb_channel.push_note("Снижение температуры", "Включаю нагрев")
                    self.heat_for_heads()
                    self.downcount = 0
            elif self.T_prev < self.temperature_boiler:
                self.downcount = 0

    def csv_write(self):
        self.print_str.append(time.strftime("%H:%M:%S", self.current_ts))
        self.print_str.append(str(self.temperature_boiler))
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
                                  str(self.temperature_boiler)
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
                loc_t = self.sensor.get_temperature()
                t_failed_cnt = 0
            except:
                t_failed_cnt += 1
            else:
                self.T_prev = self.temperature_boiler
                self.temperature_boiler = loc_t

            if t_failed_cnt > self.temperature_error_limit:
                t_failed_cnt = 0
                self.pb_channel.push_note("Сбой получения температуры", "Требуется вмешательство")

            if abs((self.temperature_boiler - self.T_prev) / self.T_prev) \
               > self.temperature_delta_limit:
                self.temperature_boiler = self.T_prev
                logging.warning('Over {:.0%} difference T_prev={}, t_in_Cels={}'.
                                format(self.temperature_delta_limit,
                                       self.T_prev,
                                       self.temperature_boiler))

            self.current_ts = time.localtime()
            self.coord_time.append(time.strftime("%H:%M:%S", self.current_ts))
            self.coord_temp.append(self.temperature_boiler)

            self.pause_monitor()
            self.decrease_monitor()

            if self.temperature_boiler > self.Tstage:
                over_cnt += 1

            if over_cnt > self.temperature_over_limit:
                over_cnt = 0
                self.do_cmd()

            self.csv_write()
            time.sleep(self.T_sleep)

        logging.debug('temperature_loop exiting')

    def do_nothing(self, gpio_id=-1, value="-1"):
        print("do_nothing "
              + time.strftime("%H:%M:%S")
              + ", gpio_id=" + str(gpio_id)
              + ", value=" + str(value), file=self.log)
        pass

    def start_process(self):
        self.cooker.switch_on()
        self.cooker.set_fry()
        self.stage = 'heat'
        logging.debug('stage is "{}"'.format(self.stage))

    def heat_4_low_wine(self):
        self.cooker.switch_on()
        self.stage = 'heat'
        logging.debug('stage is "{}"'.format(self.stage))

    def stop_process(self):
        self.loop_flag = False
        time.sleep(self.T_sleep+0.5)
        self.cooker.switch_off()
        self.stage = 'finish'
        logging.debug('stage is "{}"'.format(self.stage))

    def heat_on_pause(self):
        self.cooker.switch_off()
        self.pause_start_ts = time.time()
        self.stage = 'pause'
        logging.debug('stage is "{}"'.format(self.stage))

    def heat_for_heads(self):
        if 'heat' != self.stage:  # если и так фаза нагрева, выходим
            self.cooker.set_power_600()
            self.stage = 'heat'
            logging.debug('stage is "{}"'.format(self.stage))

    def heads_started(self, gpio_id, value):
        if 'heads' == self.stage:
            pass
        else:
            self.stage = 'heads'
            logging.debug('stage is "{}"'.format(self.stage))
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
            logging.debug('stage is "{}"'.format(self.stage))
            self.Tcmd_last = 'heads_finished'
            try:
                int(value)
            except ValueError:
                print("heads_finished BAD value="+str(value))
                value = -1
            self.pb_channel.push_note("Закончились головы",
                                      "gpio_id=" + str(gpio_id)
                                      + ", value=" + str(value))
            self.valve3way.way_2()
            self.cooker.switch_off()
            self.cooker.switch_on()  # set power 1400
            self.heads_sensor.ignore_stop(),

    def start_watch_heads(self):
        self.valve3way.way_1()
        self.heads_sensor.watch_start(self.heads_started)
        self.cooker.set_power(300)

    def wait4body(self):
        self.cooker.switch_on()
        self.valve3way.way_2()
        self.stage = 'heat'
        logging.debug('stage is "{}"'.format(self.stage))

#    def stop_body_power_on(self):
#        self.stop_body()

    def temperature_step(self):
        t_failed_cnt = 0
        try:
            loc_t = self.sensor.get_temperature()
            t_failed_cnt = 0
        except:
            t_failed_cnt += 1
        else:
            self.T_prev = self.temperature_boiler
            self.temperature_boiler = loc_t

        if t_failed_cnt > self.temperature_error_limit:
            t_failed_cnt = 0
            self.pb_channel.push_note("Сбой получения температуры", "Требуется вмешательство")

        if abs((self.temperature_boiler - self.T_prev) / self.T_prev) \
           > self.temperature_delta_limit:
            self.temperature_boiler = self.T_prev
            logging.warning('Over {:.0%} difference T_prev={}, t_in_Cels={}'.
                            format(self.temperature_delta_limit,
                                   self.T_prev,
                                   self.temperature_boiler))

    def stop_body(self):
        self.stage = 'tail'
        logging.debug('stage is "{}"'.format(self.stage))
        self.valve3way.way_3()
        self.pb_channel.push_note("Закончилось тело",
                                  "Клапан выключен")

    def finish(self):
        self.stop_process()
