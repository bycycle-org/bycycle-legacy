/**
 * Query Base Class
 */
Class(byCycle.UI, 'Query', null, function () {
  var self;

  return {
    initialize: function(service, form, result_container,
                         opts /* input=undefined */) {
      if (arguments.length == 0) return;
      self = this;
      this.ui = byCycle.UI;
      this.service = service;
      this.form = form;
      this.result_container = result_container;
      if (opts) {
        this.input = opts.input;  // Hash or undefined
      }
    },

    run: function() {
      var error_before = false;
      try {
        this.before();
      } catch (e) {
        error_before = true;
        this.ui.showErrors(e.message);
      }
      if (!error_before) {
        this.doQuery();
      }
    },

    before: function() {
      // Always do this
      // Base version should not raise errors
      this.ui.spinner.show();
    },

    doQuery: function() {
      // Done only if no errors in before()
      var path = [
        'regions', byCycle.region_id, self.service, 'find.json'].join('/');
      var url = [byCycle.prefix, path].join('');
      var params = self.input;

      // TODO: Make bookmark???

      var args = {
        url: url,
        type: 'GET',
        data: params,
        dataType: 'json',
        beforeSend: self.onLoading,
        complete: self.onComplete,
        success: self.on200,
        error: self.onFailure
      };
      self.request = $j.ajax(args);
      self.ui.query = self;
    },

    onLoading: function(request) {
      self.ui.spinner.show();
    },

    on200: function(response) {
      // Process the results for ``service``
      // I.e., recenter map, place markers, draw line, etc
      var results = self.makeResults(response);
      self.processResults(response, results);
      self.ui.is_first_result = false;
    },

    onFailure: function(request) {
      self.ui.spinner.hide();
      eval('var response = ' + request.responseText + ';');
      self.ui.showException(response.result.fragment, false);
    },

    onComplete: function(request) {
      self.ui.spinner.hide();
      self.http_status = response.status;
      byCycle.logDebug(self.http_status);
    },

    onException: function(request) {
      self.ui.spinner.hide();
    },

    /**
     * Make a ``Result`` for each result in the response. Each ``Result``
     * contains an ID, result object, associated map overlays, widget reference,
     * etc.
     *
     * @param response The response object (responseText evaled)
     */
    makeResults: function(response) {
      // Extract top level DOM nodes from response HTML fragment (skipping text
      // nodes). These nodes will be inserted as the content of each result's
      // widget.
      var div = $j('<div></div>');
      div.html(response.result.fragment);
      var nodes = div.find('.query-result');
      var dom_node, result, results = [];
      var self = this;
      $j.each(response.result.results, function (i, obj) {
        dom_node = nodes[i];
        result = self.makeResult(obj, dom_node);
        results.push(result);
      });
      return results;
    },

    /**
     * Make a ``Result`` for the given (JSON) ``result`` and ``dom_node``.
     * The ``Result`` will contain an ID, JSON result object, associated map
     * overlays, widget reference, etc.
     *
     * @param result A simple object from the evaled JSON response
     * @param dom_node A DOM node that contains the necessary elements to create
     *        a ``FixedPane`` widget.
     * @return ``Result``
     */
    makeResult: function (result, dom_node) {
      var id = [this.service, 'result', new Date().getTime()].join('_');
      dom_node = $j(dom_node);
      dom_node.attr('id', id);
      dom_node.css({display: 'none'});
      $j('body').append(dom_node);
      var num_tabs = self.result_container.tabs('length');
      self.result_container.tabs('add', '#' + id, 'Result #' + (num_tabs));
      dom_node.css({display: 'block'});
      self.result_container.tabs('select', num_tabs);
      var li = $j(self.result_container.find('li')[num_tabs]);
      li.addClass('ui-tabs-nav-item');
      var result_obj = new this.ui.Result(id, result, this.service);
      //widget.register_listeners('close', result_obj.remove.bind(result_obj));
      this.ui.results[this.service][id] = result_obj;
      return result_obj;
    },

    processResults: function(response, results) {}
  }
}());


/**
 * Geocode Query
 */
