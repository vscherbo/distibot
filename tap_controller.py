#!/usr/bin/env python
""" An AR500 Tap Controller """

import logging
import time

# import RPi.GPIO as GPIO
from gpio_dev import GPIO, GPIO_DEV

MIN_CHANGE_TIME = 1  # hardware limit
ROTATION_TIME = 0.4

class TapController(GPIO_DEV):
    def __init__(self, arg_flow_sensor, valid_low, valid_high,
                 open_pin=19, close_pin=13,
                 min_change_interval=5.0,   # увеличенная пауза
                 rotation_time=0.3,         # максимальное время одного шага
                 hysteresis=2.0,
                 kp=0.1,                    # коэффициент усиления (сек/ед. rpm)
                 min_pulse=0.15,            # минимальная длительность импульса
                 max_pulse=1.5):            # максимальная длительность импульса
        super().__init__()
        self.flow_sensor = arg_flow_sensor
        self.valid_low = valid_low
        self.valid_high = valid_high
        self.min_change_interval = min_change_interval
        self.rotation_time = rotation_time
        self.hysteresis = hysteresis
        self.kp = kp
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse

        self.open_pin = open_pin
        self.close_pin = close_pin
        self.last_change_time = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.open_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.close_pin, GPIO.OUT, initial=GPIO.LOW)

    def _pulse(self, pin, duration):
        """Выдать импульс на указанный пин."""
        now = time.time()
        min_allowed_interval = max(self.min_change_interval, MIN_CHANGE_TIME)
        if now - self.last_change_time < min_allowed_interval:
            logging.warning('Слишком рано (прошло %.1f с)',
                            now - self.last_change_time)
            return
        self.last_change_time = now
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)
        action = 'Открываем' if pin == self.open_pin else 'Закрываем'
        logging.debug('%s кран на %.3f с', action, duration)

    def open_tap(self, arg_time=None):
        if arg_time is None:
            arg_time = self.rotation_time
        self._pulse(self.open_pin, arg_time)

    def close_tap(self, arg_time=None):
        if arg_time is None:
            arg_time = self.rotation_time
        self._pulse(self.close_pin, arg_time)

    def adjust_flow(self):
        """
        Пропорциональное регулирование:
        - вычисляется ошибка относительно середины допустимого диапазона
        - длительность импульса пропорциональна ошибке
        - применяется импульс в нужную сторону
        - затем ожидание min_change_interval
        """
        now = time.time()
        if now - self.last_change_time < self.min_change_interval:
            logging.debug("Пропуск регулировки: слишком рано (%.1f с)",
                          now - self.last_change_time)
            return

        rpm = self.flow_sensor.get_rpm(max_age=2.0)
        logging.debug("Текущий rpm = %.1f", rpm)

        target = (self.valid_low + self.valid_high) / 2.0
        error = rpm - target   # положительная -> перебор, нужна закрытие

        # Зона нечувствительности с гистерезисом
        if rpm < self.valid_low - self.hysteresis:
            # недобор – открываем
            pulse_time = min(max(self.kp * abs(error), self.min_pulse), self.max_pulse)
            self._pulse(self.open_pin, pulse_time)
        elif rpm > self.valid_high + self.hysteresis:
            # перебор – закрываем
            pulse_time = min(max(self.kp * abs(error), self.min_pulse), self.max_pulse)
            self._pulse(self.close_pin, pulse_time)
        else:
            logging.debug("Поток в норме: %.1f Гц", rpm)

    def close_tap_completely(self, duration=15.0):  # 15 - from AR-500-2 Manual
        """Подаёт сигнал на закрытие крана в течение duration секунд."""
        self.call_log()
        logging.info("Closing tap completely for %.1f sec", duration)
        GPIO.output(self.close_pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.close_pin, GPIO.LOW)
        self.last_change_time = time.time()

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
