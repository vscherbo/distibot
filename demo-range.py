#!/usr/bin/python -t
# -*- coding: utf-8 -*-


def step_emu_mode(x):
    if x < 16:
        return 1.0
    elif x < 18:
        return 0.1
    else:
        return 0.5

"""
def setup_emu_mode():
    self.emu_mode = True
    self.Trange = [x * 0.1 for x in range(200, 99999)]
    self.emu_iterator = iter(self.Trange)
"""


v = 1

for i in range(1, 55):
    v += step_emu_mode(v)
    print v
