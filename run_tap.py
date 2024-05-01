#!/usr/bin/env python
""" An AR500 Tap Controller """

import tap_controller

if __name__ == '__main__':
    import sys
    import logging
    import flow_sensor

    LOG_FORMAT = '%(asctime)-15s | %(levelname)-7s | %(message)s'
    logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT,
                        level=logging.DEBUG)

    FLOW_SENSOR = flow_sensor.FlowSensor(5)
    #FLOW_SENSOR = flow_sensor.FlowSensorFake(5)
    TAP_CTRL = tap_controller.TapController(FLOW_SENSOR, [18, 22])

    TAP_CTRL.open_tap()

    sys.exit()
