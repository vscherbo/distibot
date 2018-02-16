#!/usr/bin/python -t
# -*- coding: utf-8 -*-

import collections
import sys

class Moonshine_controller(object):

    def __init__(self, log):
        self.log = log
        self.Tsteps = collections.OrderedDict()

    def load_config(self, conf_file_name):
        conf = open(conf_file_name, 'r')
        # self.Tsteps = collections.OrderedDict(sorted(eval(conf.read()).items(), key=lambda t: t[0]))
        self.conf_dict = collections.OrderedDict(sorted(eval(conf.read()).items(), key=lambda t: t[0]))
        conf.close()
        # self.set_Tsteps(self.Tsteps)

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

    def heat_on_pause(self):
        print "heat_on_pause"

    def start_watch_temperature(self):
        print "start_watch_temperature"

    def finish(self):
        print "finish"

    def do_nothing(self):
        print "do_nothing"

    def emergency_finish(self):
        print "emergency_finish"

    def send_msg(self, msg):
        print "send_msg={0}".format(msg)

    def set_power(self, power):
        print "set_power={0}".format(power)

mshinectl = Moonshine_controller(None)

"""
Tsteps = collections.OrderedDict()

inf = open('myfile.txt','r')
# dict_from_file = eval(inf.read())
Tsteps = collections.OrderedDict(sorted(eval(inf.read()).items(), key=lambda t: t[0]))
inf.close()
"""
mshinectl.load_config('dib-test.play2')

print "=== conf_dict"
print len(mshinectl.conf_dict)
print mshinectl.conf_dict.keys()

for key,val in mshinectl.conf_dict.iteritems():
    print 'key={0}\n'.format(key)
    val_ordered = collections.OrderedDict(sorted(val.iteritems(), key=lambda t: t[0]))
    for k1, v1 in val_ordered.iteritems():
        if 'tuple' == type(v1).__name__:
            for k2, v2 in enumerate(v1):
                print '      k1={0}, k2={1}, v2={2}\n'.format(k1, k2, v2.__name__)
        else:
            print '   k1={0}, v1={1}\n'.format(k1, v1.__name__)

sys.exit(0)

print "=== Tsteps"
print mshinectl.Tsteps

Tkeys = mshinectl.Tsteps.keys()
print "=== Tkeys"
print Tkeys


Talarm = Tkeys.pop(0)
Tcmd = mshinectl.Tsteps.pop(Talarm)

import time


while True:

    Tcmd()
    # self.function(*self.args, **self.kwargs)
    try:
        Talarm = Tkeys.pop(0)
    except IndexError:
        Talarm = 999.0
        break

    Tcmd = mshinectl.Tsteps.pop(Talarm, mshinectl.do_nothing)
    time.sleep(2)
