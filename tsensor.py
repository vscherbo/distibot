#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
import imp
try:
    imp.find_module('w1thermsensor')
    import w1thermsensor
    emu_mode = False
except ImportError:
    import stub_w1thermsensor as w1thermsensor
    emu_mode = True
import re
import time


class Tsensor(object):
    def __init__(self, sensor_type=None, sensor_id=None, delta_threshold=0.4):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.sensor_id = sensor_id
        self.initial_T = 4
        self.curr_T = 4
        self.failed_cnt = 0
        self.delta_threshold = delta_threshold
        if emu_mode:
            logging.warning('tsensor emulation mode')
        try:
            # sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
            # ll /sys/bus/w1/devices/
            self.sensor = w1thermsensor.W1ThermSensor(sensor_type=sensor_type, sensor_id=sensor_id)
        except w1thermsensor.core.KernelModuleLoadError:
            logging.error('w1thermsensor.core.KernelModuleLoadError', exc_info=True)

    def get_temperature(self, unit=w1thermsensor.W1ThermSensor.DEGREES_C):
        try:
            loc_T = round(self.sensor.get_temperature(unit), 1)
        except BaseException:
            logging.exception('get_temperature')
            self.failed_cnt += 1
            # use current value
            loc_T = self.curr_T
        else:
            self.failed_cnt = 0
            if self.delta_over(loc_T, self.delta_threshold):
                # ignore, use current value
                logging.warning('Over {:.0%} difference curr_T={}, \
                        new loc_T={}'.format(self.delta_threshold, self.curr_T, loc_T))
                loc_T = self.curr_T
            else:
                # save current T
                self.curr_T = loc_T
        return loc_T

    def delta_over(self, check_t, delta_threshold):
        if self.curr_T == self.initial_T:
            return False
        else:
            return abs((check_t - self.curr_T) / self.curr_T) > delta_threshold


class Tsensors():
    temperature_error_limit = 3
    def __init__(self, config):
        # if config.has_section('tsensors'):
        ts_list = config.options('tsensors')
        self.ts_dict = {}
        self.ts_data = {}
        self.ts_ids = []
        for ts in ts_list:
            res = re.match('^ts_(.*)_id$', ts)
            if res:
                # ID of T sensor, i.e. "boiler"
                sensor_id = res.group(1)
                self.ts_ids.append(sensor_id)
                self.ts_dict[sensor_id] = Tsensor(sensor_id=config.get('tsensors', ts))

    def get_t(self):
        got_temp = True
        # for k in self.ts_dict.keys():
        for k in self.ts_ids:
            self.ts_data[k] = self.ts_dict[k].get_temperature()
            if self.ts_dict[k].failed_cnt > self.temperature_error_limit:
                self.ts_dict[k].failed_cnt = 0
                got_temp = False
            time.sleep(0.5)
        return got_temp

    @property
    def current_t(self):
        return [self.ts_data[k] for k in self.ts_ids]

    def t_over(self, tsensor_id, tlimit):
        logging.debug('ts_data=%s', self.ts_data)
        t_curr = self.ts_data[tsensor_id]
        logging.debug('tsensor_id=%s, t_curr=%s', tsensor_id, t_curr)
        if t_curr > tlimit:
            return True
        return False


if __name__ == '__main__':
    from time import sleep, strftime
    import argparse
    import os
    import sys
    import signal
    from configparser import ConfigParser

    def signal_handler(signal, frame):
        global loop_flag
        loop_flag = False

    signal.signal(signal.SIGINT, signal_handler)

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    conf_file_name = "distibot.conf"

    parser = argparse.ArgumentParser(description='Distibot "tsensor" module')
    parser.add_argument('--conf', type=str, default=conf_file_name, help='conf file')
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

    logging.info('Started')

    config = ConfigParser()
    config.read(args.conf)

    tsensors = Tsensors(config)
    tsensors.get_t()
    logging.info('ts_ids=%s', tsensors.ts_ids)

    # TODO read from conf file
    Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9]  # 1st production
    # Talarms = [94.5, 98.7, 999.9]  # tails
    alarm_limit = 3

    csv = open('{0}-{1}.csv'.format(prg_name, strftime("%Y-%m-%d-%H-%M")), 'w')
    Talarm = Talarms.pop(0)
    alarm_cnt = 0
    finish_cnt = 0
    loop_flag = True
    while loop_flag:
        tsensors.get_t()
        for ts_id, t in tsensors.ts_data.items():
            logging.info('ts_id={0}, t={1}'.format(ts_id, t))
        #is_over = tsensors.t_over('boiler', Talarm)
        is_over = False
        if is_over:
            logging.info("Превысили {0}, ts_id={1}, T={2}".format(Talarm, ts_id, tsensors.ts_data[ts_id]))
            # TODO alarm_cnt for the each sensor
            alarm_cnt += 1
            if alarm_cnt >= alarm_limit:
                alarm_cnt = 0
                Talarm = Talarms.pop(0)
            # print("T={0}".format(tsensors.ts_data[ts_id]))
            if tsensors.ts_data[ts_id] >= 99.9:
                finish_cnt += 1
                logging.debug('>>> finish_cnt={0}'.format(finish_cnt))
            if finish_cnt >= 3:
                loop_flag = False

        sleep(1)

    csv.close()
