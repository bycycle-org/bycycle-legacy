// Add custom map type
function addMapType() {
  // Create a copyright for the charts
  var copyCollection = new GCopyrightCollection();
  var copyright = new GCopyright(1,
                 new GLatLngBounds(new GLatLng(-90, -180),
                           new GLatLng(90, 180)),
                 0,
                 "&copy;2006 byCycle.org");
  copyCollection.addCopyright(copyright);


  // Single layer custom chart map
  var tilelayer = new GTileLayer(copyCollection, 0, 18);

  tilelayer.getTileUrl = function(a,b) {
    var url = "http://terraserver-usa.com/tile.ashx?T=1&S=10&X=2903&Y=22523&Z=18";
    return url;
  };

  var layers = [tilelayer];

  // Create the GMapType
  var custommap = new GMapType(layers,
                               new GMercatorProjection(12),
                               "Test",
                               {errorMessage: "No data"});

  // Add the custom map type to the map and set it as the default
  map.addMapType(custommap);
}
