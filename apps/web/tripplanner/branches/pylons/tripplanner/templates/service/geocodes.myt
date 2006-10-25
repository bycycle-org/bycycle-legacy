<%doc>
   geocodes.myt
   Mad template logic
</%doc>

<%flags>
   inherit = 'result.myt'
</%flags>

<%args>
   oResult
</%args>


% import time
% import simplejson


% region_key = c.service.region.key
% multi_id = c.result_id
% onclick_template = '''byCycle.UI.selectGeocode("%s"); return false;'''


<div class="multi">
% for i, geocode in enumerate(oResult):
%   oAddr = geocode.address
%   addr = '%s, %s' % (oAddr.street_name, oAddr.place)
%   id_addr = geocode.network_id
%   try:
%     num = oAddr.number
%   except AttributeError:
%     pass
%   else:
%     addr = '%s %s' % (num, addr)
%     id_addr = '%s %s' % (num, id_addr)
%   result_id = ('%.6f' % time.time()).replace('.', '')
%   url_addr = ';'.join((addr, id_addr))
%   json = simplejson.dumps(eval(repr(geocode)))
%   onclick = onclick_template % (result_id)
%   link = """<a href='/%s/geocode/%s' onclick='%s'>%%s</a>""" % (region_key, url_addr, onclick)
%   c.classes = ['', 'first_multi'][i == 0]
%   c.title = '''<span id="title%s">Geocode %s</span>''' % (result_id, link % ('#%s' % (i + 1)))
%   c.result_id = result_id
%   c.json = json
%   extra = '''<span id="extra%s"> | %s</span>''' % (result_id, (link % 'Select'))
  <% m.subexec('geocode.myt', oResult=geocode, extra_content=extra) %>
% #for
</div>
