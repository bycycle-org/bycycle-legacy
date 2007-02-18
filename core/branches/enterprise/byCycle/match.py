#!/usr/bin/python
import re

p = '(?P<name>\w+)\s*:(?P<value>\w[\w\s]*\w) '

q = 'address:633 n alberta region: portlandor'
vars = {}
m = re.split('\w+\s*:', q)
print m
while 0 and m:
    i, j = m.start(), m.end()
    var = q[i:j].strip().rstrip(':')
    vars[var] = ''
    print var, j, q[j:]
    m = re.match('\s+\w+\s*:', q[j:])

print vars
