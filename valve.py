#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gpio_dev import GPIO_DEV, GPIO
import logging


class Valve(GPIO_DEV):

    def __init__(self, valve_gpio):
        super(Valve, self).__init__()
        self.valve_default_way = True
        self.valve_gpio = valve_gpio
        self.gpio_list.append(valve_gpio)
        GPIO.setup(self.valve_gpio, GPIO.OUT, initial=GPIO.LOW)

    def release(self):
        self.default_way()
        super(Valve, self).release()

    def default_way(self):
        logging.info("valve.default_way")
        if self.valve_default_way:
            pass
        else:
            GPIO.output(self.valve_gpio, GPIO.LOW)
            self.valve_default_way = True

    def power_on_way(self):
        logging.info("valve.power_on_way")
        if self.valve_default_way:
            GPIO.output(self.valve_gpio, GPIO.HIGH)
            self.valve_default_way = False

    def demo(self, sleep_time=2):
        logging.info("SingleValve power_on_way")
        v1.power_on_way()
        sleep(sleep_time)

        logging.info("SingleValve default_way")
        v1.default_way()


class DoubleValve(GPIO_DEV):

    def __init__(self, gpio_v1, gpio_v2):
        super(DoubleValve, self).__init__()
        self.v1_on = False
        self.v2_on = False
        self.way = 3
        # TODO check initial values
        self.gpio_v1 = gpio_v1
        self.gpio_v2 = gpio_v2
        self.gpio_list.append(gpio_v1)
        self.gpio_list.append(gpio_v2)
        GPIO.setup(self.gpio_v1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.gpio_v2, GPIO.OUT, initial=GPIO.LOW)
        # super(DoubleValve, self).setup((gpio_v1, gpio_v2), GPIO.OUT, initial=GPIO.LOW)

    def release(self):
        self.v1_turn_off()
        self.v2_turn_off()
        super(DoubleValve, self).release()
        logging.info("DblValve switched off")

    def v1_turn_on(self):
        if not self.v1_on:
            GPIO.output(self.gpio_v1, GPIO.HIGH)
            logging.info("DblValve v1_turn_on")
            self.v1_on = True

    def v1_turn_off(self):
        if self.v1_on:
            GPIO.output(self.gpio_v1, GPIO.LOW)
            logging.info("DblValve v1_turn_off")
            self.v1_on = False

    def v2_turn_on(self):
        if not self.v2_on:
            GPIO.output(self.gpio_v2, GPIO.HIGH)
            logging.info("DblValve v2_turn_on")
            self.v2_on = True

    def v2_turn_off(self):
        if self.v2_on:
            GPIO.output(self.gpio_v2, GPIO.LOW)
            logging.info("DblValve v2_turn_off")
            self.v2_on = False

    def way_1(self):
        if not self.way == 1:
            self.v1_turn_on()
            self.v2_turn_off()
            self.way = 1

    def way_2(self):
        if not self.way == 2:
            self.v1_turn_off()
            self.v2_turn_on()
            self.way = 2

    def way_3(self):
        if not self.way == 3:
            self.v1_turn_off()
            self.v2_turn_off()
            self.way = 3

    def demo(self, sleep_time=2):
        logging.info("way_1")
        v1.way_1()
        sleep(sleep_time)

        logging.info("way_2")
        v1.way_2()
        sleep(sleep_time)

        # default way, both valves are off
        logging.info("way_3")
        v1.way_3()
        sleep(sleep_time)

        logging.info("way_1 again")
        v1.way_1()
        sleep(sleep_time)


if __name__ == "__main__":
    from time import sleep
    import argparse
    import os
    import sys
    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    # conf_file = prg_name +".conf"

    parser = argparse.ArgumentParser(description='Distibot "valve" module')
    parser.add_argument('--log_to_file', type=bool, default=False, help='log destination')
    parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
    parser.add_argument('--ports', type=str, help='valve port OR comma separated ports')
    parser.add_argument('--delay', type=int, default=2, help='seconds between steps')
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

    # end of prolog
    logging.info('Started')

    ports = args.ports.split(",")
    if len(ports) > 1:
        v_port1 = int(ports[0])  # 23
        v_port2 = int(ports[1])  # 24
        logging.debug('DoubleValve port1={0}, port2={1}'.format(v_port1, v_port2))
        v1 = DoubleValve(gpio_v1=v_port1, gpio_v2=v_port2)
    else:
        v_port1 = int(ports[0])
        logging.debug('SingleValve port1={0}'.format(v_port1))
        v1 = Valve(valve_gpio=v_port1)

    v1.demo(sleep_time=args.delay)

    logging.info("release")
    v1.release()
    sys.exit()
