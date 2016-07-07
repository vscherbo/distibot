#!/usr/bin/python -t
# -*- coding: utf-8 -*-

import collections
import time

class Moonshine_controller(object):

    def __init__(self, log):
        self.log = log

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

inf = open('myfile.txt','r')
dict_from_file = eval(inf.read())
inf.close()

print dict_from_file

Tsteps = collections.OrderedDict()
#Tsteps = dict_from_file
Tsteps = collections.OrderedDict(sorted(dict_from_file.items(), key=lambda t: t[0]))

print "=== Tsteps"
print Tsteps

Tkeys = Tsteps.keys()
print "=== Tkeys"
print Tkeys


Talarm = Tkeys.pop(0)
Tcmd = Tsteps.pop(Talarm)

while True:

    Tcmd()
    try:
        Talarm = Tkeys.pop(0)
    except IndexError:
        Talarm = 999.0
        break

    Tcmd = Tsteps.pop(Talarm, mshinectl.do_nothing)
    time.sleep(2)
