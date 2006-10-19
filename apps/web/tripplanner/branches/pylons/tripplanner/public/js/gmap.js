/**
 * Implements the byCycle Map interface for a Google Map.
 */


// Register this map type in the byCycle Map namespace
byCycle.Map.google = {

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
      'dev.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQSskL_eAzZotWlegWekqLPLda0sxQZNf0_IshFell3z8qP8s0Car117A',
      'dev.bycycle.org:5000': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhTkxokDJkt52pLJLqHCpDW3lL7iXBTREVLn9gCRhMUesO754WIidhTq2g',
      'www.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ9bMyOoze7XFWIje4XR3o1o-U-cBTwScNT8SYtwSl70gt4wHCO-23Y3g'
    }
    var api_key = api_keys[byCycle.domain];
    if (api_key) {
      writeScript(api_url + api_key);
      byCycle.Map.google.api_loaded = true;
      byCycle.logInfo('Google Maps API Loaded');
    } else {
      byCycle.logDebug('No API key found for ' + byCycle.domain);
    }
  },

  isLoadable: function() {
    var is_loadable = false;
    if (byCycle.Map.google.api_loaded && GBrowserIsCompatible()) {
      is_loadable = true;
    } else {
      byCycle.logInfo('<p style="margin:10px;">Your browser doesn\'t seem to meet the requirements for using this application. The following browsers are currently supported and are all free to download (<a href="http://www.mozilla.com/">Firefox</a> is an excellent choice):</p><ul><li><a href="http://www.microsoft.com/windows/ie/downloads/default.asp">IE</a> 5.5+ (Windows)</li><li><a href="http://www.mozilla.com/">Firefox</a> 0.8+ (Windows, Mac, Linux)</li><li><a href="http://www.apple.com/safari/download/">Safari</a> 1.2.4+ (Mac)</li><li><a href="http://channels.netscape.com/ns/browsers/download.jsp">Netscape</a> 7.1+ (Windows, Mac, Linux)</li><li><a href="http://www.mozilla.org/products/mozilla1.x/">Mozilla</a> 1.4+ (Windows, Mac, Linux)</li><li><a href="http://www.opera.com/download/">Opera</a> 7.5+ (Windows, Mac, Linux)</li></ul>');
    }
    return is_loadable;
  }
};


/**
 * byCycle Google Map Constructor
 *
 * @param parent UI object
 * @param container Widget that contains this map
 */
byCycle.Map.google.Map = function(parent, container) {
  byCycle.Map.Map.call(this, parent, container);
  this.createIcons();
  this.initListeners();
};


/**
 * byCycle Google Map Methods
 */
