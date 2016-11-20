#!/usr/bin/python -t
# -*- coding: utf-8 -*-

# from __future__ import print_function
import w1thermsensor


class Tsensor(w1thermsensor.W1ThermSensor):
    def __init__(self):  # TODO name or id of sensor
        try:
            # sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000066c6502")
            # ll /sys/bus/w1/devices/
            self.sensor = w1thermsensor.W1ThermSensor()
            self.emu_mode = False
        except w1thermsensor.core.KernelModuleLoadError:
            self.emu_mode = True
            self.Trange = [x * 0.1 for x in range(200, 99999)]
            self.emu_iterator = iter(self.Trange)

    def get_temperature(self, unit=w1thermsensor.W1ThermSensor.DEGREES_C):
        if self.emu_mode:
            return self.emu_iterator.next()
        else:
            return self.sensor.get_temperature(unit)
