#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
import RPIO
import time
import valve
import sys

RPIO.setmode(RPIO.BCM)
# res = RPIO.gpio_function(10)
# print "res=",str(res)
# sys.exit()

v1 = valve.DoubleValve(gpio_v1=24, gpio_v2=23)


def socket_callback(socket, val):
    print("socket %s: '%s'" % (socket.fileno(), val))
    global do_flag
    do_flag = False
    socket.send("echo: %s\n" % val)
    global v1
    if 1 == val:
        v1.way_1()
    elif 2 == val:
        v1.way_2()
    elif 3 == val:
        v1.way_3()
    else:
        print("unknown valve way=%s" % val)
    # RPIO.close_tcp_client(socket.fileno())

# TCP socket server callback on port 8080
# RPIO.add_tcp_callback(8080, socket_callback, threaded_callback=True)

# Blocking main epoll loop
# RPIO.wait_for_interrupts(threaded=True)

# do_flag = True
# main loop
# while do_flag:
#    print "wait for cmd on port 8080"
#    time.sleep(2)

way_time = 3

print("way_1")
v1.way_1()
time.sleep(way_time)

print("way_2")
v1.way_2()
time.sleep(way_time)

# default way, both valves are off
print("way_3")
v1.way_3()
time.sleep(way_time)

print("way_1 again")
v1.way_1()
time.sleep(way_time)

print("release")
v1.release()
sys.exit()
