#!/usr/bin/env python
# *-* coding: utf-8 *-*

import json
import jsontree

json1_file = open('dib-test.json')
json1_str = json1_file.read()
json1_data = json.loads(json1_str)

def dict_generator(indict, pre=None):
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_generator(value, pre + [key]):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in dict_generator(v, pre + [key]):
                        yield d
            else:
                yield pre + [key, value]
    else:
        yield indict


print type(json1_data)
#print json.dumps(json1_data, sort_keys=True, indent=4, separators=(',', ': '))


#for i in dict_generator(json1_data):
#    print i

dib_tree = jsontree.loads(json1_str)
for i in dib_tree['temperature_sensors']:
    print "id={0}".format(i.id)
    for s in i.play:
        print "t={0}".format(s.temperature)
        for f in s.funcs:
            # print "func.name={0}".format(f.name)
            f_name = "{0}".format(f.name)
            loc_args = []
            for kwa in f.args:
                loc_args.append("{}='{}'".format(kwa, f.args[kwa].encode('utf-8')))
            print "  {}({})".format(f_name, ','.join(loc_args))
