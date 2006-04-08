/* This module initializes the interface. */

var local = 0;

// The base location (domain) of the web interface
var domain = location.href.split('/')[2];

// The URL minus the query string
var base_url = location.href.split('?')[0];

var urls_to_keys_map = {
  'http://tripplanner.bycycle.org/':
  'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ8y5tnWrQRsyOlME1eHkOS3wQveBSeFCpOUAfP10H6ec-HcFWPgiJOCA',
  
  'http://dev.bycycle.org/':
  'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQSskL_eAzZotWlegWekqLPLda0sxQZNf0_IshFell3z8qP8s0Car117A',
  
  'http://www.bycycle.org/tripplanner/':
  'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ9bMyOoze7XFWIje4XR3o1o-U-cBTwScNT8SYtwSl70gt4wHCO-23Y3g'
};


// Get the API key associated with the URL
var api_key = urls_to_keys_map[base_url];

// If we're running locally, load local GMap script. If we're running, load 
// official script, but only if the URL has an associated API key.
if (local) {
  alert('Running locally!');
} else if (api_key) {
  script('http://maps.google.com/maps?file=api&amp;v=2&amp;key=' + api_key);
}


function script(src) 
{ 
  echo('<'+'script src="'+src+'"'+' type="text/javascript"><'+'/script>'); 
}

