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

  var map_state = byCycle.getParamVal('map_state', function(map_state) {
    // Anything but '', '0' or 'off' is on
    return (!(map_state == '0' || map_state == 'off' || map_state === ''));
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
    status_el: $('status'),
    region_el: $('regions'),
    bookmark_el: $('bookmark'),
    display_el: $('display'),
    info_el: $('info'),
    help_el: $('help'),
    results_el: $('results'),
    errors_el: $('errors'),

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
    results: {},
    route_choices: null,
    http_status: null,
    response_text: null,

    status_messages: {
      200: 'Done',
      300: 'Please choose carefully',
      400: 'Oops',
      404: 'Sorry, that wasn\'t found',
      500: 'Something unexpected happened'
    },

    colors: colors,
    color_index: 0,
    colors_len: colors.length,

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
      Event.observe(window, 'load', byCycle.UI.onLoad);
    },

    onLoad: function() {
      self = byCycle.UI;
      // Figure out which map to use
      if (!(self.map_state && self.map_type.isLoadable())) {
        // Either the map is off or the map is not loadable.
        // Otherwise, below we'll use whatever self.map_type is set to.
        self.map_type = byCycle.Map.base;
      }
      var s = self.service;
      s = (s == 'route' ? s : 'query');
      var _tmp = new self.TabPane('input', s + '_label');
      self.setEventHandlers();
      self.map = new self.map_type.Map(self, self.map_el);
      Element.hide('map_msg');
      Element.show(self.map_el);
      Element.show('ads');
      if (debug) {
        Element.show('debug_window');
      }
      self.onResize();
      self.setRegionFromSelectBox();
      self.handleResult();  // For non-AJAX queries, bookmarks, etc
    },

    /** Events **/

    unload: function() {
      self.map.unload();
    },

    setEventHandlers: function() {
      Event.observe(window, 'resize', self.onResize);
      Event.observe(document.body, 'unload', self.unload);
      Event.observe('swap_s_and_e', 'click', self.swapStartAndEnd);
      Event.observe('change_region_link', 'click', self.showRegionSelectBox);
      Event.observe('hide_ads', 'click', self.hideAds);
      //Event.observe('map_find_at_center', 'click', self.findAddressAtCenter)
      //Event.observe('map_clear', 'click', self.clearMap);
    },

    onResize: function() {
      var dims = Element.getDimensions(document.body);
      byCycle.logDebug('Viewport dimensions:', dims.width, dims.height);

      // Resize map
      var pos = Position.cumulativeOffset(self.map_el);
      var width = dims.width - pos[0] - (self.ads_width ? self.ads_width : 0);
      var height = dims.height - pos[1];
      self.map.setSize({w: width, h: height});

      // Resize display (include padding)
      pos = Position.cumulativeOffset(self.display_el);
      height = dims.height - pos[1];
      self.display_el.style.height =  (height - 8) + 'px';

      // Resize ads (if visible)
      if (self.ads_width) {
        $('ads').style.height =  height + 'px';
      }
    },

    /** Query-related **/

    handleResult: function() {
      if (!self.http_status) {
        return;
      }
      var s = self.service;
      var query_class = [s.charAt(0).toUpperCase(), s.substr(1), 'Query'];
      self.simulateQuery(query_class.join(''), self.http_status);
    },

    simulateQuery: function(query_class, http_status, response_text) {
      query_class = self[query_class];
      if (!query_class) {
        return;
      }
      http_status = http_status || 200;
      response_text = response_text || '';
      var query_obj = new query_class(null);
      var request = {status: http_status, responseText: response_text};
      if (http_status == 200) {
        query_obj.onSuccess(request);
      } else {
        query_obj.onFailure(request);
      }
      query_obj.onComplete(request);
      query_obj.after(request);
    },

    /**
     * Select from multiple matching geocodes
     */
    selectGeocode: function(select_link) {
      var r = self.results_el;

      // Get a handle to the selected geocode's "window"
      var selected = select_link.parentNode.parentNode.parentNode;

      // Change the title of the selected geocode's window to "Geocode"
      var el = document.getElementsByClassName('title', selected)[0];
      Element.update(el, 'Geocode');

      // Remove the selected geocode's "Select" link
      Element.remove(select_link.parentNode);

      // Insert the selected geocode at the top of the results div
      r.insertBefore(selected, r.firstChild);

      // Clear and hide the errors div
      Element.update(self.errors_el, '');
      Element.hide(self.errors_el);

      var json = document.getElementsByClassName('json', selected)[0];
      json.id = 'json';

      self.simulateQuery('GeocodeQuery');
      Element.update(self.status_el, 'Good choice!');
    },

    /**
     * Select from multiple matching geocodes for a route
     */
    selectRouteGeocode: function(select_link, i) {
      byCycle.logDebug('Entered selectRouteGeocode...');

      var geocodes = select_link.parentNode.parentNode.parentNode.parentNode;

      var multi = geocodes.parentNode;
      Element.remove(geocodes);

      var parts = select_link.href.split('/');
      var last_i = parts.length - 1;
      if (parts[last_i] == '') {
        last_i -= 1;
      }
      var addr = parts[last_i];
      self.route_choices[i] = addr;

      var next_multi = document.getElementsByClassName('geocodes', multi)[0];

      if (next_multi) {
        Element.show(next_multi);
        Element.update(self.status_el, 'Way to go!');
      } else {
        Element.update(self.errors_el, '');
        Element.hide(self.errors_el);
        var _tmp = new self.RouteQuery(null, self.route_choices);
        _tmp.run();
      }
    },

    removeResult: function(result_el) {
      try {
        self.results[result_el.id].remove();
      } catch (e) {
        if (e instanceof TypeError) {
          // result_el wasn't registered as a Result (hopefully intentionally)
          Element.remove(result_el);
        } else {
          byCycle.logDebug('Unhandle Exception in byCycle.UI.removeResult: ',
                           e.name, e.message);
        }
      }
    },

    reverseDirections: function(s, e) {
      self.s_el.value = s;
      self.e_el.value = e;
      var _tmp = new self.RouteQuery($('route_form'));
      _tmp.run();
    },

    /** Misc **/

    setBookmark: function(form) {
      byCycle.logDebug('Entered setBookmark...');
      var path_info = [];
      var query_args = $H();
      path_info.push(self.region, self.service, $F(self.q_el));
      if (self.service == 'route') {
        var pref = $F(self.pref_el);
        if (pref) {
          query_args.pref = pref;
        }
      }
      var url = ['http://', byCycle.domain, '/', path_info.join('/')].join('');
      var query_string = query_args.toQueryString();
      if (query_string) {
        self.bookmark_el.href = [url, query_args.toQueryString()].join('?');
      } else {
        self.bookmark_el.href = url;
      }
      byCycle.logDebug('Bookmark:', self.bookmark_el.href);
    },

    hideAds: function() {
      Element.hide('ads');
      self.ads_width = 0;
      self.onResize();
    },

    swapStartAndEnd: function() {
      var s = self.s_el.value;
      self.s_el.value = self.e_el.value;
      self.e_el.value = s;
    },

    /** Map **/

    findAddressAtCenter: function() {
      var center = self.map.getCenterString();
      self.q_el.value = center;
      new byCycle.UI.GeocodeQuery(null).run();
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

    /** Regions **/

    showRegionSelectBox: function() {
      Element.show('regions_window');
    },

    setRegionFromSelectBox: function() {
      var opts = self.region_el.options;
      var region = opts[self.region_el.selectedIndex].value;
      self.setRegion(region);
    },

    setRegion: function(region) {
      var regions = byCycle.regions;
      self.region = region || 'all';
      region = regions[region] || regions.all;
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
  };

  return _public;
})();


