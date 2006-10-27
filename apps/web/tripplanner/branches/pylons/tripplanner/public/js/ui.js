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
      Event.observe(window, 'load', byCycle.UI.onLoad);
    },

    onLoad: function() {
      self = byCycle.UI;
      // Figure out which map to use
      if (!self.map_state) {
        // Either the map is off or the map is not loadable.
        // Otherwise, below we'll use whatever self.map_type is set to.
        self.map_type = byCycle.Map.base;
      }
      var _tmp = new self.TabPane('input', 'query_label');
      self.setEventHandlers();
      self.map = new self.map_type.Map(self, self.map_el);
      Element.hide('map_msg');
      Element.show(self.map_el);
      Element.show('ads');
      if (byCycle.debug) {
        Element.show('debug_window');
      }
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
      Event.observe(window, 'resize', self.onResize);
      Event.observe(document.body, 'unload', self.unload);
      Event.observe('swap_s_and_e', 'click', self.swapStartAndEnd);
      Event.observe('change_region_link', 'click', self.showRegionSelectBox);
      Event.observe('hide_ads', 'click', self.hideAds);
      //connect('find_center_map', 'onclick', self.findAddressAtCenter)
      //connect('clear_map', 'onclick', self.clearMap);
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

    /** UI Manipulation ("DHTML") **/

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

    /**
     * Select from multiple matching geocodes
     */
    selectGeocode: function(id) {
      var chosen = $(id);
      var r = self.results_el;
      r.insertBefore(chosen, r.firstChild);
      Element.update('title'+id, 'Geocode');
      Element.remove('extra'+id);
      Element.update(self.errors_el, '');
      Element.hide(self.errors_el);
      var gq = new byCycle.UI.GeocodeQuery({});
      var request = {status: 200, responseText: ''};
      gq.onSuccess(request);
      gq.onComplete(request);
      gq.after(request);
      Element.update(self.status_el, 'Good choice!');
    },
  
    reverseDirections: function() {
      // TODO: Do this right--that is, use the from and to values from the
      // result, not just whatever happens to be in the input form
      $('route_form').submit();
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
      s = self.s;
      self.s = e;
      self.e = s;
    },

    setStatus: function(content) {
      self.status_el.innerHTML = content.toString();
    },

    setResult: function(content) {
      self.results_el.innerHTML = content;
    },
    clearResult: function() {
      self.results_el.innerHTML = '';
    },

    setErrors: function(content) {
      Element.show(self.errors_el);
      self.errors_el.innerHTML = content;
    },
    clearErrors: function() {
      self.errors_el.update('');
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
 * Query Base Class
 */
byCycle.UI.Query = function(form) {
  if (typeof(form) == 'undefined') {
    return;
  }
  this.form = form;
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
      this.showErrors(e.message);
    }
  },

  before: function() {
    byCycle.logDebug('Entered beforeQuery...');
    this.start_ms = new Date().getTime();
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
      parameters: Form.serialize(this.form)
    };
    var _tmp = new Ajax.Updater({success: 'results', failure: 'errors'}, 
                                url, 
                                args);
  },

  onLoading: function(request) {
    Element.update('status', this.updater_message);
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
    Element.update('errors', '');
    this.successful = false;
  },

  onComplete: function(request) {
    byCycle.logDebug('Entered onComplete...');
    Element.update('status', this.getElapsedTimeMessage());
    if (this.successful) {
      eval('var result = ' + $F('json') + ';');
      this.callback(result);
    }
    Element.remove('json');
    byCycle.logDebug('Left onComplete.');
  },

  after: function() {
    byCycle.logDebug('Base after().');
  },

  showErrors: function(errors) {
    // Handle errors that happen *before* the updater would have run (the
    // updater doesn't get run if there are errors).
    Element.update('status', 'Oops!');
    Element.show('errors');
    if (!(errors instanceof Array)) {
      errors = [errors];
    }
    var content = ['<ul class="result_list"><li>',
                   errors.join('</li><li>'),
                   '</li></ul>'].join('');
    Element.update('errors', content);
  },

  getElapsedTimeMessage: function() {
    var elapsed_time = (new Date().getTime() - this.start_ms) / 1000.0;
    var msg = (this.successful ? 'Done' : 'Something unexpected happened');
    elapsed_time = [msg, '. Took ', elapsed_time, ' second',
                    (elapsed_time == 1.00 ? '' : 's'), '.'].join('');
    return elapsed_time;
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
        //Event.trigger('route_label', 'click');
        query_class = new byCycle.UI.RouteQuery(this.form);
      } else {
        // Query doesn't look like a route
        query_class = new byCycle.UI.GeocodeQuery(this.form);
      }
      query_class.run();
    }
  },

  updater: function() {}
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
    map.placeMarker(result.point);
    map.setCenter(result.point, 14);
    byCycle.logDebug('Left geocodeCallback.');
  }
});


/**
 * Route Query
 */
byCycle.UI.RouteQuery = function() {
  byCycle.UI.Query.call(this);
  this.service = 'route';
  this.updater_message = 'Finding route...';
};

byCycle.UI.RouteQuery.prototype = Object.extend(new byCycle.UI.Query(), {
  before: function(form) {
    byCycle.UI.Query.prototype.before.call(this);
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

  callback: function(status, result_set) {
    byCycle.logDebug('In _routeCallback');
    var route = result_set.result;
    switch (status) {
      case 200:
        var map = self.map;
        var ls = route.linestring;

        // Zoom to linestring
        map.centerAndZoomToBounds(map.getBoundsForPoints(ls));

        // Place from and to markers
        var s_e_markers = map.placeMarkers([ls[0], ls[ls.length - 1]], 
                                           [map.start_icon, map.end_icon]);

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
  }
});


/**
 * `TabPane` class; holds a bunch of `Tab`s.
 */
byCycle.UI.TabPane = function(container, selected_id) {
  this.tabs = {};
  var labels_container = document.body.getElementsByClassName('tab_labels', container)[0];
  var contents_container = document.body.getElementsByClassName('tab_contents', container)[0];
  var labels = document.body.getElementsByClassName('tab_label', labels_container);
  var contents = document.body.getElementsByClassName('tab_content', contents_container);
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
