<%doc>
   route_multi.myt
</%doc>

<%flags>
   inherit = 'result.myt'
</%flags>

<%args>
   oResult
</%args>


<%python>
import time
import simplejson
region_key = c.region_key
multi_id = c.result_id
json = c.json
title = c.title
classes = c.classes
last_i = (len(oResult) - 1)
order = {0: 'Start', last_i: 'End'}
href_template = '/%s/route/%s' % (region_key, '%s')
onclick = "byCycle.UI.selectRouteGeocode(this, %s); return false;"
link_template = '<a href="%s" onclick="%s">%s</a>' % ('%s', onclick, '%s')
first = True  # First in oResult having multiple matches
</%python>

<div class="multi">
    <%python>
    for i, geocodes in enumerate(oResult):
        if not isinstance(geocodes, list):
            continue
        m.write("""
        <div class="geocodes" style="display: %s;">
            <b>Choose %s Address</b>
        """ % (['none', 'block'][first], order.get(i, (i + 1))))
        for j, geocode in enumerate(geocodes):
            href = href_template % geocode.urlStr()
            link = (link_template % (href.replace('%', '%%'), i, '%s'))
            c.title = '#%s' % (j + 1)
            c.classes = ''  # Needed to override inherited c.classes == 'error'
            c.result_id = ('%.6f' % time.time()).replace('.', '')
            c.json_id = '%s' % j
            c.json = simplejson.dumps(eval(repr(geocode)))
            extra = '<span> | %s</span>' % (link % 'Select')
            m.write(m.subexec('geocode.myt', oResult=geocode, extra_content=extra, set_as_s_or_e_display='none'))
        m.write("""
        </div>
        """)            
        if first:
            first = False
    c.result_id = multi_id
    c.collapsible = False
    c.title = title
    c.classes = classes
    c.json_id = ''
    c.json = json
    </%python>
</div>
