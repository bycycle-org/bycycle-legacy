<%
from urllib import unquote_plus
code = c.geocode
x = code.xy_ll.x
y = code.xy_ll.y
str_addr = str(code.address)
html_addr = str_addr.replace('\n', '<br />')
field_addr = unquote_plus(code.urlStr())
%>

<div class="fixed-pane">
   <div class="title-bar">
      <div class="title">Location</div>
   </div>

   <div class="content-pane">
      <div class="header"></div>

      <div class="body">
         <div class="address">
            ${html_addr}
         </div>
      </div>

      <div class="footer" style="display: none;">
         <div class="show-on-map">
            <a class="show-on-map-link"
               href="#show-on-map"
               title="Show this location on the map"
               onclick="byCycle.UI.map.setCenter({x: ${x}, y: ${y}}); return false;"
               >Show on map</a>
         </div>

         <div class="set_as_s_or_e">
            Set as
            <a class="set-as-start"
               href="#set-as-start"
               title="Use this as the starting point of a route"
               onclick='byCycle.UI.setAsStart("${field_addr}"); return false;'
               ><i>start</i></a> or
            <a class="set-as-end"
               href="#set-as-end"
               title="Use this as the end point of a route"
               onclick='byCycle.UI.setAsEnd("${field_addr}"); return false;'
               ><i>end</i></a>
            address for route
         </div>
      </div>
   </div>
</div>