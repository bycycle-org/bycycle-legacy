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

  var map_state = byCycle.getParamVal('map_state', function(map_state) {
    // Anything but '', '0' or 'off' is on
    return (map_state != '0' || map_state != 'off' || map_state == '');
  });

  var map_type = byCycle.getParamVal('map_type');


  // public:
  var _public = {
    ads_width: 120,
    service: 'query',

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
    
    /**
     * Do stuff that must happen *during* page load, not after
     */
    preload: function() {
      byCycle.Map[map_type].mapPreload();
      MochiKit.Signal.connect(window, 'onload', byCycle.UI.onload);
    },

    onload: function() {
      self = byCycle.UI;
      // Figure out which map to use
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
      showElement('map');
      showElement('google_ads');
      self.onResize();
      self.initTabPanes();
      self.setEventHandlers();
      //self.setRegionFromSelectBox();
      self.setRegion('portlandor');
      self.handleQuery();

      if (byCycle.debug) {
	self.hideAds();
      }
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

    unload: function() {
      self.map.unload();
    },

    setEventHandlers: function() {
      connect(window, 'onresize', self.onResize);
      connect(document.body, 'onunload', self.unload);
      connect('query_form', 'onsubmit', self.doFind);
      connect('route_form', 'onsubmit', self.doFind);
      connect('swap_fr_and_to', 'onclick', self.swapFrAndTo);
      connect('region', 'onchange', self.setRegionFromSelectBox);
      connect('region_form', 'onsubmit', self.setRegionFromSelectBox);
      connect('hide_ads', 'onclick', self.hideAds);
      //connect('find_center_map', 'onclick', self.findAddressAtCenter)
      //connect('clear_map', 'onclick', self.clearMap);
    },

    onResize: function() {
      var dims = getViewportDimensions();
      byCycle.logDebug(dims.w, dims.h);

      // 9 = 4px (padding) * 2 + 1px (border)
      var status_h = parseInt(computedStyle('footer', 'height')) + 9;

      // Resize map
      var pos = elementPosition(self.map_el);
      var width = dims.w - pos.x - self.ads_width;
      var height = dims.h - pos.y - status_h;
      self.map.setSize({w: width, h: height});

      // Resize display
      var display = $('display');
      pos = elementPosition(display);
      height = dims.h - pos.y - status_h;
      // Subtract display padding too
      $('google_ads').style.height =  height + 'px';
      display.style.height =  (height - 8) + 'px';
    },

    hideAds: function() {
      hideElement('google_ads');
      self.ads_width = 0;
      self.onResize();
    },
    
    /* Find */

    doFind: function(service, q) {
      // Handle called-as-slot
      if (typeof(service.src) == 'function') {
        byCycle.logDebug('doFind() called-as-slot');
	var event = service;
	service = self.service;
	if (service == 'query') {
	  q = self.q_el.value; 
	} else if (service == 'route') {
	  q = [self.fr_el.value, self.to_el.value];
	}
      }

      byCycle.logDebug(service);

      self.start_ms = new Date().getTime();
      self.result_el.innerHTML = '';
      self.setStatus('Processing. Please wait<blink>...</blink>');
      
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

      if (errors.length) {
	errors = ['<h2>Errors</h2><ul class="mma_list"><li>', 
		  errors.join('</li><li>'),
		  '</li></ul>'].join('');
	self.setResult(errors);
      } else {
	var query_args = {service: service, q: q};
	var region = self.region_el.value;
	if (region) {
	  query_args.region = region;
	}
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
	cb(status, result_set.result_set);
	self.setStatus('Done');
      } else {
	self.setResult(['<h2>Error</h2><p><ul class="mma_list"><li>', 
			result_set.error.replace('\n', '</li><li>'), 
			'</li></ul></p>'].join(''));
	self.setStatus('Error');
      }
    },
    
    _geocodeCallback: function(status, result_set) {
      byCycle.logDebug('In _geocodeCallback');
      self.geocodes = result_set.result;
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
      var route = result_set.result;
      switch (status) 
      {
      case 200:
	var map = self.map;
	var ls = route.linestring;

	// Zoom to linestring
	map.centerAndZoomToBounds(map.getBoundsForPoints(ls));

	// Place from and to markers
	var fr_to_markers = map.placeMarkers([ls[0], ls[ls.length - 1]],
					     [map.start_icon, map.end_icon]);

	// Add listeners to from and to markers
	var fr_mkr = fr_to_markers[0];
	var to_mkr = fr_to_markers[1];
	map.addListener(fr_mkr, 'click', function() { 
	  map.showMapBlowup(ls[0]);
	});
	map.addListener(to_mkr, 'click', function() { 
	  map.showMapBlowup(ls[ls.length - 1]); 
	});			
	
	// Draw linestring
	map.drawPolyLine(ls, colors[color_index++]);
	if (color_index == colors_len) {
	  color_index = 0;
	}
	break;			 
      case 300: // Multiple matches for from and/or to address
	break;
      }
    },


    /* Miscellaneous */

    reverseDirections: function(fr, to) {
      // TODO: Do this right--that is, use the from and to values from the
      // result, not just whatever happens to be in the input form
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

    initTabPanes: function() {
      var tab_panes = getElementsByTagAndClassName('div', 'tab_pane', 
						   document.body);
      for (var i = 0; i < tab_panes.length; ++i) {
	var tab_pane = new self.TabPane(tab_panes[i]);  
      }
    },

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
      map(hideElement, [section.input, section.label]);
      // Show new section
      self.selected = selected;
      section = self.input_sections[selected];
      section.link.className = 'selected';
      map(showElement, [section.input, section.label]);
      section.focus.focus();
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

    setStatus: function(content) {	      
      $('status').innerHTML = content.toString();
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

    getMap: function(map_type) {
      byCycle.logDebug('Map type:', map_type);
      if (!self[map_type]) {
	var map = new byCycle.Map[map_type].Map(self, self.map_el);
	self[map_type] = map;
      }
      return self[map_type];
    },

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
      self.map.clear();
      var regions = byCycle.regions;
      for (var reg_key in regions) {
	reg = regions[reg_key];
	if (!reg.all) {
	  self._initRegion(reg);
	  self._showRegionOverlays(reg);
	}
      }
      // Just shows the red dot???
      //self.map.setCenter(self.map.getCenter());
    },

    showGeocode: function(index, open_info_win) {
      var geocode = self.geocodes[index];
      geocode.html = unescape(geocode.html);
      self.setResult(geocode.html);
      self.map.showGeocode(geocode);
    },


    /* Regions */

    setRegionFromSelectBox: function() {
      var opts = self.region_el.options;
      var region = opts[self.region_el.selectedIndex].value;
      logDebug('Setting region to', region, '...');
      self.setRegion(region);
      hideElement('region_controls');
    },

    setRegion: function(region) {
      var regions = byCycle.regions;
      region = regions[region] || regions.all;
      document.title = 'byCycle - Bicycle Trip Planner - ' + region.heading;  
      $('active_region').innerHTML = region.heading;
      self.setStatus('Changed region to ' + region.heading);
      self._initRegion(region);
      self.map.centerAndZoomToBounds(region.bounds, region.center);
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

    _initRegion: function(region) {
      if (!region.center) {
	region.center = self.map.getCenterOfBounds(region.bounds);
      }
      if (!region.linestring) {
	var bounds = region.bounds;
	var nw = {x: bounds.sw.x, y: bounds.ne.y};
	var se = {x: bounds.ne.x , y: bounds.sw.y};
	region.linestring = [nw, bounds.ne, se, bounds.sw, nw];
      }
    },

    _showRegionOverlays: function(region, use_cached) {
      if (!region.marker) {
	region.marker = self.map.makeRegionMarker(region);
      } else if (use_cached) {
	self.map.addOverlay(region.marker);
      }
      if (!region.line) {
	region.line = self.map.drawPolyLine(region.linestring); 
      } else if (use_cached) {
	self.map.addOverlay(region.line);
      }
    }
  }

  return _public;
})();


byCycle.UI.TabPane = function(container, selected_id) {
  this.tabs = new Object();
  var labels_container = getElementsByTagAndClassName('div', 'tab_labels', 
						      container)[0];
  var contents_container = getElementsByTagAndClassName('div', 'tab_contents', 
							container)[0];
  var labels = getElementsByTagAndClassName('li', 'tab_label',
					    labels_container);
  var contents = getElementsByTagAndClassName('div', 'tab_content',
					      contents_container);
  var container_id = container.id;
  for (var i = 0; i < contents.length; ++i) {
    var id = container_id + '_tab_pane_tab' + i;
    var tab = new byCycle.UI.Tab(this, id, labels[i], contents[i]);
    this.tabs[tab.link.id] = tab;
  }
  this.selected_id = container_id + '_tab_pane_tab' + (selected_id || '0');
};


/** 
 * Given a label.link DOM element, make the label "active" and show the 
 * associated contents
 */
byCycle.UI.TabPane.prototype.selectTab = function(link) {
  // Handle called-as-slot
  if (typeof(link.src) == 'function') {
    var event = link;
    link = event.src();
  }
  // Hide the last selected tab
  var self = link.tab_pane;
  var last_tab = self.tabs[self.selected_id];
  removeElementClass(last_tab.label, 'selected');
  hideElement(last_tab.content);
  // Activate the selected tab
  var tab = self.tabs[link.id];
  addElementClass(tab.label, 'selected');
  showElement(tab.content);
  self.selected_id = link.id;
};

byCycle.UI.Tab = function(tab_pane, id, label, content) {
  this.label = label;
  this.content = content;
  
  var link = getElementsByTagAndClassName('a', null, label)[0];
  link.tab_pane = tab_pane;
  link.id = id;
  connect(link, 'onclick', tab_pane.selectTab);
  this.link = link;
};

