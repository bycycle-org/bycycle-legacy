/**
 * Query Base Class
 */
byCycle.UI.Query = Class.create()
byCycle.UI.Query.prototype = {
  initialize: function(service, form, result_list,
                       opts /* processing_message='Processing...'
                               input=undefined */) {
    if (arguments.length == 0) return;
    byCycle.logDebug('Q initialize');
    this.ui = byCycle.UI;
    this.service = service;
    this.form = form;
    this.result_list = result_list;
    if (opts) {
      this.processing_message = opts.processing_message || 'Processing...';
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
    byCycle.logDebug('Entered before()...');
    this.start_ms = new Date().getTime();
    Element.show(this.ui.spinner);
    this.ui.status.innerHTML = this.processing_message;
    Element.hide(this.ui.message_pane);
    byCycle.logDebug('Left before()');
  },

  doQuery: function() {
    // Done only if no errors in before()
    byCycle.logDebug('Entered doQuery...');
    var path = ['regions', this.ui.region, this.service + ';find'].join('/')
    var url = [byCycle.prefix, path].join('');
    var params = this.input ? this.input : this.form.serialize(true);
    params.format = 'json';
    var args = {
      method:'get',
      onLoading: this.onLoading.bind(this),
      onSuccess: this.onSuccess.bind(this),
      onFailure: this.onFailure.bind(this),
      onComplete: this.onComplete.bind(this),
      parameters: params
    };
    this.request = new Ajax.Request(url, args);
  },

  onLoading: function(request) {
    this.ui.status.update(this.processing_message);
    this.ui.spinner.show();
  },

  onSuccess: function(request) {
    byCycle.logDebug('Entered onSuccess...');
    this.successful = true;
    this.ui.showResultPane(this.result_list);
    byCycle.logDebug('Left onSuccess.');
  },

  onFailure: function(request) {
    byCycle.logDebug('Search failed. Status: ' + request.status);
    this.ui.showMessagePane(this.ui.error_pane);
    byCycle.logDebug('Left onFailure.');
  },

  onComplete: function(request) {
    byCycle.logDebug('Entered onComplete...');
    this.http_status = request.status;
    eval('var response = ' + request.responseText + ';');
    if (this.successful) {
      var results = this.makeResults(response);

      // Process the results
      // I.e., recenter map, place markers, draw line, etc
      this.processResults(response, results);

      // Show widget in result list for ``service``
      var li;
      var result_list = this.result_list;
      results.each(function (r) {
        li = document.createElement('li');
        li.appendChild.bind(li)(r.widget.dom_node);
        result_list.appendChild(li);
      });
    }
    this.ui.status.update(this.getElapsedTimeMessage());
    this.ui.spinner.hide();
    byCycle.logDebug('Left onComplete. (Request processing complete.)');
  },

  /**
   * Make a ``Result`` for each result in the response. Each ``Result``
   * contains an ID, result object, associated map overlays, widget reference,
   * etc.
   *
   * @param response The response object (responseText evaled)
   */
  makeResults: function(response) {
    byCycle.logDebug('Entered makeResults...');
    var results = [];

    // Extract top level DOM nodes from response HTML fragment (skipping text
    // nodes).
    // Note: The fragment should consist of a set of top level elements that
    // can be transformed into widgets.
    var div = document.createElement('div');
    div.innerHTML = response.fragment;
    var first_child = $(div.getElementsByTagName('div')[0])
    var nodes = [first_child];
    var siblings = first_child.siblings();
    siblings && nodes.concat(siblings);

    var service = this.service;
    var Result = this.ui.Result;
    var ui_results = this.ui.results;
    var result, id, widget, dom_node;  // w: widget, n: node
    response.results.each(function (r, i) {
      dom_node = nodes[i];

      widget = new byCycle.widget.FixedPane(dom_node);

      id = [service, 'result', new Date().getTime()].join('_');
      result = new Result(id, r, service, widget);

      widget.dom_node.id = id;
      widget.register_listeners('close', result.remove.bind(result));

      results.push(result);
      ui_results[service][id] = result;
    });

    this.ui.is_first_result = false;
    byCycle.logDebug('Left makeResults.');
    return results;
  },

  processResults: function(response, results) {},

  getElapsedTimeMessage: function() {
    var elapsed_time_msg = '';
    if (this.http_status < 400 && this.start_ms) {
      elapsed_time = (new Date().getTime() - this.start_ms) / 1000.0;
      var s = (elapsed_time != 1 ? 's' : '');
      elapsed_time_msg = ['Took ', elapsed_time, ' second', s, '.'].join('');
    }
    var status_message = this.ui.status_messages[this.http_status || 200];
    elapsed_time_msg = [status_message, '. ', elapsed_time_msg].join('');
    return elapsed_time_msg;
  }
};


/**
 * Geocode Query
 */
byCycle.UI.GeocodeQuery = Class.create();
byCycle.UI.GeocodeQuery.prototype = Object.extend(new byCycle.UI.Query(), {
  // Kludge.
  superclass: byCycle.UI.Query.prototype,

  initialize: function(opts /* form=byCycle.UI.query_form,
                               result_list=byCycle.UI.location_list,
                               processing_message='Locating address...',
                               input=undefined */) {
    byCycle.logDebug('GQ initialize');

    // Arguments for superclass
    var ui = byCycle.UI;

    if (opts) {
      var form = opts.form || ui.query_form;
      var result_list = opts.result_list || ui.location_list;
    }

    this.superclass.initialize.call(this, 'geocodes', form, result_list, opts);
  },

  before: function() {
    byCycle.logDebug('Entered GeocodeQuery.before()...');
    this.superclass.before.apply(this, arguments);
    var q;
    if (typeof(this.input) == 'undefined') {
      q = this.ui.q_el.value;
      if (!q) {
        this.ui.q_el.focus();
        throw new Error('Please enter an address!');
      }
    } else {
      q = this.input;
    }
    this.q = q;
  },

  processResults: function(response, results) {
    byCycle.logDebug('Entered GeocodeQuery.processResults()...');
    var zoom = this.ui.is_first_result ? 14 : undefined;
    // For each result, place a marker on the map.
    var div, content_pane;
    var placeGeocodeMarker = this.ui.map.placeGeocodeMarker.bind(this.ui.map);
    results.each(function (r) {
      div = document.createElement('div');
      content_pane = r.widget.content_pane.cloneNode(true);
      //content_pane.getElementsByClassName('show-on-map')[0].remove();
      div.appendChild(content_pane);
      r.addOverlay(placeGeocodeMarker(r.result.point, div, zoom));
    });
    byCycle.logDebug('Left GeocodeQuery.processResults().');
  }
});


/**
 * Route Query
 */
byCycle.UI.RouteQuery = Class.create();
byCycle.UI.RouteQuery.superclass = byCycle.UI.Query.prototype;
byCycle.UI.RouteQuery.prototype = Object.extend(new byCycle.UI.Query(), {
  // Kludge.
  superclass: byCycle.UI.Query.prototype,

  initialize: function(opts /* form=byCycle.UI.query_form,
                               result_list=byCycle.UI.location_list,
                               processing_message='Finding route...',
                               input=undefined */) {
    byCycle.logDebug('RQ initialize');
    var ui = byCycle.UI;

    // Arguments for superclass
    if (opts) {
      var form = opts.form || ui.route_form;
      var result_list = opts.result_list || ui.route_list;
    }

    this.superclass.initialize.call(this, 'routes', form, result_list, opts);

    // this.ui.selectInputTab(service);
  },

  before: function() {
    byCycle.logDebug('Entered RouteQuery.before()...');
    this.superclass.before.call(this);
    var errors = [];
    if (typeof(this.input) == 'undefined') {
      // Use form fields for input
      var s = this.ui.s_el.value;
      var e = this.ui.e_el.value;
      if (s && e) {
        this.q = ['["', s, '", "', e, '"]'].join('');
      } else {
        if (!s) {
          errors.push('Please enter a start address');
          this.ui.s_el.focus();
        }
        if (!e) {
          errors.push('Please enter an end address');
          if (s) {is
            this.ui.e_el.focus();
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

  onLoad: function(request) {
    this.inherited('onLoad', arguments);
    if (this.request.status == 300) {
      this.ui.route_choices = this.getAndRemoveJSON();
    }
  },

  processResults: function(response, results, widget) {
    byCycle.logDebug('Entered RouteQuery.processResults()...');
    var route = result.result[0];
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
    byCycle.logDebug('Left routeprocessResults.');
  }
});
