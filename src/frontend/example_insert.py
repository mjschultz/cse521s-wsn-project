#!/usr/bin/env python

import httplib
import sys

if len(sys.argv) >= 2 :
    hostname = sys.argv[1]
else :
    hostname = 'cse521s-wsn-project.appspot.com'

if len(sys.argv) >= 3 :
    lotname = sys.argv[2]
else :
    lotname = 'wustl_millbrook'

print 'PUT to',hostname,'in lot',lotname

host = httplib.HTTPConnection(hostname)

my_json = """
[
 {
  "space_id":1,
  "is_empty":false,
  "temperature":71
 },
 {
  "space_id":2,
  "is_empty":true,
  "temperature":31
 },
 {
  "space_id":3,
  "is_empty":false,
  "temperature":91
 }
]
"""

host.request('PUT', '/lot/'+lotname, my_json)
resp = host.getresponse()
print resp.status, resp.reason
print resp.read()
