#!/usr/bin/env python

import httplib
import sys
import random
import json
import time
from datetime import datetime as dtdt
from datetime import time as dtt

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

simulating = True
while simulating :
    host = httplib.HTTPConnection(hostname)
    print 'PUT to',hostname,'in lot',lotname,'...',

    # generage a random number of spaces to change
    spaces = []
    changed = random.randint(1, 10)
    now = dtdt.now()
    six_oclock = dtdt.combine(now.date(), dtt(6, 00))
    seven_oclock = dtdt.combine(now.date(), dtt(7, 00))
    twelve_oclock = dtdt.combine(now.date(), dtt(12, 00))
    thirteen_oclock = dtdt.combine(now.date(), dtt(13, 00))
    eighteen_oclock = dtdt.combine(now.date(), dtt(18, 00))
    nineteen_oclock = dtdt.combine(now.date(), dtt(19, 00))
    twentytwo_oclock = dtdt.combine(now.date(), dtt(22, 00))
    five_oclock = dtdt.combine(now.date(), dtt(5, 00))
    if six_oclock <= now <= seven_oclock :
        weight = 3
    elif twelve_oclock <= now <= thirteen_oclock :
        changed *= 2
        weight = 3
    elif eighteen_oclock <= now <= nineteen_oclock :
        weight = 3
    elif now >= twentytwo_oclock or now <= five_oclock :
        weight = 5
        changed /= 2
    else :
        weight = 1

    for space_id in space_list(0, 30, changed) :
        space = {'space_id': space_id,
                 'is_empty': bool(random.randint(0,weight))}
        for thing in ('temperature','sonar','light','magnet') :
            if bool(random.randint(0,1)) :
                space[thing] = int(random.random()*256)
        spaces.append(space)

    host.request('PUT', '/lot/'+lotname, json.dumps(spaces))
    print json.dumps(spaces)
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

    host.close()
    time.sleep(90+random.randint(-30,30))
    # sleeps between 60 and 120 seconds

print 'Done.'
