#!/usr/bin/python -t
# -*- coding: utf-8 -*-

# from __future__ import print_function
import w1thermsensor
import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('moonshine.log')
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Tsensor(w1thermsensor.W1ThermSensor):
    def __init__(self, emu_mode=False):  # TODO name or id of sensor
        if emu_mode:
            self.setup_emu_mode()
        else:
            try:
                # sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
                # ll /sys/bus/w1/devices/
                self.sensor = w1thermsensor.W1ThermSensor()
                self.emu_mode = False
            except w1thermsensor.core.KernelModuleLoadError:
                self.setup_emu_mode()

    def setup_emu_mode(self):
        self.emu_mode = True
        self.Trange = [x * 0.1 for x in range(200, 99999)]
        self.emu_iterator = iter(self.Trange)

    def get_temperature(self, unit=w1thermsensor.W1ThermSensor.DEGREES_C):
        # logger.debug('get_temperature emu_mode={}'.format(self.emu_mode))
        if self.emu_mode:
            return self.emu_iterator.next()
        else:
            loc_T = self.sensor.get_temperature(unit)
            # logger.debug('get_temperature loc_T={}'.format(loc_T))
            return loc_T
