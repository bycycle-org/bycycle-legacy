/* This module initializes the interface. */

// The base location (domain) of the web interface
var domain = location.href.split('/')[2];

// Decide if we are running locally (where locally means not on the production
// server)
if (domain == 'tripplanner.bycycle.org')
  {
    var local = 0;
    var dir = '';
    alert('live');
  }
else
  {
    var local = 1;
    var dir = 'tripplanner/';    
  }

// The URL minus the query string
var base_url = location.href.split('?')[0];

var urls_to_keys_map = {
  'http://tripplanner.bycycle.org/':
  'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ8y5tnWrQRsyOlME1eHkOS3wQveBSeFCpOUAfP10H6ec-HcFWPgiJOCA',
  'http://www.bycycle.org/tripplanner/':
  'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ9bMyOoze7XFWIje4XR3o1o-U-cBTwScNT8SYtwSl70gt4wHCO-23Y3g'
};


// Get the API key associated with the URL
var api_key = urls_to_keys_map[base_url];

// If we're running locally, load local GMap script. If we're running, load 
// official script, but only if the URL has an associated API key.
if (local)
  script('js/G_map.js');
else if (api_key)
  script('http://maps.google.com/maps?file=api&amp;v=1&amp;key=' + api_key);


function script(src) 
{ 
  echo('<'+'script src="'+src+'"'+' type="text/javascript"><'+'/script>'); 
}

