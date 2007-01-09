<%args>
   id
   window_classes = ''
   window_style = ''
   display = 'block'
   closeable = True
   toggleable = False
   title = ''
   toggle_handler = None
   close_handler = None
   content = ''
   content_style = ''
</%args>

<%python>
  window_classes = ' '.join(('window', window_classes)).strip()
  window_style = ';'.join((window_style, 'display: %s;' % display)).strip().lstrip(';')
  slug = title.lower().replace(' ', '-')
  content_id = '%s_content' % id
  content_id_attr = ['', 'id="%s"' % content_id][bool(id)]
  content_style_attr = ['', 'style="%s"' % content_style][bool(content_style)]
  toggle_handler = toggle_handler or ("""Element.toggle('%s')""" % content_id)
  close_handler = close_handler or ("""Element.remove('%s')""" % id)
</%python>

<div id="<% id %>"
     class="<% window_classes %>"
     style="<% window_style %>">
  <div class="title_bar">
    <table>
      <tbody>
        <tr>
          <td class="window_title l"><% title %></td>
          <td class="r">
            &nbsp;
% if toggleable and content_id:
            <a class="button" href="#<% '-'.join(('toggle', slug)).rstrip('-') %>"
               onclick="<% toggle_handler %>; return false;"
               title="Show/Hide">+/-</a>
% #if
% if closeable:
            <a class="button" href="#<% '-'.join(('close', slug)).rstrip('-') %>"
               onclick="<% close_handler %>; return false;"
               >X</a>
% #if
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div <% content_id_attr %> class="content_pane" <% content_style_attr %>>
    <% content %>
  </div>
</div>
