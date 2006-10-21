<%args>
  form_id = None
</%args>

<form id="<% form_id or 'regions_form' %>" method="get" action="/">
  <div style="margin-bottom: 2px;">
    <select id="regions" name="region">
      <option value="">All Regions</option>
      <% c.region_options %>
    </select>
  </div>
  <div style="text-align: right;">
    <input type="submit" value="Go" />
    <input type="button" value="Cancel" onclick="hideElement('regions_win'); return false;" />
  </div>
</form>
