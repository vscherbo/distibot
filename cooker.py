#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gpio_dev import GPIO_DEV, GPIO
import time
import logging


class Cooker(GPIO_DEV):

    def __init__(self, gpio_on_off, gpio_up, gpio_down, gpio_special, powers, init_power):
        super(Cooker, self).__init__()
        self.gpio_on_off = gpio_on_off
        self.gpio_list.append(gpio_on_off)
        GPIO.setup(self.gpio_on_off, GPIO.OUT, initial=GPIO.LOW)
        #
        self.gpio_up = gpio_up
        self.gpio_list.append(gpio_up)
        GPIO.setup(self.gpio_up, GPIO.OUT, initial=GPIO.LOW)
        #
        self.gpio_down = gpio_down
        self.gpio_list.append(gpio_down)
        GPIO.setup(self.gpio_down, GPIO.OUT, initial=GPIO.LOW)
        #
        self.gpio_special = gpio_special
        self.gpio_list.append(gpio_special)
        GPIO.setup(self.gpio_special, GPIO.OUT, initial=GPIO.LOW)
        #
        self.power_index = 6  # 1400W
        self.state_on = False
        self.target_power_index = 0

        # powers = (120, 300, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000)
        self.powers = powers
        self.max_power_index = len(powers)-1
        self.power_max = powers[-1]
        self.power_min = powers[0]
        self.init_power = init_power
        self.ini_power_index = self.powers.index(init_power)

    def release(self):
        logging.info("cooker.release")
        self.switch_off()
        super(Cooker, self).release()

    def click_button(self, gpio_port_num):
        time.sleep(0.1)  # для двух "нажатий" подряд
        GPIO.output(gpio_port_num, 1)
        time.sleep(0.1)
        GPIO.output(gpio_port_num, 0)
        logging.debug('clicked self_port={gpio}'.format(gpio=gpio_port_num))

    def switch_on(self, force_mode=False):
        if force_mode:
            self.state_on = False
        if not self.state_on:
            self.click_button(self.gpio_on_off)
            # self.power_index = 6  # 1400W
            self.power_index = self.ini_power_index
            self.state_on = True

    def switch_off(self, force_mode=False):
        if force_mode:
            self.state_on = True
        if self.state_on:
            logging.info("switch_OFF")
            self.click_button(self.gpio_on_off)
            self.state_on = False

    def set_special(self):
        # TODO different cookers, diffirent special
        logging.info("set_special")
        self.click_button(self.gpio_special)
        self.power_index = self.max_power_index

    def power_up(self):
        if self.power_index < self.max_power_index:
            self.click_button(self.gpio_up)
            self.power_index += 1
            logging.debug("power_up, new_index={}".format(self.power_index))
            return True
        else:
            logging.debug("power_up False, index={}".format(self.power_index))
            return False

    def set_power_max(self):
        while self.power_up():
            pass
            logging.debug("set_power_max loop, power={}".format(self.current_power()))

    def power_down(self):
        if self.power_index > 0:
            self.click_button(self.gpio_down)
            self.power_index -= 1
            logging.debug("power_down, new_index={}".format(self.power_index))
            return True
        else:
            logging.debug("power_down False, index={}".format(self.power_index))
            return False

    def set_power_min(self):
        while self.power_down():
            pass
            logging.debug("set_power_min loop, power={}".format(self.current_power()))

    def set_power_600(self):
        self.switch_on()
        while self.current_power() > 600:
            self.power_down()
            logging.debug("power_600 loop, power={}".format(self.current_power()))

    def set_power_300(self):
        self.set_power(300)

    def set_power_1200(self):
        self.set_power(1200)

    def set_power_1800(self):
        self.set_power(1800)

    def set_power(self, power):
        # TODO detect wrong power OR approximate
        try:
            self.target_power_index = self.powers.index(power)
        except LookupError:
            logging.error('set_power index lookup', exc_info=True)
            self.switch_off()
            self.switch_on()
        else:
            if self.power_index > self.target_power_index:
                change_power = self.power_down
            else:
                change_power = self.power_up
            while self.power_index != self.target_power_index:
                change_power()

    def current_power(self):
        return self.powers[self.power_index]

if __name__ == '__main__':
    from time import sleep
    import argparse
    import os
    import sys
    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    # conf_file = prg_name +".conf"

    parser = argparse.ArgumentParser(description='Distibot "cooker" module')
    parser.add_argument('--log_to_file', type=bool, default=False, help='log destination')
    parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
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

    logging.info('Started')

    ck = Cooker(gpio_on_off=17, gpio_up=22, gpio_down=27, gpio_special=15,
                powers=(120, 300, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000),
                init_power=1400)
    logging.info('ini_power_index={0}'.format(ck.ini_power_index))
    ck.switch_on()
    sleep(2)

    ck.set_power_1800()
    logging.info(ck.current_power())
    sleep(3)

    ck.set_power_1200()
    logging.info(ck.current_power())
    sleep(3)

    ck.set_special()
    sleep(2)
    logging.info(ck.current_power())

    ck.release()

    logging.info('Finished')
