byCycle.regions = function() {
  var getCenterOfBounds = byCycle.Map.base.Map.prototype.getCenterOfBounds;

  // sw => minx, miny
  // ne => maxx, maxy
  // Initially set to sw => max_possible, ne => min_possible
  var bounds_all = {sw: {x: 180, y: 90}, ne: {x: -180, y: -90}};

  var regions = {
    portlandor: {
      key: 'portlandor',
      map_type: 'openlayers',
      units: 'feet',
      srid: 2913,
      bounds: {
        sw: {x: 7435781, y: 447887},
        ne: {x: 7904954, y: 877395},
        degrees: {
          sw: {x: -123.485755, y: 44.885219},
          ne: {x: -121.649618, y: 45.814153}
        }
      }
    },

    milwaukeewi: {
      key: 'milwaukeewi',
      map_type: 'google',
      units: 'degrees',
      srid: 4326,
      bounds: {
        sw: {x: -88.069888, y: 42.842059},
        ne: {x: -87.828241, y: 43.192647},
        degrees: {
          sw: {x: -88.069888, y: 42.842059},
          ne: {x: -87.828241, y: 43.192647}
        }
      }
    }
  };

  // Initialize other region attributes and calculate minimum bounds
  // containing all regions
  var r, bounds, nw, ne, se, sw;
  var region_values = util.values(regions);
  for (var i = 0; i < region_values.length; ++i) {
    // Set attrs on region ``r``
    r = region_values[i];
    bounds = r.bounds;
    ne = bounds.ne;
    sw = bounds.sw;
    nw = {x: sw.x, y: ne.y};
    se = {x: ne.x , y: sw.y};

    r.center = getCenterOfBounds(bounds);
    r.linestring = [nw, ne, se, sw, nw];

    // Do it again for degrees
    bounds = r.bounds.degrees;
    ne = bounds.ne;
    sw = bounds.sw;
    nw = {x: sw.x, y: ne.y};
    se = {x: ne.x , y: sw.y};

    r.center_degrees = getCenterOfBounds(bounds);
    r.linestring_degrees = [nw, ne, se, sw, nw];

    // Adjust all-regions bounds
    if (sw.x < bounds_all.sw.x) { bounds_all.sw.x = sw.x; }
    if (sw.y < bounds_all.sw.y) { bounds_all.sw.y = sw.y; }
    if (ne.x > bounds_all.ne.x) { bounds_all.ne.x = ne.x; }
    if (ne.y > bounds_all.ne.y) { bounds_all.ne.y = ne.y; }
  };

  bounds_all.degrees = bounds_all;
  var all = {
      key: 'all',
      map_type: 'google',
      units: 'degrees',
      srid: 4326,
      bounds: bounds_all,
      center: getCenterOfBounds(bounds_all)
  };

  return {
    all: all,
    regions: regions
  };
}();
