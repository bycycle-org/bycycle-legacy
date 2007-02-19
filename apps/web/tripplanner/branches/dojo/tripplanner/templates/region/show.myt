<%inherit file="/layouts/region/region.myt"/>

<%def name="make_tab_buttons(*tab_ids)">
<!--
  Make the 'tab buttons' for a tab control (a set of LIs)
  ``tab_ids`` is one or more strings suitable for a URL hash (like tab-id-13)
  Each generated LI has class 'tab-button'
  Each LI has an A element that has href='#tab-id'
  The A element's link text and title attribute are 'Tab Id'
-->
  % for t in tab_ids:
<% link_text = t.replace('-', ' ').capitalize() %>\
<li class="tab-button">${h.link_to(link_text, '#%s' % t, title=link_text)}</li>\
  % endfor
</%def>
