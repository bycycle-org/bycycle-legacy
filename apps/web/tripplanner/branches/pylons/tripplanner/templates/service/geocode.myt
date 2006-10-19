<div id="<% c.result_id %>" class="window result">
  <div class="title_bar">
    <table>
      <tbody>
        <tr>
          <td class="l"><b>Address</b></td>
          <td class="r">
            <a class="button"
               href=""
               title="Remove this Result"
               onclick="$('<% c.result_id %>').parentNode.removeChild($('<% c.result_id %>')); return false;"
               >X</a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="content_pane">
    <% str(c.geocode.address).replace('\n', '<br />') %><br />
    <a href=""
       onclick="byCycle.UI.map.setCenter(
                    {x: <% c.geocode.xy.x %>, y: <% c.geocode.xy.y %>}
                );
                return false;"
       >Show on Map</a>
    <input id='oResult' type="hidden" value='<% c.json %>' />
  </div>
</div>