/**
 * Result Base Class
 * `id` -- Unique ID for this result
 * `data` -- Evaled JSON object
 */
byCycle.UI.Result = function(id, data) {
  this.id = id;
  this.data = data;
  this.map = byCycle.UI.map;
  this.overlays = [];
};

byCycle.UI.Result.prototype = {
  remove: function() {
    Element.remove(this.id);
    for (var i = 0; i < this.overlays.length; ++i) {
       this.map.removeOverlay(this.overlays[i]);
    }
    delete byCycle.UI.results[this.id];
  }
}


/**
 * Query Base Class
 */
byCycle.UI.Query = function(form, input) {
  if (typeof(form) == 'undefined') {
    return;
  }
  this.form = form;
  this.input = input;
  this.ui = byCycle.UI;
  this.region = this.ui.region;
  this.service = 'query';
  this.updater_message = 'Processing...';
};

byCycle.UI.Query.prototype = {
  run: function() {
    try {
      this.before();
      this.updater();
      this.after();
    } catch (e) {
      throw e;
      this.showErrors(e.message);
    }
  },

  before: function() {
    byCycle.logDebug('Entered beforeQuery...');
    this.start_ms = new Date().getTime();
    Element.update('errors', '');
    ['info', 'errors', 'help'].each( function (id) { Element.hide(id); } );
    byCycle.logDebug('Hid elements');
    byCycle.logDebug('Left beforeQuery.');
  },

  updater: function() {
    byCycle.logDebug('Entered updater...');
    var self = this;
    var url = [['', this.region, this.service, this.q].join('/'),
               'format=frag'].join('?');
    var args = {
      method:'get',
      asynchronous: true,
      evalScripts: true,
      insertion: Insertion.Top,
      onLoading:  function(request) {self.onLoading(request);},
      onSuccess:  function(request) {self.onSuccess(request);},
      onFailure:  function(request) {self.onFailure(request);},
      onComplete: function(request) {self.onComplete(request);},
      parameters: (self.form ? Form.serialize(self.form) : null)
    };
    var _tmp = new Ajax.Updater({success: 'results', failure: 'errors'},
                                url,
                                args);
  },

  onLoading: function(request) {
    Element.update('status', this.updater_message);
    Element.show('spinner');
  },

  onSuccess: function(request) {
    byCycle.logDebug('Search succeeded. Status: ' + request.status);
    Element.show('results');
    this.successful = true;
  },

  onFailure: function(request) {
    byCycle.logDebug('Search failed. Status: ' + request.status);
    // For errors from the back end
    Element.show('errors');
    this.successful = false;
  },

  onComplete: function(request) {
    byCycle.logDebug('Entered onComplete...');
    if (this.successful) {
      var result = this.makeResult();
      this.callback(result);
    }
    Element.update('status', this.getElapsedTimeMessage(request.status));
    Element.hide('spinner');
    byCycle.logDebug('Left onComplete.');
  },

  makeResult: function() {
    byCycle.logDebug('Entered makeResult...');
    var id = 'result_' + new Date().getTime();
    var first_result = document.getElementsByClassName('result', 'results')[0];
    first_result.id = id;
    var result = new byCycle.UI.Result(id, this.getAndRemoveJSON());
    this.ui.results[id] = result;
    byCycle.logDebug('Left makeResult...');
    return result;
  },

  after: function() {
    byCycle.logDebug('Base after().');
  },

  showErrors: function(errors) {
    // Handle errors that happen *before* the updater would have run (the
    // updater doesn't get run if there are errors in preprocessing a query).
    Element.update('status', 'Oops!');
    Element.show('errors');
    errors = errors.split('\n');
    var content = ['<b>Error', (errors.length == 1 ? '' : 's'), '</b>',
                   '<div class="errors">',
                     '<div class="error">',
                        errors.join('</div><div class="error">'),
                   '</div>'].join('');
    Element.update('errors', content);
  },

  getAndRemoveJSON: function() {
    eval('var json = ' + $F('json') + ';');
    Element.remove('json');
    return json;
  },

  getElapsedTimeMessage: function(status) {
    var elapsed_time_msg;
    if (this.start_ms) {
      elapsed_time = (new Date().getTime() - this.start_ms) / 1000.0;
      elapsed_time_msg = ['Took ', elapsed_time, ' second',
                          (elapsed_time == 1.00 ? '' : 's'), '.'].join('');
    } else {
      elapsed_time_msg = '';
    }
    elapsed_time_msg = [this.ui.status_messages[status], '. ',
                        elapsed_time_msg].join('');
    return elapsed_time_msg;
  }
};


