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
    var superclass = byCycle.Map.openlayers.Map.superclass;
    superclass.initialize.apply(this, arguments);
  },

  createMap: function(container) {
    var opts = {
      theme: null,
      controls: [
        new OpenLayers.Control.PanZoomBar({zoomWorldIcon: true}),
        new OpenLayers.Control.LayerSwitcher({'ascending':false}),
        new OpenLayers.Control.Navigation(),
        new OpenLayers.Control.OverviewMap()
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
    map.addLayers([map_layer]);

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
    this.setSize({w: undefined, h: height});
  },

  getCenter: function() {
    return {x: 0, y: 0};
  },

  getCenterString: function() {
    return '0, 0';
  },

  setCenter: function(center, zoom) {
    //
  },

  getZoom: function() {
    return 1;
  },

  setZoom: function(zoom) {
    //
  },

  /* Other */

  openInfoWindowHtml: function(point, html) {},

  closeInfoWindow: function() {},

  showMapBlowup: function(point) {
    //
  },

  addOverlay: function(overlay) {
    //
  },

  removeOverlay: function(overlay) {
    //
  },

  drawPolyLine: function(points, color, weight, opacity) {
    var line = {};
    return this.addOverlay(line);
  },

  placeMarker: function(point, icon) {
    var marker = {};
    return this.addOverlay(marker);
  },

  placeGeocodeMarker: function(point, node, zoom, icon) {
    var marker = {};
    return this.addOverlay(marker);
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
