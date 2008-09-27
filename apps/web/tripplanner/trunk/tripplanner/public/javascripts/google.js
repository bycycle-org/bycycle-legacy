/**
 * Implements the byCycle Map interface for a Google Map.
 */
NameSpace('google', byCycle.Map, {
  description: 'Google Map',

  /**
   * Do map initialization that needs to happen before page is done loading.
   * For example, for Google Maps, the API init script needs to be loaded
   * inline because it does a document.write to load the actual API.
   */
  beforeLoad: function() {
    var api_url = 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=';
    var api_keys = {
      'tripplanner.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ8y5tnWrQRsyOlME1eHkOS3wQveBSeFCpOUAfP10H6ec-HcFWPgiJOCA',

      'satellite.bycycle.org:5000':
'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhRY_I4CLwGh95qVWYjrRjsuZNzP3BSOxRXLsVSuuatyFhv0hQfFohQxBQ',

      'prototype.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhTPU6PNPDk7LC31EIff_k4JZWpNmBQshai4v8RM5FaT-4FRWeyJA4VHaQ',

      'bycycle.metro-region.org':
'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhR7upyhxOh7UQa5Yu3ebGZe2uQ8SxRPJtyMUYYgIBQsAROpcOySx6G1RQ',

      'dev.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQSskL_eAzZotWlegWekqLPLda0sxQZNf0_IshFell3z8qP8s0Car117A',

      'dev.bycycle.org:5000': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhTkxokDJkt52pLJLqHCpDW3lL7iXBTREVLn9gCRhMUesO754WIidhTq2g',

      'www.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhR8QNZ8KuqqtskDzJsLddnT1fGweRTgDdVI-oPLr79jrZgA_-87uWVc5w',

      'bycycle.org': 'ABQIAAAAupb-OM5MU-8ZDqS4tVNkBBRa1vtdiGjU4Osv1KyKd6Mlr4BuWxQrO1eNXOimVbjcfI1DiLeH-XnIuw'
    };
    var api_key = api_keys[byCycle.domain];
    if (api_key) {
      util.writeScript(api_url + api_key);
      this.api_loaded = true;
      byCycle.logDebug('Google Maps API Loaded');
    } else {
      byCycle.logDebug('No API key found for ' + byCycle.domain);
    }
  },

  isLoadable: function() {
    var is_loadable = false;
    if (this.api_loaded && GBrowserIsCompatible()) {
      is_loadable = true;
    } else {
      if (!this.api_loaded) {
        byCycle.UI.showErrors('No Google Maps API key found for ' + byCycle.domain);
      }
    }
    return is_loadable;
  }
});


/**
 * byCycle Google Map
 */
