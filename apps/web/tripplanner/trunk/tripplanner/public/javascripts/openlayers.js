NameSpace('openlayers', byCycle.Map, {
  description: 'Open Layers Map',
  beforeLoad: function() {
    util.writeScript('/javascripts/OpenLayers/OpenLayers.js');
  },
  isLoadable: function() { return true; }
});


Class(byCycle.Map.openlayers, 'Map', byCycle.Map.base.Map, {
  default_zoom: 5,

  initialize: function(ui, container) {
    this.superclass.initialize.apply(this, arguments);
  },

  createMap: function(container) {
    var opts = {
      theme: null,
      controls: [
        new OpenLayers.Control.MousePosition(),
        new OpenLayers.Control.PanZoomBar({zoomWorldIcon: true}),
        new OpenLayers.Control.LayerSwitcher({'ascending':false}),
        new OpenLayers.Control.Navigation(),
        new OpenLayers.Control.OverviewMap(),
        new OpenLayers.Control.KeyboardDefaults()
      ],
      projection: 'EPSG:2913',
      units: 'feet',
      numZoomLevels: 10,
      maxResolution: 256,
      maxExtent: new OpenLayers.Bounds(7435781, 447887, 7904954, 877395)
    };

    var map = new OpenLayers.Map(container.attr('id'), opts);

    var tile_urls = [
      'http://tilea.trimet.org/tilecache/tilecache.py?',
      'http://tileb.trimet.org/tilecache/tilecache.py?',
      'http://tilec.trimet.org/tilecache/tilecache.py?',
      'http://tiled.trimet.org/tilecache/tilecache.py?'
    ];
    var map_layer = new OpenLayers.Layer.WMS(
      'Map', tile_urls,
      {layers: 'baseOSPN', format: 'image/png',  EXCEPTIONS: ''},
      {buffer: 0, transitionEffect: 'none'});

    // TODO: need trimet.js
    //var hybrid_layer = new trimet.layer.Hybrid(
      //'Hybrid', tile_urls,
      //{layers: 'h10', format: 'image/jpeg', EXCEPTIONS: ''},
      //{buffer: 0, transitionEffect: 'none'});

    this.marker_layer = new OpenLayers.Layer.Markers('Locations');
    map.addLayers([map_layer, this.marker_layer]);

    // Init
    map.setCenter(new OpenLayers.LonLat(7643672, 683029), 2);

    this.map = map;
  },

  /* Events */

  onUnload: function() {},

  /* Size/Dimensions */

  setSize: function(dims) {
    this.superclass.setSize.call(this, dims);
  },

  setHeight: function(height) {
    this.setSize({w: null, h: height});
  },

  getCenter: function() {
    var c = this.map.getCenter();
    return {x: c.lon, y: c.lat};
  },

  getCenterString: function() {
    var c = this.map.getCenter();
    var x = Math.round(c.lon * 1000000) / 1000000;
    var y = Math.round(c.lat * 1000000) / 1000000;
    return [x, y].join(', ');
  },

  setCenter: function(center, zoom) {
    this.map.setCenter(new OpenLayers.LonLat(center.x, center.y), zoom);
  },

  getZoom: function() {
    return this.map.getZoom();
  },

  setZoom: function(zoom) {
    this.map.zoomTo(zoom);
  },

  /* Other */

  openInfoWindowHtml: function(point, html) {},

  closeInfoWindow: function() {},

  showMapBlowup: function(point) {
    //
  },

  addOverlay: function(overlay) {
    // Select layer based on type of overlay
    this.marker_layer.addMarker(overlay);
  },

  removeOverlay: function(overlay) {
    //
  },

  drawPolyLine: function(points, color, weight, opacity) {
    var line = new OpenLayers(points, color, weight, opacity);
    this.route_layer.addOverlay(line);
    return line;
  },

  placeMarker: function(point, icon) {
    var marker = new OpenLayers.Marker(
      new OpenLayers.LonLat(point.x, point.y));
    this.marker_layer.addMarker(marker);
    return marker;
  },

  placeGeocodeMarker: function(point, node, zoom, icon) {
    zoom = (typeof(zoom) != 'undefined' ? zoom : this.map.getZoom());
    this.setCenter(point, zoom);
    var marker = this.placeMarker(point, icon);
    var coord = new OpenLayers.LonLat(point.x, point.y);
    var self = this;
    //GEvent.addListener(marker, "click", function() {
      //self.map.openInfoWindow(g_lat_lng, node);
    //});
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
    var bounds = {
      sw: {x: xs[0], y: ys[0]},
      ne: {x: xs.pop(), y: ys.pop()}
    };
    return bounds;
  },

  /**
   * @param bounds A set of points representing a bounding box (sw, ne)
   * @return Center of bounding box {x: x, y: y}
   */
  getCenterOfBounds: function(bounds) {
    var sw = bounds.sw;
    var ne = bounds.ne;
    return {x: (sw.x + ne.x) / 2.0, y: (sw.y + ne.y) / 2.0};
  },

  centerAndZoomToBounds: function(bounds, center) {},

  showGeocode: function(geocode) {

  },

  makeBounds: function(bounds) {},

  makePoint: function(point) {
    return point;
  }
});
