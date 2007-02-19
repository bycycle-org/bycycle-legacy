<%flags>
    inherit = 'result.myt'
</%flags>


<%args>
   oResult
</%args>


<%python>
    from urllib import unquote_plus
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
    linestring = route.linestring_ll
    s_addr = str(s_addr).replace('\n', '<br/>')
    e_addr = str(e_addr).replace('\n', '<br/>')
    last_street = e_addr.split('<br/>', 1)[0]
    s_url_str = s.urlStr()
    e_url_str = e.urlStr()
    tab = '&nbsp;&nbsp;&nbsp;&nbsp;'
    map_blowup_href = "#show-map-blowup"
    map_blowup_onclick = "byCycle.UI.map.showMapBlowup({x: %s, y: %s}); return false;"
</%python>


<div class="summary">
    <div class="start">
        <a href="<% map_blowup_href %>" class="start"
           onclick="<% map_blowup_onclick % (s.xy_ll.x, s.xy_ll.y) %>"
           ><% s_addr %></a></h2>
    </div>
    <div class="end">
        <a href="<% map_blowup_href %>" class="end"
           onclick="<% map_blowup_onclick % (e.xy_ll.x, e.xy_ll.y) %>;"
           ><% e_addr %></a>
    </div>
    <div class="total_distance" style="border-bottom: none;">
        <% mi %> miles (<% km %> km)
    </div>
</div>


<div id="reverse_div">
    <a href="/<% c.region_key %>/route/['<% e_url_str %>', '<% s_url_str %>']"
       onclick="byCycle.UI.reverseDirections('<% unquote_plus(e_url_str) %>', '<% unquote_plus(s_url_str) %>'); return false;"
       >Reverse Directions</a>
</div>


<div class="directions">
% last_i = len(directions) - 1
% row_class = 'a'
% for i, d in enumerate(directions):
%     row_class = h.cycle('a', 'b')
%     turn = d['turn']
%     street = d['street']
%     point = linestring.pointN(d['linestring_index'])
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
        <a href="<% map_blowup_href %>"
           onclick="<% map_blowup_onclick % (point.x, point.y) %>"
           ><% cmd_on %></a>
           <% toward %>
           -- <% mi %>mi (<% km %> km)
           <% bikemodes %>
           <% jogs %>
    </div>
% #for


    <div class="<% row_class %>">
        <a href="<% map_blowup_href %>"
           onclick="<% map_blowup_onclick % (e.xy_ll.x, e.xy_ll.y) %>"
           ><b>End</b> at <b><% last_street %></b></a>
    </div>
</div>


<p>
  <b>Disclaimer</b>: As you are riding, please keep in mind that you don't 
  <i>have</i> to follow the suggested route. <i>It may not be safe at any 
  given point.</i> If you see what looks like an unsafe or undesirable 
  stretch in the suggested route, you can decide to walk, ride on the 
  sidewalk, or go a different way.
</p>


<p>
  Users should independently verify all information presented here. This 
  service is provided <b>AS IS</b> with <b>NO WARRANTY</b> of any kind.
</p>
