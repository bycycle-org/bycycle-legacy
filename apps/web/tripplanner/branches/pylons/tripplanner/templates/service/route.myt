<%flags>
    inherit = 'result.myt'
</%flags>


<%args>
   oResult
</%args>


<%python>
    # route = {
    #    'start': {'geocode': Geocode, 'original': string},
    #    'end': {'geocode': Geocode, 'original': string},
    #    'linestring': [],
    #    'directions': [],
    #    'distance':   {},
    # }
    route = oResult[0]
    units = c.service.region.units
    distance = route.distance[units]
    miles = distance / 5280.0
    mi = '%.2f' % miles
    km = '%.2f' % (miles * 1.609344)
    s = route.start['geocode']
    s_addr = s.address
    e = route.end['geocode']
    e_addr = e.address
    directions = route.directions
    linestring = route.linestring
    s_addr = str(s_addr).replace('\n', '<br/>')
    e_addr = str(e_addr).replace('\n', '<br/>')
    last_street = e_addr.split('<br/>', 1)[0]
    tab = '&nbsp;&nbsp;&nbsp;&nbsp;'
</%python>


<div class="summary">
    <div class="start">
        <a href="javascript:void('Show map blowup')" class="start"
           onclick="byCycle.UI.map.showMapBlowup(0); return false;"
           ><% s_addr %></a></h2>
    </div>
    <div class="end">
        <a href="javascript:void('Show map blowup');" class="end"
           onclick="byCycle.UI.map.showMapBlowup(<% linestring.numPoints() - 1 %>);"
           ><% e_addr %></a>
    </div>
    <div class="total_distance" style="border-bottom: none;">
        <% mi %> miles (<% km %> km)
    </div>
</div>


<div id="reverse_div">
    <a href="/%s/route/%s to %s"
       onclick="reverseDirections('%s', '%s');"
       >Reverse Directions</a>
</div>


<div class="directions">
% row_class = 'a'
% last_i = len(directions) - 1
% for i, d in enumerate(directions):
%     turn = d['turn']
%     street = d['street']
%     if turn == 'straight':
%         prev = street[0]
%         curr = street[1]
%         cmd_on = '%s <b>becomes</b> %s' % (prev, curr)
%     else:
%         if i == 0:
%             cmd, on = 'Go', 'on'
%         else:
%             cmd, on = 'Turn', 'onto'
%         onto = '<b>%s</b>' % street
%         cmd_on = '%s <b>%s</b> %s %s' % (cmd, turn, on, onto)
%     toward_street = d['toward']
%     toward = 'toward %s'
%     if not toward_street:
%         toward = ['', toward % last_street][i == last_i]
%     else:
%         toward = toward % toward_street
%     jogs = d['jogs']
%     if jogs:
%         J = ['<br/>%sJogs...' % tab]
%         for j in jogs:
%             J.append('<br/>%s%s&middot; <i>%s</i> at %s' %
%                      (tab, tab, j['turn'], j['street']))
%         jogs = ''.join(J)
%     else:
%         jogs = ''
%     ls_index = d['linestring_index']
%     distance = d['distance'][units]
%     miles = distance / 5280.0  # TODO: region.toMiles(distance)
%     mi = '%.2f' % miles
%     km = '%.2f' % (miles * 1.609344)
%     bikemodes = d['bikemode']
%     bikemodes = ['', ' [%s]' % ', '.join([b for b in bikemodes])][bool(bikemodes)]
    <div class="<% row_class %>">
        <b><% i + 1 %>.</b>
        <a href="javascript:void('Show map blowup')"
           onclick="byCycle.UI.map.showMapBlowup()"
           ><% cmd_on %></a>
           <% toward %>
           -- <% mi %>mi (<% km %> km)
           <% bikemodes %>
           <% jogs %>
    </div>
%     row_class = ['a', 'b'][row_class == 'a']
% #for
    <div class="<% row_class %>">
        <a href="javascript:void('Show map blowup')"
           onclick="byCycle.UI.map.showMapBlowup()"
           ><b>End</b> at <b><% last_street %></b></a>    
    </div>
</div>
