/* Namespace for User Interface objects and functions. */
byCycle.UI = function () {
  // private:
  var self = null;

  var map_state = byCycle.getParamVal('map_state', function(map_state) {
    // Anything but '', '0' or 'off' is on
    return map_state == '' || map_state == '0' || map_state == 'off';
  });

  var map_type_name = byCycle.getParamVal('map_type').toLowerCase();
  var map_type = (byCycle.Map[map_type_name] ||            // URL override
                  byCycle.Map[byCycle.config.map_type] ||  // config setting
                  byCycle.Map.base);                       // default
  byCycle.logDebug('Map type:', map_type.description);

  // public:
  return {
    region_id: null,
    map: null,
    map_state: map_state,
    map_type: map_type,

    service: 'services',
    query: null,  // query.Query object (not query string)
    is_first_result: true,
    result: null,
    results: {'geocodes': {}, 'routes': {}},
    http_status: null,
    response_text: null,
    bike_overlay: null,
    bike_overlay_state: false,

    status_messages: {
      200: 'One result was found',
      300: 'Multiple matches were found',
      400: 'Sorry, we were unable to understand your request',
      404: "Sorry, that wasn't found",
      500: 'Something unexpected happened'
    },

    route_line_color: '#000000',


    /* Initialization ********************************************************/

    /**
     * Do stuff that must happen _during_ page load
     */
    beforeLoad: function() {
      $j('#spinner').show();
      if (map_state) {
        map_type.beforeLoad();
      }
      $j(window).load(byCycle.UI.onLoad);
    },

    /**
     * Do stuff that must happen once page has loaded
     */
    onLoad: function() {
      self = byCycle.UI;
      self._assignUIElements();
      self._createWidgets();
      // If map is "on" and specified map type is loadable, use that map type.
      // Otherwise, use the default map type (base).
      if (!(self.map_state && self.map_type.isLoadable())) {
        self.map_type = byCycle.Map.base;
      }
      self.map = new self.map_type.Map(self, self.map_pane);
      self.setRegion(self.region_id);
      self.region_id = 'portlandor';
      self._createEventHandlers();
      var zoom = parseInt(byCycle.getParamVal('zoom'), 10);
      if (!isNaN(zoom)) {
        self.map.setZoom(zoom);
      }
      self.handleQuery();
      if (byCycle.getParamVal('bike_map')) {
        self.toggleBikeTileOverlay();
      }
      self.spinner.hide();
    },

    _assignUIElements: function() {
      self.spinner = $j('#spinner');
      self.controls = $j('#controls');
      self.region_el = $j('#regions');
      self.map_pane = $j('#map_pane');
      // Service
      self.query_pane = $j('#search-the-map');
      self.route_pane = $j('#find-a-route');
      self.query_form = $j('#query_form');
      self.route_form = $j('#route_form');
      self.q_el = $j('#q');
      self.s_el = $j('#s');
      self.e_el = $j('#e');
      self.pref_el = $j('#pref');
      self.location_list = $j('#location_list');
      self.route_list = $j('#route_list');
      self.bike_overlay_link = $j('#bike-overlay-link');
      self.map_buttons = $j('#map-buttons');
      self.legend_button = $j('#legend-map-button');
    },

    _createWidgets: function () {
      self.controls.accordion();
    },

    /* Events ****************************************************************/

    _createEventHandlers: function() {
      $j(window).resize(self.onResize);
      $j(document.body).unload(self.onUnload);
      if (self.region_el) {
        self.region_el.change(self.setRegionFromSelectBox);
	  }
      self.spinner.click(function (event) {
	    self.spinner.hide();
        return false;
      });

      // Services
      $j('#swap_s_and_e').click(self.swapStartAndEnd);
      self.query_form.submit(self.runGenericQuery);
      self.route_form.submit(self.runRouteQuery);
      if (self.bike_overlay_link) {
        self.bike_overlay_link.click(self.toggleBikeTileOverlay);
      }
      self.legend_button.click(function (event) {
        var url = '/static/regions/' + self.region_id + '/map_legend_popup.html';
        var w = window.open(url, 'bike_map_legend_window', 'status=0,toolbar=0,scrollbars=1,location=0,menubar=0,directories=0,width=755,height=490,left=0,top=0');
      });
    },

    onUnload: function(event) {
      document.body.style.display = 'none';
      self.map.onUnload();
    },

    handleMapClick: function (event) {},


    /* Regions ***************************************************************/

    setRegionFromSelectBox: function() {
      self.setRegion($jF(self.region_el));
    },

    setRegion: function(region_id) {
      self.region_id = region_id;
      var regions = byCycle.regions.regions;
      var region = regions[region_id];
      if (region) {
        // Zoom to a specific region
        self.map.centerAndZoomToBounds(region.bounds, region.center);
        self._showRegionOverlays(region);
      } else {
        // Show all regions
        var all_regions = byCycle.regions;
	self.map.centerAndZoomToBounds(all_regions.bounds, all_regions.center);
        $j.each(util.values(regions), function (r) {
          self._showRegionOverlays(r);
        });
      }
    },

    // Show map overlays for a region, creating and caching them first if
    // necessary
    _showRegionOverlays: function(region, use_cached) {
      if (!self.region_id && !region.marker) {
        region.marker = self.map.makeRegionMarker(region);
      } else if (use_cached) {
        self.map.addOverlay(region.marker);
      }
      if (!region.line) {
        region.line = self.map.drawPolyLine(region.linestring);
      } else if (use_cached) {
        self.map.addOverlay(region.line);
      }
    },


    /* Services Input ********************************************************/

    focusServiceElement: function(service) {
      service == 'route' ? self.s_el.focus() : self.q_el.focus();
    },

    selectInputTab: function(service) {
      self.input_tab_control.select(service == 'routes' ? 1 : 0);
    },

    swapStartAndEnd: function(event) {
      event && Event.stop(event);
      var s = self.s_el.value;
      self.s_el.value = self.e_el.value;
      self.e_el.value = s;
    },

    setAsStart: function(addr) {
      self.s_el.value = addr;
      self.selectInputTab('routes');
      self.s_el.focus();
    },

    setAsEnd: function(addr) {
      self.e_el.value = addr;
      self.selectInputTab('routes');
      self.e_el.focus();
    },

    showResultPane: function(list_pane) {

    },


    /* Query-related *********************************************************/

    handleQuery: function() {
      if (!self.http_status) { return; }
      var res = self.member_name;

      // E.g., query_class := GeocodeQuery
      var query_class = [res.charAt(0).toUpperCase(), res.substr(1),
                         'Query'].join('');
      query_class = self[query_class];

      var query_obj = new query_class();
      if (self.http_status == 200) {
        var pane = $j(self.collection_name == 'routes' ? 'routes' : 'locations');
        var fragment = $j(pane.find('.fragment')[0]);
        var json = $j(fragment.find('.json')[0]);
        var request = {status: self.http_status, responseText: json.val()};
        fragment.remove();
        json.remove();
        query_obj.on200(request);
      } else if (self.http_status == 300) {
        var json = self.error_pane.find('.json')[0];
        var request = {status: self.http_status, responseText: json.val()};
        json.remove();
        query_obj.on300(request);
      }
      self.query = query_obj;
    },

    runGenericQuery: function(event, input /* =undefined */) {
      byCycle.logDebug('Entered runGenericQuery...');
      var q = input || self.q_el.val();
      if (q) {
        var query_class;
        // Is the query a route?
        var waypoints = q.toLowerCase().split(' to ');
        byCycle.logDebug(waypoints);
        if (waypoints.length > 1) {
          // Query looks like a route
          self.s_el.value = waypoints[0];
          self.e_el.value = waypoints[1];
          // Override using ``s`` and ``e``
          query_class = self.RouteQuery;
        } else {
          // Query doesn't look like a route; default to geocode query
          query_class = self.GeocodeQuery;
        }
        input = {q: q};
        self.runQuery(query_class, event, input);
      } else {
        self.q_el.focus();
        self.showErrors('Please enter something to search for!');
      }
      byCycle.logDebug('Left runGenericQuery');
    },

    /* Run all queries through here for consistency. */
    runQuery: function(query_class,
                       event /* =undefined */,
                       input /* =undefined */) {
      if (event) {
        event.preventDefault();
      }
      self.query = new query_class({input: input});
      self.query.run();
    },

    runGeocodeQuery: function(event, input) {
      self.runQuery(self.GeocodeQuery, event, input);
    },

    runRouteQuery: function(event, input) {
      self.runQuery(self.RouteQuery, event, input);
    },

    showErrors: function(/* args */) {
      var errors = [];
      $j.each(arguments, function (i, a) { errors.push(a) });
      byCycle.logDebug('Oops!');
      self.spinner.hide();
      var content = [
          '<li class="error">',
             errors.join('</li><li class="error">'),
          '</li>'].join('');
      self.controls.accordion('activate', 2 )
      $j('#errors ul').html(content);
    },

    /**
     * Select from multiple matching geocodes
     */
    selectGeocode: function(select_link, i) {
      byCycle.logDebug('Entered selectGeocode...');
      var response = self.query.response;
      var dom_node = $j(select_link).up('.fixed-pane');
      var result = self.query.makeResult(response.results[i], dom_node);
      self.query.processResults('', [result])

      // Remove the selected result's selection links ("show on map" & "select")
      Element.remove(select_link.parentNode);

      // Show the title bar and "set as start or end" links
      dom_node.getElementsByClassName('title-bar')[0].show();
      dom_node.getElementsByClassName('set_as_s_or_e')[0].show();

      // Append the widget to the list of locations
      var li = document.createElement('li');
      li.appendChild(dom_node);
      this.location_list.appendChild(li);

      self.showResultPane(self.location_list);
      self.status.update('Added location to locations list.');

      if (self.is_first_result) {
        self.map.setZoom(self.map.default_zoom);
      } else {
        self.is_first_result = false;
      }

      byCycle.logDebug('Left selectGeocode.');
    },

    /**
     * Select from multiple matching geocodes for a route
     */
    selectRouteGeocode: function(select_link, i, j) {
      byCycle.logDebug('Entered selectRouteGeocode...');
      var dom_node = $j(select_link).up('ul');
      var next = dom_node.next();
      var choice = self.query.response.choices[i][j];
      var addr;
      if (choice.number) {
        addr = [choice.number, choice.network_id].join('-');
      } else {
        addr = choice.network_id
      }
      self.query.route_choices[i] = addr;
      dom_node.remove();
      if (next) {
        next.show();
      } else {
        self.runRouteQuery(null, {q: self.query.route_choices.join(' to ')});
      }
    },

    removeResult: function(result_el) {
      try {
        self.results[result_el.id].remove();
      } catch (e) {
        if (e instanceof TypeError) {
          // result_el wasn't registered as a `Result` (hopefully intentionally)
          Element.remove(result_el);
        } else {
          byCycle.logDebug('Unhandled Exception in byCycle.UI.removeResult: ',
                           e.name, e.message);
        }
      }
    },

    clearResults: function(event) {
      event && Event.stop(event);
      if (!confirm('Remove all of your results and clear the map?')) {
        return;
      }
      self.results.values().each(function (service_results) {
        service_results.values().each(function (result) {
          service_results[result.id].remove();
        });
      });
    },

    reverseDirections: function(s, e) {
      self.s_el.value = s;
      self.e_el.value = e;
      new self.RouteQuery(self.route_form).run();
    },


    /* Map *******************************************************************/

    identifyIntersectionAtCenter: function(event) {
      byCycle.logDebug('In find-intersection-at-center callback');
      var center = self.map.getCenter();
      self.q_el.value = self.map.getCenterString();
      self.identifyIntersection(center, event);
    },

    handleMapClick: function(point, event) {
      var handler = self[$j('#map_mode').value];
      if (typeof(handler) != 'undefined') {
        handler(point);
      }
    },

    identifyIntersection: function(point, event) {
      self.runGeocodeQuery(event, {q: [point.x, point.y].join()});
    },

    identifyStreet: function(point, event) {
      self.status.innerHTML = '"Identify Street" feature not implemented yet.';
    },

    toggleBikeTileOverlay: function (event) {
      event && Event.stop(event);
      if (self.bike_overlay_state) {
        // Bike layer was on; turn it off
        self.map.removeOverlay(self.bike_overlay);
        Element.hide('map-buttons');
        self.bike_overlay_link.value = 'Show bike map';
      } else {
        // Bike layer was off; turn it on
        self.bike_overlay = self.map.makeBikeTileOverlay(20);
        self.map.addOverlay(self.bike_overlay);
        Element.show('map-buttons');
        self.bike_overlay_link.value = 'Hide bike map';
        if (self.map.getZoom() < 9) { self.map.setZoom(9); }
        self.bike_overlay.show();
      }
      self.bike_overlay_state = !self.bike_overlay_state;
    }
  };
}();
