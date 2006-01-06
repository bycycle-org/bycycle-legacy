#!/usr/local/bin/python2.4
print 'Content-Type: text/html\r\n\r'

import os, cgi, datetime
import time 
import byCycle

template = '%stripplanner/ui/web/tripplanner.tmpl' % byCycle.install_path

E = os.environ
host = E['HTTP_HOST']

cgi_data = cgi.FieldStorage(keep_blank_values=True)
form_data = {}
for key in cgi_data.keys():
    val = cgi_data.getfirst(key, '').strip()
    if val: form_data[key.strip()] = val


# Create an options list of regions, setting the selected region if we got here
# by http://x.bycycle.org/tripplanner where x is the name of some region
region = host.split('.')[0]
region_option = '<option value="%s">%s</option>'
region_option_selected = '<option value="%s" selected="selected">%s</option>'
regions_map = {'Milwaukee, WI': 'milwaukee',
              'Portland, OR': 'portland'}
regions = regions_map.keys()
regions.sort()
regions_option_list = []
for r in regions:
    region_abbrev = regions_map[r]
    if region_abbrev == region:
        regions_option_list.append(region_option_selected%(region_abbrev, r))
    else:
        regions_option_list.append(region_option%(region_abbrev, r))
regions_option_list = '\n'.join(regions_option_list)

# Get the last modified date of the template
stat = os.stat(template)
last_modified = datetime.date.fromtimestamp(stat.st_mtime)
last_modified = last_modified.strftime("%B %d, %Y")


data = {'last_modified': last_modified,
        'regions_option_list': regions_option_list}


template_file = open(template)
print template_file.read() % data
template_file.close()
