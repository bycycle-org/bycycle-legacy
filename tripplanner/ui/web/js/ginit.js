/* This module initializes the interface. It also defines common functions. */


// Switch to indicate whether we're running on localhost
var local = 1;


// The base location (domain) of the web interface
var domain;
if (local) domain = 'localhost';
else domain = location.href.split('/')[2];


// The URL minus the query string
var base_url = location.href.split('?')[0];

    
// If we're running locally, load local GMap script 
// If we're running, load "official" script, but only if the URL has an associated API key
var api_key = getApiKey(base_url);
if (local) script("js/G_map.js");
else if (api_key) script("http://maps.google.com/maps?file=api&amp;v=1&amp;key=" + api_key);
	

/**
 * Event handler for stuff that should be done after the window has completed loading
 */
window.onload = function()
{
    ui__init__();
	if (local || api_key) gmap__init__();
	else _setIH("map", 'Error loading map: Could not find valid API key for ' + base_url + '.');
}


/**
 * Get the API key associated with the URL
 */
function getApiKey(base_url)
{
	var urls_to_keys_map =
		{"http://www.bycycle.org/tripplanner/":
		 "ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ9bMyOoze7XFWIje4XR3o1o-U-cBTwScNT8SYtwSl70gt4wHCO-23Y3g",
		 "http://www.bycycle.org/routefinder/":
		 "ABQIAAAAK1lojbVFd0iN7wam4g8XZhRUJ_a3mhnm0_Lzi5OorAQUylSPBhQS0u0c0I_UZr2P8TOtRApKc8xAoQ",
		 "http://testsite.bycycle.org/routefinder/":
		 "ABQIAAAAd_4WmZlgvQzchd_BQM0MPhTdNPmNFsjeptADRw2mjwBZI5k75BQiz9jRiM_xT-aGT3SpF8y6E9CCvQ",
		 "http://24.22.45.178/routefinder/":
		 "ABQIAAAAd_4WmZlgvQzchd_BQM0MPhS6wxNuMO_CH7ubezRAq5_s5CDwAhS8nFQy5lWxuSKAABHKY8CIdboQgQ",
		 "http://24.22.45.178:8080/":
		 "ABQIAAAAd_4WmZlgvQzchd_BQM0MPhTYxx1LSfXeZjOCBx9xRz8m4aTCzxTba2J_A8BANZ403cGl0LmY5haDjw"};
	if (urls_to_keys_map[base_url]) return urls_to_keys_map[base_url];
	else return '';
}


function script(src) { echo('<'+'script src="'+src+'"'+' type="text/javascript"><'+'/script>'); }
