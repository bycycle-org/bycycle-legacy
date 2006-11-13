<%flags>
    inherit = 'result.myt'
</%flags>

<%args>
   oResult
   extra_content = None
   set_as_s_or_e_display = 'block'
</%args>

% from urllib import unquote_plus
% sAddr = str(oResult.address)
% hAddr = sAddr.replace('\n', '<br />')
% fAddr = unquote_plus(oResult.urlStr())

<div class="address">
   <% hAddr %>
</div>

<div>
   <span class="show_on_map">
      <a href=""
         onclick="byCycle.UI.map.setCenter({
                    x: <% oResult.xy_ll.x %>, y: <% oResult.xy_ll.y %>
                  });
                  return false;"
         >Show on Map</a>
   </span>
   <% extra_content %>
</div>

<div class="set_as_s_or_e" style="display: <% set_as_s_or_e_display %>;">
   Set as
   <a href="#set-as-start"
      onclick="byCycle.UI.setAsStart('<% fAddr %>'); return false;"
      ><i>start</i></a> or
   <a href="#set-as-end"
      onclick="byCycle.UI.setAsEnd('<% fAddr %>'); return false;"
      ><i>end</i></a>
   address for route
</div>
