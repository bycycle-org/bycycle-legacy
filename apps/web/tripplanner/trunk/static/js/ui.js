/* $Id: ui.js 190 2006-08-16 02:29:29Z bycycle $ */

// Widgets
var input_tabs;
//var donate_panel;

// Input elements
var mach_q;
var mach_fr;
var mach_to;
var user_q;
var user_fr;
var user_to;

// Result stuff
var start_ms;
var geocodes;
var route_line_color = '#000000';
var linestring;

// UI elements
var map_el;
var bike_layer = null;
var center;
var result_el;
var region_el;


var address_tip = 'You can type in an address or intersection -OR- choose a point from the map. Please note that you can\'t enter businesses or other points of interest at this time, only addresses. <br/><br/>To pick a point from the map, first zoom in and center the map on the point you want, then click the red dot and choose the link "Find address of closest intersection."<br/><br/>The easiest way to center the map is to double click it. The point you double-click will move to the center.';
	  
var route_address_tip = 'For each of your "from" and "to" addresses you can type in an address or intersection -OR- choose a point from the map. Please note that you can"t enter businesses or other points of interest at this time, only addresses.<br/><br/>To pick a point from the map, first zoom in and center the map on the point you want, then click the red dot and choose the "From" or "To" link in "Set as From or To address for route."<br/><br/>The easiest way to center the map is to double click it. The point you double-click will move to the center.';      


function afterPageLoad() {  
  YAHOO.util.Event.addListener(window, 'resize', resizeMap);
  var unload_func = typeof(GUnload) != 'undefined' ? GUnload : (function () {});
  YAHOO.util.Event.addListener(window, 'unload', unload_func);
  
  map_el = el('map');
  result_el = el('result');
  region_el = el('regions');
  
  input_tabs = new YAHOO.widget.TabView('input_tab_container');

  if (api_key) {
	if (mapLoad()) {
	  // do nothing for now
	} else {
	  setIH('map', 'Error loading map.');
	}
  } else {
	setIH('map', 'Error loading map: Could not find valid API key for ' + base_url + '.');
  }

  resizeMap();  // Don't remove this!

  try {
    selectRegion(region_el[region_el.selectedIndex].value);
  } catch(e) {
	// regions element is not a <select>
    selectRegion(region_el.value);
  } 
  
  if (status && response_text != '""') {
	var req = {status: http_status, responseText: response_text};
	_callback(req);
  }

  resizeMap();
  el('input_tab_contents').style.display = 'block';   
}

var bike_layer_state = false;
function toggleBikeLayer() {
  if (!map) return;
  if (bike_layer_state) {
	// Bike layer was on; turn it off
	bike_layer.hide();
	el('show_hide_bike_map').innerHTML = 'Show';
  } else {
	// Bike layer was off; turn it on
	if (!bike_layer) {
	  // First time turning bike layer on, create it
	  bike_layer = makeBikeLayer(20);
	  map.addOverlay(bike_layer);
	}
	el('show_hide_bike_map').innerHTML = 'Hide';
	if (map.getZoom() < 9) map.setZoom(9);
	bike_layer.show();
  }
  bike_layer_state = !bike_layer_state
}

function getVal(id, mach_v, user_v) {
  var el_v = cleanString(elV(id));
  if (mach_v == undefined) {
    var val = el_v;
  } else if (el_v.toLowerCase() != user_v.toLowerCase()) {
    var val = el_v;
    eval(['mach_', id, ' = undefined'].join(''));
    eval(['user_', id, ' = "', el_v, '"'].join(''));
  } else {
    var val = mach_v;
  }
  return val;
}


function setVal(id, mach_v, user_v) {
  if (mach_v != undefined) {
    eval(['mach_', id, ' = "', mach_v, '"'].join(''));
  }
  if (user_v != undefined) {  
    eval(['user_', id, ' = "', cleanString(user_v), '"'].join(''));
    setElV(id, user_v);
  }
}


function swapFrAndTo() {
  var fr = elV('fr');
  setElV('fr', elV('to'));
  setElV('to', fr);
  fr = mach_fr;
  mach_fr = mach_to;
  mach_to = fr;
  fr = user_fr;
  user_fr = user_to;
  user_to = fr;
}

