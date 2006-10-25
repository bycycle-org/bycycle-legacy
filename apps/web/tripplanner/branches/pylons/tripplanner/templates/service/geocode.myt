<%flags>
    inherit = 'result.myt'
</%flags>

<%args>
   oResult
   extra_content = None
</%args>

<% str(oResult.address).replace('\n', '<br />') %><br />
<a href=""
   onclick="byCycle.UI.map.setCenter({
              x: <% oResult.xy.x %>, y: <% oResult.xy.y %>
            });
            return false;"
   >Show on Map</a>
   <% extra_content %>
