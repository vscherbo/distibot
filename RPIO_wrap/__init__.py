#!/usr/bin/python -t
# -*- coding: utf-8 -*-


import os
is_raspi = os.uname()[4].startswith('arm')
if is_raspi:
    import RPIO
    rpi_ver = RPIO.version()
else:
    import RPIO_emu as RPIO
    rpi_ver = RPIO.version()
