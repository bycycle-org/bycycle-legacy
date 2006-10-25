<div id="<% c.result_id %>" class="window result <% c.classes %>">
  <div class="title_bar">
    <table>
      <tbody>
        <tr>
          <td class="l"><b><% c.title %></b></td>
          <td class="r">
            <a class="button"
               href=""
               title="Close"
               onclick="Element.remove('<% c.result_id %>'); return false;"
               >X</a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="content_pane">
    <% m.call_next() %>
    <input id='json' type="hidden" value='<% c.json %>' />
  </div>
</div>
