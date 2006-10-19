/* Namespace for User Interface functions and classes. */


byCycle.UI = (function() {
  /** private: **/

  var self = null;

  // Route colors
  var colors = [
      '#0000ff', '#00ff00', '#ff0000',
      '#00ffff', '#ff00ff', '#ff8800',
      '#000000'
  ];
  var color_index = 0;
  var colors_len = colors.length;

  var map_state = byCycle.getParamVal('map_state', function(map_state) {
    // Anything but '', '0' or 'off' is on
    return (!(map_state == '0' || map_state == 'off' || map_state == ''));
  });

  var map_type_name = byCycle.getParamVal('map_type').toLowerCase();
  var map_type = byCycle.Map[map_type_name] || byCycle.Map.base;
  byCycle.logDebug('Map type:', map_type.description);

  /** public: **/
  
  var _public = {
    ads_width: 120,

    // Interface elements
    q_el: $('q'),
    s_el: $('s'),
    e_el: $('e'),
    pref_el: $('pref'),
    region_el: $('regions'),
    status_el: $('status'),
    result_el: $('result'),
    errors_el: $('errors'),
    bookmark_el: $('bookmark'),
    display_el: $('display'),
    google_ads_el: $('google_ads'),

    // The map object
    map: null,
    map_el: $('map'),
    map_state: map_state,
    map_type: map_type,

    // Current state (TODO: Make object for these???)
    region: 'all',
    service: 'query',
    query: null,
    result: null,
    results: [],
    http_status: null,
    response_text: null,

    // Pairs of human & machine readable values
    // TODO: Use these (or implement a better version)
    q: {u: null, m: null},
    s: {u: null, m: null},
    e: {u: null, m: null},

    /** Initialization **/

    /**
     * Do stuff that must happen *during* page load, not after
     */
    beforeLoad: function() {
      if (map_state) {
        var map_msg = $('map_msg');
        map_msg.className = 'loading';
        map_msg.innerHTML = 'Loading map...';
        map_type.beforeLoad();
      }
      MochiKit.Signal.connect(window, 'onload', byCycle.UI.onLoad);
    },

    onLoad: function() {
      self = byCycle.UI;
      // Figure out which map to use
      if (!self.map_state) {
        // Either the map is off or the map is not loadable.
        // Otherwise, below we'll use whatever self.map_type is set to.
        self.map_type = byCycle.Map.base;
      }
      self.initTabPanes();
      self.setEventHandlers();
      self.map = new self.map_type.Map(self, self.map_el);
      hideElement('map_msg');
      showElement('map');
      showElement('google_ads');
      self.onResize();
      self.setRegionFromSelectBox();
      self.handleQuery();
    },

    handleQuery: function() {
      if (self.http_status && self.response_text) {
        var request = {status: self.status, responseText: self.response_text};
        //self.callback(request);
      }
    },

    /** Events **/

    unload: function() {
      self.map.unload();
    },

    setEventHandlers: function() {
      connect(window, 'onresize', self.onResize);
      connect(document.body, 'onunload', self.unload);
      //connect('query_form', 'onsubmit', self.doFind);
      //connect('route_form', 'onsubmit', self.doFind);
      connect('swap_s_and_e', 'onclick', self.swapStartAndEnd);
      //connect('regions', 'onchange', self.setRegionFromSelectBox);
      //connect('regions_form', 'onsubmit', self.setRegionFromSelectBox);
      connect('hide_ads', 'onclick', self.hideAds);
      //connect('find_center_map', 'onclick', self.findAddressAtCenter)
      //connect('clear_map', 'onclick', self.clearMap);
    },

    onResize: function() {
      var dims = getViewportDimensions();
      byCycle.logDebug('Viewport dimensions:', dims.w, dims.h);

      // Resize map
      var pos = elementPosition(self.map_el);
      var width = dims.w - pos.x - (self.ads_width ? self.ads_width : 0);
      var height = dims.h - pos.y;
      self.map.setSize({w: width, h: height});

      // Resize display (include padding)
      pos = elementPosition(self.display_el);
      height = dims.h - pos.y;
      self.display_el.style.height =  (height - 8) + 'px';

      // Resize ads (if visible)
      if (self.ads_width) {
        self.google_ads_el.style.height =  height + 'px';
      }
    },

    /** Common Hooks, Callbacks, Helpers **/

    beforeQuery: function(form, service, q, errors) {
      byCycle.logDebug('Entered beforeQuery...');
      if (self.showErrors(errors)) {
        self.abort_request = true;
        byCycle.logDebug('Query errors encountered.');
        return;
      }
      self.abort_request = false;
      self.form = form;
      self.start_ms = new Date().getTime();
      map(hideElement, ['info', 'help', 'errors']);
    },

    onQueryLoading: function(request, msg) {
      byCycle.logDebug('Entered onQueryLoading...');
      if (self.abort_request) {
        request.abort();
        byCycle.logDebug('Aborted request');
      } else {
        self.setStatus(msg || 'Processing...');
      }
    },

    onQueryLoaded: function(request) {
      self.setStatus(self.getElapsedTimeMessage());
    },

    showErrors: function(errors) {
      // TODO: Cancel AJAX request (How?)
      // Show the list of errors; return true if errors, false if not
      var has_errors = (errors.length > 0);
      if (has_errors) {
        var content = ['<h2>Errors</h2><ul class="result_list"><li>',
                       errors.join('</li><li>'), '</li></ul>'].join('');
        self.setErrors(content);
      }
      return has_errors;
    },

    setBookmark: function(form) {
      byCycle.logDebug('Entered setBookmark...');
      var path_info = [];
      var query_args = {};
      path_info.push(self.region, self.service, ':q');
      if (self.service == 'route') {
        var pref = self.pref_el.value;
        if (pref) {
          query_args.pref = pref;
        }
      }
      var url = ['http://', byCycle.domain, '/', path_info.join('/')].join('');
      self.bookmark_el.href = [url, queryString(query_args)].join('?');

      byCycle.logDebug('Bookmark:', self.bookmark_el.href);
    },

    getElapsedTimeMessage: function() {
      if (self.start_ms) {
        var elapsed_time = (new Date().getTime() - self.start_ms) / 1000.0;
        elapsed_time = ['Done. Took ', elapsed_time, ' second',
                        (elapsed_time == 1.00 ? '' : 's'), '.'].join('');
      } else {
        var elapsed_time = '';
      }
      return elapsed_time;
    },

    /** Search Hooks, Callbacks, Helpers **/

    beforeSearchQuery: function(form) {
      byCycle.logDebug('Entered beforeSearchQuery...');
      var errors = [];
      var q = self.q_el.value;
      if (!q) {
        errors.push('Please enter something to search for!');
        self.q_el.focus();
      } else {
        // Is the query a route?
        var i = q.toLowerCase().indexOf(' to ');
        if (i != -1) {
          // Query looks like a route
          service = 'route';
          var s = q.substring(0, i);
          var e = q.substring(i + 4);
          self.s_el.value = s;
          self.e_el.value = e;
          signal('route_label', 'onclick');
          self.beforeRouteQuery(form, s, e);
          return;
        }
      }
      // Query doesn't look like a route
      self.beforeQuery(form, 'query', q, errors);
    },

    onSearchSuccess: function(request) {
      byCycle.logDebug('Query succeeded. Status: ' + request.status);
    },

    onSearchFailure: function(request) {
      self.setStatus('Query failed. Status: ' + request.status +
                     'Response Text:\n' + request.responseText);
    },

    onSearchComplete: function(request) {
      // TODO: Check status; success refers to request only, not status
      byCycle.logDebug('Entered onSearchComplete');
      var status = request.status;
      var response_text = request.responseText;
      eval('var result = ' + $('oResult').value);
      self.result = result;
      self.map.placeMarker(result.point);
      if (self.successfulQuery) {
        self.map.setCenter(result.point);
      } else {
        self.successfulQuery = true;
        self.map.setCenter(result.point, 14);
      }
      self.setBookmark();
      byCycle.logDebug('Query complete.');
    },

    geocodeCallback: function(status, result_set) {
      byCycle.logDebug('Entered geocodeCallback');
      self.geocodes = result_set.result;
      switch (status) {
        case 200: // A-OK, one match
          self.showGeocode(0, true);
          break;
        case 300:
          break;
      }
    },

    /** Route Hooks, Callbacks, Helpers **/

    beforeRouteQuery: function(form, s, e) {
      var errors = [];
      var s = s || self.s_el.value;
      var e = e || self.e_el.value;
      if (s && e) {
        q = ['["', s, '", "', e, '"]'].join('');
      } else {
        if (!s) {
          errors.push('Please enter a start address');
          self.s_el.focus();
        }
        if (!e) {
          errors.push('Please enter an end address');
          if (s) {
            self.e_el.focus();
          }
        }
      }
      self.beforeQuery(form, 'route', q, errors);
    },

    routeCallback: function(status, result_set) {
      byCycle.logDebug('In _routeCallback');
      var route = result_set.result;
      switch (status) {
        case 200:
          var map = self.map;
          var ls = route.linestring;

          // Zoom to linestring
          map.centerAndZoomToBounds(map.getBoundsForPoints(ls));

          // Place from and to markers
          var s_e_markers = map.placeMarkers(
            [ls[0], ls[ls.length - 1]], [map.start_icon, map.end_icon]
          );

          // Add listeners to from and to markers
          var s_mkr = s_e_markers[0];
          var e_mkr = s_e_markers[1];
          map.addListener(s_mkr, 'click', function() {
            map.showMapBlowup(ls[0]);
          });
          map.addListener(e_mkr, 'click', function() {
            map.showMapBlowup(ls[ls.length - 1]);
          });

          // Draw linestring
          map.drawPolyLine(ls, colors[color_index]);
          color_index += 1;
          if (color_index == colors_len) {
            color_index = 0;
          }
          break;
        case 300: // Multiple matches for start and/or end address
          break;
      }
    },

    /** Miscellaneous **/

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

    /** UI Manipulation ("DHTML") **/

    initTabPanes: function() {
      new self.TabPane('input', 'query_label');
    },

    reverseDirections: function() {
      // TODO: Do this right--that is, use the from and to values from the
      // result, not just whatever happens to be in the input form
      $('route_form').submit();
    },

    //setSelected: function(selected) {
      //// Handle called-as-slot
      //if (typeof(selected.src) == 'function') {
        //byCycle.logDebug('setSelected called-as-slot');
    //var event = selected;
    //var link = event.src();
    //selected = link.name;
      //}
      //byCycle.logDebug('selected:', selected);
      //if (selected == self.selected) {
    //return;
      //}
      //// Hide old section
      //var section = self.input_sections[self.selected];
      //section.link.className = '';
      //map(hideElement, [section.input, section.label]);
      //// Show new section
      //self.selected = selected;
      //section = self.input_sections[selected];
      //section.link.className = 'selected';
      //map(showElement, [section.input, section.label]);
      //section.focus.focus();
    //},

    hideAds: function() {
      hideElement('google_ads');
      self.ads_width = 0;
      self.onResize();
    },

    swapStartAndEnd: function() {
      var s = self.s_el.value;
      self.s_el.value = self.e_el.value;
      self.e_el.value = s;
      s = self.s;
      self.s = e;
      self.e = s;
    },

    setStatus: function(content) {
      self.status_el.innerHTML = content.toString();
    },

    setResult: function(content) {
      self.result_el.innerHTML = content;
    },
    clearResult: function() {
      self.result_el.innerHTML = '';
    },

    setErrors: function(content) {
      showElement(self.errors_el);
      self.errors_el.innerHTML = content;
    },
    clearErrors: function() {
      self.errors_el.innerHTML = '';
    },

    /** Map **/

    findAddressAtCenter: function() {
      var center = self.map.getCenterString();
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

    /** Regions **/

    showRegionSelectBox: function() {
      showElement($('regions_win'));
    },

    setRegionFromSelectBox: function() {
      var opts = self.region_el.options;
      var region = opts[self.region_el.selectedIndex].value;
      self.setRegion(region);
      //hideElement('regions_win');
      //logDebug('Region set to', opts[self.region_el.selectedIndex].innerHTML || 'All Regions');
    },

    setRegion: function(region) {
      var regions = byCycle.regions;
      self.region = region;
      region = regions[region] || regions.all;
      //document.title = 'byCycle - Bicycle Trip Planner - ' + region.heading;
      //$('active_region').innerHTML = region.heading;
      //self.setStatus('Changed region to ' + region.heading);
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


/**
 * `TabPane` class; holds a bunch of `Tab`s.
 */
byCycle.UI.TabPane = function(container, selected_id) {
  this.tabs = new Object();
  var labels_container = getElementsByTagAndClassName('div', 'tab_labels', container)[0];
  var contents_container = getElementsByTagAndClassName('div', 'tab_contents', container)[0];
  var labels = getElementsByTagAndClassName('li', 'tab_label', labels_container);
  var contents = getElementsByTagAndClassName('div', 'tab_content', contents_container);
  var container_id = container.id;
  for (var i = 0; i < contents.length; ++i) {
    var id = container_id + '_tab_pane_tab' + i;
    var tab = new byCycle.UI.Tab(this, id, labels[i], contents[i]);
    this.tabs[tab.link.id] = tab;
  }
  if (!selected_id)
    this.selected_id = container_id + '_tab_pane_tab' + (selected_id || '0');
  else
    this.selected_id = selected_id;
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
  var self = link.tab_pane;
  // Hide the last selected tab
  var last_tab = self.tabs[self.selected_id];
  removeElementClass(last_tab.label, 'selected');
  hideElement(last_tab.content);
  // Activate the selected tab
  var tab = self.tabs[link.id];
  addElementClass(tab.label, 'selected');
  showElement(tab.content);
  self.selected_id = link.id;
  byCycle.UI.service = link.name;
  byCycle.logDebug('Service set to', byCycle.UI.service);
};


/**
 * `Tab` class; consists of tab label and tab contents.
 */
byCycle.UI.Tab = function(tab_pane, id, label, content) {
  this.label = label;
  this.content = content;
  var link = getElementsByTagAndClassName('a', null, label)[0];
  link.tab_pane = tab_pane;
  if (!link.id)
    link.id = id;
  connect(link, 'onclick', tab_pane.selectTab);
  this.link = link;
};
