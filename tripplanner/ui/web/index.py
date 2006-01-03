#!/usr/local/bin/python2.4
print 'Content-Type: text/html\r\n\r'

import os, datetime
import time 
import byCycle

#E = os.environ
#print E['HTTP_HOST']


template = '%stripplanner/ui/web/tripplanner.tmpl' % byCycle.install_path
stat = os.stat(template)
last_modified = datetime.date.fromtimestamp(stat.st_mtime)
last_modified = last_modified.strftime("%B %d, %Y")

data = {'last_modified': last_modified}

template_file = open(template)
print template_file.read() % data
template_file.close()