var has_donated = false;
function doFind(service, fr, to) {
  if (!has_donated) {
    var amount = el((service == 'route' ? 'route' : 'geocode') + '_amount').value;
    if (amount != '') {
      var opts = 'width=800,height=600,status=no,toolbar=yes,menubar=no,scrollbars=yes,' + 
	'location=yes,directories=no,personalbar=no,resizable=yes';
      window.open('http://bycycle.org/donate.html?amount=' + amount, 'byCycle_donate_window', opts);
    }
    has_donated = true;
  }
    
  start_ms = new Date().getTime();
  clearResult();
  showStatus('Processing. Please wait<blink>...</blink>');

  var region = region_el.value;
  var errors = [];

  map && map.closeInfoWindow();
  
  if (!region) {
    errors.push('Please select a region (at top left of map).');
    region_el.focus();
  }

  if (service == 'geocode') {
    var q = getVal('q', mach_q, user_q);
    if (!q) {
      errors.push('Please enter something to search for.');
      if (region)
	el('q').focus();
    } else {
      // Is the address really a route request?
      var i = q.toLowerCase().indexOf(' to ');
      if (i != -1) {
		setElV('fr', q.substring(0, i));
		setElV('to', q.substring(i+4));
      }
    }
  } else if (service == 'route') {
	if (!(fr || to)) {
	  // When fr and to are set in params, we're doing reverse directions
	  var fr = getVal('fr', mach_fr, user_fr);
	  var to = getVal('to', mach_to, user_to);
	}
	if (fr && to) {
	  var q = ['["', fr, '", "', to, '"]'].join('');
	} else {
	  if (!fr) {
		errors.push('Please enter a "from" address.');
		if (region) {
		  el('fr').focus();
		}
	  }
	  if (!to) {
		errors.push('Please enter a "to" address.');
		if (fr && region) {
		  el('to').focus();
		}
	  }
	}
  } else {
	errors.push('Unknown service: ' + service);
  }

  if (errors.length) {
    errors = ['<h2>Errors</h2><ul class="mma_list"><li>', 
              errors.join('</li><li>'),
	      '</li></ul>'].join('');
    setResult(errors);
  } else {
    var url_parts = [base_url,
		     '?region=', region, 
		     '&q=', escape(q), 
		     '&pref=', elV('pref'),
		     '&format='];

    url_parts.push('html');
    var bookmark = url_parts.join('');
    el('bookmark').href = bookmark;

    url_parts[url_parts.length-1] = 'json';
    url = url_parts.join('');
    
    //alert(url);
    doXmlHttpReq('GET', url, _callback);
  }
}


/* Callbacks */

/** 
 * Do stuff that's common to all callbacks in here
 */
function _callback(req) {
  var status = req.status;
  var response_text = req.responseText;
  //alert(status + '\n' + response_text);
  eval("var result_set = " + response_text + ";");
  if (status < 400) {
    if (start_ms) {
      var elapsed_time = (new Date().getTime() - start_ms) / 1000.0;
	  var s = elapsed_time == 1.00 ? '' : 's';
      var elapsed_time = ['Took ', elapsed_time, ' second', s, 
	                      ' to find result.'].join('');
    } else {
      var elapsed_time = '';
    }
	showStatus(elapsed_time);
    setResult(unescape(result_set.result_set.html));
    eval('_' + result_set.result_set.type + 'Callback')(status, result_set);
  } else {
    setStatus('Error.');
    setResult(['<h2>Error</h2><p><ul class="mma_list"><li>', 
               result_set.error.replace('\n', '</li><li>'), 
               '</li></ul></p>'].join(''));
  }
}

function _geocodeCallback(status, result_set) {
  geocodes = result_set.result_set.result;
  switch (status) {
    case 200: // A-OK, one match
      if (map) {
		showGeocode(0, true);
	  }
      break;
    case 300:
      break;
  }
}
	
function _routeCallback(status, result_set) {
  var route = result_set.result_set.result;
  switch (status) 
    {
    case 200: // A-OK, one match
      if (map) {
		var route_linestring = route.linestring;
		linestring = [];
		for (var i = 0; i < route_linestring.length; ++i) {
		  var p = route_linestring[i];
		  linestring.push(new GLatLng(p.y, p.x));
		}
		var linestring_len = linestring.length;
		var last_point_ix = linestring.length - 1;
		var bounds = getBoundsForPoints(linestring);
		var s_e_markers = placeMarkers([linestring[0],
						linestring[last_point_ix]],
					   [start_icon, end_icon]);
		var s_mkr = s_e_markers[0];
		var e_mkr = s_e_markers[1];
		GEvent.addListener(s_mkr, 'click', function() { 
		  map.showMapBlowup(linestring[0]);
		});	           
		GEvent.addListener(e_mkr, 'click', function() { 
		  map.showMapBlowup(linestring[last_point_ix]); 
		});			
		centerAndZoomToBounds(bounds);
		drawPolyLine(linestring, route_line_color, null, .625);
      }
      break;			 
    case 300: // Multiple matches
      break;
    }
}


/* UI Manipulation */

function hideAds() {
  // Save center before resizing
  var c = (map && map.getCenter());
  // Remove entirely the container that holds the ads
  document.body.removeChild(el('ads')); 
  el('header').style.marginRight = '0px';
  el('bar').style.marginRight = '0px';
  el('content').style.marginRight = '0px';
  // Set center back to original center
  resizeMap();
  c && map.setCenter(c);
}

function hideNotice() {
  setElStyle('notice', 'display', 'none'); 
  resizeMap();  
  return false;
}

function setStatus(content, error) {
  if (error) 
    setElStyle('status', 'color', 'red');
  else 
    setElStyle('status', 'color', 'black');
  setIH('status', content.toString());
}

function showStatus(content, error)
{	      
  if (content) {
	setElStyle('status', 'display', 'block');
	el('status').innerHTML = content;
  }
}

function hideStatus() {
  setElStyle('status', 'display', 'none');
}

