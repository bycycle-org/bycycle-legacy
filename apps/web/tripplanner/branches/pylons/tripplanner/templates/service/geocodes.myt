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
href_template = '/%s/geocode/%%s' % region_key
onclick_template = "byCycle.UI.selectGeocode('%s'); return false;"
link_template = '<a href="%s" onclick="%s">%%s</a>'
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
        onclick = onclick_template % result_id
        link = link_template % (href, onclick)

        s = (result_id, link % ('Geocode #%s' % (i + 1)))
        c.title = '<span id="title%s">%s</span>' % s
        # Needed to override inherited c.classes == 'error'
        c.classes = ['', 'first_multi'][i == 0]
        c.result_id = result_id
        c.json = simplejson.dumps(eval(repr(geocode)))

        s = (result_id, link % 'Select')
        extra = '<span id="extra%s"> | %s</span>' % s

        m.write(m.subexec('geocode.myt', oResult=geocode, extra_content=extra))
    </%python>
</div>
