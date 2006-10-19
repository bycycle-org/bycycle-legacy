<h2>Multiple Matches Found</h2>

<p>
  <ul class="result_list">

% region_key = c.service.region.key
% for i, geocode in enumerate(c.geocodes):
%     oAddr = geocode.address
%     field_addr = '%s, %s' % (oAddr.street_name, oAddr.place)
%     try:
%         num = oAddr.number
%     except AttributeError:
%         id_addr = geocode.network_id
%     else:
%         id_addr = '%s+%s' % (num, geocode.network_id)
%

      <li>
        <% str(oAddr).replace('\n', '<br />') %><br />
        <a href="<% c.region %>/geocode/<% id_addr %>"
           onclick="byCycle.UI.map.setCenter(
                        {x: <% geocode.xy.x %>, y: <% geocode.xy.y %>}
                    );
                    return false;"
           >Show on Map</a>
        &middot;
        <a href="/<% c.region %>/geocode/<% id_addr %>?region=<% region_key %>"
           onclick="byCycle.UI.selectGeocode(<% i %>); return false;"
           >Select</a>
      </li>

% #for

  </ul>
</p>


<p>
  <input id='oResult' type="hidden" value='<% c.json %>' />
</p>
