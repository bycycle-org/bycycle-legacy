/* Augments the base UI namespace */
(function () {
  var self = byCycle.UI;

  // Route colors
  var colors = [
      '#0000ff', '#00ff00', '#ff0000',
      '#00ffff', '#ff00ff', '#ff8800',
      '#000000'
  ];

  // Save old versions of UI functions
  var onLoad = self.onLoad;
  var _assignUIElements = self._assignUIElements;
  var _createEventHandlers = self._createEventHandlers;

  $H({
    service: 'services',
    query: null,
    is_first_result: true,
    result: null,
    results: $H({'geocodes': $H({}), 'routes': $H({})}),
    route_choices: null,
    http_status: null,
    response_text: null,

    status_messages: {
      200: 'One result was found',
      300: 'Multiple matches were found',
      400: 'Sorry, we were unable to understand your request',
      404: "Sorry, that wasn't found",
      500: 'Something unexpected happened'
    },

    colors: colors,
    color_index: 0,
    colors_len: colors.length,


    /* BEGIN Functions that replace functions in byCycle.UI */

    onLoad: function () {
      onLoad();
      var w = byCycle.widget.TabControl;
      var initial_tab_id = (self.service == 'routes' ?
                            'find-a-route' :
                            'search-the-map');
      self.input_tab_control = new w(self.input_container, initial_tab_id);
      initial_tab_id = (self.service == 'routes' ? 'routes' : 'locations');
      self.result_tab_control = new w(self.result_pane, initial_tab_id,
                                      initial_tab_id);
      self.handleQuery();
      self.onResize();
    },

    _assignUIElements: function() {
      _assignUIElements();
      self.input_container = $('input_container');
      self.query_pane = $('search-the-map');
      self.route_pane = $('find-a-route');
      self.query_form = $('query_form');
      self.route_form = $('route_form');
      self.q_el = $('q');
      self.s_el = $('s');
      self.e_el = $('e');
      self.pref_el = $('pref');
      self.location_list = $('location_list');
      self.route_list = $('route_list');
    },

    _createEventHandlers: function () {
      _createEventHandlers();
      Event.observe('swap_s_and_e', 'click', self.swapStartAndEnd);
      Event.observe(self.query_form, 'submit', self.runGenericQuery);
      Event.observe(self.route_form, 'submit', self.runRouteQuery);
      Event.observe($('clear-map-link'), 'click', self.clearResults);
    },

    showResultPane: function(list_pane) {
      list_pane = list_pane || self.location_list;
      self.message_pane.hide();
      self.result_tab_control.select_by_id(list_pane.parentNode.id)
      self.result_pane.show();
    },

    /* END Functions that replace functions in byCycle.UI */


    /* Services Input ********************************************************/

    focusServiceElement: function(service) {
      service == 'route' ? self.s_el.focus() : self.q_el.focus();
    },

    selectInputTab: function(service) {
      self.input_tab_control.select(service == 'routes' ? 1 : 0);
    },

    swapStartAndEnd: function() {
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
        var pane = $(self.collection_name == 'routes' ? 'routes' : 'locations');
        var fragment = pane.getElementsByClassName('fragment')[0];
        var json = fragment.getElementsByClassName('json')[0];
        var request = {status: self.http_status, responseText: $F(json)};
        Element.remove(fragment);
        Element.remove(json);
        query_obj.on200(request);
      }
    },

    runGenericQuery: function(event, input /* =undefined */) {
      byCycle.logDebug('Entered runGenericQuery...');
      var q = input || self.q_el.value;
      if (q) {
        var query_class;
        // Is the query a route?
        var i = q.toLowerCase().indexOf(' to ');
        if (i != -1) {
          // Query looks like a route
          self.s_el.value = q.substring(0, i);
          self.e_el.value = q.substring(i + 4);
          query_class = self.RouteQuery;
        } else {
          // Query doesn't look like a route; default to geocode query
          query_class = self.GeocodeQuery;
        }
        self.runQuery(query_class, event);
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
      event && Event.stop(event);
      self.query = new query_class({input: input});
      self.query.run();
    },

    runGeocodeQuery: function(event, input) {
      self.runQuery(self.GeocodeQuery, event, input);
    },

    runRouteQuery: function(event, input) {
      self.runQuery(self.RouteQuery, event, input);
    },

    showErrors: function(errors) {
      self.status.innerHTML = 'Oops!';
      // FIXME: Why?
      errors = errors.split('\n');
      var content = ['<b>Error', (errors.length == 1 ? '' : 's'), '</b>',
                     '<div class="errors">',
                       '<div class="error">',
                          errors.join('</div><div class="error">'),
                     '</div>'].join('');
      self.showMessagePane(self.error_pane, content);
    },

    /**
     * Select from multiple matching geocodes
     */
    selectGeocode: function(select_link, i) {
      byCycle.logDebug('Entered selectGeocode...');
      var response = self.query.response;
      var dom_node = $(select_link).up('.fixed-pane');
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
      byCycle.logDebug('Left selectGeocode.');
    },

    /**
     * Select from multiple matching geocodes for a route
     */
    selectRouteGeocode: function(select_link, i) {
      byCycle.logDebug('Entered selectRouteGeocode...');

      var geocodes = select_link.parentNode.parentNode.parentNode.parentNode.parentNode;

      var multi = geocodes.parentNode;
      Element.remove(geocodes);

      var parts = select_link.href.split('/');
      var last_i = parts.length - 1;
      if (parts[last_i] == '') {
        last_i -= 1;
      }
      var addr = parts[last_i];
      self.route_choices[i] = addr;

      var next_multi = multi.getElementsByClassName('geocodes')[0];

      if (next_multi) {
        Element.show(next_multi);
        self.status.innerHTML = 'Way to go!';
      } else {
        self.error_pane.innerHTML = '';
        Element.hide(self.error_pane);
        new self.RouteQuery(null, self.route_choices).run();
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
    }

  }).each(function (item) { self[item.key] = item.value; });

})();
