#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import gpio_class
import time


class Cooker(gpio_class.gpio):
    powers = (120, 300, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000)
    max_power_index = len(powers)-1
    power_max = powers[-1]
    power_min = powers[0]

    def __init__(self, gpio_on_off, gpio_up, gpio_down, gpio_fry):
        super(Cooker, self).__init__()
        self.gpio_on_off = gpio_on_off
        self.gpio_list.append(gpio_on_off)
        GPIO.setup(self.gpio_on_off, GPIO.OUT, initial=GPIO.HIGH)
        #
        self.gpio_up = gpio_up
        self.gpio_list.append(gpio_up)
        GPIO.setup(self.gpio_up, GPIO.OUT, initial=GPIO.HIGH)
        #
        self.gpio_down = gpio_down
        self.gpio_list.append(gpio_down)
        GPIO.setup(self.gpio_down, GPIO.OUT, initial=GPIO.HIGH)
        #
        self.gpio_fry = gpio_fry
        self.gpio_list.append(gpio_fry)
        GPIO.setup(self.gpio_fry, GPIO.OUT, initial=GPIO.HIGH)
        #
        self.power_index = 6  # 1400W
        self.state_on = False
        self.target_power_index = 0

    def release(self):
        self.logger.info("cooker.release")
        self.switch_off()
        super(Cooker, self).release()


    def click_button(self, gpio_port_num):
        time.sleep(0.1)  # для двух "нажатий" подряд
        GPIO.output(gpio_port_num, 0)
        time.sleep(0.1)
        GPIO.output(gpio_port_num, 1)
        self.logger.debug('clicked GPIO_port={gpio}'.format(gpio=gpio_port_num))

    def switch_on(self, force_mode=False):
        if force_mode:
            self.state_on = False
        if not self.state_on:
            self.click_button(self.gpio_on_off)
            self.power_index = 6  # 1400W
            self.state_on = True

    def switch_off(self, force_mode=False):
        if force_mode:
            self.state_on = True
        if self.state_on:
            self.logger.info("switch_OFF")
            self.click_button(self.gpio_on_off)
            self.state_on = False

    def set_fry(self):
        self.logger.info("set_Fry")
        self.click_button(self.gpio_fry)
        self.power_index = self.max_power_index

    def power_up(self):
        if self.power_index < self.max_power_index:
            self.click_button(self.gpio_up)
            self.power_index += 1
            self.logger.debug("power_up, new_index={}".format(self.power_index))
            return True
        else:
            self.logger.debug("power_up False, index={}".format(self.power_index))
            return False

    def set_power_max(self):
        while self.power_up():
            pass
            self.logger.debug("set_power_max loop, power={}".format(self.current_power()))

    def power_down(self):
        if self.power_index > 0:
            self.click_button(self.gpio_down)
            self.power_index -= 1
            self.logger.debug("power_down, new_index={}".format(self.power_index))
            return True
        else:
            self.logger.debug("power_down False, index={}".format(self.power_index))
            return False

    def set_power_min(self):
        while self.power_down():
            pass
            self.logger.debug("set_power_min loop, power={}".format(self.current_power()))

    def set_power_600(self):
        self.switch_on()
        while self.current_power() > 600:
            self.power_down()
            self.logger.debug("power_600 loop, power={}".format(self.current_power()))

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
        except LookupError as e:
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
    ck = Cooker(gpio_on_off=17, gpio_up=22, gpio_down=27, gpio_fry=15)
    ck.switch_on()
    sleep(2)

    ck.set_power_1800()
    sleep(3)

    ck.set_power_1200()
    ck.logger.info(ck.current_power())
    sleep(3)

    ck.logger.info('set Fry mode')
    ck.set_fry()
    sleep(2)
    ck.logger.info(ck.current_power())

    ck.release()

