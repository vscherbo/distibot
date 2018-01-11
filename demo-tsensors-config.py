#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import ConfigParser
import io
import re

conf_file_name = 'distibot.ini'

with open(conf_file_name) as f:
    dib_config = f.read()

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(io.BytesIO(dib_config))

s_list = config.sections()
print(s_list)

if config.has_section('tsensors'):
    ts_list = config.options('tsensors')
    # print(ts_list)
    for ts in ts_list:
        res = re.match('^ts_(.*)_id$', ts)
        if res:
            print(res.group(1))
