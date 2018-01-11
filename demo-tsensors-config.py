#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import ConfigParser
import io
import re

conf_file_name = 'distibot.conf'

with open(conf_file_name) as f:
    dib_config = f.read()

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(io.BytesIO(dib_config))

# if config.has_section('tsensors'):
ts_list = config.options('tsensors')
ts_names = []
for ts in ts_list:
    res = re.match('^ts_(.*)_id$', ts)
    if res:
        ts_names.append(res.group(1))
        ts_id = config.get('tsensors', ts)
        print(ts_id)
print(ts_names)
