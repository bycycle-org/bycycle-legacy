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


<%python>
import time
import simplejson
region_key = c.service.region.key
multi_id = c.result_id
json = c.json
href_template = '/%s/geocode/%s' % (region_key, '%s')
onclick = "byCycle.UI.selectGeocode(this); return false;"
link_template = '<a href="%s" onclick="%s">%s</a>' % ('%s', onclick, '%s')
</%python>

<div class="multi">
    <%python>
    for i, geocode in enumerate(oResult):
        oAddr = geocode.address
        addr = '%s, %s' % (oAddr.street_name, oAddr.place)
        id_addr = geocode.network_id
        try:
            num = oAddr.number
        except AttributeError:
            pass
        else:
            addr = '%s %s' % (num, addr)
            id_addr = '%s %s' % (num, id_addr)
        url_addr = ';'.join((addr, id_addr)).replace(' ', '+')

        result_id = ('%.6f' % time.time()).replace('.', '')

        href = href_template % url_addr
        link = link_template % (href, '%s')
        
        c.title = link % ('Geocode #%s' % (i + 1))
        c.classes = ''  # Needed to override inherited c.classes == 'error'
        c.result_id = result_id
        c.json_id = '%s' % i
        c.json = simplejson.dumps(eval(repr(geocode)))

        extra = '<span> | %s</span>' % (link % 'Select')

        m.write(m.subexec('geocode.myt', oResult=geocode, extra_content=extra))
    c.result_id = multi_id
    c.json = json
    </%python>
</div>
