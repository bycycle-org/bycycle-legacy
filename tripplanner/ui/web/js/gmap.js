/* This module contains variables and functions relating to the Google Map. */


var map;

// Burnside Bridge and Willamette River
var default_x = -122.667847;
var default_y = 45.523127;

// Milwaukee
default_x = -87.906418;
default_y = 43.038783;

var tl = {'x': -88.069888, 'y': 42.842059};
var br = {'x': -87.828241, 'y': 43.192647};
var milwaukee_box = [tl, {'x': br.x, 'y': tl.y}, br, {'x': tl.x, 'y': br.y}, tl];

var default_zoom_level = 3;
var linestring;
var center_marker;
var center_point;

// Start and end markers for routes
var base_icon;
var start_icon;
var end_icon


function gmap__init__()
{
	if (GBrowserIsCompatible()) {
		_setIH("map", '<div id="loading">Loading<blink>...</blink></div>');
		if (_noActiveX()) {
			_setIH("map",
			       '<p>ActiveX is not enabled in your browser. \
                                If your browser is Internet Explorer, \
                                you must have ActiveX enabled to use this application.</p>');
		} else {
			_createMap();
		}
		_setElStyle('loading', 'display', 'none');
	} else {
		_setIH('map',
		       '<p style="margin:10px;">\
		       Your browser doesn\'t seem to meet the requirements for using this application. \
		       The following browsers are currently supported and are all free to download \
                       (<a href="http://www.mozilla.org/products/firefox/">Firefox</a> is an excellent choice):<br/>\
		       <ul>\
		       <li><a href="http://www.microsoft.com/windows/ie/downloads/default.asp">IE</a> 5.5+ (Windows)</li>\
		       <li><a href="http://www.mozilla.com/">Firefox</a> 0.8+ (Windows, Mac, Linux)</li>\
		       <li><a href="http://www.apple.com/safari/download/">Safari</a> 1.2.4+ (Mac)</li>\
		       <li><a href="http://channels.netscape.com/ns/browsers/download.jsp">Netscape</a> 7.1+ (Windows, Mac, Linux)</li>\
		       <li><a href="http://www.mozilla.org/products/mozilla1.x/">Mozilla</a> 1.4+ (Windows, Mac, Linux)</li>\
		       <li><a href="http://www.opera.com/download/">Opera</a> 7.5+ (Windows, Mac, Linux)</li>\
		       </ul>\
		       </p>\
		       <p style="margin:20px;">\
		       We recommend that it not be Internet Explorer.\
		       <br/>\
		       </p>');
	}
}


function _createMap()
{
  map = new GMap(_el("map"));
  map.addControl(new GLargeMapControl());
  map.addControl(new GMapTypeControl());
  map.addControl(new GScaleControl());
  
  var icon = new GIcon();
  icon.image = "images/crosshair4.gif";
  icon.iconSize = new GSize(41, 41);
  icon.iconAnchor = new GPoint(21, 21);
  
  GEvent.addListener(map, "moveend", function() {
		       if (center_marker) { map.removeOverlay(center_marker); }
		       center_point = map.getCenterLatLng();
		       center_point.x = Math.round(center_point.x * 1000000) / 1000000;
		       center_point.y = Math.round(center_point.y * 1000000) / 1000000;
		       center_marker = placeMarkers([center_point], [icon])[0];
		       // TODO: Figure out how to register this listener just once
		       GEvent.addListener(center_marker, "click", function() {
					    var html = '<div style="width: 200px;">' + center_point.x + ', ' + center_point.y + '<br/>' +
					      '    <a href="javascript:void(0);" ' +
					      '       onclick="_setElVToMapLonLat(\'q\'); _find(\'search\');">' +
					      '       Find address of closest intersection</a>' + 
					      '</div>';
					    map.openInfoWindowHtml(center_point, html);
					  });
		       //if (network_visible) showBikeThereNetwork()
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

  // Draw box and zoom out to full extent
  var box = getBoxForPoints([tl, br]);
  centerAndZoomToBox(box);
  drawPolyLine(milwaukee_box);
}


function parsePointsFromXml(xml_str)
{
  var xml_dom = GXml.parse(xml_str);
  var xml_points = xml_dom.documentElement.getElementsByTagName("point");
  var points = [];
  for (var i = 0; i < xml_points.length; i++) 
    {
      points.push(new GPoint(parseFloat(xml_points[i].getAttribute("lon")),
			     parseFloat(xml_points[i].getAttribute("lat"))));
    }
  return points;
}


function drawPolyLine(points, color, weight, opacity)
{
	map.addOverlay(new GPolyline(points, color, weight, opacity));
}


function placeMarkers(points, icons)
{
	// Put some markers on the map
	// points -- an array of GPoints
	// icons -- an array of GIcons (optional)
	var markers = []
	for (var i = 0; i < points.length; i++) {
		if (icons) {
			var marker = new GMarker(points[i], icons[i]);
		} else {
			var marker = new GMarker(points[i]);
		}
		markers.push(marker);
		map.addOverlay(marker);
	}
	return markers;
}

function doAddr()
{
	map.centerAndZoom(default_point, default_zoom_level);
	//point = parsePointsFromXml(_el('addr_data').value)[0];
	//map.centerAndZoom(point, 2);
	//placeMarkers([point]);
}


function doTransit()
{
	map.centerAndZoom(default_point, default_zoom_level);
}


function getBoxForPoints(points)
{
	var min_x = 180;
	var max_x = -180;
	var min_y = 90;
	var max_y = -90;
	for (var i = 0; i < points.length; i++) {
		var p = points[i]
		var x = p.x;
		var y = p.y;
		min_x = x < min_x ? x : min_x;
		max_x = x > max_x ? x : max_x;
		min_y = y < min_y ? y : min_y;
		max_y = y > max_y ? y : max_y;
	}
	return new GBounds(min_x, min_y, max_x, max_y);
}


function getCenterOfBox(box)
{
	var x = (box.minX + box.maxX) / 2.0;
	var y = (box.minY + box.maxY) / 2.0;
	return new GPoint(x, y);
}


function getBoxDimensions(box)
{
	return new GSize(box.maxX - box.minX, box.maxY - box.minY);
}


function centerAndZoomToBox(box)
{
	// Center the map at the box's center
	// Zoom such that the box fits in the map
	var center = getCenterOfBox(box);
	var dims = getBoxDimensions(box);

	if (map.spec.getLowestZoomLevel) {
		var zoom_level = map.spec.getLowestZoomLevel(center, dims, map.viewSize);
		map.centerAndZoom(center, zoom_level);
	} else {
		map.centerAndZoom(center, 0);

		var rw = dims.width * 1.05;
		var rh = dims.height * 1.05;

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
	_el('bikeThereToggle').onclick = showBikeThereNetwork;
	_el('bikeThereToggle').innerHTML = "Show Bike Route Network";
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


		_el("bikeThereMsg").innerHTML = "Drawing network. Please wait...";
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
		_el("bikeThereMsg").innerHTML = "";
		_el('bikeThereToggle').style.display = "";
		_el('bikeThereToggle').innerHTML = "Hide Bike Route Network";
	};

	if (map.getZoomLev_el() > 1) map.zoomTo(1);
	_el('bikeThereToggle').style.display = "none";
	_el('bikeThereToggle').onclick = hideBikeThereNetwork;

	if (!network) {
		_el("bikeThereMsg").innerHTML = "Getting network data. Please wait...";
		doXmlHttpReq("GET", "/static/javascript/bikethere.json", processResponse);
	} else {
		processResponse();
	}
}
