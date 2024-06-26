#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A cooker control module"""

import time
import logging
from configparser import ConfigParser
from gpio_dev import GPIO_DEV, GPIO


class Cooker(GPIO_DEV):
    """A Cooker class"""

    def __init__(self, gpio_on_off, gpio_up, gpio_down, gpio_special,
                 powers, init_power, special_power, do_init_special):
        super().__init__()
        self.gpio_on_off = gpio_on_off
        self.setup(self.gpio_on_off, GPIO.OUT, initial=GPIO.LOW)

        self.gpio_up = gpio_up
        self.setup(self.gpio_up, GPIO.OUT, initial=GPIO.LOW)

        self.gpio_down = gpio_down
        self.setup(self.gpio_down, GPIO.OUT, initial=GPIO.LOW)

        self.gpio_special = gpio_special
        self.setup(self.gpio_special, GPIO.OUT, initial=GPIO.LOW)

        self.click_delay = 0.5
        self.state_on = False
        self.target_power_index = 0

        self.powers = powers
        self.max_power_index = len(powers)-1
        self.power_max = powers[-1]
        self.power_min = powers[0]
        self.do_init_special = do_init_special
        self.ini_power_index = self.powers.index(init_power)
        self.ini_special_index = self.powers.index(special_power)
        self.power_index = None

    def release(self):
        """Release the cooker control module"""
        self.call_log()
        logging.info("cooker.release")
        self.switch_off()
        super().release()

    def click_button(self, gpio_port_num):
        """Click a button of the cooker"""
        time.sleep(self.click_delay)  # для двух "нажатий" подряд
        self.output(gpio_port_num, GPIO.HIGH)
        time.sleep(self.click_delay)
        self.output(gpio_port_num, GPIO.LOW)

    def switch_on(self, power_value=None):
        """
        Switch the cooker on

        Args:
            power_value: The power value for the cooker

        """
        self.call_log()
        if not self.state_on:
            self.click_button(self.gpio_on_off)
            self.power_index = self.ini_power_index
            self.state_on = True
            logging.info("switched ON")
        if self.do_init_special:
            self.click_button(self.gpio_special)
            self.power_index = self.ini_special_index

        if power_value is not None:
            logging.debug("switch_on, arg power_value=%s", power_value)
            self.set_power(power_value)
            self.power_index = self.powers.index(power_value)
            logging.debug("switched on, current_power=%s", self.current_power())

    def switch_off(self):
        """Switch the cooker off"""
        self.call_log()
        if self.state_on:
            logging.info("switch_OFF")
            self.click_button(self.gpio_on_off)
            self.state_on = False

    def power_up(self):
        """Increase the power of the cooker"""
        if self.power_index < self.max_power_index:
            self.click_button(self.gpio_up)
            self.power_index += 1
            logging.debug("power_up, new_index=%s, new_power=%s",
                          self.power_index, self.current_power())
            result = True
        else:
            logging.debug("power_up, False index=%s, power=%s",
                          self.power_index, self.current_power())
            result = False
        return result

    def set_power_max(self):
        """Set the maximum power of the cooker"""
        while self.power_up():
            logging.debug("set_power_max loop, power=%s", self.current_power())

    def power_down(self):
        """Decrease the power of the cooker by pressing the <-> button.

        Returns:
            True if the power was successfully lowered,
            False if it was already at the minimum power level and could not be lowered further.
        """
        if self.power_index > 0:
            self.click_button(self.gpio_down)
            self.power_index -= 1
            logging.debug("power_down, new_index=%s, new_power=%s",\
                          self.power_index, self.current_power())
            result = True
        else:
            logging.debug("power_down, False index=%s, power=%s",\
                          self.power_index, self.current_power())
            result = False
        return result

    def set_power_min(self):
        while self.power_down():
            logging.debug("set_power_min loop, power=%s" ,self.current_power())

        # TODO detect wrong power OR approximate
    def set_power(self, power):
        """Set the power of the cooker to the specified level.

        Args:
            power: The desired power level.

        Raises:
            Exception: If the power level is invalid.

        Returns:
            None.
        """
        logging.debug("set_power arg_power=%s" ,power)
        try:
            self.target_power_index = self.powers.index(power)
        except Exception:
            logging.exception('set_power index error', exc_info=True)
            self.switch_off()
            self.switch_on()
        else:
            if self.power_index > self.target_power_index:
                change_power = self.power_down
                do_change = True
            elif self.power_index < self.target_power_index:
                change_power = self.power_up
                do_change = True
            else:
                do_change = False
            while do_change:
                change_power()
                do_change = (self.power_index != self.target_power_index)

    def current_power(self):
        """Get the current power level of the cooker."""
        return self.powers[self.power_index]


class CookerTester():
    """ tester running play script """
    def __init__(self, conf_filename='distibot.conf'):
        self.config = ConfigParser()
        self.config.read(conf_filename)
        self.play = None

        self.cooker = Cooker(gpio_on_off=self.config.getint('cooker', 'gpio_cooker_on_off'),
                             gpio_up=self.config.getint('cooker', 'gpio_cooker_up'),
                             gpio_down=self.config.getint('cooker', 'gpio_cooker_down'),
                             gpio_special=self.config.getint('cooker', 'gpio_cooker_special'),
                             powers=eval(self.config.get('cooker', 'cooker_powers')),
                             init_power=self.config.getint('cooker', 'cooker_init_power'),
                             special_power=self.config.getint('cooker', 'cooker_special_power'),
                             do_init_special=self.config.getboolean('cooker', 'init_special')
                             )

    def load_script(self, play_file_name):
        script = open(play_file_name, 'r')
        self.play = eval(script.read())
        script.close()

    def play_script(self, arg_delay=3):
        for play_stage in self.play:
            logging.debug('======================== run play_stage={0}'.format(play_stage))
            self.cooker.set_power(play_stage)
            logging.info('>>> current_power={}'.format(self.cooker.current_power()))
            time.sleep(arg_delay)

if __name__ == '__main__':
    import argparse
    import os
    import sys

    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))

    parser = argparse.ArgumentParser(description='Distibot "cooker" module')
    parser.add_argument('--conf', type=str, default="distibot.conf", help='conf file')
    parser.add_argument('--play', type=str, default="cooker.play", help='play file')
    parser.add_argument('--log_to_file', type=bool, default=False, help='log destination')
    parser.add_argument('--log_level', type=str, default="DEBUG", help='log level')
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)

    LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(message)s'

    if args.log_to_file:
        LOG_DIR = ''
        log_file = LOG_DIR + prg_name + ".log"
        logging.basicConfig(filename=log_file, format=LOG_FORMAT, level=numeric_level)
    else:
        logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT, level=numeric_level)

    logging.info('Started')
    ckt = CookerTester(args.conf)

    ckt.cooker.switch_on()
    time.sleep(2)

    # cooker_play = (240, 150, 80, 150)
    ckt.load_script(args.play)
    ckt.play_script()

    bck_power = ckt.cooker.current_power()
    logging.debug('bck_power=%s', bck_power)

    ckt.cooker.switch_off()
    time.sleep(2)
    ckt.cooker.switch_on(bck_power)
    time.sleep(2)

    ckt.cooker.release()

    logging.info('Finished')
