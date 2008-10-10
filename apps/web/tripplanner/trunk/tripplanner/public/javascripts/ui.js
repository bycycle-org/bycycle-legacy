/** Namespace for User Interface objects and functions.
 *
 * This namespace should have ZERO dependencies.
 */
NameSpace('UI', APP, function () {
  var self = null;

  var Event = YAHOO.util.Event;
  var Element = YAHOO.util.Element;
  var Dom = YAHOO.util.Dom;

  return {
    region_id: null,
	region: null,
	in_region: false,

    map: null,
	map_pane_id: 'map_pane',

    service: null,
    query: null,  // query.Query object (not query string)
	queries: {},
    is_first_result: true,
    result: null,
    results: {'geocodes': {}, 'routes': {}},
    http_status: null,

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
	  self.in_region = (self.region_id != 'all');

      self._assignUIElements();
	  self.layout = self._createLayout();
      self._createWidgets();

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

      self._createEventHandlers();

      var zoom = parseInt(util.getParamVal('zoom'), 10);
      if (!isNaN(zoom)) {
        self.map.setZoom(zoom);
      }

      self.handleQuery();

	  self.selectInputPane(self.service);
	  self.hideSpinner();
	  var loading_el = document.getElementById('loading');
	  loading_el.parentNode.removeChild(loading_el);
    },

    _assignUIElements: function () {
	  if (!self.in_region) {
        self.region_el = document.getElementById('regions');
	  }
	  // Common
      self.spinner = new Element('spinner');
      self.controls = new Element('controls');
	  // Service/query related
	  if (self.in_region) {
		self.query_pane = new Element('search-the-map');
		self.route_pane = new Element('find-a-route');
		self.query_form = new Element('query_form');
		self.route_form = new Element('route_form');
		self.q_el = new Element('q');
		self.s_el = new Element('s');
		self.e_el = new Element('e');
		self.pref_el = new Element('pref');
	  }
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
			  width: 380,
			  resize: true,
			  scroll: false,
			  gutter: '4px 0 0 0'
			},
			{
			  position: 'center',
			  body: 'center',
			  gutter: '4px 0 0 0'
			}
		]
	  });

	  layout.render()
	  return layout;
	},

    _createWidgets: function () {
	  // Container in left panel for query forms and other controls
	  self.controls = new YAHOO.widget.TabView('controls', {
		orientation: 'left'
	  });

	  if (self.in_region) {
		// Containers for location and route results
		self.locations_container = new YAHOO.widget.TabView('locations');
		self.routes_container = new YAHOO.widget.TabView('routes');
	  }

	  // Dialog for info and errors
	  var alert_panel = new YAHOO.widget.SimpleDialog('alert_panel', {
		fixedcenter: true,
		visible: false,
		modal: true,
		width: '400px',
		constraintoviewport: true,
		icon: YAHOO.widget.SimpleDialog.ICON_WARN,
		buttons: [
		  {
			text: 'OK', handler: function() { alert_panel.hide(); },
		    isDefault: true
		  }
		]
	  });
	  alert_panel.setHeader('Alert');
	  alert_panel.setBody('...');
	  alert_panel.render(document.body);
	  self.alert_panel = alert_panel;
    },

    /* Events ****************************************************************/

    _createEventHandlers: function () {
	  document.body.onunload = self.onUnload;
      if (self.region_el) {
	    // KLUDGE: Why doesn't YUI's on('change') work here?!?!?!
        self.region_el.onchange = self.setRegionFromSelectBox;
	  }
      self.spinner.on('click', function (event) {
	    self.hideSpinner();
      });
      // Services
	  if (self.in_region) {
		Event.addListener('swap_s_and_e', 'click', self.swapStartAndEnd);
		Event.addListener('query_form_button', 'click', self.runGenericQuery);
		Event.addListener('route_form_button', 'click', self.runRouteQuery);
	  }
    },

    onUnload: function (event) {
      self.map.onUnload();
    },

    handleMapClick: function (event) {},

	stopEvent: function (event) {
	  if (event) {
		Event.stopEvent(event);
	  }
	},


	/* UI ********************************************************************/

	showSpinner: function () {
	  self.spinner.setStyle('display', 'block');
	},

	hideSpinner: function () {
	  self.spinner.setStyle('display', 'none');
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
	  var content = ['<ul class="errors">', lis.join(''), '</ul>'].join('');
	  self.showAlertPanel('Oops!', content, 'error')
	  self.hideSpinner();
    },

    showException: function(content) {
	  self.showAlertPanel('Achtung!', content, 'error');
	  self.hideSpinner();
    },

	showAlertPanel: function (title, content, icon_type) {
	  var icon;
	  if (typeof icon_type == 'undefined') {
		icon_type = 'warn';
	  }
	  var icon_types = {
		info: YAHOO.widget.SimpleDialog.ICON_INFO,
		warn: YAHOO.widget.SimpleDialog.ICON_WARN,
		error: YAHOO.widget.SimpleDialog.ICON_ALARM,
		alarm: YAHOO.widget.SimpleDialog.ICON_ALARM,
		help: YAHOO.widget.SimpleDialog.ICON_HELP
	  }
	  var icon = icon_types[icon_type];
	  self.alert_panel.setHeader(title);
	  self.alert_panel.setBody(content);
	  self.alert_panel.cfg.setProperty('icon', icon);
	  self.alert_panel.show();
	},

	getErrorTab: function () {
	  var tabview = self.controls;
      return tabview.getTab(tabview.get('tabs').length - 1);
	},

	selectErrorTab: function (content) {
	  var tab = self.getErrorTab();
	  if (content) {
        tab.set('content', content);
	  }
	  self.controls.set('activeTab', tab);
	},


    /* Regions ***************************************************************/

    setRegionFromSelectBox: function() {
	  var el = self.region_el;
	  var val = el.options[el.selectedIndex].value;
      self.setRegion(val);
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
	  var el = (service == 'route' ? self.s_el : self.q_el);
	  el.get('element').focus();
    },

    selectInputPane: function(service) {
	  if (self.http_status && self.http_status != 200) {
		self.selectErrorTab();
	  }	else if (self.in_region) {
        self.controls.set('activeIndex', (service == 'routes' ? 1 : 0));
	  }
    },

    swapStartAndEnd: function(event) {
      self.stopEvent(event);
      var s = self.s_el.get('value');
      self.s_el.set('value', self.e_el.get('value'));
      self.e_el.set('value', s);
    },

    setAsStart: function(addr) {
      self.s_el.set('value', addr);
      self.selectInputPane('routes');
      self.s_el.get('element').focus();
    },

    setAsEnd: function(addr) {
      self.e_el.set('value', addr);
      self.selectInputPane('routes');
      self.e_el.get('element').focus();
    },


    /* Query-related *********************************************************/

    handleQuery: function() {
	  var status = self.http_status;
      if (!status) { return; }
	  if (status != 200 && status != 300) { return; }

      var res = self.member_name;

      // E.g., query_class := GeocodeQuery
      var query_class = [
		res.charAt(0).toUpperCase(), res.substr(1), 'Query'].join('');
      query_class = self[query_class];

      var query_obj = new query_class();

	  var pane = APP.el(
		self.collection_name == 'routes' ? 'routes' : 'locations');
	  var json = pane.getElementsByClassName('json')[0];
	  var request = {status: self.http_status, responseText: json.value};

      if (self.http_status == 200) {
        var fragment = pane.getElementsByClassName('query-result')[0];
        fragment.parentNode.removeChild(fragment);
        query_obj.on200(request);
      } else if (self.http_status == 300) {
        var fn = query_obj.on300 || query_obj.onFailure;
		fn.call(query_obj, request);
      }

	  json.parentNode.removeChild(json);
      self.query = query_obj;
    },

    runGenericQuery: function(event, input /* =undefined */) {
	  self.stopEvent(event);
      var q = input || self.q_el.get('value');
      if (q) {
        var query_class;
        // Is the query a route?
        var waypoints = q.toLowerCase().split(' to ');
        if (waypoints.length > 1) {
          // Query looks like a route
          self.s_el.set('value', waypoints[0]);
          self.e_el.set('value', waypoints[1]);
          // Override using ``s`` and ``e``
          query_class = self.RouteQuery;
        } else {
          // Query doesn't look like a route; default to geocode query
          query_class = self.GeocodeQuery;
        }
        self.runQuery(query_class, event, input);
      } else {
        self.showErrors('Please enter something to search for!');
		// TODO: Make this work--error dialog appears to grab focus.
        self.q_el.get('element').focus();
      }
    },

    /* Run all queries through here for consistency. */
    runQuery: function(query_class,
                       event /* =undefined */,
                       input /* =undefined */) {
      self.stopEvent(event);
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
     * Select from multiple matching geocodes
     */
    selectGeocode: function(select_link, i) {
	  var query = self.queries['query-' + self.query.request.tId];
	  var query_result = query.result;

      var dom_node = Dom.getAncestorByClassName(select_link, 'query-result');

      // Remove the selected result's "select link
	  var span = dom_node.getElementsByClassName('select-geocode-span')[0];
	  span.parentNode.removeChild(span);

      //// Show the "set as start or end" link
      var link = dom_node.getElementsByClassName('set_as_s_or_e')[0];
	  link = new Element(link);
	  link.setStyle('display', 'block');

      var result = self.query.makeResult(query_result.result.results[i], dom_node);
      self.query.processResults('', [result])

	  self.selectInputPane('geocodes');
	  dom_node.parentNode.removeChild(dom_node);

      if (self.is_first_result) {
        self.map.setZoom(self.map.default_zoom);
      } else {
        self.is_first_result = false;
      }
    },

    /**
     * Select from multiple matching geocodes for a route
     */
    selectRouteGeocode: function(select_link, i, j) {
	  var query = self.queries['query-' + self.query.request.tId];
	  var query_result = query.result;
	  var dom_node = Dom.getAncestorByTagName(select_link, 'ul');
      var next = Dom.getNextSibling(dom_node);
      var choice = query_result.result.choices[i][j];
      var addr;
      if (choice.number) {
        addr = [choice.number, choice.network_id].join('-');
      } else {
        addr = choice.network_id;
      }
      self.query.route_choices[i] = addr;
      dom_node.parentNode.removeChild(dom_node);
      if (next) {
		next = new Element(next);
        next.setStyle('display', 'block');
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
          result_el.parentNode.removeChild(result_el);
        } else {
          util.log.debug(
			'Unhandled Exception in APP.UI.removeResult: ', e.name,
			e.message);
        }
      }
    },

    clearResults: function(event) {
	  self.stopEvent(event);
      if (!confirm('Remove all of your results and clear the map?')) {
        return;
      }
	  var results = self.results;
	  var service_results, result;
	  for (var service in results) {
		service_results = results[service];
		for (var i = 0; i < service_results.length; ++i) {
		  result = service_results[i];
		  result.remove();
		}
	  }
    },

    reverseDirections: function(s, e) {
      self.s_el.set('value', s);
      self.e_el.set('value', e);
      new self.RouteQuery(self.route_form).run();
    },


    /* Map *******************************************************************/

    identifyIntersectionAtCenter: function(event) {
      var center = self.map.getCenter();
      self.q_el.set('value', self.map.getCenterString());
      self.identifyIntersection(center, event);
    },

    handleMapClick: function(point, event) {
	  //
    },

    identifyIntersection: function(point, event) {
      self.runGeocodeQuery(event, {q: [point.x, point.y].join(',')});
    }
  };
}());
