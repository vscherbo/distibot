#!/usr/bin/python -t
# -*- coding: utf-8 -*-


rpi_ver = 'emu v0.1'
VERSION_GPIO = 0
RPI_REVISION = 0
RPI_REVISION_HEX = 0
HIGH = 0
LOW = 0
OUT = 0
IN = 0
ALT0 = 0
BOARD = 0
BCM = 0
PUD_OFF = 0
PUD_UP = 0
PUD_DOWN = 0


def setup(channel, direction, pull_up_down=PUD_OFF, initial=0):
    pass


def output(channel, state):
    pass


def sysinfo():
    return "rpi-emu"


def version():
    """ Returns a tuple of (VERSION, VERSION_GPIO) """
    return ("0.1", "0.0")


def add_tcp_callback(port, callback, threaded_callback=False):
    pass


def add_interrupt_callback(gpio_id, callback, edge='both',
                           pull_up_down=None, threaded_callback=False,
                           debounce_timeout_ms=None):
    pass


def del_interrupt_callback(gpio_id):
    pass


def close_tcp_client(fileno):
    pass


def wait_for_interrupts(threaded=False, epoll_timeout=1):
    pass


def stop_waiting_for_interrupts():
    pass


def cleanup_interrupts():
    pass


def cleanup():
    pass


def setwarnings(enabled=True):
    pass

