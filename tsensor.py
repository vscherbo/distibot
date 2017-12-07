#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
try:
    import w1thermsensor
    assert w1thermsensor
except ImportError:
    import stub_w1thermsensor as w1thermsensor
import logging


class Tsensor(w1thermsensor.W1ThermSensor):
    def __init__(self, sensor_type=None, sensor_id=None):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.curr_T = 20
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



if __name__ == '__main__':
    from time import sleep, strftime
    import argparse
    import os, sys
    import signal

    def signal_handler(signal, frame):
        global loop_flag, csv
        loop_flag = False
        csv.close()

    signal.signal(signal.SIGINT, signal_handler)

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    conf_file = prg_name +".conf"

    parser = argparse.ArgumentParser(description='Distibot "tsensor" module')
    parser.add_argument('--conf', type=str, default=conf_file, help='conf file')
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

    conf = {}
    execfile(args.conf, conf)

    # TODO read from conf file
    # Talarms = [25.0, 25.5, 25.9, 999.9] # debug
    Talarms = [77.0, 79.0, 85.0, 88.0, 94.5, 98.5, 999.9] # 1st production
    # Talarms = [94.5, 98.7, 999.9]  # tails
    alarm_limit = 3
    ts1_id='1234567890'

    sensor = Tsensor(sensor_id=ts1_id)
    logging.info("Sensor is created")
    csv = open('{0}-{1}.csv'.format(prg_name, strftime("%Y-%m-%d-%H-%M")), 'w', 0)  # 0 - unbuffered write
    Talarm = Talarms.pop(0)
    alarm_cnt = 0
    finish_cnt = 0
    loop_flag = True
    while loop_flag:
        temperature_in_celsius = sensor.get_temperature()
        print("{0}^{1}".format(strftime("%H:%M:%S"), temperature_in_celsius), file=csv)
        logging.info(temperature_in_celsius)
        if temperature_in_celsius > Talarm:
            logging.info("Превысили {0}, t={1}".format(Talarm, temperature_in_celsius))
            alarm_cnt += 1
            if alarm_cnt >= alarm_limit:
                alarm_cnt = 0
                Talarm = Talarms.pop(0)
            if temperature_in_celsius == 99.9:
                finish_cnt += 1
            if finish_cnt > 3:
                loop_flag = False
        sleep(1)

    csv.close()
