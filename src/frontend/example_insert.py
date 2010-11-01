#!/usr/bin/env python

import httplib

host = httplib.HTTPConnection('cse521s-wsn-project.appspot.com')

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
  "temperature":61
 }
]
"""

host.request('PUT', '/lot/my_home', my_json)
resp = host.getresponse()
print resp.status, resp.reason
print resp.read()
