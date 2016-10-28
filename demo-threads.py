#!/usr/bin/python

import thread
import time

# Define a function for the thread
def print_time( threadName, delay):
    global var1
    count = 0
    while count < 5:
        time.sleep(delay)
        count += 1
        print "%s: %s, var1=%s" % ( threadName, time.ctime(time.time()), var1 )
        if "Thread-1" == threadName:
            var1 = count + 1

var1 = 0;
# Create two threads as follows
try:
   thread.start_new_thread( print_time, ("Thread-1", 2, ) )
   thread.start_new_thread( print_time, ("Thread-2", 4, ) )
except:
   print "Error: unable to start thread"

while 1:
   pass
