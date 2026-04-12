#!/usr/bin/env python
""" An AR500 Tap Controller """

import logging
import time

# import RPi.GPIO as GPIO
from gpio_dev import GPIO, GPIO_DEV

MIN_CHANGE_TIME = 1  # hardware limit
ROTATION_TIME = 0.4


class TapController(GPIO_DEV):
    # pylint: disable=too-many-instance-attributes
    """
        A class to control a tap with an electrical driver and two wires for switch rotation.
    """

    # def __init__(self, arg_flow_sensor, valid_range, open_pin=19, close_pin=13):
    def __init__(self, arg_flow_sensor, valid_low, valid_high,
                 open_pin=19, close_pin=13,
                 min_change_interval=3.0, rotation_time=0.4,
                 hysteresis=2.0):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        """
        A class to control a tap with an electrical driver and two wires for switch rotation.

        :param arg_flow_sensor: A FlowSensor instance that provides the current flow rate.
        :param valid_range: A tuple (low, high) representing the valid range of flow rates.
        :param min_change_time: The minimum time (in seconds) between changes in tap position
                (default: 1).
        :param open_pin: The GPIO pin number to use for opening the tap (default: 18).
        :param close_pin: The GPIO pin number to use for closing the tap (default: 23).
        """
        super().__init__()
        self.flow_sensor = arg_flow_sensor
        self.valid_low = valid_low
        self.valid_high = valid_high
        self.min_change_interval = min_change_interval
        self.rotation_time = rotation_time
        self.hysteresis = hysteresis

        self.open_pin = open_pin
        self.close_pin = close_pin
        self.last_change_time = 0   # время последнего движения крана

        # Настройка GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.open_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.close_pin, GPIO.OUT, initial=GPIO.LOW)

    def open_tap(self, arg_time=None):
        """
        Rotate the tap to the open position.
        """
        if arg_time is None:
            arg_time = self.rotation_time
        current_time = time.time()
        # if current_time - self.last_change_time >= self.min_change_interval:
        min_allowed_interval = max(self.min_change_interval, MIN_CHANGE_TIME)
        if current_time - self.last_change_time >= min_allowed_interval:
            self.last_change_time = current_time
            GPIO.output(self.open_pin, GPIO.HIGH)
            time.sleep(arg_time)
            GPIO.output(self.open_pin, GPIO.LOW)
            logging.debug('Открываем кран на %.2f с', arg_time)
        else:
            logging.warning('Слишком рано открывать (прошло %.1f с)',
                            current_time - self.last_change_time)

    def close_tap(self, arg_time=None):
        """
        Rotate the tap to the closed position.
        """
        if arg_time is None:
            arg_time = self.rotation_time
        current_time = time.time()
        # if current_time - self.last_change_time >= self.min_change_interval:
        min_allowed_interval = max(self.min_change_interval, MIN_CHANGE_TIME)
        if current_time - self.last_change_time >= min_allowed_interval:
            self.last_change_time = current_time
            GPIO.output(self.close_pin, GPIO.HIGH)
            time.sleep(arg_time)
            GPIO.output(self.close_pin, GPIO.LOW)
            logging.debug('Закрываем кран на %.2f с', arg_time)
        else:
            logging.warning('Слишком рано закрывать (прошло %.1f с)',
                            current_time - self.last_change_time)

    def close_tap_completely(self, duration=15.0):  # 15 - from AR-500-2 Manual
        """Подаёт сигнал на закрытие крана в течение duration секунд."""
        self.call_log()
        logging.info("Closing tap completely for %.1f sec", duration)
        GPIO.output(self.close_pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.close_pin, GPIO.LOW)
        self.last_change_time = time.time()

    def adjust_flow(self):
        """
        Adjust the tap position based on the current flow rate.
        If the flow rate is below the valid range, open the tap.
        If the flow rate is above the valid range, close the tap.
        """
        now = time.time()
        if now - self.last_change_time < self.min_change_interval:
            logging.debug("Пропуск регулировки: слишком рано (%.1f с)",
                          now - self.last_change_time)
            return

        rpm = self.flow_sensor.get_rpm(max_age=2.0)   # используем новый метод
        logging.debug("Текущий rpm = %.1f", rpm)

        if rpm < self.valid_low - self.hysteresis:
            self.open_tap(self.rotation_time)
        elif rpm > self.valid_high + self.hysteresis:
            self.close_tap(self.rotation_time)
        else:
            logging.debug("Поток в норме: %.1f Гц", rpm)

    def release(self):
        """Освободить ресурсы: выключить оба пина."""
        GPIO.output(self.open_pin, GPIO.LOW)
        GPIO.output(self.close_pin, GPIO.LOW)
        super().release()
        logging.info("TapController released")


if __name__ == '__main__':
    import sys

    import flow_sensor

    LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(message)s'
    logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT,
                        level=logging.DEBUG)

    FLOW_SENSOR = flow_sensor.FlowSensor(5)
    # FLOW_SENSOR = flow_sensor.FlowSensorFake(5)
    TAP_CTRL = TapController(FLOW_SENSOR, valid_low=18, valid_high=22)
    """
    TAP_CTRL.open_tap()
    time.sleep(1)
    TAP_CTRL.open_tap()
    time.sleep(1)
    TAP_CTRL.open_tap()
    time.sleep(1)
    TAP_CTRL.open_tap()
    time.sleep(1)
    TAP_CTRL.open_tap()
    time.sleep(1)
    TAP_CTRL.open_tap()
    time.sleep(1)
    TAP_CTRL.open_tap()
    time.sleep(1)
    TAP_CTRL.open_tap()
    time.sleep(1)
    """
    DO_FLAG = True
    while DO_FLAG:
        try:
            time.sleep(2)
            logging.debug('adjust loop')
            TAP_CTRL.adjust_flow()
        except KeyboardInterrupt:
            logging.info('\ncaught keyboard interrupt!, bye')
            DO_FLAG = False

    sys.exit()
