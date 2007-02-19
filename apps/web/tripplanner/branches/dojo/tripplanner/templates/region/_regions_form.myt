<%args>
  form_id = None
</%args>

<form id="<% form_id or 'regions_form' %>" method="get" action="<% h.url_for('/') %>">
  <div style="margin-bottom: 2px;">
    <select id="regions" name="region">
      <option value="all">All Regions</option>
      <% h.options_for_select(c.region_options, selected=c.region_key) %>
    </select>
  </div>
  <div>
    <input type="submit" value="Go" onclick="Event.hide('regions_pane');" />
    <input type="button" value="Cancel" 
           onclick="Event.hide('regions_pane'); return false;" />
  </div>
</form>
