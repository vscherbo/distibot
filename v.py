#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gpio_dib import GPIO_DIB, GPIO
import logging
import inspect


class Valve(GPIO_DIB):

    def __init__(self, valve_gpio):
        super(Valve, self).__init__()
        self.valve_gpio = valve_gpio
        self.gpio_list.append(valve_gpio)
        GPIO.setup(self.valve_gpio, GPIO.OUT, initial=GPIO.LOW)

    def release(self):
        self.output(self.valve_gpio, GPIO.LOW)
        super(Valve, self).release()

    def output(self, channel, value):
        super(Valve, self).output(channel, value)

    @property
    def default_way(self):
        """ Returns True if valve is switched off (default way)."""
        # LOW=0=False
        return not GPIO.input(self.valve_gpio)

    def switch_off(self):
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__
        the_method = stack[1][0].f_code.co_name
        logging.info("called from method=%s.%s", the_class, the_method)
        logging.info('self.default_way=%s', 
                      self.default_way)
        if self.default_way:
            logging.info("Do nothing, already on default way")
        else:
            self.output(self.valve_gpio, GPIO.LOW)

    def power_on_way(self):
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__
        the_method = stack[1][0].f_code.co_name
        logging.info("called from method=%s.%s", the_class, the_method)
        logging.info('self.default_way=%s', 
                      self.default_way)
        if self.default_way:
            self.output(self.valve_gpio, GPIO.HIGH)
        else:
            logging.info("Do nothing, already power_on_way")

    # create Demo class
    def demo(self, sleep_time=2):
        logging.info("SingleValve power_on_way")
        v1.power_on_way()
        sleep(sleep_time)

        logging.info("SingleValve default_way")
        v1.switch_off()


class DoubleValve(GPIO_DIB):

    def __init__(self, gpio_v1, gpio_v2):
        super(DoubleValve, self).__init__()
        self.way = 3
        # TODO check initial values
        self.gpio_v1 = gpio_v1
        self.gpio_v2 = gpio_v2
        #super(DoubleValve, self).setup(self.gpio_v1, GPIO.OUT, initial=GPIO.LOW)
        #super(DoubleValve, self).setup(self.gpio_v2, GPIO.OUT, initial=GPIO.LOW)
        super(DoubleValve, self).setup([gpio_v1, gpio_v2], GPIO.OUT, initial=GPIO.LOW)

    def release(self):
        # forced set way_3: both valves are off
        self.way_3(True)
        super(DoubleValve, self).release()
        logging.info("DblValve switched off")

    @property
    def v1_on(self):
        """ Returns True if v1 is switched on."""
        # HIGH=1=True
        return GPIO.input(self.gpio_v1)

    @property
    def v2_on(self):
        """ Returns True if v2 is switched on."""
        # HIGH=1=True
        return GPIO.input(self.gpio_v2)

    def v1_turn_on(self):
        if not self.v1_on:
            super(DoubleValve, self).output(self.gpio_v1, GPIO.HIGH)
            logging.info("DblValve v1_turn_on")

    def v1_turn_off(self):
        if self.v1_on:
            super(DoubleValve, self).output(self.gpio_v1, GPIO.LOW)
            logging.info("DblValve v1_turn_off")

    def v2_turn_on(self):
        if not self.v2_on:
            super(DoubleValve, self).output(self.gpio_v2, GPIO.HIGH)
            logging.info("DblValve v2_turn_on")

    def v2_turn_off(self):
        if self.v2_on:
            super(DoubleValve, self).output(self.gpio_v2, GPIO.LOW)
            logging.info("DblValve v2_turn_off")

    def way_1(self):
        if not self.way == 1:
            self.v1_turn_on()
            self.v2_turn_off()
            self.way = 1
        else:
            logging.info("Do nothing: DblValve is on way_1")

    def way_2(self):
        if not self.way == 2:
            self.v1_turn_off()
            self.v2_turn_on()
            self.way = 2
        else:
            logging.info("Do nothing: DblValve is on way_2")

    def way_3(self, forced=True):
        if forced or (not self.way == 3):
            self.v1_turn_off()
            self.v2_turn_off()
            self.way = 3
        else:
            logging.info("Do nothing: DblValve is on way_3")

    # create Demo class, move method to it
    def demo(self, sleep_time=2):
        #logging.info("way_1")
        #v1.way_1()
        #sleep(sleep_time)

        logging.info("way_2")
        v1.way_2()
        sleep(sleep_time)

        # default way, both valves are off
        #logging.info("way_3")
        #v1.way_3()
        #sleep(sleep_time)

        #logging.info("way_1 again")
        #v1.way_1()
        #sleep(sleep_time)


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

    #log_format = '[%(filename)-20s:%(lineno)4s - %(funcName)18s()] %(levelname)-7s\
    #    | %(asctime)-15s | %(message)s'
    log_format = '[%(filename)-12s:%(lineno)4s - %(funcName)18s()] \
        | %(asctime)-15s | %(message)s'

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
