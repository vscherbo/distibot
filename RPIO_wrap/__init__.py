#!/usr/bin/python -t
# -*- coding: utf-8 -*-

try:
    import RPIO
except:
    import RPIO_wrap.RPIO as RPIO
finally:
    print RPIO.rpi_ver
