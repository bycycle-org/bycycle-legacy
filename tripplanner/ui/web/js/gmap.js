/**
 * This module contains variables and functions relating to the Google Map. It 
 * should be considered an extension of the ui module.
 */


var map;
var center_marker;
var center_point;
var center_marker_html = '<div style="width:225px; text-align:center;"><a href="javascript:void(0);" onclick="_setElVToMapLonLat(\'q\'); doFind();">Find address of closest intersection</a></div>';

// Start and end markers for routes
var base_icon;
var start_icon;
var end_icon;


function mapLoad()
{
  var bRet = false;
  if (GBrowserIsCompatible()) 
    {
      el('map').innerHTML = 
	'<div id="loading">Loading<blink>...</blink></div>';
      if (_noActiveX()) 
	{
	  _setIH("map",
		 '<p>ActiveX is not enabled in your browser. \
                                If your browser is Internet Explorer,	\
                                you must have ActiveX enabled to use this application.</p>');
	} 
      else 
	{
	  mapCreate();
	  bRet = true;
	}
      _setElStyle('loading', 'display', 'none');
    } 
  else 
    {
      el('map').innerHTML = 
	'<p style="margin:10px;">\
	         Your browser doesn\'t seem to meet the requirements for using this application. The following browsers are currently supported and are all free to download (<a href="http://www.mozilla.com/">Firefox</a> is an excellent choice):</p> \
               <ul> \
	         <li><a href="http://www.microsoft.com/windows/ie/downloads/default.asp">IE</a> 5.5+ (Windows)</li> \
		 <li><a href="http://www.mozilla.com/">Firefox</a> 0.8+ (Windows, Mac, Linux)</li> \
		 <li><a href="http://www.apple.com/safari/download/">Safari</a> 1.2.4+ (Mac)</li> \
		 <li><a href="http://channels.netscape.com/ns/browsers/download.jsp">Netscape</a> 7.1+ (Windows, Mac, Linux)</li> \
		 <li><a href="http://www.mozilla.org/products/mozilla1.x/">Mozilla</a> 1.4+ (Windows, Mac, Linux)</li> \
		 <li><a href="http://www.opera.com/download/">Opera</a> 7.5+ (Windows, Mac, Linux)</li> \
	       </ul>';
    }
  return bRet;
}


function mapCreate()
{
  map = new GMap(el("map"));
  map.addControl(new GLargeMapControl());
  map.addControl(new GMapTypeControl());
  map.addControl(new GScaleControl());
  
  var icon = new GIcon();
  icon.image = "images/reddot15.png";
  icon.iconSize = new GSize(15, 15);
  icon.iconAnchor = new GPoint(7, 7);

  GEvent.addListener(map, "moveend", function() {
                       if (center_marker)
			 map.removeOverlay(center_marker);
                       var center = map.getCenterLatLng();
                       center.x = Math.round(center.x * 1000000) /
			 1000000;
                       center.y = Math.round(center.y * 1000000) /
			 1000000;
                       center_marker = new GMarker(center, icon);
                       map.addOverlay(center_marker);
		       GEvent.clearListeners(center_marker, "click");
		       GEvent.addListener(center_marker, "click", function() {
					    map.openInfoWindowHtml(center,
								   center_marker_html);
					  });
                     });
  
  base_icon = new GIcon();
  base_icon.shadow = "images/shadow50.png";
  base_icon.iconSize = new GSize(20, 34);
  base_icon.shadowSize = new GSize(37, 34);
  base_icon.iconAnchor = new GPoint(9, 34);
  base_icon.infoWindowAnchor = new GPoint(9, 2);
  base_icon.infoShadowAnchor = new GPoint(18, 25);
  start_icon = new GIcon(base_icon);
  start_icon.image = "images/dd-start.png";
  end_icon = new GIcon(base_icon);
  end_icon.image = "images/dd-end.png";
  var reg_el = el('region');
  selectRegion(reg_el[reg_el.selectedIndex].value);
}


function drawPolyLine(points, color, weight, opacity)
{
  var line = new GPolyline(points, color, weight, opacity);
  map.addOverlay(line);
  return line;
}


function placeMarker(point, icon)
{
  var marker = new GMarker(point, icon);
  map.addOverlay(marker);
  return marker;
}

/**
 * Put some markers on the map
 * @param points An array of GPoints
 * @param icons An array of GIcons (optional)
 */
