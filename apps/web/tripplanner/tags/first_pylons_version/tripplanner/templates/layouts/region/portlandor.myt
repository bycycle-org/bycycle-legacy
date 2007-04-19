<%flags>
    inherit = 'region.myt'
</%flags>


<&|SELF:section, name='region' &>
  Portland, OR
</&>


<!-- Route preference form control -->
<&|SELF:section, name='route_pref' &>
  <select id="pref" name="pref" tabindex="8">
    <option value="default">- Route Type -</option>
    <option value="default">Normal</option>
    <option value="safer">Safer</option>
  </select>
</&>
