/**
 * byCycle.Map namespace
 */
byCycle.Map = {
  // Mapping of map type to map object
  base: {
    description: 'Default byCycle map type',
    beforeLoad: function() {},
    isLoadable: function() {
      return true;
    }
  }
  // Other map types will be registered on load
};


/**
 * Base byCycle Map widget
 */
byCycle.Map.Map = function (parent, container) {
  if (typeof(parent) == 'undefined') {
    return;
  }
  this.parent = parent;
  this.container = container;
  this.createMap(container);
};


byCycle.Map.base.Map = byCycle.Map.Map;


byCycle.Map.Map.prototype = {

  createMap: function(container) {
    var map = document.createElement('div');
    map.style.overflow = 'auto';
    map.style.padding = '5px';
    Element.update(container, '');
    container.appendChild(map);
    Element.update(map, 'Default byCycle Map Interface');
    this.map = map;
  },

  put: function(content) {
    this.map.appendChild(Builder.node('div', content));
  },
  
  clear: function() {
    this.map.innerHTML = '';
  },

  setSize: function(dims) {
    if (typeof(dims.w) != 'undefined') {
      this.container.style.width = dims.w + 'px';
    }
    if (typeof(dims.h) != 'undefined') {
      this.container.style.height = dims.h + 'px';
    }
  },

  setWidth: function(width) {
    this.container.style.width = width + 'px';
  },

  setHeight: function(height) {
    this.container.style.height = height + 'px';
  },

  unload: function() {
    document.body.innerHTML = 'Bye.';
  },

  getCenter: function() {
    return {x: 0, y: 0};
  },

  setCenter: function(center, zoom) {
    this.put(['Set Center: ', center.y, ', ', center.x, 
              (zoom ? ' Zoom: ' + zoom : '')].join(''));
  },

  setZoom: function(zoom) {
    this.map.innerHTML += ('<br/>New zoom level: ' + zoom);
  },

  openInfoWindowHtml: function(point, html) {},

  closeInfoWindow: function() {},

  showMapBlowup: function(point) {
    alert('Map blowup: ' + point);
  },

  addOverlay: function(overlay) {
    var content = 'Added Overlay: ' + overlay.toString();
    this.put(content);
  },

  removeOverlay: function(overlay) {
    var content = 'Removed Overlay: ' + overlay.toString();
    this.put(content);
  },

  drawPolyLine: function(points, color, weight, opacity) {
    var line = {
      type: 'PolyLine', 
      toString: function() {
        return this.type;
      }
    };
    this.addOverlay(line);
    return line;  
  },

  placeMarker: function(point, icon) {
    var marker = {
      type: 'Marker', 
      x: point.x, 
      y: point.y, 
      toString: function() {
        return [this.type, ' at ', this.x, ', ', this.y].join('');
      }
    };
    this.addOverlay(marker);
    return marker;
  },

  /**
   * Put some markers on the map
   * @param points An array of points
   * @param icons An array of icons (optional)
   * @return An array of the markers added
   */
  placeMarkers: function(points, icons) {
    var markers = [];
    var len = points.length;
    for (var i = 0; i < len; ++i) {
      p = points[i];
      var marker = DIV();
      marker.innerHTML = 'Marker: ' + p.x + ', ' + p.y;
      markers.push(marker);
      this.addOverlay(marker);
    }
    return markers;
  },

  makeRegionMarker: function() {
  },


  /* Bounds */

  getBoundsForPoints: function(points) {
    var xs = [];
    var ys = [];
    for (var i = 0; i < points.length; ++i) {
      var p = points[i];
      xs.push(p.x);
      ys.push(p.y);
    }
    var comp = function(a, b) { return a - b; };
    xs.sort(comp);
    ys.sort(comp);
    byCycle.logInfo(xs);
    var bounds = {
      sw: {x: xs[0], y: ys[0]},
      ne: {x: xs.pop(), y: ys.pop()}
    };
    return bounds;
  },

  /**
   * @param bounds A set of points representing a bounding box (sw, ne)
   * @return Center of bounding box
   */
  getCenterOfBounds: function(bounds) {
    var sw = bounds.sw;
    var ne = bounds.ne;
    return {x: (sw.x + ne.x) / 2.0, y: (sw.y + ne.y) / 2.0};
  },

  centerAndZoomToBounds: function(bounds, center) {},


  showGeocode: function(geocode) {
    this.map.innerHTML += ('<br/>x: ' + geocode.x + ', y: ' + geocode.y);
  },

  makeBounds: function(bounds) {},

  makePoint: function(point) {
    return point;
  },

  addListener: function(obj, signal, func) {
    connect(obj, signal, func);
  }
};


byCycle.Map.Map.prototype.base = byCycle.Map.Map.prototype;
