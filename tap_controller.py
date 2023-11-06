""" An AR500 Tap Controller """

import time
#import RPi.GPIO as GPIO
from gpio_dev import GPIO_DEV, GPIO

MIN_CHANGE_TIME=1

class TapController(GPIO_DEV):
    """
        A class to control a tap with an electrical driver and two wires for switch rotation.
    """
    def __init__(self, arg_flow_sensor, valid_range, open_pin=19, close_pin=13):
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
        self.valid_range = valid_range
        self.min_change_time = MIN_CHANGE_TIME
        self.last_change_time = 0
        self.open_pin = open_pin
        self.close_pin = close_pin
        self.pins = [open_pin, close_pin]
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.open_pin, GPIO.OUT)
        GPIO.setup(self.close_pin, GPIO.OUT)
        GPIO.output(self.open_pin, GPIO.LOW)
        GPIO.output(self.close_pin, GPIO.LOW)

    def open_tap(self):
        """
        Rotate the tap to the open position.
        """
        current_time = time.time()
        if current_time - self.last_change_time >= self.min_change_time:
            self.last_change_time = current_time
            GPIO.output(self.open_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.open_pin, GPIO.LOW)

    def close_tap(self):
        """
        Rotate the tap to the closed position.
        """
        current_time = time.time()
        if current_time - self.last_change_time >= self.min_change_time:
            self.last_change_time = current_time
            GPIO.output(self.close_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.close_pin, GPIO.LOW)

    def adjust_flow(self):
        """
        Adjust the tap position based on the current flow rate.
        If the flow rate is below the valid range, open the tap.
        If the flow rate is above the valid range, close the tap.
        """
        current_rpm = self.flow_sensor.get_rpm()
        if current_rpm < self.valid_range[0]:
            logging.debug('LESS current_rpm=%s', current_rpm)
            self.open_tap()
            time.sleep(self.min_change_time)
        elif current_rpm > self.valid_range[1]:
            logging.debug('MORE current_rpm=%s', current_rpm)
            self.close_tap()
            time.sleep(self.min_change_time)
        else:
            # Flow is within valid range
            pass

    def __del__(self):
        """
        Clean up the GPIO pins that were used by the TapController object.
        """
        for pin in self.pins:
            GPIO.setup(pin, GPIO.IN)

if __name__ == '__main__':
    import sys
    import logging
    import flow_sensor

    LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(message)s'
    logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT,
                        level=logging.DEBUG)

    #FLOW_SENSOR = flow_sensor.FlowSensor(5)
    FLOW_SENSOR = flow_sensor.FlowSensorFake(5)
    TAP_CTRL = TapController(FLOW_SENSOR, [18, 22])
    DO_FLAG = True
    while DO_FLAG:
        try:
            time.sleep(2)
            TAP_CTRL.adjust_flow()
        except KeyboardInterrupt:
            logging.info('\ncaught keyboard interrupt!, bye')
            DO_FLAG = False

    sys.exit()
