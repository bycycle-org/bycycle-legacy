<div id="<% c.result_id %>" class="window result errors">
  <div class="title_bar">
    <table>
      <tbody>
        <tr>
          <td class="l"><b>Not Found</b></td>
          <td class="r">
            <a class="button"
               href=""
               title="Remove this Result"
               onclick="Element.remove('<% c.result_id %>'); return false;"
               >X</a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="content_pane">
    <% c.error_msg %>
  </div>
</div>
