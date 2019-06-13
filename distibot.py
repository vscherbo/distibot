#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Distibot main module
"""

from __future__ import print_function
import time
from configparser import ConfigParser
import threading
import logging
import socket
import requests

from pushbullet import Pushbullet

from cooker import Cooker
import valve
import heads_sensor
import tsensor
import flow_sensor

def wait_for_internet():
    """
    Loop until an internet connection to pushbullet.com port 80 is
    available.
    """

    while True:
        try:
            logging.info("Trying connection to Pushbullet API.")
            socket.create_connection(('api.pushbullet.com', '80'), timeout=30)
            logging.info("Connection successful.")
            break

        except (socket.gaierror, socket.timeout,
                ConnectionRefusedError, requests.exceptions.ConnectionError):
            logging.warning("Connection failed. Retrying in 10 seconds")
            time.sleep(10)



class PBWrap(Pushbullet):
    """
        Pushbullet api calls wrapper
    """
    def __init__(self, api_key, emu_mode=False):
        if str(api_key).lower() == 'xxx':
            self.emu_mode = True
            logging.info('api_key=%s, set emu_mode True', api_key)
        else:
            self.emu_mode = emu_mode
            logging.info('set emu_mode=%s', emu_mode)

        if self.emu_mode:
            self.channels = []
        else:
            super(PBWrap, self).__init__(api_key)

    def get_channel(self, channel_tag=u"Billy's moonshine"):
        if self.emu_mode:
            pb_channel = PBChannelEmu()
        else:
            pb_channel = [x for x in self.channels if x.name == channel_tag][0]
        return pb_channel

class PBChannelEmu(object):

    def push_note(self, subject, msg):
        logging.info("subj=%s/msg=%s", subject, msg)


class Distibot(object):

    def __init__(self, conf_filename='distibot.conf', play_script='distibot.play'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.ts_play_set = set()
        self.t_stages = []
        self.coord = []
        self.coord_csv = []
        self.coord_list = []
        self.coord_time = []
        self.coord_t_boiler = []
        self.coord_t_condenser = []


        self.outdir = 'output'  # TODO config
        self.cmd_prev = 'before start'
        self.cmd_last = 'before start'
        self.curr_t = 0.0
        self.curr_ts = ''
        self.curr_method = ''
        self.csv_write_period = 3
        self.temperature_over_limit = 3
        self.temperature_delta_limit = 0.3  # 30%
        self.stage = 'start'
        self.pause_start_ts = 0
        self.pause_limit = 180
        self.cooker_period = 3600
        self.cooker_timeout = 3
        self.drop_period = 4000
        self.drop_timeout = 15
        self.t_sleep = 1
        self.csv_delay = 0
        self.water_on = False

        self.timestamp = time.localtime()
        self.dt_string = time.strftime("%Y-%m-%d-%H-%M")

        if self.load_script(play_script):
            self.config = ConfigParser()
            self.config.read(conf_filename)
            (self.curr_t, self.curr_ts, self.curr_method) = self.t_stages.pop(0)
        else:
            logging.error('Ошибка при разборе сценария: %s', play_script)

        self.timers = []
        self.drop_timer = threading.Timer(self.drop_period,
                                          self.drop_container)
        self.timers.append(self.drop_timer)
        self.cooker_timer = threading.Timer(self.cooker_period,
                                            self.cooker_off)
        self.timers.append(self.cooker_timer)

        if self.config.has_option('tsensors', 'gpio_ts'):
            # TODO switch gpio to INPUT
            self.tsensors = tsensor.Tsensors(self.config)
            self.tsensors.get_t()
        if self.ts_play_set <= set(self.tsensors.ts_ids):
            self.loop_flag = True
            logging.info('OK. Every ts in ts_play_set is described in conf, loop_flag=%s', self.loop_flag)
        else:
            self.loop_flag = False
            logging.info('self.ts_play_set=%s', self.ts_play_set)
            logging.info('set(self.tsensors.ts_ids)%s', set(self.tsensors.ts_ids))
            logging.info('ERROR, temperature_loop is impossible, loop_flag=%s', self.loop_flag)

        powers_list = self.config.get('cooker', 'cooker_powers').replace(' ', '').split(',')
        logging.debug('Cooker config: %d', int(self.config['cooker']['gpio_cooker_on_off']))
        self.cooker = Cooker(gpio_on_off=self.config.getint(
            'cooker', 'gpio_cooker_on_off'),
                             gpio_up=self.config.getint(
                                 'cooker', 'gpio_cooker_up'),
                             gpio_down=self.config.getint(
                                 'cooker', 'gpio_cooker_down'),
                             gpio_special=self.config.getint(
                                 'cooker', 'gpio_cooker_special'),
                             powers=tuple(map(int, powers_list)),
                             init_power=self.config.getint(
                                 'cooker', 'cooker_init_power'),
                             special_power=self.config.getint(
                                 'cooker', 'cooker_special_power'),
                             do_init_special=self.config.getboolean(
                                 'cooker', 'init_special')
                             )
        self.power_for_heads = self.config.getint('cooker', 'power_for_heads')
        # self.cooker_current_power = self.cooker.current_power()
        self.cooker_current_power = None

        self.valve_water = valve.Valve(valve_gpio=self.config.getint(
            'valve_water',
            'gpio_valve_water'))
        self.valve_drop = valve.Valve(valve_gpio=self.config.getint(
            'valve_drop',
            'gpio_valve_drop'))

        self.valve3way = valve.DoubleValve(gpio_v1=self.config.getint(
            'dbl_valve',
            'gpio_dbl_valve_1'),
                                           gpio_v2=self.config.getint(
                                               'dbl_valve',
                                               'gpio_dbl_valve_2'))

        self.heads_sensor = \
            heads_sensor.Heads_sensor(hs_type=self.config.get(
                'heads_sensor',
                'hs_type'),
                                      gpio_heads_start=self.config.getint(
                                          'heads_sensor',
                                          'gpio_hs_start'),
                                      gpio_heads_finish=self.config.getint(
                                          'heads_sensor',
                                          'gpio_hs_finish'),
                                      timeout=1000)

        self.flow_sensor = flow_sensor.FlowSensor(gpio_fs=self.config.getint('flow_sensor', 'gpio_fs'))
        if tsensor.emu_mode:
            self.flow_period = 86400
        else:
            self.flow_period = self.config.getint('flow_sensor', 'flow_period')

        self.pb = PBWrap(self.config.get('pushbullet', 'api_key'))
        self.pb_channel = self.pb.get_channel()
        self.log = open('{}/sensor-{}.csv'.format(self.outdir, self.dt_string), 'w')

    def release(self):
        """
        call from self.finish()
        """
        for t in self.timers:
            t.cancel()
        self.flow_sensor.release()
        self.cooker.release()
        self.valve3way.release()
        self.valve_water.release()
        self.valve_drop.release()
        self.heads_sensor.release()

    def load_script(self, play_filename):
        """
        read script file and set t_stages
        """
        try:
            t_steps = [line.partition('#')[0].rstrip().split(', ')
                       for line in open(play_filename, 'r')]
            logging.debug('t_steps=%s', t_steps)
            for (loc_t, loc_ts, loc_method) in t_steps:
                self.t_stages.append([float(loc_t), loc_ts.strip(), eval(loc_method.strip())])
                self.ts_play_set.add(loc_ts.strip())
            logging.debug('t_stages=%s', self.t_stages)
        except BaseException:
            res = False
            logging.exception('load_script exception')
        else:
            res = True
        return res

    def send_msg(self, msg_subj, msg_body):
        logging.info("send_msg: subj=%s, msg='%s'", msg_subj, msg_body)
        msg_body = "{}: {}".format(time.strftime("%Y-%m-%d %H:%M"), msg_body)
        for i in range(1, 4):
            try:
                self.pb_channel.push_note(msg_subj, msg_body)
            except BaseException:
                logging.exception('exception in send_msg[%d]', i)
                time.sleep(1)
            else:
                break

            """
            except OSError as e:
                err_code, err_text = e.args
                if err_code == 104:
                    logging.warning('Connection reset by peer in send_msg[%d]', i)
                else:
                    logging.exception('exception in send_msg[%d]', i)
                time.sleep(1)
            """

    def save_coord_file(self):
        outf_name = '{}/{}.dat'.format(self.outdir, self.dt_string)
        with open(outf_name, 'w') as save_coord :
            for crd in self.coord_list:
                save_coord.write('^'.join([str(c1) for c1 in crd]) + '\n')
        logging.info('coordinates saved to file')

    def csv_write(self):
        self.csv_delay += self.t_sleep
        if self.csv_delay >= self.csv_write_period:
            self.csv_delay = 0
            for crd in self.coord_csv:
                print(','.join([str(c1) for c1 in crd]), file=self.log)

        if self.cmd_last != self.cmd_prev:
            self.cmd_prev = self.cmd_last
            crd = self.coord_csv.pop(-1)
            crd.append(self.cmd_last)
            print(','.join([str(c1) for c1 in crd]), file=self.log)

    def run_cmd(self):
        self.cmd_last = self.curr_method.__name__
        self.curr_method()
        self.send_msg("Превысили {}".format(self.curr_t),
                      "current_t={}, tsensor={} команда={}".format(
                          self.tsensors.current_t, self.curr_ts, self.cmd_last))

        try:
            (self.curr_t, self.curr_ts, self.curr_method) = self.t_stages.pop(0)
        except IndexError:
            # dirty patch
            self.curr_t = 999.0
            self.curr_ts = 'boiler'
            self.curr_method = self.do_nothing

    def temperature_loop(self):
        over_cnt = 0
        while self.loop_flag:
            coord = []
            if self.tsensors.get_t():
                self.timestamp = time.localtime()
                coord.append(time.strftime("%H:%M:%S", self.timestamp))
                coord.extend(self.tsensors.current_t)
                coord.append(self.flow_sensor.clicks)
                coord.append(self.flow_sensor.hertz)
                logging.info('current coord=%s', coord)
                self.coord_csv.append(coord)
                self.coord_list.append(coord)
                self.coord_time.append(coord[0])
                self.coord_t_boiler.append(coord[1])
                self.coord_t_condenser.append(coord[2])

                if self.tsensors.ts_data[self.curr_ts] > self.curr_t:
                    over_cnt += 1

                if over_cnt > self.temperature_over_limit or self.curr_t == 0.0:
                    over_cnt = 0
                    self.run_cmd()

                self.csv_write()
            else:
                self.send_msg("Сбой получения температуры", "Требуется вмешательство")
                # ? self.stop_process() ?

            time.sleep(self.t_sleep)

        logging.info('temperature_loop exiting')

    def do_nothing(self, gpio_id=-1, value="-1"):
        print("do_nothing "
              + time.strftime("%H:%M:%S")
              + ", gpio_id=" + str(gpio_id)
              + ", value=" + str(value), file=self.log)

    def start_process(self):
        self.cooker_on()
        self.stage = 'heat'
        # moved to start_water()
        # self.drop_timer.start()
        logging.debug('stage is "%s"', self.stage)

    def stop_process(self):
        """
        call from self.finish()
        """
        self.loop_flag = False
        time.sleep(self.t_sleep+0.5)
        self.stage = 'finish'  # before cooker_off!
        self.cooker_off()
        logging.debug('stage is "%s"', self.stage)
        self.save_coord_file()

    def cooker_off(self):
        self.cooker_timer.cancel()
        if self.cooker_timer in self.timers:
            self.timers.remove(self.cooker_timer)

        # TODO simplify
        if self.cooker.power_index:
            self.cooker_current_power = self.cooker.current_power()
            self.cooker.switch_off()

        if self.stage == 'finish':
            loc_str = "Финиш"
        else:
            self.cooker_timer = threading.Timer(self.cooker_timeout,
                                                self.cooker_on)
            self.timers.append(self.cooker_timer)
            self.cooker_timer.start()
            loc_str = "Установлен таймер на {}".format(self.cooker_timeout)

        self.send_msg("Нагрев отключён", loc_str)

    def cooker_on(self):
        self.cooker_timer.cancel()
        self.timers.remove(self.cooker_timer)

        # TODO simplify
        if self.cooker_current_power is not None and \
           self.cooker_current_power > 0:
            self.cooker.switch_on(self.cooker_current_power)
        else:
            self.cooker.switch_on()

        self.cooker_timer = threading.Timer(self.cooker_period,
                                            self.cooker_off)
        self.timers.append(self.cooker_timer)
        self.cooker_timer.start()
        self.send_msg("Нагрев включён",
                      "Установлен таймер на {}".format(self.cooker_period))

    def heads_started(self, gpio_id=-1):
        logging.debug('inside heads_started')
        if self.heads_sensor.flag_ignore_start:
            logging.info('flag_ignore_start detected!')
        else:
            if 'heads' == self.stage:
                # ? Never will occured
                logging.debug('stage is already heads. Skipping')
            else:
                self.stage = 'heads'
                logging.debug('stage set to "{}"'.format(self.stage))
                self.cmd_last = 'heads_started'
                if gpio_id > 0:
                    self.send_msg("Стартовали головы",
                                  "gpio_id={}".format(gpio_id))
                    # call heads_sensor.ignore_start()
                    self.heads_sensor.watch_finish(self.heads_finished)
                logging.debug('after watch_finish')

    def heads_finished(self, gpio_id=-1):
        logging.debug('inside heads_finished')
        if self.heads_sensor.flag_ignore_finish:
            logging.info('flag_ignore_finish detected!')
        else:
            if 'heads' != self.stage:
                logging.debug('NOT heads, stage="{}". Skipping'.
                              format(self.stage))
                pass
            else:
                self.stage = 'body'
                logging.debug('stage set to "{}"'.format(self.stage))
                self.cmd_last = 'heads_finished'
                if gpio_id > 0:
                    self.send_msg("Закончились головы",
                                  "gpio_id={}".format(gpio_id))
                    self.heads_sensor.ignore_finish()
                self.valve3way.way_2()  # way for body
                self.cooker.set_power(1400)  # TODO from config?
                self.start_water()

    def start_watch_heads(self):
        logging.debug('inside start_watch_heads')
        self.start_water()
        self.cooker.set_power(self.power_for_heads)
        self.heads_sensor.watch_start(self.heads_started)
        self.valve3way.way_1()

    def wait4body(self):
        # self.cooker_on()
        self.cooker.set_power(1400)
        self.start_water()
        self.valve3way.way_2()
        self.stage = 'body'
        logging.debug('stage is "%s"', self.stage)

    def set_stage_body(self):
        self.stage = 'body'

    def start_water(self):
        if not self.water_on:
            self.valve_water.power_on_way()
            self.water_on = True
            self.flow_timer = threading.Timer(self.flow_period, self.no_flow)
            self.timers.append(self.flow_timer)
            self.flow_timer.start()
            self.flow_sensor.watch_flow(self.flow_detected)
            self.drop_timer.start()
            logging.info('water_on={}, flow_timer.is_alive={}'.format(
                          self.water_on, self.flow_timer.is_alive()))

    def drop_container(self):
        self.drop_timer.cancel()
        self.timers.remove(self.drop_timer)

        self.valve_drop.power_on_way()
        logging.debug('drop is on')
        self.send_msg("Сброс сухопарника", "Клапан сброса включён")

        self.drop_timer = threading.Timer(self.drop_timeout,
                                          self.close_container)
        self.timers.append(self.drop_timer)
        self.drop_timer.start()

    def close_container(self):
        self.drop_timer.cancel()
        self.timers.remove(self.drop_timer)

        self.valve_drop.switch_off()
        logging.debug('drop is off')
        self.send_msg("Сухопарник закрыт", "Клапан сброса отключён")

        self.drop_timer = threading.Timer(self.drop_period,
                                          self.drop_container)
        self.timers.append(self.drop_timer)
        self.drop_timer.start()

#    def stop_body_power_on(self):
#        self.stop_body()

    def stop_body(self):
        self.stage = 'tail'
        self.start_water()
        logging.info('stage is "{}"'.format(self.stage))
        self.valve3way.way_3()
        self.send_msg("Закончилось тело", "Клапан выключен")

    def flow_detected(self, gpio_id):
        self.flow_timer.cancel()
        self.timers.remove(self.flow_timer)

        self.flow_timer = threading.Timer(self.flow_period, self.no_flow)
        self.timers.append(self.flow_timer)
        self.flow_timer.start()

        self.flow_sensor.handle_click()

    def no_flow(self):
        logging.warning("Нет потока охлаждения \
        за flow_period={}, Аварийное отключение".format(self.flow_period))
        self.send_msg("Аварийное отключение", "Нет потока охлаждения")
        # temporary do not STOP
        # self.stop_process()
        # self.release()

    def finish(self):
        if self.stage != 'finish':
            logging.info('========== distibot.finish()')
            self.stop_process()
            logging.info('after stop_process()')
            self.release()
            logging.info('after release()')


if __name__ == "__main__":
    import argparse
    import os
    import sys
    import signal

    def dib_stop():
        global dib
        dib.stop_process()
        logging.info('after stop_process')
        dib.release()
        logging.info('after dib.release')

    def signal_handler(signal, frame):
        logging.info('Catched signal {}'.format(signal))
        dib_stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)

    def segv_handler(signal, frame):
        logging.info('Catched signal {}'.format(signal))
        logging.info('frame.f_locals={}'.format(frame.f_locals))
        logging.info('frame: filename={}, function={}, line_no={}'.format(
                      frame.f_code.co_filename,
                      frame.f_code.co_name, frame.f_lineno))
        dib_stop()

    signal.signal(signal.SIGSEGV, segv_handler)

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    # conf_file = prg_name +".conf"

    parser = argparse.ArgumentParser(description='Distibot module')
    parser.add_argument('--conf', type=str, default="distibot.conf",
                        help='conf file')
    parser.add_argument('--play', type=str, default="dib-debug-cond2.play",
                        help='play file')
    parser.add_argument('--log_to_file', type=bool, default=True,
                        help='log destination')
    parser.add_argument('--log_level', type=str, default="DEBUG",
                        help='log level')
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {0}'.format(numeric_level))

    log_format = '[%(filename)-22s:%(lineno)4s - %(funcName)20s()] \
            %(levelname)-7s | %(asctime)-15s | %(message)s'
    # log_format = '%(asctime)-15s | %(levelname)-7s | %(message)s'

    if args.log_to_file:
        log_dir = ''
        log_file = log_dir + prg_name + ".log"
        logging.basicConfig(filename=log_file, format=log_format,
                            level=numeric_level)
    else:
        logging.basicConfig(stream=sys.stdout, format=log_format,
                            level=numeric_level)

    # end of prolog
    logging.info('Started')

    dib = Distibot(conf_filename=args.conf, play_script=args.play)
    dib.temperature_loop()

    logging.info('Exit')
