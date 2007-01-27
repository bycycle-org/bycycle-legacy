<%args>
  form_id = None
</%args>

<form id="<% form_id or 'regions_form' %>" method="get" action="<% h.url_for('/') %>">
  <div style="margin-bottom: 2px;">
    <select id="regions" name="region">
      <option value="all">All Regions</option>
      <% c.region_options %>
    </select>
  </div>
  <div>
    <input type="submit" value="Go" onclick="dojo.html.hide('regions_pane');" />
    <input type="button" value="Cancel" 
           onclick="dojo.html.hide('regions_pane'); return false;" />
  </div>
</form>
