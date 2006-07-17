/**
 * Implements the byCycle Map interface for a Google Map. 
 */


// Register this map type in the byCycle Map namespace
byCycle.Map.Google = {
  
/**
 * Do map initialization that needs to happen before page is done loading.
 * For example, for Google Maps, the API init script needs to be loaded 
 * inline because it does a document.write to load the actual API.
 */
  mapPreload: function() {
    var api_url = 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=';
    var api_keys = {
      'tripplanner.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ8y5tnWrQRsyOlME1eHkOS3wQveBSeFCpOUAfP10H6ec-HcFWPgiJOCA',
      'dev.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQSskL_eAzZotWlegWekqLPLda0sxQZNf0_IshFell3z8qP8s0Car117A',
      'www.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ9bMyOoze7XFWIje4XR3o1o-U-cBTwScNT8SYtwSl70gt4wHCO-23Y3g'
    }
    var api_key = api_keys[byCycle.domain];
    if (api_key) {
      $('map_msg').innerHTML = 'Loading map<blink>...</blink>';
      writeScript(api_url + api_key);
      byCycle.Map.Google.api_loaded = true;
      byCycle.logInfo('Google Maps API Loaded');
    } else {
      byCycle.logDebug('No API key found for ' + byCycle.domain);
    }
  },
  
  mapIsLoadable: function() {
    var is_loadable = false;
    if (byCycle.Map.Google.api_loaded && GBrowserIsCompatible()) {
      is_loadable = true;
    } else {
      byCycle.logInfo('<p style="margin:10px;">Your browser doesn\'t seem to meet the requirements for using this application. The following browsers are currently supported and are all free to download (<a href="http://www.mozilla.com/">Firefox</a> is an excellent choice):</p><ul><li><a href="http://www.microsoft.com/windows/ie/downloads/default.asp">IE</a> 5.5+ (Windows)</li><li><a href="http://www.mozilla.com/">Firefox</a> 0.8+ (Windows, Mac, Linux)</li><li><a href="http://www.apple.com/safari/download/">Safari</a> 1.2.4+ (Mac)</li><li><a href="http://channels.netscape.com/ns/browsers/download.jsp">Netscape</a> 7.1+ (Windows, Mac, Linux)</li><li><a href="http://www.mozilla.org/products/mozilla1.x/">Mozilla</a> 1.4+ (Windows, Mac, Linux)</li><li><a href="http://www.opera.com/download/">Opera</a> 7.5+ (Windows, Mac, Linux)</li></ul>');
    }
    return is_loadable;
  }
};


/**
 *  byCycle Google Map Class Definition 
 */
byCycle.Map.Google.Map = function(parent, container) {
  byCycle.Map.Map.call(this, parent, container);
  this.createIcons();
  this.addListeners();
};


