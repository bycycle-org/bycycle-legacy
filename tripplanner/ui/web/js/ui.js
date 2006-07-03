/* User Interface */


byCycle.UI = (function() {
  var self = null;

  var _public = {
    map: null,
    region_el: $('region'),
    q_el: $('q'),
    fr_el: $('fr'),
    to_el: $('to'),
    pref_el: $('pref'),
    result_el: $('result'),
    map_el: $('map'),
    bookmark_state: 0,
    bookmark_el: $('bookmark'),
    bookmark_toggle_el: $('bookmark_toggle'),
    bookmark_link_el: $('bookmark_link'),
    /*   mach_q, */
    /*   mach_fr, */
    /*   mach_to, */
    /*   user_q, */
    /*   user_fr, */
    /*   user_to, */
    /*   geocodes, */
    /*   linestring, */
    /*   center, */
    /*   start_ms, */

    /* Initialization */

    init: function() {
      self = byCycle.UI;
      if (byCycle.no_map) {
	$('map_msg').innerHTML = 'Map off';
	self.map = new IbCMap(self, self.map_el);
      } else {
	if (byCycle.Map.mapIsLoadable()) {
	  self.map = new byCycle.Map.Map(self, self.map_el);
	} else {
	  self.map = new IbCMap(self, self.map_el);	  
	}
	self.onResize();
	self.setRegionFromSelectBox();
	self.handleQuery();
      } 
      self.setEventHandlers();
    },

    setEventHandlers: function() {
      var connect = MochiKit.Signal.connect;
      var body = document.body;
      connect(window, 'onresize', self.onResize);
      connect(body, 'onunload', self.unload);
      connect(self.region_el, 'onchange', self.setRegionFromSelectBox);
      connect('swap_fr_and_to', 'onclick', self.swapFrAndTo);
      connect(self.bookmark_toggle_el, 'onclick', self.toggleBookmark);
    },

    handleQuery: function() {
      //var status = elV('http_status');
      //var response_text = unescape(elV('response_text'));
      //if (status && response_text != '""') {
      //  var req = {status: parseInt(status), responseText: response_text};
      //  callback(req);
      //}
    },


    /* UI Manipulation ("DHTML") */

    onResize: function() {
      var win_height = getWindowHeight();
      var height = win_height - elOffset('map') - 25;
      if (height >= 0) {
	self.map.setSize(null, height);
      }
      height = win_height - elOffset('result') - 5;
      if (height >= 0)
      self.result_el.style.height =  height + 'px'; 
    },

    toggleBookmark: function() {
      if (self.bookmark_state) {
	setElStyle('bookmark', 'display', 'none');
	self.bookmark_state = 0;
	self.bookmark_toggle_el.innerHTML = 'Show Bookmark';
      } else {
	setElStyle('bookmark', 'display', 'block');
	self.bookmark_state = 1;
	self.bookmark_toggle_el.innerHTML = 'Hide Bookmark';
      }
      self.onResize();
    },

    swapFrAndTo: function() {
      // Swap field values
      var fr = self.fr_el.value;
      self.fr_el.value = self.to_el.value;
      self.to_el.value = fr;
      // Swap machine values
      //fr = mach_fr;
      //mach_fr = mach_to;
      //mach_to = fr;
      // Swap user values
      //fr = user_fr;
      //user_fr = user_to;
      //user_to = fr;
    },


    /* Regions */

    setRegion: function(region) {
      region = regions[region] || regions.all;
      document.title = 'byCycle - Bicycle Trip Planner - ' + region.heading;  
      self._initRegion(region);
      self.map.centerAndZoomToBounds(region.bounds.gbounds, region.center);
      if (region.all) {
	var reg;
	for (var reg_key in regions) {
	  reg = regions[reg_key];
	  if (!reg.all) {
	    self._initRegion(reg);
	    self._showRegionOverlays(reg);
	  }
	}
      } else {
	self._showRegionOverlays(region);
      }
    },

    setRegionFromSelectBox: function() {
      var opts = self.region_el.options;
      var i = self.region_el.selectedIndex;
      self.setRegion(opts[i].value);
    },

    _initRegion: function(region) {
      if (!region.bounds.gbounds) {
	var sw = region.bounds.sw;
	var ne = region.bounds.ne;
	region.bounds.gbounds = new GLatLngBounds(new GLatLng(sw.lat, sw.lng),
						  new GLatLng(ne.lat, ne.lng));
      }
      if (!region.center) {
	region.center = self.map.getCenterOfBounds(region.bounds.gbounds);
      }
      if (!region.linestring) {
	var sw = region.bounds.gbounds.getSouthWest();
	var ne = region.bounds.gbounds.getNorthEast();
	var nw = new GLatLng(ne.lat(), sw.lng());
	var se = new GLatLng(sw.lat(), ne.lng());
	region.linestring = [nw, ne, se, sw, nw];
      }
    },

    _showRegionOverlays: function(region, use_cached) {
      if (!region.marker) {
	var icon = new GIcon();
	icon.image = "images/x.png";
	icon.iconSize = new GSize(17, 19);
	icon.iconAnchor = new GPoint(9, 10);
	icon.infoWindowAnchor = new GPoint(9, 10);
	icon.infoShadowAnchor = new GPoint(9, 10);
	region.marker = self.map.placeMarker(region.center, icon);
	GEvent.addListener(region.marker, "click", function() { 
	  var id = region.id;
	  var sel = region_el;
	  for (var i = 0; i < sel.length; ++i) {
	    var opt = sel.options[i];
	    if (opt.value == id) {
	      sel.selectedIndex = i;
	      setRegion(id);
	      break;
	    }
	  }
	});
      } else if (use_cached) {
	self.map.addOverlay(region.marker);
      }
      if (!region.line) {
	region.line = self.map.drawPolyLine(region.linestring); 
      } else if (use_cached) {
	self.map.addOverlay(region.line);
      }
    },
  
    unload: function() {
      self.map.unload();
    }
  }

  return _public;
})();