function placeMarkers(points, icons)
{
  var markers = [];
  var len = points.length;
  if (icons) 
    {
      for (var i = 0; i < len; ++i) 
	{
	  var marker = new GMarker(points[i], icons[i]);
	  markers.push(marker);
	  map.addOverlay(marker);
	}
    }
  else 
    {
      for (var i = 0; i < len; ++i) 
	{
	  var marker = new GMarker(points[i]);
	  markers.push(marker);
	  map.addOverlay(marker);
	}
    }
  return markers;
}


function getBoxForPoints(points)
{
  var min_x = 180;
  var max_x = -180;
  var min_y = 90;
  var max_y = -90;
  for (var i = 0; i < points.length; i++) 
    {
      var p = points[i];
      var x = p.x;
      var y = p.y;
      min_x = x < min_x ? x : min_x;
      max_x = x > max_x ? x : max_x;
      min_y = y < min_y ? y : min_y;
      max_y = y > max_y ? y : max_y;
    }
  return {'minX': min_x, 'minY': min_y, 'maxX': max_x, 'maxY': max_y};
}


function getCenterOfBox(box)
{
  var x = (box.minX + box.maxX) / 2.0;
  var y = (box.minY + box.maxY) / 2.0;
  return {'x': x, 'y': y};
}


function getBoxDimensions(box)
{
  return {'width': box.maxX - box.minX, 'height': box.maxY - box.minY};
}


function centerAndZoomToBox(box, center, dimensions)
{
  // Center the map at the box's center
  // Zoom such that the box fits in the map
  var cent = center || getCenterOfBox(box);
  var dims = dimensions || getBoxDimensions(box);
  dims.width *= 1.05;
  dims.height *= 1.05;

  if (map.spec.getLowestZoomLevel) {
    var zoom_level = map.spec.getLowestZoomLevel(cent, dims, map.viewSize);
    map.centerAndZoom(cent, zoom_level);
  } else {
    map.centerAndZoom(cent, 0);

    var rw = dims.width;
    var rh = dims.height;

    var wh = map.getSpanLatLng();
    var w = wh.width;
    var h = wh.height;

    var i = 1;
    while (rw > w || rh > h) {
      map.zoomTo(i);
      wh = map.getSpanLatLng();
      w = wh.width;
      h = wh.height;
      if (i == 7) break;
      ++i;
    }
  }
}


function hideBikeThereNetwork()
{
  network_visible = false;
  el('bikeThereToggle').onclick = showBikeThereNetwork;
  el('bikeThereToggle').innerHTML = "Show Bike Route Network";
  map.clearOverlays();
}


var network_visible = false;
var network = false;
function showBikeThereNetwork()
{
  var processResponse = function(req) {
    // Note: this is going to get called AFTER the outer function returns!!!
    var colors = {"mu": "#660099",
		  "bl": "#0000ff",
		  "lt": "#006600",
		  "mt": "#FF9933",
		  "ht": "#FF6600",
		  "ca": "#CC0033"}
    if (!network) { eval("network = " + req.responseText + ";"); }


    el("bikeThereMsg").innerHTML = "Drawing network. Please wait...";
    var modelines;
    var line;
    var color;
    var last_idx;

    // TODO: only draw inside some particular size box, not just whatever size the map happens to be (like inside a square mile centered at map center).
    // function to determine if a point is in bounds
    // function to  draw network

    var bounds = map.getBoundsLatLng();
    minX = bounds.minX;
    maxX = bounds.maxX;
    minY = bounds.minY;
    maxY = bounds.maxY;
    for (var mode in network) {
      modelines = network[mode];
      color = colors[mode];
      for (var i = 0; i < modelines.length; ++i) {
	line = modelines[i];
	last_idx = line.length - 1;
	if (((minX <= line[0].x && line[0].x <= maxX) &&
	     (minY <= line[0].y && line[0].y <= maxY)) ||
	    ((minX <= line[last_idx].x && line[last_idx].x <= maxX) &&
	     (minY <= line[last_idx].y && line[last_idx].y <= maxY))) {
	  map.addOverlay(new GPolyline(line, color, 3, 1));
	}
      }
    }

    network_visible = true;
    el("bikeThereMsg").innerHTML = "";
    el('bikeThereToggle').style.display = "";
    el('bikeThereToggle').innerHTML = "Hide Bike Route Network";
  };

  if (map.getZoomLevel() > 1) map.zoomTo(1);
  el('bikeThereToggle').style.display = "none";
  el('bikeThereToggle').onclick = hideBikeThereNetwork;

  if (!network) {
    el("bikeThereMsg").innerHTML = "Getting network data. Please wait...";
    doXmlHttpReq("GET", "/static/javascript/bikethere.json", processResponse);
  } else {
    processResponse();
  }
}
