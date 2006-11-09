<%flags>
    inherit = 'result.myt'
</%flags>

<%args>
   oResult
   extra_content = None
</%args>

<div class="address">
   <% str(oResult.address).replace('\n', '<br />') %><br />
</div>

<div class="show_on_map">
   <a href=""
      onclick="byCycle.UI.map.setCenter({
                 x: <% oResult.xy_ll.x %>, y: <% oResult.xy_ll.y %>
               });
               return false;"
      >Show on Map</a>
      <% extra_content %>
</div>
