#!/bin/sh

./flow_sensor.py & ./valve.py --port=6 --delay=25
# ./flow_sensor.py & { sleep 0;  ./valve.py --port=6 --delay=25; }

