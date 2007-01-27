/* Namespace for User Interface objects and functions. */


byCycle.UI = (function() {
  // private:
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
  var map_type = (byCycle.Map[map_type_name] ||            // URL override
                  byCycle.Map[byCycle.config.map_type] ||  // config setting
                  byCycle.Map.base);                       // default
  byCycle.logDebug('Map type:', map_type.description);

  // public:
  return {

    // Map and related
    map: null,
    map_state: map_state,
    map_type: map_type,

    // Current state (TODO: Make object for these???)
    region: 'all',
    service: 'query',
    query: null,
    is_first_result: true,
    result: null,
    results: {},
    route_choices: null,
    http_status: null,
    response_text: null,

    status_messages: {
      200: 'Done',
      300: 'Please choose carefully',
      400: 'Oops',
      404: "Sorry, that wasn't found",
      500: 'Something unexpected happened'
    },

    colors: colors,
    color_index: 0,
    colors_len: colors.length,

    /* Initialization ********************************************************/

    setLoadingStatus: function(msg) {
      $('loading_status').innerHTML = msg;
    },

    /**
     * Do stuff that must happen _during_ page load
     */
    beforeLoad: function() {
      byCycle.UI.setLoadingStatus('Initializing map...');
      map_state && map_type.beforeLoad();
      dojo.addOnLoad(byCycle.UI.onLoad);
    },

    /**
     * Do stuff that must happen once page has loaded
     */
    onLoad: function() {
      self = byCycle.UI;
      self._assignUIElements();

      // If map is "on" and specified map type is loadable, use that map type.
      // Otherwise, use the default map type (base).
      if (!(self.map_state && self.map_type.isLoadable())) {
        self.map_type = byCycle.Map.base;
      }
      self.map = new self.map_type.Map(self, self.map_pane);

      self.setEventHandlers();
      self.setRegionFromSelectBox();

      // For URLs containing a query
      // TODO: Do async call after load
      self.handleQuery();

      dojo.html.setVisibility('root_container', 'visible');
      dojo.html.hide($('result_container'));
      self.focusServiceElement(self.service == 'route' ? 'route' : 'query');
      dojo.dom.destroyNode($('loading'));
    },

    _assignUIElements: function() {
      // Input elements
      self.input_container = dojo.widget.byId('input_container');
      self.query_pane = dojo.widget.byId('query_pane');
      self.route_pane = dojo.widget.byId('route_pane');
      self.query_form = $('query_form');
      self.route_form = $('route_form');
      self.q_el = $('q');
      self.s_el = $('s');
      self.e_el = $('e');
      self.pref_el = $('pref');

      self.status = $('status');
      self.bookmark_el = $('bookmark');

      // Display panes (results and messages)
      self.display_container = dojo.widget.byId('display_container');
      self.message_pane = dojo.widget.byId('message_pane');
      self.info_pane = $('info_pane');
      self.error_pane = $('error_pane');
      self.help_pane = $('help_pane');
      self.message_panes = [self.info_pane, self.error_pane, self.help_pane];

      // Result elements (location and route lists in tab container)
      self.result_container = dojo.widget.byId('result_container');
      self.location_list_pane = dojo.widget.byId('location_list_pane');
      self.route_list_pane = dojo.widget.byId('route_list_pane');
      self.location_list = $('location_list');
      self.route_list = $('route_list');

      // Map and related
      self.region_el = $('regions');
      self.map_pane = $('map_pane');
    },

    /* Events ****************************************************************/

    setEventHandlers: function() {
      dojo.event.connect(window, 'resize', self.onResize);
      dojo.event.connect(document.body, 'unload', self.onUnload);
      dojo.event.connect('swap_s_and_e', 'click', self.swapStartAndEnd);
    },

    onUnload: function() {
      document.body.style.display = 'none';
      self.map.onUnload();
    },

    /** Input **/

    focusServiceElement: function(service) {
      service == 'route' ? self.s_el.focus() : self.q_el.focus();
    },

    selectInputTab: function(service) {
      self.input_container.selectChild(service == 'route' ?
                                       self.route_pane :
                                       self.query_pane);
    },

    swapStartAndEnd: function() {
      var s = self.s_el.value;
      self.s_el.value = self.e_el.value;
      self.e_el.value = s;
    },

    setAsStart: function(addr) {
      self.s_el.value = addr;
      self.selectInputTab('route');
      self.s_el.focus();
    },

    setAsEnd: function(addr) {
      self.e_el.value = addr;
      self.selectInputTab('route');
      self.e_el.focus();
    },

    /* Query-related *********************************************************/

    handleQuery: function() {
      // TODO: Do async call after load, if there's a query in the URL (use a
      // query param or maybe hidden var to indicate this)
      // - Split URL into parts (/region/query type/query)
      // - Run an async query just as if the input form had been used (based
      //   on the URL parts)
      if (!self.http_status) {
        return;
      }
      self.setLoadingStatus('Processing query...');
      var s = self.service;
      // E.g., query_class := GeocodeQuery
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
        query_obj.onLoad(request);
      } else {
        query_obj.onError(request);
      }
      query_obj.after(request);
    },

    runQuery: function(form, input) {
      byCycle.logDebug('Entered runQuery...');
      var query_class;
      var q = self.q_el.value;
      if (!q) {
        self.q_el.focus();
        self.showErrors('Please enter something to search for!');
      } else {
        // Is the query a route?
        var i = q.toLowerCase().indexOf(' to ');
        if (i != -1) {
          // Query looks like a route
          self.s_el.value = q.substring(0, i);
          self.e_el.value = q.substring(i + 4);
          query_class = 'Route';
        } else {
          // Query doesn't look like a route
          query_class = 'Geocode';
        }
        // Run query
        new self[query_class + 'Query'](form, input).run();
      }
      byCycle.logDebug('Left runQuery');
    },

    showErrors: function(errors) {
      self.status.innerHTML = 'Oops!';
      self.showMessagePane(self.error_pane);
      // FIXME: Why?
      errors = errors.split('\n');
      var content = ['<b>Error', (errors.length == 1 ? '' : 's'), '</b>',
                     '<div class="errors">',
                       '<div class="error">',
                          errors.join('</div><div class="error">'),
                     '</div>'].join('');
      self.error_pane.innerHTML = content;
    },

    /**
     * Select from multiple matching geocodes
     */
    selectGeocode: function(select_link) {
      var r = self.result_container;

      // Get a handle to the selected geocode's "window"
      var selected = select_link.parentNode.parentNode.parentNode.parentNode;

      // Change the title of the selected geocode's window to "Geocode"
      var el = dojo.html.getElementsByClass('window_title', selected)[0];
      el.innerHTML = 'Geocode';

      // Remove the selected geocode's "Select" link
      dojo.dom.removeNode(select_link.parentNode);

      // Show the "set as start or end" links
      var el = dojo.html.getElementsByClass('set_as_s_or_e', selected)[0];
      el.style.display = 'block';

      // Insert the selected geocode at the top of the results div
      r.insertBefore(selected, r.firstChild);

      // Clear and hide the errors div
      self.error_pane.innerHTML = '';
      dojo.html.hide(self.error_pane);

      var json = dojo.html.getElementsByClass('json', selected)[0];
      json.id = 'json';

      self.simulateQuery('GeocodeQuery');
      self.status.innerHTML = 'Good choice!';
    },

    /**
     * Select from multiple matching geocodes for a route
     */
    selectRouteGeocode: function(select_link, i) {
      byCycle.logDebug('Entered selectRouteGeocode...');

      var geocodes = select_link.parentNode.parentNode.parentNode.parentNode.parentNode;

      var multi = geocodes.parentNode;
      dojo.dom.removeNode(geocodes);

      var parts = select_link.href.split('/');
      var last_i = parts.length - 1;
      if (parts[last_i] == '') {
        last_i -= 1;
      }
      var addr = parts[last_i];
      self.route_choices[i] = addr;

      var next_multi = dojo.html.getElementsByClass('geocodes', multi)[0];

      if (next_multi) {
        dojo.html.show(next_multi);
        self.status.innerHTML = 'Way to go!';
      } else {
        self.error_pane.innerHTML = '';
        dojo.html.hide(self.error_pane);
        new self.RouteQuery(null, self.route_choices).run();
      }
    },

    removeResult: function(result_el) {
      try {
        self.results[result_el.id].remove();
      } catch (e) {
        if (e instanceof TypeError) {
          // result_el wasn't registered as a `Result` (hopefully intentionally)
          dojo.dom.destroyNode(result_el);
        } else {
          byCycle.logDebug('Unhandled Exception in byCycle.UI.removeResult: ',
                           e.name, e.message);
        }
      }
    },

    clearResults: function() {
      if (!confirm('Remove all of your results and clear the map?')) {
        return;
      }
      for (var result_id in self.results) {
        self.results[result_id].remove();
      }
    },

    reverseDirections: function(s, e) {
      self.s_el.value = s;
      self.e_el.value = e;
      new self.RouteQuery(self.route_form).run();
    },

    /* Links *****************************************************************/

    setBookmark: function(form) {
      byCycle.logDebug('Entered setBookmark...');
      var path_info = [];
      var query_args = $H();
      path_info.push(self.region, self.service, self.q_el.value);
      if (self.service == 'route') {
        var pref = self.pref_el.value;
        if (pref) {
          query_args.pref = pref;
        }
      }
      var url = ['http://', byCycle.domain, byCycle.prefix,
                 path_info.join('/')].join('');
      var query_string = query_args.toQueryString();
      if (query_string) {
        self.bookmark_el.href = [url, query_args.toQueryString()].join('?');
      } else {
        self.bookmark_el.href = url;
      }
      byCycle.logDebug('Bookmark:', self.bookmark_el.href);
    },

    /* Display Pane **********************************************************/

    showMessagePane: function(sub_pane) {
      dojo.html.hide(self.result_container.domNode);
      dojo.lang.forEach(self.message_panes, dojo.html.hide);
      dojo.html.show(sub_pane || self.info_pane);
      dojo.html.show(self.message_pane.domNode);
      self.display_container.onResized();
    },

    showResultContainer: function(list_pane) {
      dojo.html.hide(self.message_pane.domNode);
      dojo.html.show(self.result_container.domNode);
      self.result_container.selectChild(list_pane || self.location_list_pane);
      self.result_container.onResized();
      self.display_container.onResized();
    },

    /* Map *******************************************************************/

    findAddressAtCenter: function() {
      var center = self.map.getCenterString();
      self.q_el.value = center;
      new byCycle.UI.GeocodeQuery(null).run();
    },

    handleMapClick: function(point) {
      var handler = self[$('map_mode').value];
      if (typeof(handler) != 'undefined') {
        handler(point);
      }
    },

    identifyIntersection: function(point) {
      var q = [point.x, point.y].join(',');
      new byCycle.UI.GeocodeQuery(null, q).run();
    },

    identifyStreet: function(point) {
      self.status.innerHTML = '"Identify Street" feature not implemented yet.';
    },

    /* Regions ***************************************************************/

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
      if (self.region == 'all' && !region.marker) {
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
})();
