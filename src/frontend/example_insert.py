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
  "temperature":31
 },
 {
  "space_id":3,
  "is_empty":false,
  "temperature":91
 },
 {
  "space_id":4,
  "is_empty":false,
  "magnet":226
 },
 {
  "space_id":5,
  "is_empty":true,
  "light":89
 }
]
"""

host.request('PUT', '/lot/mjs_home', my_json)
resp = host.getresponse()
print resp.status, resp.reason
print resp.read()
