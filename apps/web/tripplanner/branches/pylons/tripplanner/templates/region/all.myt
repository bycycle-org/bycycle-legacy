<%flags>
    inherit = 'layout.myt'
</%flags>


<!--
  NOTE: This says to call the method `section` with the arg `name`. `section`
  will "do something" (?) and grab the content ("All Regions") and store it
  in the request context under the name "region".
-->
<&|SELF:section, name='region' &>
  All Regions
</&>


<&|SELF:section, name='route_pref' &></&>
