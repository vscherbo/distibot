#!/usr/bin/python -t
# -*- coding: utf-8 -*-


# Emulator
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
RAISING = 0
FALLING = 0
BOTH = 0

def setup(channel, direction, pull_up_down=PUD_OFF, initial=0):
    pass


def output(channel, state):
    pass


def sysinfo():
    return "rpi-emu"


def version():
    """ Returns a tuple of (VERSION, VERSION_GPIO) """
    return ("0.1", "0.0")


def remove_event_detect(port):
    pass


def add_event_detect(port, edge, bouncetime):
    pass


def add_event_callback(port, callback):
    pass


def cleanup(gpio_list=[]):
    pass


def setwarnings(enabled=True):
    pass


def getmode():
    pass


def setmode(mode):
    pass
