byCycle.regions = (function() {
  // sw => minx, miny
  // ne => maxx, maxy
  // Initially set to sw => max_possible, ne => min_possible
  var bounds = {sw: {x: 180, y: 90}, ne: {x: -180, y: -90}};

  var regions = {
    portlandor: {
      bounds: {
        sw: {x: -123.485755, y: 44.885219},
        ne: {x: -121.649618, y: 45.814153}
      }
    },

    milwaukeewi: {
      bounds: {
        sw: {x: -88.069888, y: 42.842059},
        ne: {x: -87.828241, y: 43.192647}
      }
    }
  };

  // Calculate minimum bounds containing all regions
  for (var key in regions) {
    var r = regions[key];
    if (r.bounds.sw.x < bounds.sw.x) {
      bounds.sw.x = r.bounds.sw.x;
    }
    if (r.bounds.sw.y < bounds.sw.y) {
      bounds.sw.y = r.bounds.sw.y;
    }
    if (r.bounds.ne.x > bounds.ne.x) {
      bounds.ne.x = r.bounds.ne.x;
    }
    if (r.bounds.ne.y > bounds.ne.y) {
      bounds.ne.y = r.bounds.ne.y;
    }
  };

  return {
    bounds: bounds,
    regions: regions
  };
})();
