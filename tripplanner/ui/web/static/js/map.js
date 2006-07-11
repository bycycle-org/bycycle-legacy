/**
 * byCycle.Map namespace 
 */
byCycle.Map = {
  // Mapping of map type to map object
  Base: {},

  mapPreload: function() {
    // pass
  },

  mapIsLoadable: function() {
    return false;
  },
};


/**
 * Base byCycle Map widget
 */
byCycle.Map.Map = function (parent, container) {
  this.parent = parent;
  this.container = container;
}


byCycle.Map.Base.Map = byCycle.Map.Map;



byCycle.Map.Map.prototype = {


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
  },


  setHeight: function(height) {
    this.container.style.height = height + 'px';
  },


  unload: function() {},


  getCenter: function() {
    return {x: 0, y: 0};
  },


  setCenter: function(center, zoom) {},


  openInfoWindowHtml: function(point, html) {},


  closeInfoWindow: function() {},


  showMapBlowup: function(point) {
    this.map.showMapBlowup(point);
  },


  addOverlay: function(overlay) {},


  removeOverlay: function(overlay) {},


  drawPolyLine: function(points, color, weight, opacity) {},


  placeMarker: function(point, icon) {},

  /**
   * Put some markers on the map
   * @param points An array of points
   * @param icons An array of icons (optional)
   */
  placeMarkers: function(points, icons) {},


  getBoundsForPoints: function(points) {},


  /**
   * @param bounds A set of point representing a bounding box
   * @return Center of bounding box
   */
  getCenterOfBounds: function(bounds) {
    var sw = bounds.sw;
    var ne = bounds.ne;
    return {x: (sw.x + ne.x) / 2.0, y: (sw.y + ne.y) / 2.0};
  },


  centerAndZoomToBounds: function(bounds, center) {},


  showGeocode: function(geocode) {},


  makeBounds: function(bounds) {}
};