byCycle.Map.google.Map.prototype = update(new byCycle.Map.Map(), {

  center_marker_html: '<div class="info_win"><p><a href="javascript:void(0);" onclick="byCycle.UI.findAddressAtCenter();">Find address of closest intersection</a></p><p>Set as <a href="javascript:void(0);" onclick="byCycle.UI.s_el = byCycle.UI.map.getCenterString();">From</a> or <a href="javascript:void(0);" onclick="byCycle.UI.s_el = byCycle.UI.map.getCenterString();">To</a> address for route</p></div>',


  /* Initialization */

  createMap: function(container) {
    var map = new GMap2(container);
    //map.addMapType(this.makeMercatorMapType(G_NORMAL_MAP, 'Bike/Map', 18));
    //map.addMapType(this.makeMercatorMapType(G_SATELLITE_MAP, 'Bike/Sat', 20));
    map.setCenter(new GLatLng(0, 0), 7);
    map.addControl(new GLargeMapControl());
    map.addControl(new GMapTypeControl());
    map.addControl(new GScaleControl());
    map.addControl(new GOverviewMapControl());
    // Change default styling of map overview so it sits flush in the corner
    var style = $('map_overview').firstChild.firstChild.style;
    style.top = '8px';
    style.left = '7px';
    //style.borderTop = style.borderBottom;
    // Add keyboard navigation
    new GKeyboardHandler(map);
    this.map = map;
  },

  createIcons: function() {
    // Center icon
    var center_icon = new GIcon();
    center_icon.image = '/images/reddot15.png';
    center_icon.iconSize = new GSize(15, 15);
    center_icon.iconAnchor = new GPoint(7, 7);
    // Base icon for start and end of route icons
    var base_icon = new GIcon();
    base_icon.shadow = '/images/shadow50.png';
    base_icon.iconSize = new GSize(20, 34);
    base_icon.shadowSize = new GSize(37, 34);
    base_icon.iconAnchor = new GPoint(9, 34);
    base_icon.infoWindowAnchor = new GPoint(9, 2);
    base_icon.infoShadowAnchor = new GPoint(18, 25);
    // Start icon
    var start_icon = new GIcon(base_icon);
    start_icon.image = '/images/dd-start.png';
    // End icon
    var end_icon = new GIcon(base_icon);
    end_icon.image = '/images/dd-end.png';
    // Assign icons to self
    this.center_icon = center_icon;
    this.start_icon = start_icon;
    this.end_icon = end_icon;
  },

  initListeners: function() {
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


  /* Events */

  addListener: function(obj, signal, func) {
    GEvent.addListener(obj, signal, func);
  },

  unload: function() {
    GUnload();
  },


  /* Size/Dimensions */

  setSize: function(dims) {
    this.base.setSize.call(this, dims);
    this.map.checkResize();
    this.map.setCenter(this.map.getCenter());
  },

  setHeight: function(height) {
    this.setSize({w: undefined, h: height})
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

  placeMarker: function(point, icon) {
    var marker = new GMarker(point, icon);
    this.map.addOverlay(marker);
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

  makeRegionMarker: function(region) {
    var icon = new GIcon();
    icon.image = '/images/x.png';
    icon.iconSize = new GSize(17, 19);
    icon.iconAnchor = new GPoint(9, 10);
    icon.infoWindowAnchor = new GPoint(9, 10);
    icon.infoShadowAnchor = new GPoint(9, 10);
    var marker = this.placeMarker(region.center, icon);
    var self = this;
    GEvent.addListener(marker, 'click', function() {
      // TODO: Get active params and send those too
      window.location = region.id + '?map_type=google';
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
    this.parent.setResult(html);
      });
    }
    this.map.setCenter(new GLatLng(geocode.y, geocode.x), 14);
    self.map.openInfoWindowHtml(point, html);
  },



  /**
   * Factory for creating Mercator map types (or at least it will be; right
   * now it's Metro-specific).
   */
  makeMercatorMapType: function(base_type, name, zoom_levels) {
    var domain = 'mica.metro-region.org';
    var transparent_png = 'http://' + domain +
    '/bycycle/images/transparent.png';
    var copyrights = new GCopyrightCollection("&copy; Metro");
    var wms_url = 'http://' + domain +
    '/cgi-bin/mapserv-postgis?map=/var/www/html/bycycle/bycycle.map&';
    var layers = 'pirate_network,county_lines';
    var tile_size = 256;
    var tile_size_less_one = tile_size - 1;
    var img_format = 'image/png';
    var srs = "EPSG:4326";
    var se, nw;
    var min_zoom = 9;
    var url = [wms_url,
           "SERVICE=WMS",
           "&VERSION=1.1.1",
           "&REQUEST=GetMap",
           "&LAYERS=", layers,
           "&STYLES=",
           "&FORMAT=", img_format,
           "&BGCOLOR=0xFFFFFF",
           "&TRANSPARENT=TRUE",
           "&SRS=", srs,
           "&WIDTH=", tile_size,
           "&HEIGHT=", tile_size].join('');

    var pdx_bounds = byCycle.regions.portlandor.bounds;
    var pdx_sw = pdx_bounds.sw;
    var pdx_ne = pdx_bounds.ne;
    var bounds = new GLatLngBounds(new GLatLng(pdx_sw.y, pdx_sw.x),
                   new GLatLng(pdx_ne.y, pdx_ne.x));

    var projection = new GMercatorProjection(zoom_levels);
    projection.XXXtileCheckRange = function(tile, zoom, tile_size) {
      var x = tile.x * tile_size;
      var y = tile.y * tile_size;
      var sw_point = new GPoint(x, y + tile_size_less_one);
      var ne_point = new GPoint(x + tile_size_less_one, y);
      sw = this.fromPixelToLatLng(sw_point, zoom);
      ne = this.fromPixelToLatLng(ne_point, zoom );
      var tile_bounds = new GLatLngBounds(sw, ne);
      if (tile_bounds.intersects(bounds)) {
        return true;
      } else {
        return false;
      }
    };

    var layer = new GTileLayer(copyrights, 0, zoom_levels - 1);
    layer.getTileUrl = function(tile, zoom) {
      projection.XXXtileCheckRange(tile, zoom, tile_size);
      if (zoom < min_zoom) {
        var tile_url = transparent_png;
      } else {
        var bbox = [sw.lng(), sw.lat(), ne.lng(), ne.lat()].join(',');
        var tile_url = [url, "&BBOX=", bbox].join('');
      }
      return tile_url;
    };

    layer.isPng = function() {
      return true;
    };

    layer.getOpacity = function() {
      return .625;
    };

    var layers = [base_type.getTileLayers()[0], layer];
    var opts = {errorMessage: 'Here Be Dragons'};
    var map_type = new GMapType(layers, projection, name, opts);

    map_type.onChangeTo = function() {
      if (map.getZoom() < min_zoom) {
    map.setZoom(min_zoom);
      }
      if (!bounds.intersects(map.getBounds())) {
    selectRegion('portlandor');
      }
    };
    return map_type;
  },


  /**
   * Factory for creating the Mercator map types (or at least it will be; right
   * now it's Metro-specific).
   */
  makeMercatorMapTypeOLD: function() {
    var domain = 'mica.metro-region.org';
    var transparent_png = 'http://' + domain +
    '/bycycle/images/transparent.png';
    var copyrights = new GCopyrightCollection("&copy; Metro");
    var wms_url = 'http://' + domain +
    '/cgi-bin/mapserv-postgis?map=/var/www/html/bycycle/bycycle.map&';
    var layers = 'bike';
    var tile_size = 256;
    var tile_size_less_one = tile_size - 1;
    var img_format = 'image/gif';
    var srs = "EPSG:4326";
    var url = [wms_url,
           "SERVICE=WMS",
           "&VERSION=1.1.1",
           "&REQUEST=GetMap",
           "&LAYERS=", layers,
           "&STYLES=",
           "&FORMAT=", img_format,
           "&BGCOLOR=0xFFFFFF",
           "&TRANSPARENT=TRUE",
           "&SRS=", srs,
           "&WIDTH=", tile_size,
           "&HEIGHT=", tile_size].join('');

    var projection = new GMercatorProjection(18);
    var pdx_bounds = byCycle.regions.portlandor.bounds;
    var sw = pdx_bounds.sw;
    var ne = pdx_bounds.ne;
    var bounds = new GLatLngBounds(new GLatLng(sw.y, sw.x),
                   new GLatLng(ne.y, ne.x));

    var metro_layer = new GTileLayer(copyrights, 0, 17);
    metro_layer.getTileUrl = function(tile, zoom) {
      var tile_url;
      if (zoom < 6) {
        tile_url = transparent_png;
      } else {
    var x = tile.x * tile_size;
    var y = tile.y * tile_size;
    var sw_point = new GPoint(x, y + tile_size_less_one);
    var ne_point = new GPoint(x + tile_size_less_one, y);
    var sw = projection.fromPixelToLatLng(sw_point, zoom);
    var ne = projection.fromPixelToLatLng(ne_point, zoom );
    var tile_bounds = new GLatLngBounds(sw, ne);
    if (tile_bounds.intersects(bounds)) {
      var bbox = [sw.x, sw.y, ne.x, ne.y].join(',');
      tile_url = [url, "&BBOX=", bbox].join('');
    } else {
      tile_url = transparent_png;
    }
      }
      byCycle.logDebug(tile_url);
      return tile_url;
    };

    metro_layer.isPng = function() {
      return true;
    };

    metro_layer.getOpacity = function() {
      return .5;
    };

    var layers = [G_NORMAL_MAP.getTileLayers()[0], metro_layer];
    var name = 'Bike Map';
    var opts = {errorMessage: 'Here Be Dragons'};
    var metro_map = new GMapType(layers, projection, name, opts);
    return metro_map;
  }
});


var x = function() {
  // was nb
  fromPixelToLatLng = function(pixel, zoom, unbounded) {
    // if zoom = 0; then e = (128, 128)
    // bd is just a list of points with x = y = 128, 256, 512, 1024, 2^n/2
    // Or... it's half the size of a tile for the given zoom level
    // Take what will fit into a tile of size n and then shrink the tile down
    // to 256x256
    var e = this.bd[zoom];

    // Move right half tile; divide the result by px/deg at this zoom level
    // Result is longitude
    var lng = (pixel.x - e.x) / this.dd[zoom];

    // Move up a half tile; div result by px/radian
    // Result is ???
    var g = (pixel.y - e.y) / -this.ed[zoom];
    var h = rad2deg(2*Math.atan(Math.exp(g))-Math.PI/2);
    return new B(h, lng, c);
  };
};
