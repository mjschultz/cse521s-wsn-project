#!/usr/bin/env python

import httplib
import sys
import random
import json

if len(sys.argv) >= 2 :
    hostname = sys.argv[1]
else :
    hostname = 'cse521s-wsn-project.appspot.com'

if len(sys.argv) >= 3 :
    lotname = sys.argv[2]
else :
    lotname = 'wustl_millbrook'

def space_list(min, max, items) :
    for i in range(items) :
        yield random.randint(min,max)

host = httplib.HTTPConnection(hostname)
simulating = True
while simulating :
    print 'PUT to',hostname,'in lot',lotname,'...',

    # generage a random number of spaces to change
    spaces = []
    changed = random.randint(1, 8)
    for space_id in space_list(0, 10, changed) :
        space = {'space_id': space_id,
                 'is_empty': bool(random.randint(0,1))}
        for thing in ('temperature','sonar','light','magnet') :
            if bool(random.randint(0,1)) :
                space[thing] = int(random.random()*256)
        spaces.append(space)

    host.request('PUT', '/lot/'+lotname, json.dumps(spaces))
    resp = host.getresponse()
    print resp.read()
    for space in spaces :
        print 'space_id:',space['space_id'],
        if space['is_empty'] :
            print 'is empty'
        else :
            print 'is filled'
        del space['space_id']
        del space['is_empty']
        print '\t'+str(space)

    next_round = raw_input('Continue (Y/n): ')
    if next_round not in ('', 'yes', 'y', 'Y') :
        simulating = False

print 'Done.'