function setResult(content, error) {
  if (error) 
    setElStyle('result', 'color', 'red');
  else 
    setElStyle('result', 'color', 'black');
  setIH('result', content.toString());
}

function clearResult() {
  setIH('result', '');
}


/* Map */

function setElVToMapLonLat(id) {
  if (!map) 
    return;
  var lon_lat = map.getCenter();
  var x = Math.round(lon_lat.x * 1000000) / 1000000;
  var y = Math.round(lon_lat.y * 1000000) / 1000000;
  setElV(id, "lon=" + x + ", " + "lat=" + y);
}

function clearMap() {
  if (map) {
    map.clearOverlays();
	if (bike_layer_state) {
	  bike_layer.show();
	}
    for (var reg_key in regions) {
      var reg = regions[reg_key];
      if (!reg.all) {
		_showRegionOverlays(reg, true);
	  }
    }
    map.setCenter(map.getCenter());
  }
}

var bC_footer_height = 19;

function resizeDisplay(dims) {
  dims = dims || getWindowDimensions();
  var height = dims.h - elOffsetY(result_el) - bC_footer_height;
  if (height >= 0) {
    result_el.style.height =  height + 'px'; 
  }
}

function resizeMap() {
  var dims = getWindowDimensions();
  var height = dims.h - elOffsetY(map_el) - bC_footer_height;
  if (height >= 0) {
    map_el.style.height = height + 'px';
    if (map) {
      map.checkResize();
      map.setCenter(map.getCenter());
    }
  }
  resizeDisplay(dims);
}

function showGeocode(index, open_info_win) {
  var geocode = geocodes[index];
  var html = unescape(geocode.html);
  setResult(html);
  if (map) {
    var point = new GLatLng(geocode.y, geocode.x);
    if (!geocode.marker) {
      geocode.marker = placeMarkers([point])[0];
      GEvent.addListener(geocode.marker, "click", function() {
	map.openInfoWindowHtml(point, html);
	setResult(html);
      });
    }
    if (open_info_win) {
      map.setCenter(point, 14);
      map.openInfoWindowHtml(point, html);
    }
  }
}


/* Regions */

function selectRegion(region) {
  region = regions[region] || regions.all;
  document.title = 'byCycle - Bicycle Trip Planner - ' + region.heading;
  if (region.id != 'portlandor') {
	el('pref').style.display = 'none';
  } else {
	el('pref').style.display = '';
  }
  if (map) {
    _initRegion(region);
    centerAndZoomToBounds(region.bounds.gbounds, region.center);
    if (region.all) {
      var reg;
      for (var reg_key in regions) {
	    reg = regions[reg_key];
	    if (!reg.all) {
	      _initRegion(reg);
	      _showRegionOverlays(reg);
	    }
      }
    } else {
      _showRegionOverlays(region);
    }
  }
}

function _initRegion(region) {
  if (map) {
    if (!region.bounds.gbounds) {
      var sw = region.bounds.sw;
      var ne = region.bounds.ne;
      region.bounds.gbounds = new GLatLngBounds(new GLatLng(sw.lat, sw.lng),
						new GLatLng(ne.lat, ne.lng));
    }
    if (!region.center) {
      region.center = getCenterOfBounds(region.bounds.gbounds);
    }
    if (typeof(region.linestring) == 'undefined') {
      var sw = region.bounds.gbounds.getSouthWest();
      var ne = region.bounds.gbounds.getNorthEast();
      var nw = new GLatLng(ne.lat(), sw.lng());
      var se = new GLatLng(sw.lat(), ne.lng());
      region.linestring = [nw, ne, se, sw, nw];
    }
  }
}

function _showRegionOverlays(region, use_cached) {
  if (!map) return;

  if (!region.marker) {
    icon = new GIcon();
    icon.image = "static/images/x.png";
    icon.iconSize = new GSize(17, 19);
    icon.iconAnchor = new GPoint(9, 10);
    icon.infoWindowAnchor = new GPoint(9, 10);
    icon.infoShadowAnchor = new GPoint(9, 10);
	if (!region.center) {
	  _initRegion(region);
	}
	region.marker = placeMarker(region.center, icon);
    GEvent.addListener(region.marker, "click", function() { 
      var id = region.id;
      var sel = el('regions');
      if (sel.type == 'hidden') {
		selectRegion(id);
      } else {
		for (var i = 0; i < sel.length; ++i) {
		  var opt = sel.options[i];
		  if (opt.value == id) {
		    sel.selectedIndex = i;
		    selectRegion(id);
		    break;
		  }
		}
      }
    });
  } else if (use_cached) {
    map.addOverlay(region.marker);
  }
  
  if (typeof(region.line) == 'undefined')
    region.line = drawPolyLine(region.linestring); 
  else if (region.line && use_cached)
    map.addOverlay(region.line);
}

function showBookmarkForThisPage() {
  setElStyle('bookmark', 'display', 'block');
  resizeMap();
}

function hideBookmarkForThisPage() {
  setElStyle('bookmark', 'display', 'none');
  resizeMap();  
}

function reverseDirections(fr, to) {
  doFind('route', fr, to);
  swapFrAndTo();
}