Class(byCycle.UI, 'GeocodeQuery', byCycle.UI.Query, {
  initialize: function(opts /* form=byCycle.UI.query_form,
                               result_container=byCycle.UI.locations_container,
                               input=undefined */) {
    opts = opts || {};
    var ui = byCycle.UI;
    var form = opts.form || ui.query_form;
    var result_container = opts.result_container || ui.locations_container;
    this.superclass.initialize.call(this, 'geocodes', form, result_container, opts);
  },

  before: function() {
    this.superclass.before.apply(this, arguments);
    if (typeof this.input == 'undefined') {
      var q = this.ui.q_el.val();
      if (!q) {
        this.ui.q_el.focus();
        throw new Error('Please enter an address!');
      }
    }
  },

  processResults: function(response, results) {
    var zoom = this.ui.is_first_result ? this.ui.map.default_zoom : undefined;
    // For each result, place a marker on the map.
    var div, content_pane, marker;
    var map = this.ui.map;
    var placeGeocodeMarker = map.placeGeocodeMarker;
    var self = this;
    $j.each(results, function (i, r) {
      div = $j('#' + r.id);
      div = div.clone(true);
      div.find('.show-on-map-link').remove();
      marker = placeGeocodeMarker.call(map, r.result.point, div, zoom);
      r.addOverlay(marker, self.ui.map.locations_layer);
    });
  }
});


/**
 * Route Query
 */
Class(byCycle.UI, 'RouteQuery', byCycle.UI.Query, {
  initialize: function(opts /* form=byCycle.UI.route_form,
                               result_container=byCycle.UI.routes_container,
                               input=undefined */) {
    opts = opts || {};
    var ui = byCycle.UI;
    var form = opts.form || ui.route_form;
    var result_container = opts.result_container || ui.routes_container;
    var service = 'routes';
    this.superclass.initialize.call(this, service, form, result_container, opts);
    this.ui.selectInputPane(service);
  },

  before: function() {
    this.superclass.before.apply(this, arguments);
    var errors = [];
    if (typeof(this.input) == 'undefined') {
      // Use form fields for input
      var s = this.ui.s_el.val();
      var e = this.ui.e_el.val();
      if (!(s && e)) {
        if (!s) {
          errors.push('Please enter a start address');
          this.ui.s_el.focus();
        }
        if (!e) {
          errors.push('Please enter an end address');
          if (s) {
            this.ui.e_el.focus();
          }
        }
        throw new Error(errors.join('\n'));
      }
      this.input = {s: s, e: e};
    }
  },

  onFailure: function(request) {
    if (request.status == 300) {
      self.on300(request);
    } else {
      self.superclass.onFailure(request);
    }
  },

  on300: function(request) {
    this.superclass.on300.call(this, request);
    eval('var response = ' + self.query.request.responseText + ';');
    var route_choices = [];
    var addr;
    $j.each(response.result, function (i, c) {
      if (typeof c == 'Array') {
        addr = null;
      } else {
        if (c.number) {
          addr = [c.number, c.network_id].join('-');
        } else {
          addr = c.network_id
        }
      }
      route_choices[i] = addr;
    });
    this.route_choices = route_choices;
  },

  processResults: function(response, results) {
    debugger;
    var route, ls, s_e_markers, s_marker, e_marker, line;
    var ui = this.ui;
    var map = ui.map;
    var getBoundsForPoints = map.getBoundsForPoints;
    var centerAndZoomToBounds = map.centerAndZoomToBounds;
    var placeMarkers = map.placeMarkers;
    var addListener = map.addListener;
    var showMapBlowup = map.showMapBlowup;
    var drawPolyLine;
    if (map.drawPolyLineFromEncodedPoints) {
      drawPolyLine = map.drawPolyLineFromEncodedPoints;
    } else {
      drawPolyLine = map.drawPolyLine;
    }
    $j.each(results, function (i, r) {
      route = r.result;
      ls = route.linestring;

      // Zoom to linestring
      // TODO: Compute this in back end???
      centerAndZoomToBounds.call(map, route.bounds, route.center);

      // Place from and to markers
      s_e_markers = placeMarkers.call(
        map, [ls[0], ls[ls.length - 1]], [map.start_icon, map.end_icon]);

      // Add listeners to start and end markers
      s_marker = s_e_markers[0];
      e_marker = s_e_markers[1];
      addListener(s_marker, 'click', function() {
        showMapBlowup.call(map, ls[0]);
      });
      addListener(e_marker, 'click', function() {
        showMapBlowup.call(map, ls[ls.length - 1]);
      });

      // Draw linestring
      var line;
      var color = ui.route_line_color;
      if (map.drawPolyLineFromEncodedPoints) {
        line = drawPolyLine.call(
          map, route.google_points, route.google_levels, color);
      } else {
        line = drawPolyLine.call(map, ls, color);
      }

      // Add overlays to result object
      r.overlays.push(s_marker, e_marker, line);
    });
  }
});
