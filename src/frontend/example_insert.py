#!/usr/bin/env python

import httplib

host = httplib.HTTPConnection('localhost:8080')

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

host.request('PUT', '/lot/31', my_json)
resp = host.getresponse()
print resp.status, resp.reason
print resp.read()
