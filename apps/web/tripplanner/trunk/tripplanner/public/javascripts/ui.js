/** Namespace for User Interface objects and functions.
 *
 * This namespace should have ZERO dependencies.
 */
NameSpace('UI', APP, function () {
  var self = null;

  return {
    region_id: null,
	region: null,

    map: null,
	map_pane_id: 'map_pane',

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
     * Do stuff that must happen once page has loaded
     */
    onLoad: function() {
      self = APP.UI;

	  self.region_id = APP.region_id;
	  self.region = APP.region;

      self._assignUIElements();

	  self.layout = self._createLayout();

      //self._createWidgets();
      // If map is "on" and specified map type is loadable, use that map type.
      // Otherwise, use the default map type (base).
      if (!(self.map_state && self.map_type.isLoadable())) {
        self.map_type = APP.Map.base;
      }
      self.map = new self.map_type.Map(self, self.map_pane_id);

      if (self.region_id == 'all') {
		self.setRegion(self.region_id);
		var region, regions = APP.regions.regions;
		for (var slug in regions) {
		  region = APP.regions.regions[slug];
		  geom = region.geometry['4326'];
		  self.map.makeRegionMarker(region.slug, geom.center);
		  self.map.drawPolyLine(geom.linestring);
		}
	  } else {
		self.map.drawPolyLine(self.region.geometry.linestring);
	  }

      //self._createEventHandlers();

      //var zoom = parseInt(APP.getParamVal('zoom'), 10);
      //if (!isNaN(zoom)) {
        //self.map.setZoom(zoom);
      //}
      //self.handleQuery();
	  //self.selectInputPane(self.service);
      self.spinner.setStyle('display', 'none');
	  var loading_el = document.getElementById('loading');
	  loading_el.parentNode.removeChild(loading_el);
    },

    _assignUIElements: function () {
	  var Element = YAHOO.util.Element;
      self.spinner = new Element('spinner');
      self.controls = new Element('controls');
	  self.errors = new Element('errors');
      self.region_el = new Element('regions');
      self.query_pane = new Element('search-the-map');
      self.route_pane = new Element('find-a-route');
      self.query_form = new Element('query_form');
      self.route_form = new Element('route_form');
      self.q_el = new Element('q');
      self.s_el = new Element('s');
      self.e_el = new Element('e');
      self.pref_el = new Element('pref');
    },

	_createLayout: function () {
	  var layout = new YAHOO.widget.Layout({
		minWidth: 400,
		minHeight: 300,
		units: [
			{
			  position: 'top',
			  body: 'top',
			  height: 22,
			  scroll: null,
			  zIndex: 2
			},
			{
			  position: 'left',
			  body: 'left',
			  width: 300,
			  resize: true,
			  scroll: false
			},
			{
			  position: 'center',
			  body: 'center'
			}
		]
	  });

	  layout.render()
	  return layout;
	},

    _createWidgets: function () {
      self.controls.accordion({
		header: '.ui-accordion-header',
		clearStyle: true
	  });

	  self.locations_container = $j('#locations ul').tabs().
		bind('tabsremove', function (event, ui) {
		  self.results.geocodes[ui.panel.id].remove();
		});

	  self.routes_container = $j('#routes ul').tabs().
		bind('tabsremove', function (event, ui) {
		  self.results.routes[ui.panel.id].remove();
		});

	  self.errors.dialog({
		autoOpen: false,
		width: 400,
		height: 300,
		resizable: true,
		buttons: {
		  'OK': function () { self.errors.dialog('close');}
		}
	  });
    },

    /* Events ****************************************************************/

    _createEventHandlers: function () {
	  var addListener = YAHOO.util.Event.addListener;
	  addListener(document.body, 'unload', self.onUnload);
      if (self.region_el) {
        self.region_el.on('change', self.setRegionFromSelectBox);
	  }
      self.spinner.on('click', function (event) {
	    self.spinner.hide();
        return false;
      });

      // Services
      addListener('swap_s_and_e', 'click', self.swapStartAndEnd);
      self.query_form.on('submit', self.runGenericQuery);
      self.route_form.on('submit', self.runRouteQuery);
    },

    onUnload: function (event) {
      self.map.onUnload();
    },

    handleMapClick: function (event) {},


    /* Regions ***************************************************************/

    setRegionFromSelectBox: function() {
      self.setRegion(self.region_el.val());
    },

    setRegion: function(region_id) {
	  // This is only meant to be used on /regions page; that's why it uses
	  // degrees instead of the region's native units.
      var region = APP.regions.regions[region_id];
	  if (!region) {
		region = APP.regions.all;
	  }
	  var geom = region.geometry['4326'];
	  self.map.centerAndZoomToBounds(geom.bounds, geom.center);
	},


    /* Services Input ********************************************************/

    focusServiceElement: function(service) {
      service == 'route' ? self.s_el.focus() : self.q_el.focus();
    },

    selectInputPane: function(service) {
      self.controls.accordion('activate', (service == 'routes' ? 1 : 0));
    },

    swapStartAndEnd: function(event) {
      event && Event.stop(event);
      var s = self.s_el.val();
      self.s_el.val(self.e_el.val());
      self.e_el.val(s);
    },

    setAsStart: function(addr) {
      self.s_el.val(addr);
      self.selectInputPane('routes');
      self.s_el.focus();
    },

    setAsEnd: function(addr) {
      self.e_el.val(addr);
      self.selectInputPane('routes');
      self.e_el.focus();
    },

	closeResultTab: function (service, i, result_id) {
	  var container = (
		service == 'routes' ?
		self.routes_container :
		self.locations_container);
	  container.tabs('remove', i);
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
        var pane = $j(
		  self.collection_name == 'routes' ? 'routes' : 'locations');
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
      APP.logDebug('Entered runGenericQuery...');
      var q = input || self.q_el.val();
      if (q) {
        var query_class;
        // Is the query a route?
        var waypoints = q.toLowerCase().split(' to ');
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
      APP.logDebug('Left runGenericQuery');
	  return false;
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

	/**
	 * @param errors An Array of error messages or a string of error messages
	 *               separated by a newline
	 */
    showErrors: function(errors) {
	  if (typeof errors == 'string') {
		errors = errors.split('\n');
	  }
	  var e, lis = [], row_class = 'a';
	  for (var i = 0; i < errors.length; ++i) {
		e = errors[i];
		lis = lis.concat(['<li class="error ', row_class, '">', e, '</li>']);
		row_class = (row_class == 'a' ? 'b' : 'a');
	  }
	  var content = ['<ul>', lis.join(''), '</ul>'].join('');
      var el = document.getElementById('error_content');
	  el.innerHTML = content;
	  //self.errors.dialog('open');
	  //self.spinner.hide();
    },

    showException: function(content) {
      $j('#error_content').html(content);
	  self.errors.dialog('open');
	  self.spinner.hide();
    },

    /**
     * Select from multiple matching geocodes
     */
    selectGeocode: function(select_link, i) {
      eval('var response = ' + self.query.request.responseText + ';');

	  var select_link = $j(select_link);
      var dom_node = select_link.parents('.query-result:first');

      // Remove the selected result's "select link
	  $j(dom_node.find('.select-geocode-span')[0]).remove();

      // Show the "set as start or end" link
      $j(dom_node.find('.set_as_s_or_e')[0]).show();

      var result = self.query.makeResult(response.result.results[i], dom_node);
      self.query.processResults('', [result])

	  self.selectInputPane('geocodes');
	  self.errors.dialog('close');

      if (self.is_first_result) {
        self.map.setZoom(self.map.default_zoom);
      } else {
        self.is_first_result = false;
      }

	  return false;
    },

    /**
     * Select from multiple matching geocodes for a route
     */
    selectRouteGeocode: function(select_link, i, j) {
      APP.logDebug('Entered selectRouteGeocode...');
      var dom_node = $j(select_link).up('ul');
      var next = dom_node.next();
      var choice = self.query.response.choices[i][j];
      var addr;
      if (choice.number) {
        addr = [choice.number, choice.network_id].join('-');
      } else {
        addr = choice.network_id;
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
          // result_el wasn't registered as a Result (hopefully intentionally)
          result_el.remove();
        } else {
          APP.logDebug(
			'Unhandled Exception in APP.UI.removeResult: ', e.name,
			e.message);
        }
      }
    },

    clearResults: function(event) {
      if (!confirm('Remove all of your results and clear the map?')) {
        return;
      }
      $j.each(util.values(self.results), function (i, service_results) {
        $j.each(util..values(service_results), function (i, result) {
          service_results[result.id].remove();
        });
      });
	  return false;
    },

    reverseDirections: function(s, e) {
      self.s_el.val(s);
      self.e_el.val(e);
      new self.RouteQuery(self.route_form).run();
    },


    /* Map *******************************************************************/

    identifyIntersectionAtCenter: function(event) {
      APP.logDebug('In find-intersection-at-center callback');
      var center = self.map.getCenter();
      self.q_el.val(self.map.getCenterString());
      self.identifyIntersection(center, event);
    },

    handleMapClick: function(point, event) {
      var handler = self[$j('#map_mode').val()];
      if (typeof handler != 'undefined') {
        handler(point);
      }
    },

    identifyIntersection: function(point, event) {
      self.runGeocodeQuery(event, {q: [point.x, point.y].join()});
    }
  };
}());
