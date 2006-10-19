<div id="<% c.result_id %>" class="window result">
  <div class="title_bar">
    <table>
      <tbody>
        <tr>
          <td class="l"><b>Route</b></td>
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
    [Route table goes here]
    <a href=""
       onclick="return false;"
       >Show on Map</a>  
    <input id='oResult<% c.result_id %>' type="hidden" value='<% c.json %>' />
  </div>
</div>
