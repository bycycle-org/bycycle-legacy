/** $Id: ui.js 190 2006-08-16 02:29:29Z bycycle $
 *
 * User Interface.
 * 
 * Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>
 * 
 * All rights reserved.
 * 
 * TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION
 * 
 * 1. The software may be used and modified by individuals for noncommercial, 
 * private use.
 * 
 * 2. The software may not be used for any commercial purpose.
 * 
 * 3. The software may not be made available as a service to the public or within 
 * any organization.
 * 
 * 4. The software may not be redistributed.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */
var mach_q;
var mach_fr;
var mach_to;
var user_q;
var user_fr;
var user_to;
var geocodes;
var linestring;
var center;
var start_ms;
var map_el;
var result_el;
var region_el;
var route_line_color = '#000000';


function initUI() {
  map_el = el('map');
  result_el = el('result');
  region_el = el('regions');
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


function doFind(service, fr, to) {
  start_ms = new Date().getTime();
  toggleTips(1);
  clearResult();
  showStatus('Processing. Please wait<blink>...</blink>');

  var region = region_el.value;
  var errors = [];

  if (map)
    map.closeInfoWindow();
  
  if (!region) {
    errors.push('Please select a Region</a>');
    region_el.focus();
  }

  if (service == 'geocode') {
    var q = getVal('q', mach_q, user_q);
    if (!q) {
      errors.push('Please enter an Address');
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
	errors.push('Please enter a From address');
	if (region)
	  el('fr').focus();
      }
      if (!to) {
	errors.push('Please enter a To address');
	if (fr && region)
	  el('to').focus();
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
      var elapsed_time = ['<p><small>Took ', elapsed_time, ' second', 
			  (elapsed_time == 1.00 ? '' : 's'), 
			  ' to find result.</small></p>'].join('');
    } else {
      var elapsed_time = '';
    }
    setResult(unescape(result_set.result_set.html) + elapsed_time);
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
  switch (status)
    {
    case 200: // A-OK, one match
      if (map)
	showGeocode(0, true);
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

function setStatus(content, error) {
  if (error) 
    setElStyle('status', 'color', 'red');
  else 
    setElStyle('status', 'color', 'black');
  setIH('status', content.toString());
}

function showStatus(content, error)
{	      
  if (content)
    setResult('<div id="status">' + content + '</div>', error);
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

function clearMap()
{  
  if (map) {
    map.clearOverlays();
    for (var reg_key in regions) {
      var reg = regions[reg_key];
      if (!reg.all)
	_showRegionOverlays(reg, true);
    }
    map.setCenter(map.getCenter());
  }
}

function resizeDisplay(dims) {
  dims = dims || getWindowDimensions();
  var height = dims.h - elOffsetY(result_el) - 5;
  if (height >= 0) {
    result_el.style.height =  height + 'px'; 
  }
}
function resizeMap() {
  var dims = getWindowDimensions();
  var height = dims.h - elOffsetY(map_el) - 25;
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
  // WTF?: Why is this here when it could be in the regions file???
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
  if (!map)
    return;

  if (!region.marker) {
    icon = new GIcon();
    icon.image = "static/images/x.png";
    icon.iconSize = new GSize(17, 19);
    icon.iconAnchor = new GPoint(9, 10);
    icon.infoWindowAnchor = new GPoint(9, 10);
    icon.infoShadowAnchor = new GPoint(9, 10);
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