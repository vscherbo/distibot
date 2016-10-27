import RPIO
import time

def socket_callback(socket, val):
    print("socket %s: '%s'" % (socket.fileno(), val))
    global do_flag
    do_flag = False
    # socket.send("echo: %s\n" % val)

# TCP socket server callback on port 8080
RPIO.add_tcp_callback(8080, socket_callback, threaded_callback=True)

# Blocking main epoll loop
RPIO.wait_for_interrupts(threaded=True)

do_flag = True

# main loop
while do_flag:
    print "main"
    time.sleep(2)