/**
 * Search Query
 */
byCycle.UI.SearchQuery = function(form) {
  byCycle.UI.Query.call(this, form);
  this.updater_message = 'Searching...';
};

byCycle.UI.SearchQuery.prototype = Object.extend(new byCycle.UI.Query(), {
  before: function() {
    byCycle.UI.Query.prototype.before.call(this);
    var query_class;
    var q = $F('q');
    if (!q) {
      Field.focus('q');
      throw new Error('Please enter something to search for!');
    } else {
      // Is the query a route?
      var i = q.toLowerCase().indexOf(' to ');
      if (i != -1) {
        // Query looks like a route
        $('s').value = q.substring(0, i);
        $('e').value = q.substring(i + 4);
        // TODO: Switch to route view
        query_class = new byCycle.UI.RouteQuery(this.form);
      } else {
        // Query doesn't look like a route
        query_class = new byCycle.UI.GeocodeQuery(this.form);
      }
      query_class.run();
    }
  },

  updater: function() {},
  after: function() {},
  callback: function() {}
});


/**
 * Geocode Query
 */
byCycle.UI.GeocodeQuery = function(form) {
  byCycle.UI.Query.call(this, form);
  this.service = 'geocode';
  this.updater_message = 'Locating address...';
};

byCycle.UI.GeocodeQuery.prototype = Object.extend(new byCycle.UI.Query(), {
  before: function() {
    byCycle.UI.Query.prototype.before.call(this);
    byCycle.logDebug('Entered beforeGeocodeQuery...');
    var q = $F('q');
    if (!q) {
      Field.focus('q');
      throw new Error('Please enter an address!');
    }
    this.q = q;
  },

  callback: function(result) {
    byCycle.logDebug('Entered geocodeCallback...');
    var map = this.ui.map;
    var marker = map.placeMarker(result.data.point);
    result.overlays.push(marker);
    map.setCenter(result.data.point, 14);
    byCycle.logDebug('Left geocodeCallback.');
  }
});


