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
import ConfigParser


class Tsensor(object):
    def __init__(self, sensor_type=None, sensor_id=None):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.sensor_id = sensor_id
        self.curr_T = 20
        if emu_mode:
            logging.warning('tsensor emulation mode')
        try:
            # sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
            # ll /sys/bus/w1/devices/
            self.sensor = w1thermsensor.W1ThermSensor(sensor_type=sensor_type, sensor_id=sensor_id)
        except w1thermsensor.core.KernelModuleLoadError:
            logging.error('w1thermsensor.core.KernelModuleLoadError', exc_info=True)

    def get_temperature(self, unit=w1thermsensor.W1ThermSensor.DEGREES_C):
        loc_T = self.sensor.get_temperature(unit)
        # logging.debug('get_temperature loc_T={}'.format(loc_T))
        return loc_T


class Tsensors():
    def __init__(self, config):
        # if config.has_section('tsensors'):
        ts_list = config.options('tsensors')
        self.ts_dict = {}
        self.ts_data = {}
        for ts in ts_list:
            res = re.match('^ts_(.*)_id$', ts)
            if res:
                self.ts_dict[res.group(1)] = Tsensor(sensor_id=config.get('tsensors', ts))

    def get_t(self):
        for k in self.ts_dict.keys():
            self.ts_data[k] = self.ts_dict[k].get_temperature()

    def t_over(self, tlimit):
        for ts_key, t in self.ts_data.iteritems():
            if t > tlimit:
                return True, ts_key
        return False, None


if __name__ == '__main__':
    from time import sleep, strftime
    import argparse
    import os
    import sys
    import signal
    import io

    def ask_t(sensor):
        # global Talarm
        if sensor is not None:
            temperature = sensor.get_temperature()
            t_alarm = temperature > Talarm
            logging.info('ts_id={0}, t={1}'.format(sensor.sensor_id, temperature))
            print("{0}^{1}^{2}".format(strftime("%H:%M:%S"), sensor.sensor_id, temperature), file=csv)
        else:
            temperature = None
            t_alarm = False
        return t_alarm, temperature

    def signal_handler(signal, frame):
        global loop_flag, csv
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

    with open(args.conf) as f:
        dib_config = f.read()
        f.close()

    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(dib_config))
    tsensors = Tsensors(config)
    print(tsensors.ts_dict.keys())
    tsensors.get_t()
    print(tsensors.ts_data)

    # TODO change to ConfigParser
    # conf = {}
    # execfile(args.conf, conf)

    # TODO read from conf file
    Talarms = [31.0, 49.5, 65.9, 98.5, 999.9]  # debug
    # Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9]  # 1st production
    # Talarms = [94.5, 98.7, 999.9]  # tails
    alarm_limit = 3

    csv = open('{0}-{1}.csv'.format(prg_name, strftime("%Y-%m-%d-%H-%M")), 'w', 0)  # 0 - unbuffered write
    Talarm = Talarms.pop(0)
    alarm_cnt = 0
    finish_cnt = 0
    loop_flag = True
    while loop_flag:
        tsensors.get_t()
        for ts_id, t in tsensors.ts_data.iteritems():
            logging.info('ts_id={0}, t={1}'.format(ts_id, t))
            # print('ts_id={0}, t={1}'.format(ts_id, t))
            # print("{0}^{1}^{2}".format(strftime("%H:%M:%S"), sensor.sensor_id, temperature), file=csv)
        (is_over, ts_id) = tsensors.t_over(Talarm)
        if is_over:
            # logging.info("Превысили {0}, t1={1}, t2={2}".format(Talarm, tsensors))
            logging.info("Превысили {0}, ts_id={1}, T={2}".format(Talarm, ts_id, tsensors.ts_data[ts_id]))
            # TODO alarm_cnt for the each sensor
            alarm_cnt += 1
            if alarm_cnt >= alarm_limit:
                alarm_cnt = 0
                Talarm = Talarms.pop(0)
            print("T={0}".format(tsensors.ts_data[ts_id]))
            if tsensors.ts_data[ts_id] >= 89.9:
                finish_cnt += 1
                print('>>> finish_cnt={0}'.format(finish_cnt))
            if finish_cnt >= 3:
                loop_flag = False

        sleep(1)

    csv.close()
