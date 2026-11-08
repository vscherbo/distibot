#!/usr/bin/env python

"""
Тестирование связки Valve (соленоид), FlowSensor, TapController
без участия Distibot и cooker.
"""

import logging
import sys
import threading
import time

from flow_sensor import FlowSensor
from tap_controller import TapController
# Импортируем нужные классы
from valve import Valve

# from configparser import ConfigParser


# Настройка логирования
LOG_FORMAT = '[%(filename)-22s:%(lineno)4s - %(funcName)20s()] \
              %(levelname)-7s | %(asctime)-15s | %(message)s'
logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT, level=logging.DEBUG)

# Конфигурация (можно вынести в отдельный файл или задать здесь)
CONF = {
    'valve_water_gpio': 6,        # GPIO для соленоидного клапана воды
    'flow_sensor_gpio': 5,          # GPIO для датчика потока
    'tap_open_pin': 19,             # GPIO для открытия крана
    'tap_close_pin': 13,            # GPIO для закрытия крана
    'flow_valid_low': 18,           # нижняя граница потока (Гц)
    'flow_valid_high': 25,          # верхняя граница (Гц)
    'min_change_interval': 3.0,     # мин. интервал между движениями крана (сек)
    # 'rotation_time': 0.4,           # время одного импульса (сек)
    'rotation_time': 1.0,           # время одного импульса (сек)
    'hysteresis': 2.0,              # гистерезис (Гц)
    'start_flow_timeout': 30,       # время без потока до аварии (сек)
    'flow_timeout': 15              # время без потока до аварии (сек)
}


class WaterSystemTester:
    """Тестер системы охлаждения (клапан, датчик потока, кран)"""

    def __init__(self, config):
        self.config = config
        self.water_on = False
        self.loop_flag = True
        self.flow_timer = None

        # Инициализация устройств
        self.valve_water = Valve(valve_gpio=config['valve_water_gpio'])
        self.flow_sensor = FlowSensor(gpio_fs=config['flow_sensor_gpio'])
        self.tap_controller = TapController(
            arg_flow_sensor=self.flow_sensor,
            valid_low=config['flow_valid_low'],
            valid_high=config['flow_valid_high'],
            open_pin=config['tap_open_pin'],
            close_pin=config['tap_close_pin'],
            min_change_interval=config['min_change_interval'],
            rotation_time=config['rotation_time'],
            hysteresis=config['hysteresis']
        )

        # Принудительно закрываем кран при старте
        logging.info("Закрываем кран полностью (15 сек)")
        self.tap_controller.close_tap_completely(15.0)

    def start_water(self):
        """Открыть соленоидный клапан и начать контроль потока"""
        if self.water_on:
            logging.warning("Вода уже включена")
            return
        logging.info("Открываем соленоидный клапан воды")
        self.valve_water.power_on_way()
        self.water_on = True

        # Запускаем таймер контроля потока
        self.current_timeout = self.config['start_flow_timeout']
        self.flow_timer = threading.Timer(self.current_timeout, self.no_flow)
        self.flow_timer.start()
        # Устанавливаем обработчик событий датчика потока
        self.flow_sensor.watch_flow(self.flow_detected)
        logging.info("Система охлаждения запущена")

    def flow_detected(self, gpio_id):
        """Обработчик импульсов датчика потока"""
        if not self.water_on:
            return
        # Сброс таймера
        if self.flow_timer:
            self.flow_timer.cancel()
        self.current_timeout = self.config['flow_timeout']
        self.flow_timer = threading.Timer(self.current_timeout, self.no_flow)
        self.flow_timer.start()
        # Обработка клика (обновление статистики)
        self.flow_sensor.handle_click()
        logging.debug("Импульс потока, кликов: %d, Гц: %.1f",
                      self.flow_sensor.clicks, self.flow_sensor.get_rpm())

    def no_flow(self):
        """Аварийная остановка при пропадании потока"""
        logging.error("НЕТ ПОТОКА ОХЛАЖДЕНИЯ в течение %d сек! Аварийная остановка.",
                      self.current_timeout)
        self.stop_process()

    def adjust_flow_loop(self):
        """Цикл регулировки потока (вызывается периодически)"""
        while self.loop_flag and self.water_on:
            self.tap_controller.adjust_flow()
            time.sleep(self.config['min_change_interval'])

    def stop_process(self):
        """Остановка: закрыть клапан, закрыть кран, завершить циклы"""
        logging.info("Остановка системы охлаждения")
        self.loop_flag = False
        if self.water_on:
            self.tap_controller.close_tap_completely(15.0)
            logging.info("Кран закрыт")
            self.valve_water.switch_off()
            logging.info("Соленоидный клапан закрыт")
            self.water_on = False
        if self.flow_timer:
            self.flow_timer.cancel()

    def release(self):
        """Освобождение ресурсов"""
        self.stop_process()
        self.valve_water.release()
        self.flow_sensor.release()
        self.tap_controller.release()
        logging.info("Ресурсы освобождены")


def main():
    """ Just main """
    tester = WaterSystemTester(CONF)
    try:
        input("Нажмите Enter для открытия воды и запуска регулировки...")
        tester.start_water()
        # Запускаем цикл регулировки в отдельном потоке
        adjust_thread = threading.Thread(target=tester.adjust_flow_loop)
        adjust_thread.daemon = True
        adjust_thread.start()
        # Основной поток просто ждёт команды
        print("Система работает. Нажмите Ctrl+C для остановки.")
        while tester.loop_flag:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Получен сигнал прерывания")
    finally:
        tester.release()
        logging.info("Тест завершён")


if __name__ == "__main__":
    main()
