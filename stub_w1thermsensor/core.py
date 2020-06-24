# -*- coding: utf-8 -*-

import numpy as np
"""
This module provides a stub for temperature sensor of type w1 therm.
"""


class W1ThermSensor(object):
    """
    stub for W1ThermSensor
    """
    Tlist = list(range(20, 70, 2))
    Tlist = Tlist + np.arange(70, 88, 0.1).tolist()
    Tlist = Tlist + np.arange(88, 100, 0.3).tolist()
    #: Holds information about supported w1therm sensors
    THERM_SENSOR_DS18S20 = 0x10
    THERM_SENSOR_DS1822 = 0x22
    THERM_SENSOR_DS18B20 = 0x28
    THERM_SENSOR_DS1825 = 0x3B
    THERM_SENSOR_DS28EA00 = 0x42
    THERM_SENSOR_MAX31850K = 0x3B
    TYPE_NAMES = {
        THERM_SENSOR_DS18S20: "DS18S20", THERM_SENSOR_DS1822: "DS1822",
        THERM_SENSOR_DS18B20: "DS18B20", THERM_SENSOR_DS1825: "DS1825",
        THERM_SENSOR_DS28EA00: "DS28EA00", THERM_SENSOR_MAX31850K: "MAX31850K"
    }
    RESOLVE_TYPE_STR = {
        "10": THERM_SENSOR_DS18S20, "22": THERM_SENSOR_DS1822, "28": THERM_SENSOR_DS18B20,
        "42": THERM_SENSOR_DS28EA00, "3b": THERM_SENSOR_MAX31850K
    }

    #: Holds information about the location of the needed
    #  sensor devices on the system provided by the kernel modules
    BASE_DIRECTORY = "/sys/bus/w1/devices"
    SLAVE_FILE = "w1_slave"

    #: Holds information about temperature type conversion
    DEGREES_C = 0x01
    DEGREES_F = 0x02
    KELVIN = 0x03
    UNIT_FACTORS = {
        DEGREES_C: lambda x: x * 0.001,
        DEGREES_F: lambda x: x * 0.001 * 1.8 + 32.0,
        KELVIN: lambda x: x * 0.001 + 273.15
    }
    UNIT_FACTOR_NAMES = {
        "celsius": DEGREES_C,
        "fahrenheit": DEGREES_F,
        "kelvin": KELVIN
    }

    #: Holds settings for patient retries used to access the sensors
    RETRY_ATTEMPTS = 10
    RETRY_DELAY_SECONDS = 1.0 / float(RETRY_ATTEMPTS)

    def __init__(self, sensor_type=None, sensor_id=None):
        pass

    def get_temperature(self, unit=DEGREES_C):
        try:
            T = np.around(self.Tlist.pop(0)*np.random.uniform(0.997, 1.003), 2)
        except IndexError:
            T = 100
        return T

    def get_resolution(self):
        return 12
