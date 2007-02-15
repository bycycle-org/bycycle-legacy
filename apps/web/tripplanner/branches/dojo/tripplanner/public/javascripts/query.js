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
    this.ui.service = service;
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
    var path = [this.ui.region, this.ui.service].join('/')
    var url = [byCycle.prefix, path].join('');
    var params = this.input ? 
                 $H(this.input).toQueryString() : 
                 Form.serialize(this.form);
    params += '&format=json';
    var args = {
      method:'get',
      asynchronous: true,
      evalScripts: true,
      //insertion: Insertion.Bottom,
      onLoading: this.onLoading.bind(this),
      onSuccess: this.onSuccess.bind(this),
      onFailure: this.onFailure.bind(this),
      onComplete: this.onComplete.bind(this),
      parameters: params
    };
    new Ajax.Request(url, args);    
  },

  onLoading: function(request) {
    Element.update(this.ui.status, this.processing_message);
    Element.show(this.ui.spinner);
  },

  onSuccess: function(request) {
    byCycle.logDebug('Search succeeded. Status: ' + request.status);
    this.ui.showResultPane(this.result_list);
    this.successful = true;
  },

  onFailure: function(request) {
    byCycle.logDebug('Search failed. Status: ' + request.status);
    // For errors from the back end
    this.ui.showMessagePane(this.ui.error_pane);
    this.successful = false;
  },

  onComplete: function(request) {
    byCycle.logDebug('Entered onComplete...');
    this.http_status = request.status;
    if (this.successful) {
      var result = this.makeResult();
    
      //this.callback(result);

      //var li = document.createElement('li');
      //li.appendChild(result_el);
      //this.result_list.appendChild(li);
    }
    Element.update(this.ui.status, this.getElapsedTimeMessage());
    Element.hide(this.ui.spinner);    
    byCycle.logDebug('Left onComplete.');
  },

  makeResult: function() {
    byCycle.logDebug('Entered makeResult...');
    this.ui.is_first_result = false;      
    // Create result object to contain the result, its overlays, etc
    var id = 'result_' + new Date().getTime();
    var result = response.results[0];
    var result_obj = new byCycle.UI.Result(id, result);
    this.ui.results[id] = result_obj;   
    for (var k in result) byCycle.logDebug(k);
    byCycle.logDebug('Left makeResult...');
    return result;
  },  

  callback: function(result) {},

  getElapsedTimeMessage: function() {
    var elapsed_time_msg;
    if (this.start_ms) {
      elapsed_time = (new Date().getTime() - this.start_ms) / 1000.0;
      elapsed_time_msg = ['Took ', elapsed_time, ' second',
                          (elapsed_time == 1.00 ? '' : 's'), '.'].join('');
    } else {
      elapsed_time_msg = '';
    }
    byCycle.logDebug(this.http_status);
    elapsed_time_msg = [this.ui.status_messages[this.http_status || 200], '. ',
                        elapsed_time_msg, ' [', this.http_status, ']'].join('');
    return elapsed_time_msg;
  }
};


/**
 * Geocode Query
 */
byCycle.UI.GeocodeQuery = Class.create();
byCycle.UI.GeocodeQuery.prototype = Object.extend(new byCycle.UI.Query(), {
  initialize: function(opts /* form=byCycle.UI.query_form, 
                               result_list=byCycle.UI.location_list, 
                               processing_message='Locating address...', 
                               input=undefined */) {
    byCycle.logDebug('GQ initialize');
    this.superclass = byCycle.UI.Query.prototype;
    
    // Arguments for superclass
    var ui = byCycle.UI;
    
    if (opts) {
      var form = opts.form || ui.query_form;    
      var result_list = opts.result_list || ui.location_list;
    }
    
    this.superclass.initialize.call(this, 'geocode', form, result_list, opts);
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

  callback: function(result) {
    byCycle.logDebug('Entered GeocodeQuery.callback()...');
    byCycle.logDebug('Left GeocodeQuery.callback().');
    return;
    
    // Prototype version
    // Get result content pane and create a new node from it
    var cp = document.getElementsByClassName('content_pane', result.id)[0];
    var cp_copy = cp.cloneNode(true);
    cp_copy.id = cp_copy.id + '_marker';
    var node = Builder.node('div', [cp_copy]);
    // Remove the "show on map" link
    var show_on_map = document.getElementsByClassName('show_on_map', node)[0];
    Element.remove(show_on_map);
    // Put marker on map, using the new node as the info window content
    var marker = this.ui.map.placeGeocodeMarker(result.data.point, node);
    result.overlays.push(marker);
    
    // Do-jo version    
    // Get result content pane and create a new node from it
    var cp = widget.containerNode;
    var cp_copy = cp.cloneNode(true);
    cp_copy.id = cp_copy.id + '_marker';
    var node = document.createElement('div', [cp_copy]);
    // Remove the "show on map" link
    //var show_on_map = node.getElementsByClassName('show_on_map')[0];
    //Element.remove(show_on_map);
    // Put marker on map, using the new node as the info window content
    var zoom = undefined;
    if (this.ui.is_first_result) {
      zoom = 14;
    }
    var marker = this.ui.map.placeGeocodeMarker(result.result.point, node,
                                                zoom);
    result.overlays.push(marker);
  }
});


/**
 * Route Query
 */
byCycle.UI.RouteQuery = Class.create();
byCycle.UI.RouteQuery.superclass = byCycle.UI.Query.prototype;
byCycle.UI.RouteQuery.prototype = Object.extend(new byCycle.UI.Query(), {
  initialize: function(opts /* form=byCycle.UI.query_form, 
                               result_list=byCycle.UI.location_list, 
                               processing_message='Finding route...', 
                               input=undefined */) {
    byCycle.logDebug('RQ initialize');
    this.superclass = byCycle.UI.Query.prototype;

    var ui = byCycle.UI;
    
    // Arguments for superclass
    if (opts) {
      var form = opts.form || ui.route_form;    
      var result_list = opts.result_list || ui.route_list;
    }
    
    this.superclass.initialize.call(this, 'route', form, result_list, opts);
    
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

  callback: function(result) {
    byCycle.logDebug('Entered RouteQuery.callback()...');
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
    byCycle.logDebug('Left routeCallback.');
  }
});
