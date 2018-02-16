import json
json1_file = open('dib-test.json')
json1_str = json1_file.read()
json1_data = json.loads(json1_str)

def parse(o):
    print('->{0}'.format(o))
    for x in o:
        try:
           iterable = iter(o[x])
        except TypeError:
           val = o[x]
           print("%s: %s" % (x, val))
        else:
           val = parse(o[x]) 

print type(json1_data)
#print json.dumps(json1_data, sort_keys=True, indent=4, separators=(',', ': '))

# parse(json1_data)

   # print("%s: %s" % (x, json1_data[x]))

for k,v in json1_data.iteritems():
    print k, type(v)