function doFind(service, fr, to) {
  start_ms = new Date().getTime();
  clearResult('');
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
	q_el.focus();
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
	  fr_el.focus();
      }
      if (!to) {
	errors.push('Please enter a To address');
	if (fr && region)
	  to_el.focus();
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
    var query_args = {region: region, q: q, pref: pref_el.value};

    query_args.format = 'html';
    bookmark = [base_url, MochiKit.base.queryString(query_args)].join('?');
    bookmark_link_el.href = bookmark;

    query_args.format = 'json';
    var d = doSimpleXMLHttpRequest(base_url, query_args);
    d.addBoth(callback);
  }
}


/* Callbacks */

/** 
 * Do stuff that's common to all callbacks in here
 */
function callback(req) {
  if (req.number) req = req.req;
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

function _geocodeCallback(status, result_set)
{
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
	
var colors = ['#0000ff', '#00ff00', '#ff0000', 
	      '#00ffff', '#ff00ff', '#ff8800',
	      '#000000'];	
var color_index = 0;
var colors_len = colors.length;
function _routeCallback(status, result_set)
{
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
	  var bounds = map.getBoundsForPoints(linestring);
	  var s_e_markers = map.placeMarkers([linestring[0],
					      linestring[last_point_ix]],
					     [map.start_icon, map.end_icon]);
	  var s_mkr = s_e_markers[0];
	  var e_mkr = s_e_markers[1];
	  GEvent.addListener(s_mkr, 'click', function() { 
	    map.showMapBlowup(linestring[0]);
	  });	           
	  GEvent.addListener(e_mkr, 'click', function() { 
	    map.showMapBlowup(linestring[last_point_ix]); 
	  });			
	  map.centerAndZoomToBounds(bounds);
	  map.drawPolyLine(linestring, colors[color_index++]);
	  if (color_index == colors_len) {
	    color_index = 0;
	  }
	}
      break;			 
    case 300: // Multiple matches
      break;
    }
}


/* UI Manipulation */

function setStatus(content, error)
{
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

function hideStatus()
{
  setElStyle('status', 'display', 'none');
}

function setResult(content, error)
{
  if (error) 
    setElStyle('result', 'color', 'red');
  else 
    setElStyle('result', 'color', 'black');
  setIH('result', content.toString());
}

function clearResult()
{
  setIH('result', '');
}


/* Map */

function setElVToMapLonLat(id)
{
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


function showGeocode(index, open_info_win)
{
  var geocode = geocodes[index];
  geocode.html = unescape(geocode.html);
  setResult(geocode.html);
  map.showGeocode(geocode);
}





function reverseDirections(fr, to) {
  doFind('route', fr, to);
  swapFrAndTo();
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



