% top_level = 'parentNode.parentNode.parentNode.parentNode.parentNode.parentNode'
<div id="<% c.result_id %>" class="window result <% c.classes %>">
  <div class="title_bar">
    <table>
      <tbody>
        <tr>
          <td class="l title"><b><% c.title %></b></td>
          <td class="r">
            <a class="button"
               href=""
               title="Close"
               onclick="Element.remove(this.<% top_level %>); return false;"
               >X</a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="content_pane">
    <% m.call_next() %>
    <input class="json" id='json<% c.json_id %>' type="hidden" value='<% c.json %>' />
  </div>
</div>