byCycle.Map.Google.Map.prototype = update(new byCycle.Map.Map(), {

  center_marker_html: '<div class="info_win"><p><a href="javascript:void(0);" onclick="setElVToMapLonLat(\'q\'); doFind(\'geocode\');">Find address of closest intersection</a></p><p>Set as <a href="javascript:void(0);" onclick="setElVToMapLonLat(\'fr\')">From</a> or <a href="javascript:void(0);" onclick="setElVToMapLonLat(\'to\')">To</a> address for route</p></div>',

  createMap: function(container) {
    var map = new GMap2(container);
    map.setCenter(new GLatLng(0, 0), 2);
  
    map.addControl(new GLargeMapControl());
    map.addControl(new GMapTypeControl());
    map.addControl(new GScaleControl());

    map.addControl(new GOverviewMapControl());
    //container.appendChild(document.getElementById('map_overview'));

    this.map = map;
  },

  createIcons: function() {
    // Center icon
    var center_icon = new GIcon();
    center_icon.image = 'images/reddot15.png';
    center_icon.iconSize = new GSize(15, 15);
    center_icon.iconAnchor = new GPoint(7, 7);
    // Base icon for start and end of route icons
    var base_icon = new GIcon();
    base_icon.shadow = 'images/shadow50.png';
    base_icon.iconSize = new GSize(20, 34);
    base_icon.shadowSize = new GSize(37, 34);
    base_icon.iconAnchor = new GPoint(9, 34);
    base_icon.infoWindowAnchor = new GPoint(9, 2);
    base_icon.infoShadowAnchor = new GPoint(18, 25);
    // Start icon
    var start_icon = new GIcon(base_icon);
    start_icon.image = 'images/dd-start.png';
    // End icon
    var end_icon = new GIcon(base_icon);
    end_icon.image = 'images/dd-end.png';
    // Assign icons to self
    this.center_icon = center_icon;
    this.start_icon = start_icon;
    this.end_icon = end_icon;
  },

  addListeners: function() {
    var self = this;
    GEvent.addListener(self.map, 'moveend', function() {
      self.center = self.map.getCenter();
      if (typeof(self.center_marker) == 'undefined') {
	self.center_marker = new GMarker(self.center, self.center_icon);
	self.map.addOverlay(self.center_marker);
	GEvent.addListener(self.center_marker, 'click', function() {
	  self.map.openInfoWindowHtml(self.center, self.center_marker_html);
	});
      }
      self.center_marker.setPoint(self.center);
    });
    GEvent.addListener(self.map, 'click', function() {
      self.map.closeInfoWindow();
    });
  },

  setSize: function(width, height) {
    if (!(width || height)) {
      return;
    }
    if (width) {
      this.container.style.width = width + 'px';
    }
    if (height) {
      this.container.style.height = height + 'px';
    }
    this.map.checkResize();
    this.map.setCenter(this.map.getCenter());
  },

  setHeight: function(height) {
    this.container.style.height = height + 'px';
    this.map.checkResize();
    this.map.setCenter(this.map.getCenter());
  },

  unload: function() {
    GUnload();
  },

  getCenter: function() {
    return this.map.getCenter();
  },

  setCenter: function(center, zoom) {
    if (zoom) {
      this.map.setCenter(new GLatLng(center.y, center.x), zoom);
    } else {
      this.map.setCenter(new GLatLng(center.y, center.x));
    }
  },

  openInfoWindowHtml: function(point, html) {
    this.map.openInfoWindowHtml(point, html);
  },

  closeInfoWindow: function() {
    this.map.closeInfoWindow();
  },

  showMapBlowup: function(point) {
    this.map.showMapBlowup(point);
  },

  addOverlay: function(overlay) {
    this.map.addOverlay(overlay);
  },

  removeOverlay: function(overlay) {
    this.map.removeOverlay(overlay);
  },

  drawPolyLine: function(points, color, weight, 
			 opacity) {
    var line = new GPolyline(points, color, weight, opacity);
    this.map.addOverlay(line);
    return line;
  },

  placeMarker: function(point, icon) {
    var marker = new GMarker(point, icon);
    this.map.addOverlay(marker);
    return marker;
  },

  /**
   * Put some markers on the map
   * @param points An array of GPoints
   * @param icons An array of GIcons (optional)
   */
  placeMarkers: function(points, icons) {
    var markers = [];
    var len = points.length;
    if (icons) {
      for (var i = 0; i < len; ++i) {
	var marker = new GMarker(points[i], icons[i]);
	markers.push(marker);
	this.map.addOverlay(marker);
      }
    } else {
      for (var i = 0; i < len; ++i) {
	var marker = new GMarker(points[i]);
	markers.push(marker);
	this.map.addOverlay(marker);
      }
    }
    return markers;
  },

  getBoundsForPoints: function(points) {
    var min_x = 180;
    var max_x = -180;
    var min_y = 90;
    var max_y = -90;
    for (var i = 0; i < points.length; i++) {
      var p = points[i];
      var x = p.x;
      var y = p.y;
      min_x = x < min_x ? x : min_x;
      max_x = x > max_x ? x : max_x;
      min_y = y < min_y ? y : min_y;
      max_y = y > max_y ? y : max_y;
    }
    return new GLatLngBounds(new GLatLng(min_y, min_x),
			     new GLatLng(max_y, max_x));
  },

  /**
   * @param bounds A set of point representing a bounding box (GBounds)
   * @return GLatLng at center of bounding box
   */
  getCenterOfBounds: function(bounds) {    
    var center = byCycle.Map.Map.prototype.getCenterOfBounds.call(this, 
								  bounds);
    return new GLatLng(center.y, center.x);
  },

  centerAndZoomToBounds: function(bounds, center) {
    var center = center || this.getCenterOfBounds(bounds);
    this.map.setCenter(center, this.map.getBoundsZoomLevel(bounds.bounds));
  },

  showGeocode: function(geocode) {
    var self = this;
    var point = new GLatLng(geocode.y, geocode.x);
    var html = geocode.html;
    if (typeof(geocode.marker) == 'undefined') {
      geocode.marker = map.placeMarkers([point])[0];
      GEvent.addListener(geocode.marker, "click", function() {
	self.map.openInfoWindowHtml(point, html);
	setResult(html);
      });
    }
    this.map.setCenter(point, 14);
    this.map.openInfoWindowHtml(point, html);
  },

  makeBounds: function(bounds) {
    var sw = bounds.sw;
    var ne = bounds.ne;
    return new GLatLngBounds(new GLatLng(sw.y, sw.x), new GLatLng(ne.y, ne.x));
  }
});
