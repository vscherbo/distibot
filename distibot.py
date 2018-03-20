#!/usr/bin/python -t
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import collections
import ConfigParser
import io
import threading
import logging
import jsontree

from pushbullet import Pushbullet

from cooker import Cooker
import valve
import heads_sensor
import tsensor
import flow_sensor

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
        if 'xxx' == str(api_key).lower():
            self.emu_mode = True
            logging.info('api_key={0}, set emu_mode True'.format(api_key))
        else:
            self.emu_mode = emu_mode
            logging.info('set emu_mode={0}'.format(emu_mode))

        if self.emu_mode:
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
        logging.getLogger(__name__).addHandler(logging.NullHandler())
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
        self.cooker_period = 3600
        self.cooker_timeout = 10
        self.drop_period = 3600
        self.drop_timeout = 120
        self.flow_period = 300
        self.T_sleep = 1
        self.csv_delay = 0
        self.water_on = False
        self.print_str = []
        self.dt_string = time.strftime("%Y-%m-%d-%H-%M")
        self.timers = []
        self.drop_timer = threading.Timer(self.drop_period, self.drop_container)
        self.timers.append(self.drop_timer)
        self.cooker_timer = threading.Timer(self.cooker_period, self.cooker_off)
        self.timers.append(self.cooker_timer)

        if self.config.has_option('tsensors', 'gpio_ts'):
            # TODO switch gpio to INPUT
            self.tsensors = tsensor.Tsensors(self.config)
            self.tsensors.get_t()
            self.T_prev = self.tsensors.ts_data['boiler']  # TODO Tsensors(dict)

        self.loop_flag = True
        self.cooker = Cooker(gpio_on_off=self.config.getint('cooker', 'gpio_cooker_on_off'),
                             gpio_up=self.config.getint('cooker', 'gpio_cooker_up'),
                             gpio_down=self.config.getint('cooker', 'gpio_cooker_down'),
                             gpio_special=self.config.getint('cooker', 'gpio_cooker_special'),
                             powers=eval(self.config.get('cooker', 'cooker_powers')),
                             init_power=self.config.getint('cooker', 'cooker_init_power'),
                             special_power=self.config.getint('cooker', 'cooker_special_power'),
                             do_init_special=self.config.getboolean('cooker', 'init_special')
                             )

        self.valve_water = valve.Valve(valve_gpio=self.config.getint('valve_water', 'gpio_valve_water'))
        self.valve_drop = valve.Valve(valve_gpio=self.config.getint('valve_drop', 'gpio_valve_drop'))

        self.valve3way = valve.DoubleValve(gpio_v1=self.config.getint('dbl_valve', 'gpio_dbl_valve_1'),
                                           gpio_v2=self.config.getint('dbl_valve', 'gpio_dbl_valve_2'))

        self.heads_sensor = heads_sensor.Heads_sensor(hs_type=self.config.get('heads_sensor', 'hs_type'),
                                                      gpio_heads_start=self.config.getint('heads_sensor', 'gpio_hs_start'),
                                                      gpio_heads_finish=self.config.getint('heads_sensor', 'gpio_hs_finish'),
                                                      timeout=200)

        self.flow_sensor = flow_sensor.Flow_sensor(gpio_fs=self.config.getint('flow_sensor', 'gpio_fs'))

        self.pb = pb_wrap(self.config.get('pushbullet', 'api_key'))
        self.pb_channel = self.pb.get_channel()
        self.coord_time = []
        self.coord_temp = []
        self.coord_temp_condenser = []
        self.log = open(self.outdir + 'sensor-'  # + ('emu-' if emu_mode else '')
                        + self.dt_string
                        + '.csv', 'w', 0)  # 0 - unbuffered write

    def parse_conf(self, conf_filename):
        # Load and parse the conf file
        with open(conf_filename) as f:
            dib_config = f.read()
            self.config = ConfigParser.RawConfigParser(allow_no_value=True)
            self.config.readfp(io.BytesIO(dib_config))

    def load_script(self, play_filename):
        script = open(play_filename, 'r')
        self.Tsteps = collections.OrderedDict(sorted(eval(script.read()).items(),
                                              key=lambda t: t[0]))
        script.close()
        self.set_Tsteps()
        # TODO check methods existance and so on

    def load_jscript(self, play_filename):
        with open(play_filename, 'r') as script:
            jt = jsontree.load(script)
        self.Tsensors = jt['temperature_sensors']
        self.Tplays = {}
        self.Tsteps = {}
        for p in jt['temperature_sensors']:
            self.Tplays[p.id] = p.play
            self.Tsteps[p.id] = [t for t in p.play]

        script.close()
        # self.set_Tsteps()
        # TODO check methods existance and so on

    def set_jsteps(self):
        self.Tkeys = [t.temperature for t in dib.Tsteps['boiler']]

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
        for t in self.timers:
            t.cancel()
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
            if self.T_prev > self.tsensors.ts_data['boiler']:
                self.downcount += 1
                if self.downcount >= self.downcount_limit:
                    self.pb_channel.push_note("Снижение температуры", "Включаю нагрев")
                    self.heat_for_heads()
                    self.downcount = 0
            elif self.T_prev < self.tsensors.ts_data['boiler']:
                self.downcount = 0

    def csv_write(self):
        self.print_str.append(time.strftime("%H:%M:%S", self.current_ts))
        self.print_str.append(str(self.tsensors.ts_data['boiler']))
        try:
            t2 = self.tsensors.ts_data['condenser']
        except KeyError:
            t2 = 0
        self.print_str.append(str(t2))
        # self.print_str.append(str(self.tsensors.ts_data['condenser']))
        logging.debug('ts_data={0}'.format(self.tsensors.ts_data))
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
                                  str(self.tsensors.ts_data['boiler'])
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
                self.tsensors.get_t()
                t_failed_cnt = 0
            except:
                t_failed_cnt += 1
            else:
                self.T_prev = self.tsensors.ts_data['boiler']

            if t_failed_cnt > self.temperature_error_limit:
                t_failed_cnt = 0
                self.pb_channel.push_note("Сбой получения температуры", "Требуется вмешательство")

            if self.T_prev > 0:
                if abs((self.tsensors.ts_data['boiler'] - self.T_prev) / self.T_prev) \
                   > self.temperature_delta_limit:
                    self.tsensors.ts_data['boiler'] = self.T_prev  # ignore, use prev value
                    logging.warning('Over {:.0%} difference T_prev={}, t_in_Cels={}'.
                                    format(self.temperature_delta_limit,
                                           self.T_prev,
                                           self.tsensors.ts_data['boiler'])
                                    )

            self.current_ts = time.localtime()
            self.coord_time.append(time.strftime("%H:%M:%S", self.current_ts))
            self.coord_temp.append(self.tsensors.ts_data['boiler'])
            try:
                t2 = self.tsensors.ts_data['condenser']
            except KeyError:
                t2 = 0
            self.coord_temp_condenser.append(t2)
            # self.coord_temp_condenser.append(self.tsensors.ts_data['condenser'])

            self.pause_monitor()
            self.decrease_monitor()

            if self.tsensors.ts_data['boiler'] > self.Tstage:
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
        self.cooker_on()
        self.stage = 'heat'
        logging.debug('stage is "{}"'.format(self.stage))

    def stop_process(self):
        self.loop_flag = False
        time.sleep(self.T_sleep+0.5)
        self.cooker_off()
        self.stage = 'finish'
        logging.debug('stage is "{}"'.format(self.stage))

    def cooker_off(self):
        self.cooker_timer.cancel()
        self.timers.remove(self.cooker_timer)

        self.cooker.switch_off()

        self.cooker_timer = threading.Timer(self.cooker_timeout, self.cooker_on)
        self.timers.append(self.cooker_timer)
        self.cooker_timer.start()

    def cooker_on(self):
        self.cooker_timer.cancel()
        self.timers.remove(self.cooker_timer)

        self.cooker.switch_on()

        self.cooker_timer = threading.Timer(self.cooker_period, self.cooker_off)
        self.timers.append(self.cooker_timer)
        self.cooker_timer.start()

    def heat_on_pause(self):
        self.cooker_off()
        self.pause_start_ts = time.time()
        self.stage = 'pause'
        logging.debug('stage is "{}"'.format(self.stage))

    def heat_for_heads(self):
        if 'heat' != self.stage:  # если и так фаза нагрева, выходим
            self.cooker.set_power(600)
            self.stage = 'heat'
            logging.debug('stage is "{}"'.format(self.stage))

    def heads_started(self, gpio_id):
        if 'heads' == self.stage:
            pass
        else:
            self.stage = 'heads'
            logging.debug('stage is "{}"'.format(self.stage))
            self.Tcmd_last = 'heads_started'
            self.pb_channel.push_note("Стартовали головы", "gpio_id={}".format(gpio_id))
            self.heads_sensor.watch_finish(self.heads_finished)  # including heads_sensor.ignore_start()

    def heads_finished(self, gpio_id):
        if 'heads' != self.stage:
            pass
        else:
            self.stage = 'body'
            logging.debug('stage is "{}"'.format(self.stage))
            self.Tcmd_last = 'heads_finished'
            self.pb_channel.push_note("Закончились головы", "gpio_id={}".format(gpio_id))
            self.valve3way.way_2()  # way for body
            self.cooker.set_power(1400)
            # an obsolete apparoach:
            # self.cooker.switch_off()
            # self.cooker.switch_on()  # set initial_power
            self.heads_sensor.ignore_finish()

    def start_watch_heads(self):
        self.valve3way.way_1()
        self.start_water()
        self.heads_sensor.watch_start(self.heads_started)
        self.cooker.set_power(300)

    def wait4body(self):
        self.cooker_on()
        self.valve3way.way_2()
        self.stage = 'heat'
        logging.debug('stage is "{}"'.format(self.stage))

    def start_water(self):
        if not self.water_on:
            self.valve_water.power_on_way()
            self.water_on = True
            self.flow_timer = threading.Timer(self.flow_period, self.release)
            self.timers.append(self.flow_timer)
            self.flow_timer.start()
            self.flow_sensor.watch_flow(self.flow_detected)
            logging.debug('water_on={}, flow_sensor.is_alive={}'.format(self.water_on, self.flow_sensor.is_alive()))

    def drop_container(self):
        self.drop_timer.cancel()
        self.timers.remove(self.drop_timer)

        self.valve_drop.power_on_way()

        self.drop_timer = threading.Timer(self.drop_timeout, self.close_container)
        self.timers.append(self.drop_timer)
        self.drop_timer.start()
        logging.debug('drop is on')
        self.pb_channel.push_note("Сброс сухопарника", "Клапан сброса включён")

    def close_container(self):
        self.drop_timer.cancel()
        self.timers.remove(self.drop_timer)

        self.valve_drop.default_way()

        self.drop_timer = threading.Timer(self.drop_period, self.drop_container)
        self.timers.append(self.drop_timer)
        self.drop_timer.start()
        logging.debug('drop is off')
        self.pb_channel.push_note("Сухопарник закрыт", "Клапан сброса отключён")

