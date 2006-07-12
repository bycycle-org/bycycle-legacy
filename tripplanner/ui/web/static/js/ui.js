/* User Interface */


byCycle.UI = (function() {
  // private:
  var self = null;

  // Route colors
  var colors = ['#0000ff', '#00ff00', '#ff0000', 
		'#00ffff', '#ff00ff', '#ff8800',
		'#000000'];	
  var color_index = 0;
  var colors_len = colors.length;

  var map_state = byCycle.getVal('map_state', function(map_state) {
    if (map_state == '1' || map_state == 'on') {
      return 1;
    } else {
      return 0;
    }
  });
  logDebug('Map state:', map_state);

  var map_type = byCycle.getVal('map_type');
  logDebug('Map type:', map_type);


  // public:
  var _public = {
    input_sections: {
      query: {
	link: $('query_link'),
	input: $('query_section'),
        label: $('query_label'),
	focus: $('q')
      },
      route: {
	link: $('route_link'),
	input: $('route_section'),
        label: $('route_label'),
	focus: $('fr')
      }
    },
    selected: 'query',

    q_el: $('q'),
    fr_el: $('fr'),
    to_el: $('to'),
    pref_el: $('pref'),
    region_el: $('region'),

    result_el: $('result'),

    map: null,
    map_el: $('map'),
    map_state: map_state,
    map_type: map_type,

    bookmark_el: $('bookmark_link'),

    /*   mach_q, */
    /*   mach_fr, */
    /*   mach_to, */
    /*   user_q, */
    /*   user_fr, */
    /*   user_to, */
    /*   geocodes, */
    /*   linestring, */
    /*   center, */


    /* Initialization */

    init: function() {
      self = byCycle.UI;
      if (!self.map_state) {
	$('map_msg').innerHTML = 'Map off';
	$('center_panel').style.display = 'none';
	self.map = self.getMap(byCycle.default_map_type);
      } else if (byCycle.Map[self.map_type].mapIsLoadable()) {
	byCycle.logInfo('Loading map', self.map_type);
	self.map = self.getMap(self.map_type);
      } else {
	self.map_type = byCycle.default_map_type;
	self.map = self.getMap(self.map_type);
      }
      self.setEventHandlers();
      self.onResize();
      self.setRegionFromSelectBox();
      self.handleQuery();
    },

    getMap: function(map_type) {
      byCycle.logDebug('Map type:', map_type);
      if (!self[map_type]) {
	var map = new byCycle.Map[map_type].Map(self, self.map_el);
	self[map_type] = map;
      }
      return self[map_type];
    },

    handleQuery: function() {
      var status = $('http_status').value;
      var response_text = unescape($('response_text').value);
      if (status && response_text != '""') {
        var req = {status: parseInt(status), responseText: response_text};
        self.callback(req);
      }
    },


    /* Events */

    setEventHandlers: function() {
      connect(window, 'onresize', self.onResize);
      connect(document.body, 'onunload', self.unload);
      connect('query_link', 'onclick', self.setSelected);
      connect('route_link', 'onclick', self.setSelected);
      connect('input_form', 'onsubmit', self.doFind);
      connect('swap_fr_and_to', 'onclick', self.swapFrAndTo);
      connect(self.region_el, 'onclick', self.setRegionFromSelectBox);
      connect('find_center_map', 'onclick', self.findAddressAtCenter)
      connect('clear_map', 'onclick', self.clearMap);
    },

    onResize: function() {
      var win_height = getWindowHeight();
      var height = win_height - elOffset('map') - 25;
      if (height >= 0) {
	self.map.setHeight(height);
      }
      height = win_height - elOffset('result') - 10;
      if (height >= 0)
      self.result_el.style.height =  height + 'px'; 
    },

    
    /* Find */

    doFind: function(service, q) {
      // Handle called-as-slot
      if (typeof(service.src) == 'function') {
        byCycle.logDebug('doFind() called-as-slot');
	var event = service;
	service = self.selected;
	if (service == 'query') {
	  q = self.q_el.value; 
	} else if (service == 'route') {
	  q = [self.fr_el.value, self.to_el.value];
	}
      }

      byCycle.logDebug(service);

      self.start_ms = new Date().getTime();
      self.result_el.innerHTML = '';
      self.showStatus('Processing. Please wait<blink>...</blink>');
      
      var region = self.region_el.value;
      var errors = [];

      self.map.closeInfoWindow();
      
      if (service != 'query' && service != 'route') {
	errors.push('Unknown service: ' + service);
      } else {
	if (service == 'query') {
	  if (!q) {
	    errors.push('Please enter an address');
	    self.q_el.focus();
	  } else {
	    // Is the query a route?
	    var i = q.toLowerCase().indexOf(' to ');
	    if (i != -1) {
	      service = 'route';
	      var fr = q.substring(0, i);
	      var to = q.substring(i+4);
	      self.fr_el.value = fr;
	      self.to_el.value = to;
	      q = [fr, to];
	      self.setSelected('route');
	    }
	  }
	}

	if (service == 'route') {
	  var fr = q[0];
	  var to = q[1];
	  if (fr && to) {
	    q = ['["', fr, '", "', to, '"]'].join('');
	  } else {
	    if (!fr) {
	      errors.push('Please enter a start address');
	      self.fr_el.focus();
	    }
	    if (!to) {
	      errors.push('Please enter an end address');
	      if (fr) {
		self.to_el.focus();
	      }
	    }
	  }
	}
      }

      if (!region) {
	errors.push('Please select a region</a>');
	self.region_el.focus();
      }

      if (errors.length) {
	errors = ['<h2>Errors</h2><ul class="mma_list"><li>', 
		  errors.join('</li><li>'),
		  '</li></ul>'].join('');
	self.setResult(errors);
      } else {
	var query_args = {region: region, service: service, q: q};
	if (service == 'route') {
	  query_args.pref = self.pref_el.value;
	}

	query_args.format = 'html';
	bookmark = [byCycle.base_url, queryString(query_args)].join('?');
	self.bookmark_el.href = bookmark;
	byCycle.logDebug('Bookmark:', bookmark);

	query_args.format = 'json';
	var d = doSimpleXMLHttpRequest(byCycle.base_url, query_args);
	d.addBoth(self.callback);
      }
    },


    /* Callbacks */

    /** 
     * Do stuff that's common to all callbacks in here
     */
    callback: function(req) {
      byCycle.logDebug('In callback');

      var err = 'MochiKit.Async.XMLHttpRequestError("Request failed")';
      if (repr(req) == err) {
	req = req.req;
      }
      var status = req.status;
      var response_text = req.responseText;

      byCycle.logDebug('Status:', status, 
		       'responseText:', response_text);

      eval("var result_set = " + response_text + ";");
      if (status < 400) {
	if (self.start_ms) {
	  var elapsed_time = (new Date().getTime() - self.start_ms) / 1000.0;
	  var elapsed_time = ['<p><small>Took ', elapsed_time, ' second', 
			      (elapsed_time == 1.00 ? '' : 's'), 
			      ' to find result.</small></p>'].join('');
	} else {
	  var elapsed_time = '';
	}
	self.setResult(unescape(result_set.result_set.html) + elapsed_time);
	var cb = eval('self._' + result_set.result_set.type + 'Callback');
	cb(status, result_set);
      } else {
	self.setStatus('Error.');
	self.setResult(['<h2>Error</h2><p><ul class="mma_list"><li>', 
			result_set.error.replace('\n', '</li><li>'), 
			'</li></ul></p>'].join(''));
      }
    },
    
    _geocodeCallback: function(status, result_set) {
      byCycle.logDebug('In _geocodeCallback');
      geocodes = result_set.result_set.result;
      switch (status) {
      case 200: // A-OK, one match
	self.showGeocode(0, true);
	break;
      case 300:
	break;
      }
    },
	
    _routeCallback: function(status, result_set) {
      byCycle.logDebug('In _routeCallback');
      var route = result_set.result_set.result;
      switch (status) 
      {
      case 200: // A-OK, one match
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
	break;			 
      case 300: // Multiple matches
	break;
      }
    },


    reverseDirections: function(fr, to) {
      doFind('route', fr, to);
      swapFrAndTo();
    },

    getVal: function(id, mach_v, user_v) {
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
    },

    setVal: function(id, mach_v, user_v) {
      if (mach_v != undefined) {
	eval(['mach_', id, ' = "', mach_v, '"'].join(''));
      }
      if (user_v != undefined) {  
	eval(['user_', id, ' = "', cleanString(user_v), '"'].join(''));
	setElV(id, user_v);
      }
    },


    /* UI Manipulation ("DHTML") */

    setSelected: function(selected) {
      // Handle called-as-slot
      if (typeof(selected.src) == 'function') {
        byCycle.logDebug('setSelected called-as-slot');
	var event = selected;
	var link = event.src();
	selected = link.name;
      }
      byCycle.logDebug('selected:', selected);
      if (selected == self.selected) {
	return;
      }
      // Hide old section
      var section = self.input_sections[self.selected];
      section.link.className = '';
      section.input.style.display = 'none';
      section.label.style.display = 'none';
      // Show new section
      self.selected = selected;
      section = self.input_sections[selected];
      section.link.className = 'selected';
      section.input.style.display = 'block';
      section.label.style.display = 'block';
      section.focus.focus();
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

    setStatus: function(content, error) {
      if (error) {
	setElStyle('status', 'color', 'red');
      } else {
	setElStyle('status', 'color', 'black');
      }
      setIH('status', content.toString());
    },

    showStatus: function(content, error) {	      
      if (content) {
	self.setResult('<div id="status">' + content + '</div>', error);
      }
    },

    hideStatus: function() {
      setElStyle('status', 'display', 'none');
    },

    setResult: function(content, error) {
      if (error) {
	setElStyle('result', 'color', 'red');
      } else {
	setElStyle('result', 'color', 'black');
      }
      $('result').innerHTML = content;
    },


    /* Map */

    getCenterString: function() {
      var lon_lat = self.map.getCenter();
      var x = Math.round(lon_lat.x * 1000000) / 1000000;
      var y = Math.round(lon_lat.y * 1000000) / 1000000;
      return "lon=" + x + ", " + "lat=" + y;
    },

    findAddressAtCenter: function() {
      var center = self.getCenterString();
      self.q_el.value = center;
      self.doFind('query', center);
    },

    clearMap: function() {  
      self.map.clearOverlays();
      for (var reg_key in regions) {
	var reg = regions[reg_key];
	if (!reg.all)
	  _showRegionOverlays(reg, true);
      }
      self.map.setCenter(map.getCenter());
    },

    showGeocode: function(index, open_info_win) {
      var geocode = geocodes[index];
      geocode.html = unescape(geocode.html);
      setResult(geocode.html);
      map.showGeocode(geocode);
    },


    /* Regions */

    setRegionFromSelectBox: function() {
      var opts = self.region_el.options;
      var region = opts[self.region_el.selectedIndex].value;
      self.setRegion(region);
    },

    setRegion: function(region) {
      var regions = byCycle.regions;
      region = regions[region] || regions.all;
      document.title = 'byCycle - Bicycle Trip Planner - ' + region.heading;  
      self._initRegion(region);
      self.map.centerAndZoomToBounds(region.bounds, region.center);
      if (region.all) {
	var reg;
	for (var reg_key in regions) {
	  reg = regions[reg_key];
	  if (!reg.all) {
	    self._initRegion(reg);
	    //self._showRegionOverlays(reg);
	  }
	}
      } else {
	//self._showRegionOverlays(region);
      }
    },

    _initRegion: function(region) {
      if (!region.bounds.bounds) {
	region.bounds.bounds = self.map.makeBounds(region.bounds)
      }
      if (!region.center) {
	region.center = self.map.getCenterOfBounds(region.bounds);
      }
      if (!region.linestring) {
	region.linestring = [region.nw, region.ne, region.se, region.sw, 
			     region.nw];
      }
    },

    _showRegionOverlays: function(region, use_cached) {
      return;
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
