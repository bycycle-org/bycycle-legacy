<%doc>
   geocodes.myt
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
href_template = '/%s/geocode/%s' % (region_key, '%s')
onclick = "byCycle.UI.selectGeocode(this); return false;"
link_template = '<a href="%s" onclick="%s">%s</a>' % ('%s', onclick, '%s')
</%python>

<div class="multi">
    <%python>
    for i, geocode in enumerate(oResult):
        href = href_template % geocode.urlStr()
        link = link_template % (href.replace('%', '%%'), '%s')
        c.title = '#%s' % (i + 1)
        c.classes = ''  # Needed to override inherited c.classes == 'error'
        c.result_id = ('%.6f' % time.time()).replace('.', '')
        c.json_id = '%s' % i
        c.json = simplejson.dumps(eval(repr(geocode)))
        extra = '<span> | %s</span>' % (link % 'Select')
        m.write(m.subexec('geocode.myt', oResult=geocode, extra_content=extra, set_as_s_or_e_display='none'))
    c.result_id = multi_id
    c.title = title
    c.toggleable = False
    c.classes = classes
    c.json_id = ''
    c.json = json
    </%python>
</div>
