#!/usr/bin/env python
""" An AR500 Tap Controller """

import logging
import statistics
import time
from collections import deque

# import RPi.GPIO as GPIO
from gpio_dev import GPIO, GPIO_DEV

MIN_CHANGE_TIME = 1  # hardware limit


class TapController(GPIO_DEV):
    """
    Управление краном подачи воды с импульсным приводом открытия/закрытия.

    Стратегия:

    1. Пропорциональная длительность импульса:
       pulse = kp * |error|, ограничено [min_pulse, max_pulse].
       Целевое значение — середина допустимого диапазона.

    2. Гистерезис: действия выполняются только при выходе потока за пределы
       [valid_low - hysteresis, valid_high + hysteresis]. Защищает от
       реакции на шум датчика и мелкие колебания.

    3. Демпфирование разворота: если предыдущий импульс двигал кран в
       противоположную сторону (значит, мы проскочили цель), новый импульс
       уменьшается вдвое. Это гасит автоколебания.

    4. Breakaway-эскалация: при полностью закрытом кране (rpm ~ 0) одиночный
       импульс не открывает клапан, нужны последовательные попытки с
       нарастающей длительностью. Пауза в этом режиме короче обычной, а
       история фильтра сбрасывается после каждого импульса, чтобы сразу
       заметить появление потока.

    5. Медианная фильтрация: сырое значение датчика — мгновенная частота по
       последнему межимпульсному интервалу; оно очень шумное. Медиана по
       окну из N отсчётов даёт устойчивую оценку.
    """

    def __init__(self, arg_flow_sensor, valid_low, valid_high,
                 open_pin=19, close_pin=13,
                 min_change_interval=6.0,   # пауза между коррекциями, с
                 rotation_time=0.3,         # legacy: для open_tap()/close_tap()
                 hysteresis=3.0,            # мёртвая зона вокруг [valid_low, valid_high]
                 kp=0.025,                  # коэффициент усиления, с / ед. rpm
                 min_pulse=0.15,            # минимальный импульс, с
                 max_pulse=0.65,            # максимальный импульс в норм. режиме, с
                 rpm_filter_size=5,         # окно медианного фильтра (отсчётов)
                 breakaway_start=0.5,       # первый breakaway-импульс, с
                 breakaway_step=0.25,       # приращение при каждой неудаче, с
                 breakaway_max=1.5,         # потолок breakaway-импульса, с
                 breakaway_threshold=2.0,   # rpm ниже этого = "нулевой поток"
                 breakaway_interval=2.0):   # пауза между breakaway-попытками, с
        # pylint: disable=too-many-arguments,too-many-positional-arguments
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

        self.breakaway_start = breakaway_start
        self.breakaway_step = breakaway_step
        self.breakaway_max = breakaway_max
        self.breakaway_threshold = breakaway_threshold
        self.breakaway_interval = breakaway_interval

        self.open_pin = open_pin
        self.close_pin = close_pin

        self.last_change_time = 0.0
        self.last_direction = 0       # +1 открывали, -1 закрывали
        self.breakaway_attempts = 0   # подряд неудачных breakaway-попыток

        self._rpm_history = deque(maxlen=rpm_filter_size)

        # Настройка GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.open_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.close_pin, GPIO.OUT, initial=GPIO.LOW)

    # ------------------------------------------------------------------ #
    #  Низкоуровневые помощники                                          #
    # ------------------------------------------------------------------ #
    def _effective_interval(self, rpm):
        """Пауза между коррекциями. В режиме breakaway — короче."""
        if rpm < self.breakaway_threshold:
            return max(self.breakaway_interval, MIN_CHANGE_TIME)
        return max(self.min_change_interval, MIN_CHANGE_TIME)

    def _pulse(self, pin, duration):
        """Выдать импульс на указанный пин."""
        now = time.time()
        if now - self.last_change_time < MIN_CHANGE_TIME:
            logging.warning('Импульс подавлен: прошло %.2f с (< MIN_CHANGE_TIME)',
                            now - self.last_change_time)
            return False
        self.last_change_time = now
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)
        self.last_direction = +1 if pin == self.open_pin else -1
        action = 'Открываем' if self.last_direction > 0 else 'Закрываем'
        logging.debug('%s кран на %.3f с', action, duration)
        return True

    def _filtered_rpm(self):
        """Прочитать сырой rpm и вернуть медиану последних N отсчётов."""
        raw = self.flow_sensor.get_rpm(max_age=2.0)
        self._rpm_history.append(raw)
        if not self._rpm_history:
            return 0.0
        return statistics.median(self._rpm_history)

    def _proportional_pulse(self, error):
        return min(max(self.kp * abs(error), self.min_pulse), self.max_pulse)

    # ------------------------------------------------------------------ #
    #  Публичный API                                                     #
    # ------------------------------------------------------------------ #
    def open_tap(self, arg_time=None):
        """Повернуть кран в открывающую сторону."""
        if arg_time is None:
            arg_time = self.rotation_time
        return self._pulse(self.open_pin, arg_time)

    def close_tap(self, arg_time=None):
        """Повернуть кран в закрывающую сторону."""
        if arg_time is None:
            arg_time = self.rotation_time
        return self._pulse(self.close_pin, arg_time)

    def close_tap_completely(self, duration=15.0):  # 15 — из AR-500-2 Manual
        """Полное закрытие крана: импульс duration секунд."""
        self.call_log()
        logging.info("Closing tap completely for %.1f sec", duration)
        GPIO.output(self.close_pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.close_pin, GPIO.LOW)
        self.last_change_time = time.time()
        self.last_direction = -1
        self.breakaway_attempts = 0
        self._rpm_history.clear()

    def adjust_flow(self):
        """
        Один шаг управления. Читает и фильтрует rpm, при необходимости
        выполняет пропорциональный импульс с учётом гистерезиса,
        демпфирования и breakaway.
        """
        rpm = self._filtered_rpm()
        logging.debug("Текущий rpm (filtered) = %.1f", rpm)

        now = time.time()
        interval = self._effective_interval(rpm)
        if now - self.last_change_time < interval:
            logging.debug("Пропуск регулировки: слишком рано (%.1f с из %.1f)",
                          now - self.last_change_time, interval)
            return

        target = (self.valid_low + self.valid_high) / 2.0
        error = rpm - target

        # --- Недобор: открываем ------------------------------------- #
        if rpm < self.valid_low - self.hysteresis:
            if rpm < self.breakaway_threshold:
                # Кран, скорее всего, полностью закрыт: наращиваем импульс
                pulse_time = min(
                    self.breakaway_start + self.breakaway_step * self.breakaway_attempts,
                    self.breakaway_max)
                self.breakaway_attempts += 1
                logging.debug("Breakaway: открытие %.2f с (попытка %d)",
                              pulse_time, self.breakaway_attempts)
                # Сбрасываем историю, чтобы следующее чтение сразу
                # отразило появление потока, а не «залипло» на старых нулях
                self._rpm_history.clear()
            else:
                self.breakaway_attempts = 0
                pulse_time = self._proportional_pulse(error)
                if self.last_direction == -1:
                    pulse_time *= 0.5
                    logging.debug("Демпфирование разворота: импульс -> %.3f с",
                                  pulse_time)
            self._pulse(self.open_pin, pulse_time)

        # --- Перебор: закрываем ------------------------------------- #
        elif rpm > self.valid_high + self.hysteresis:
            self.breakaway_attempts = 0
            pulse_time = self._proportional_pulse(error)
            if self.last_direction == +1:
                pulse_time *= 0.5
                logging.debug("Демпфирование разворота: импульс -> %.3f с",
                              pulse_time)
            self._pulse(self.close_pin, pulse_time)

        # --- В норме ------------------------------------------------- #
        else:
            if rpm >= self.breakaway_threshold:
                self.breakaway_attempts = 0
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
    TAP_CTRL = TapController(FLOW_SENSOR, valid_low=18, valid_high=25)

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
