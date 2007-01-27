<%flags>
    inherit = 'result.myt'
</%flags>

% c.collapsible = False
% errors = c.error_msg.split('\n')
% if len(errors) == 1:
<% errors[0] %>
% else:
%     for error in errors:
<div class="error">
  <% error %>
</div>
% #for
% #if