/**
 * Route Query
 */
byCycle.UI.RouteQuery = function(form, input) {
  byCycle.UI.Query.call(this, form, input);
  this.service = 'route';
  this.updater_message = 'Finding route...';
};

byCycle.UI.RouteQuery.prototype = Object.extend(new byCycle.UI.Query(), {
  before: function(form) {
    byCycle.UI.Query.prototype.before.call(this);
    byCycle.logDebug('Entered beforeRouteQuery...');
    var errors = [];
    if (typeof(this.input) == 'undefined') {
      // Use form fields for input
      var s = $F('s');
      var e = $F('e');
      if (s && e) {
        this.q = ['["', s, '", "', e, '"]'].join('');
      } else {
        if (!s) {
          errors.push('Please enter a start address');
          $('s').focus();
        }
        if (!e) {
          errors.push('Please enter an end address');
          if (s) {
            $('e').focus();
          }
        }
        throw new Error(errors.join('\n'));
      }
    } else {
      // Use passed-in input
      if (this.input.length > 1) {
        this.q = ['["', this.input.join('", "'), '"]'].join('');
      } else {
        throw new Error('Not enough addresses for Route Query.');
      }
    }
  },

  onComplete: function(request) {
    byCycle.UI.Query.prototype.onComplete.call(this, request);
    if (request.status == 300) {
      this.ui.route_choices = this.getAndRemoveJSON();
    }
  },

  callback: function(result) {
    byCycle.logDebug('Entered routeCallback...');
    var route = result.data[0];
    var map = this.ui.map;
    var ls = route.linestring;

    // Zoom to linestring
    map.centerAndZoomToBounds(map.getBoundsForPoints(ls));

    // Place from and to markers
    var s_e_markers = map.placeMarkers([ls[0], ls[ls.length - 1]],
                                       [map.start_icon, map.end_icon]);

    // Add listeners to from and to markers
    var s_marker = s_e_markers[0];
    var e_marker = s_e_markers[1];
    map.addListener(s_marker, 'click', function() {
      map.showMapBlowup(ls[0]);
    });
    map.addListener(e_marker, 'click', function() {
      map.showMapBlowup(ls[ls.length - 1]);
    });

    // Draw linestring
    var color_index = this.ui.color_index;
    var line = map.drawPolyLine(ls, this.ui.colors[color_index]);
    color_index += 1;
    if (color_index == this.ui.colors_len) {
      color_index = 0;
    }
    this.ui.color_index = color_index;
    result.overlays.push(s_marker, e_marker, line);
    byCycle.logDebug('Left routeCallback.');
  }
});


/**
 * `TabPane` class; holds a bunch of `Tab`s.
 */
byCycle.UI.TabPane = function(container, selected_id) {
  this.tabs = {};
  var f = document.getElementsByClassName;
  var labels_container = f('tab_labels', container)[0];
  var contents_container = f('tab_contents', container)[0];
  var labels = f('tab_label', labels_container);
  var contents = f('tab_content', contents_container);
  var container_id = container.id;
  for (var i = 0; i < contents.length; ++i) {
    var id = container_id + '_tab_pane_tab' + i;
    var tab = new byCycle.UI.Tab(this, id, labels[i], contents[i]);
    this.tabs[tab.link.id] = tab;
  }
  if (!selected_id) {
    this.selected_id = container_id + '_tab_pane_tab' + (selected_id || '0');
  } else {
    this.selected_id = selected_id;
  }
};

/**
 * Given a label.link DOM element, make the label "active" and show the
 * associated contents
 */
byCycle.UI.TabPane.prototype.selectTab = function(event) {
  var class_names;
  var link = event.target;
  var self = link.tab_pane;
  // Hide the last selected tab
  var last_tab = self.tabs[self.selected_id];
  class_names = new Element.ClassNames(last_tab.label);
  class_names.remove('selected');
  Element.hide(last_tab.content);
  // Activate the selected tab
  var tab = self.tabs[link.id];
  class_names = new Element.ClassNames(tab.label);
  class_names.add('selected');
  Element.show(tab.content);
  self.selected_id = link.id;
};


/**
 * `Tab` class; consists of tab label and tab contents.
 */
byCycle.UI.Tab = function(tab_pane, id, label, content) {
  this.label = label;
  this.content = content;
  var link = label.getElementsByTagName('a')[0];
  link.tab_pane = tab_pane;
  if (!link.id) {
    link.id = id;
  }
  Event.observe(link, 'click', tab_pane.selectTab);
  link.onclick = function() { return false; };
  this.link = link;
};