#    def stop_body_power_on(self):
#        self.stop_body()

    def stop_body(self):
        self.stage = 'tail'
        logging.debug('stage is "{}"'.format(self.stage))
        self.valve3way.way_3()
        self.pb_channel.push_note("Закончилось тело", "Клапан выключен")

    def flow_detected(self, gpio_id):
        self.flow_timer.cancel()
        self.timers.remove(self.flow_timer)

        self.flow_sensor.handle_click()

        self.flow_timer = threading.Timer(self.flow_period, self.release)
        self.timers.append(self.flow_timer)
        self.flow_timer.start()

    def finish(self):
        self.stop_process()

if __name__ == "__main__":
    import argparse
    import os
    import sys
    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    # conf_file = prg_name +".conf"

    parser = argparse.ArgumentParser(description='Distibot module')
    parser.add_argument('--conf', type=str, default="distibot.conf", help='conf file')
    parser.add_argument('--play', type=str, default="dib-test.json", help='play file')
    parser.add_argument('--log_to_file', type=bool, default=False, help='log destination')
    parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)

    # log_format = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] %(levelname)-7s | %(asctime)-15s | %(message)s'
    log_format = '%(asctime)-15s | %(levelname)-7s | %(message)s'

    if args.log_to_file:
        log_dir = ''
        log_file = log_dir + prg_name + ".log"
        logging.basicConfig(filename=log_file, format=log_format, level=numeric_level)
    else:
        logging.basicConfig(stream=sys.stdout, format=log_format, level=numeric_level)

    # end of prolog
    logging.info('Started')

    dib = Distibot()
    dib.load_jscript(args.play)
    # logging.debug(dib.Tsteps['boiler'])
    b_play = dib.Tplays['boiler']
    # Tsteps = [t for t in b_play]
    logging.debug(dib.Tsteps['boiler'])
    for t in dib.Tsteps['boiler']:
        logging.debug(t.temperature)
    # logging.debug(Tkeys)
    # --- temps = b_play.index ...
    # Tkeys = b_play.keys()
    # Tstage = b_play.Tkeys.pop(0)
    # Tcmd = b_play.funcs(self.Tstage)
