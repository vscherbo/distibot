#!/usr/bin/env python
""" Temperature sensors module
"""

import logging
import imp
try:
    imp.find_module('w1thermsensor')
    import w1thermsensor
    from w1thermsensor.errors import ResetValueError
    from w1thermsensor.errors import SensorNotReadyError
    EMU_MODE = False
except ImportError:
    import stub_w1thermsensor as w1thermsensor
    from stub_w1thermsensor.errors import ResetValueError
    from stub_w1thermsensor.errors import SensorNotReadyError
    EMU_MODE = True
import re


class Tsensor():
    """ Single sensor calss
    """
    def __init__(self, sensor_type=None, sensor_id=None, delta_threshold=0.9):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.sensor_id = sensor_id
        self.initial_t = 4
        self.curr_t = 4
        self.failed_cnt = 0
        self.delta_threshold = delta_threshold
        if EMU_MODE:
            logging.warning('tsensor emulation mode')
        try:
            # sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
            # ll /sys/bus/w1/devices/
            self.sensor = w1thermsensor.W1ThermSensor(sensor_type=sensor_type, sensor_id=sensor_id)
        except w1thermsensor.errors.KernelModuleLoadError:
            logging.error('w1thermsensor.core.KernelModuleLoadError', exc_info=True)

    def get_temperature(self):
        """ Get measured temperature
        """
        loc_t = None
        try:
            loc_t = round(self.sensor.get_temperature(), 1)
        except ResetValueError:
            if self.curr_t > 84.0:
                logging.info('ResetValueError curr_t=%s', self.curr_t)
        except SensorNotReadyError:
            logging.info('SensorNotReadyError curr_t=%s', self.curr_t)
            #logging.exception('SensorNotReadyError')
        except Exception:
            logging.exception('get_temperature')
            self.failed_cnt += 1
            raise
        else:
            self.failed_cnt = 0
            if self.delta_over(loc_t):
                # ignore, use current value
                logging.warning('Over {:.0%} difference curr_t={}, \
                        new loc_t={}'.format(self.delta_threshold, self.curr_t, loc_t))
                loc_t = self.curr_t
            else:
                # save current T
                self.curr_t = loc_t
        return loc_t or self.curr_t

    def delta_over(self, check_t):
        """ Returns True if delta between values is over self.delta_threshold
        """
        return False if self.curr_t == self.initial_t \
        else abs((check_t - self.curr_t) / self.curr_t) > self.delta_threshold


class Tsensors():
    """ A class for a set of temperature sensors
    """
    temperature_error_limit = 5
    def __init__(self, tconfig):
        # if config.has_section('tsensors'):
        ts_list = tconfig.options('tsensors')
        self.ts_dict = {}
        self.ts_data = {}
        self.ts_ids = []
        for t_sensor in ts_list:
            res = re.match('^ts_(.*)_id$', t_sensor)
            if res:
                # ID of T sensor, i.e. "boiler"
                sensor_id = res.group(1)
                self.ts_ids.append(sensor_id)
                self.ts_dict[sensor_id] = Tsensor(sensor_id=tconfig.get('tsensors', t_sensor))

    def get_t(self):
        """ Get values for each sensors in the set
        """
        got_temp = True
        # for k in self.ts_dict.keys():
        for k in self.ts_ids:
            self.ts_data[k] = self.ts_dict[k].get_temperature()
            if self.ts_dict[k].failed_cnt > self.temperature_error_limit:
                self.ts_dict[k].failed_cnt = 0
                got_temp = False
            #time.sleep(0.75)
        return got_temp

    @property
    def current_t(self):
        """ Returns current value of sensors
        """
        return [self.ts_data[k] for k in self.ts_ids]

    def t_over(self, tsensor_id, tlimit):
        """ Return True if current value greater than tlimit
        """
        logging.debug('ts_data=%s', self.ts_data)
        logging.debug('tsensor_id=%s, t_curr=%s', tsensor_id, self.ts_data[tsensor_id])
        return self.ts_data[tsensor_id] > tlimit

    def get_resolution(self):
        """ Get resolution for each sensor
        """
        for k in self.ts_ids:
            #self.ts_prec[k] = self.ts_dict[k].sensor.get_resolution()
            logging.info('id=%s, resolution=%s', k, self.ts_dict[k].sensor.get_resolution())

if __name__ == '__main__':
    from time import sleep, strftime
    import argparse
    import os
    import sys
    from configparser import ConfigParser

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    CONF_FILE_NAME = "distibot.conf"

    parser = argparse.ArgumentParser(description='Distibot "tsensor" module')
    parser.add_argument('--conf', type=str, default=CONF_FILE_NAME, help='conf file')
    parser.add_argument('--log_to_file', type=bool, default=False, help='log destination')
    parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)

    # LOG_FORMAT = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] \
    # %(levelname)-7s | %(asctime)-15s | %(message)s'
    LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(message)s'

    if args.log_to_file:
        LOG_DIR = ''
        log_file = LOG_DIR + prg_name + ".log"
        logging.basicConfig(filename=log_file, format=LOG_FORMAT, level=numeric_level)
    else:
        logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT, level=numeric_level)

    logging.info('Started')

    config = ConfigParser()
    config.read(args.conf)

    tsensors = Tsensors(config)
    tsensors.get_resolution()
    tsensors.get_t()
    logging.info('ts_ids=%s', tsensors.ts_ids)

    csv = open('{0}-{1}.csv'.format(prg_name, strftime("%Y-%m-%d-%H-%M")), 'w')
    LOOP_FLAG = True
    while LOOP_FLAG:
        tsensors.get_t()
        for ts_id, t in tsensors.ts_data.items():
            logging.info('ts_id=%s, t=%s', ts_id, t)

        try:
            sleep(1)
        except KeyboardInterrupt:
            LOOP_FLAG = False
            logging.info('\nKeyboard interrupt!, bye')

    csv.close()
