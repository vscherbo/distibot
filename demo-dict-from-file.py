#!/usr/bin/python -t
# -*- coding: utf-8 -*-

import collections
import time

class Moonshine_controller(object):

    def __init__(self, log):
        self.log = log
        self.Tsteps = collections.OrderedDict()

    def load_config(self, conf_file_name):
        conf = open(conf_file_name, 'r')
        self.Tsteps = collections.OrderedDict(sorted(eval(conf.read()).items(), key=lambda t: t[0]))
        conf.close()
        self.set_Tsteps(self.Tsteps)

    def set_Tsteps(self, Tsteps):
        self.Tkeys = Tsteps.keys()
        self.Talarm = self.Tkeys.pop(0)
        self.Tcmd = Tsteps.pop(self.Talarm)

    def start_process(self):
        print "start_process"

    def start_watch_heads(self):
        print "start_watch_heads"

    def stop_body(self):
        print "stop_body"

    def finish(self):
        print "finish"

    def do_nothing(self):
        print "do_nothing"

mshinectl = Moonshine_controller(None)

"""
Tsteps = collections.OrderedDict()

inf = open('myfile.txt','r')
# dict_from_file = eval(inf.read())
Tsteps = collections.OrderedDict(sorted(eval(inf.read()).items(), key=lambda t: t[0]))
inf.close()
"""
mshinectl.load_config('myfile.txt')

print "=== Tsteps"
print mshinectl.Tsteps

Tkeys = mshinectl.Tsteps.keys()
print "=== Tkeys"
print Tkeys


Talarm = Tkeys.pop(0)
Tcmd = mshinectl.Tsteps.pop(Talarm)

while True:

    Tcmd()
    try:
        Talarm = Tkeys.pop(0)
    except IndexError:
        Talarm = 999.0
        break

    Tcmd = mshinectl.Tsteps.pop(Talarm, mshinectl.do_nothing)
    time.sleep(2)
