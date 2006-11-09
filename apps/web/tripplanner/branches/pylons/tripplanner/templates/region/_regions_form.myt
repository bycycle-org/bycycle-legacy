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
    <input type="submit" value="Go" />
    <input type="button" value="Cancel" 
           onclick="Element.hide('regions_window'); return false;" />
  </div>
</form>
