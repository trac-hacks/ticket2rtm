#!/usr/bin/env python
#
# get_token.py
#   a script to get RTM authorized token.
#
# License: revised BSD
# Motohiro Takayama <mootoh@gmail.com>
#
import rtm
import sys

permission = 'write'
api_key = sys.argv[1]
api_shared_secret = sys.argv[2]

api = rtm.API(api_key, api_shared_secret)

frob = api.get_frob()
print 'Follow this link to authorize API accesss to your RTM.'
print 'After authorized, hit any key to continue.\n'
print '  ' + api.make_auth_url(permission, frob)
sys.stdin.readline()

print 'This is your ' + permission + '-authorized token !'
token = api.get_token(frob)
print '  ' + token