Class(byCycle.Map.google, 'Map', byCycle.Map.base.Map, {
  default_zoom: 14,

  initialize: function(ui, container) {
    this.superclass.initialize.apply(this, arguments);
    this.createIcons();
    this.createListeners();
  },

  createMap: function(container) {
    var map = new GMap2(container);
    map.setCenter(new GLatLng(0, 0), 7);
    map.addControl(new GLargeMapControl());
    map.addControl(new GMapTypeControl());
    map.addControl(new GScaleControl());
    map.addControl(new GOverviewMapControl());
    map.enableContinuousZoom();
    map.enableScrollWheelZoom();
    new GKeyboardHandler(map);
    this.map = map;
  },

  createIcons: function() {
    // Center icon
    var center_icon = new GIcon();
    center_icon.image = byCycle.prefix + 'images/reddot15.png';
    center_icon.iconSize = new GSize(15, 15);
    center_icon.iconAnchor = new GPoint(7, 7);
    // Base icon for start and end of route icons
    var base_icon = new GIcon();
    base_icon.shadow = byCycle.prefix + 'images/shadow50.png';
    base_icon.iconSize = new GSize(20, 34);
    base_icon.shadowSize = new GSize(37, 34);
    base_icon.iconAnchor = new GPoint(9, 34);
    base_icon.infoWindowAnchor = new GPoint(9, 2);
    base_icon.infoShadowAnchor = new GPoint(18, 25);
    // Start icon
    var start_icon = new GIcon(base_icon);
    start_icon.image = byCycle.prefix + 'images/dd-start.png';
    // End icon
    var end_icon = new GIcon(base_icon);
    end_icon.image = byCycle.prefix + 'images/dd-end.png';
    // Assign icons to self
    this.center_icon = center_icon;
    this.start_icon = start_icon;
    this.end_icon = end_icon;
  },

  createListeners: function() {
    var self = this;
    GEvent.addListener(self.map, 'moveend', function () {
      self.center = self.map.getCenter();
      if (typeof(self.center_marker) == 'undefined') {
        self.center_marker = new GMarker(self.center, self.center_icon);
        self.map.addOverlay(self.center_marker);
        var cm_node = document.getElementById('center-marker-contents');
        GEvent.addListener(self.center_marker, 'click', function () {
          self.map.openInfoWindow(self.center, cm_node);
        });
      }
      self.center_marker.setPoint(self.center);
    });
    GEvent.addListener(self.map, 'click', function (overlay, point) {
      self.map.closeInfoWindow();
      //if (point) {
        //self.ui.handleMapClick({x: point.lng(), y: point.lat()});
      //}
    });
  },

  /* Events */

  addListener: function(obj, signal, func) {
    GEvent.addListener(obj, signal, func);
  },

  onUnload: function() {
    GUnload();
  },

  /* Size/Dimensions */

  setSize: function(dims) {
    this.superclass.setSize.call(this, dims);
    this.map.checkResize();
    this.map.setCenter(this.map.getCenter());
  },

  setHeight: function(height) {
    this.setSize({w: undefined, h: height});
  },

  getCenter: function() {
    var c = this.map.getCenter();
    return {x: c.lng(), y: c.lat()};
  },

  getCenterString: function() {
    var c = this.map.getCenter();
    var x = Math.round(c.lng() * 1000000) / 1000000;
    var y = Math.round(c.lat() * 1000000) / 1000000;
    return "longitude=" + x + ", " + "latitude=" + y;
  },

  setCenter: function(center, zoom) {
    if (typeof(zoom) == 'undefined') {
      this.map.setCenter(new GLatLng(center.y, center.x));
    } else {
      this.map.setCenter(new GLatLng(center.y, center.x), zoom);
    }
  },

  getZoom: function() {
    return this.map.getZoom();
  },

  setZoom: function(zoom) {
    this.map.setZoom(zoom);
  },


  /* Overlays */

  addOverlay: function(overlay) {
    this.map.addOverlay(overlay);
  },

  removeOverlay: function(overlay) {
    this.map.removeOverlay(overlay);
  },

  drawPolyLine: function(points, color, weight, opacity) {
    var line = new GPolyline(points, color, weight, opacity);
    this.map.addOverlay(line);
    return line;
  },

  drawPolyLineFromEncodedPoints: function (points, levels, color, weight,
                                           opacity) {
    var line = new GPolyline.fromEncoded({
      points: points,
      levels: levels,
      color: color,
      weight: weight,
      opacity: opacity,
      zoomFactor: 32,
      numLevels: 4
    });
    this.map.addOverlay(line);
    return line;
  },

  placeMarker: function(point, icon) {
    var marker = new GMarker(new GLatLng(point.y, point.x), icon);
    this.map.addOverlay(marker);
    return marker;
  },

  placeGeocodeMarker: function(point, node, zoom, icon) {
    zoom = (typeof(zoom) != 'undefined' ? zoom : this.map.getZoom());
    this.setCenter(point, zoom);
    var marker = this.placeMarker(point, icon);
    var g_lat_lng = new GLatLng(point.y, point.x);
    var self = this;
    GEvent.addListener(marker, "click", function() {
      self.map.openInfoWindow(g_lat_lng, node);
    });
    return marker;
  },

  placeMarkers: function(points, icons) {
    var markers = [];
    var len = points.length;
    if (icons) {
      for (var i = 0; i < len; ++i) {
        var p = points[i];
        var ll = new GLatLng(p.y, p.x);
        var marker = new GMarker(ll, {icon: icons[i]});
        markers.push(marker);
        this.map.addOverlay(marker);
      }
    } else {
      for (var i = 0; i < len; ++i) {
        var p = points[i];
        var ll = new GLatLng(p.y, p.x);
        var marker = new GMarker(ll);
        markers.push(marker);
        this.map.addOverlay(marker);
      }
    }
    return markers;
  },

  makeRegionMarker: function(region_key, center) {
    var icon = new GIcon();
    icon.image = byCycle.prefix + 'images/x.png';
    icon.iconSize = new GSize(17, 19);
    icon.iconAnchor = new GPoint(9, 10);
    icon.infoWindowAnchor = new GPoint(9, 10);
    icon.infoShadowAnchor = new GPoint(9, 10);
    var marker = this.placeMarker(center, icon);
    var self = this;
    GEvent.addListener(marker, 'click', function() {
      var location = [byCycle.prefix, 'regions/', region_key];
      if (byCycle.query_string) {
        location.push('?', byCycle.query_string);
      }
      window.location = location.join('');
    });
    return marker;
  },

  clear: function() {
    this.map.clearOverlays();
    this.initListeners();
  },

  /* Bounds */

  centerAndZoomToBounds: function(bounds, center) {
    center = center || this.getCenterOfBounds(bounds);
    center = new GLatLng(center.y, center.x);
    var sw = bounds.sw;
    var ne = bounds.ne;
    var gbounds = new GLatLngBounds(new GLatLng(sw.y, sw.x),
                                    new GLatLng(ne.y, ne.x));
    this.map.setCenter(center, this.map.getBoundsZoomLevel(gbounds));
  },

  /* Info Window */

  openInfoWindowHtml: function(point, html) {
    this.map.openInfoWindowHtml(new GLatLng(point.y, point.x), html);
  },

  closeInfoWindow: function() {
    this.map.closeInfoWindow();
  },

  showMapBlowup: function(point) {
    this.map.showMapBlowup(new GLatLng(point.y, point.x));
  },

  showGeocode: function(geocode) {
    var self = this;
    var point = new GLatLng(geocode.y, geocode.x);
    var html = geocode.html;
    if (!geocode.marker) {
      geocode.marker = this.placeMarker(point);
      GEvent.addListener(geocode.marker, 'click', function() {
    self.map.openInfoWindowHtml(point, html);
    this.ui.setResult(html);
      });
    }
    this.map.setCenter(new GLatLng(geocode.y, geocode.x), 14);
    self.map.openInfoWindowHtml(point, html);
  }
});
