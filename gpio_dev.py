#!/usr/bin/env python
"""
Class for GPIO devices
"""

import importlib.util
import inspect

try:
    spec = importlib.util.find_spec('RPi')
    if spec is None:
        raise ImportError
    from RPi import GPIO

    # import RPi.GPIO as GPIO
except ImportError:
    from FakeRPi import GPIO
    # import FakeRPi.GPIO as GPIO

import logging

GPIO_LEVEL = {False: 'LOW', True: 'HIGH'}


class GPIODevError(Exception):
    """Custom exception for GPIO_DEV related errors."""
    pass


class GPIO_DEV():
    """
    A class to control GPIO
    """

    def __init__(self):
        self.gpio_list = []
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        try:
            GPIO.setmode(GPIO.BCM)
        except RuntimeError as e:
            logging.error("Failed to set GPIO mode: %s", e)
            raise GPIODevError(f"GPIO initialization failed: {e}") from e
        logging.info('gpio_dev initialized')

    def setup(self, channel, mode, pull_up_down=GPIO.PUD_OFF, initial=None):
        """Setup channels with logging and collect gpio_list."""
        try:
            if initial is not None:
                GPIO.setup(channel, mode, pull_up_down=pull_up_down, initial=initial)
            else:
                GPIO.setup(channel, mode, pull_up_down=pull_up_down)
        except (ValueError, RuntimeError) as e:
            logging.error("Failed to setup channel %s: %s", channel, e)
            raise GPIODevError(f"GPIO setup error for channel {channel}: {e}") from e

        logging.info('BEFORE append gpio_list=%s, channel=%s',
                     self.gpio_list, channel)

        if isinstance(channel, (list, tuple)):
            self.gpio_list.extend(channel)
        else:
            self.gpio_list.append(channel)

        logging.info('gpio_list=%s', self.gpio_list)

    def output(self, channel, value):
        """Output with logging."""
        try:
            GPIO.output(channel, value)
        except ValueError as e:
            logging.error("Failed to set output on channel %s: %s", channel, e)
            raise GPIODevError(f"GPIO output error for channel {channel}: {e}") from e

        logging.info('OUTPUT channel=%s, value=%s', channel, GPIO_LEVEL[value])

    def input(self, channel):
        """Input with logging."""
        try:
            val = GPIO.input(channel)
        except ValueError as e:
            logging.error("Failed to read input from channel %s: %s", channel, e)
            raise GPIODevError(f"GPIO input error for channel {channel}: {e}") from e

        logging.info('INPUT channel=%s, val=%s', channel, GPIO_LEVEL[val])
        return val

    def call_log(self):
        """Logging method calls."""
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__
        the_method = stack[1][0].f_code.co_name
        logging.info("called %s.%s", the_class, the_method)

    def release(self):
        """Release GPIO resources by cleaning up assigned pins."""
        if len(self.gpio_list) > 0:
            try:
                GPIO.cleanup(self.gpio_list)
            except Exception as e:  # Catch potential cleanup issues
                logging.error("Error during GPIO cleanup: %s", e)
                # Depending on requirements, might still want to clear the list
                # or re-raise the exception.
                # Here, we log and continue to ensure the internal state is cleared.
                raise GPIODevError(f"GPIO cleanup error: {e}") from e
            pin_str = ', '.join(map(str, self.gpio_list))
            logging.info("cleaned gpio_list=[%s]", pin_str)
            self.gpio_list = []
        logging.info('gpio_dev released')


if __name__ == "__main__":
    import os
    import sys
    LOG_DIR = ''
    LOG_FORMAT = '[%(filename)-20s:%(lineno)4s - %(funcName)20s()] \
%(levelname)-7s | %(asctime)-15s | %(message)s'
    (prg_name, prg_ext) = os.path.splitext(os.path.basename(__file__))
    # logging.basicConfig(filename=prg_name+'.log', \
    #        format=log_format, level=logging.INFO)
    logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT,
                        level=logging.DEBUG)
    logging.info('Started')
    g1 = GPIO_DEV()
    g1.setup(23, GPIO.OUT, initial=GPIO.LOW)
    g1.setup(24, GPIO.OUT, initial=GPIO.LOW)
    g1.release()
    logging.info('Finished')
