#!/usr/bin/python -t
# -*- coding: utf-8 -*-

try:
    import RPIO
except:
    import RPIO_wrap.RPIO as RPIO
finally:
    # DEBUG only. Must be removed
    print RPIO.rpi_ver
