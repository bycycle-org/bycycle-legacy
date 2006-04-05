/* User Interface */

var geocodes;
var center;
var start_ms;


/* Functions */

function doFind(service)
{
  start_ms = new Date().getTime();
  setStatus('Processing. Please wait<blink>...</blink>');

  var el_region = el('region');
  var region = el_region.value;
  var errors = [];

  if (map)
    map.closeInfoWindow();
  
  if (!region) {
    errors.push('Please select a Region</a>');
    el_region.focus();
  }

  if (service == 'geocode') {
    var el_q = el('q');
    var q = cleanString(el_q.value);
    if (!q) {
      errors.push('Please enter an Address');
      if (region)
	el_q.focus();
    }
    var i = q.toLowerCase().indexOf(' to ');
    if (i != -1) {
      setElV('fr', q.substring(0, i));
      setElV('to', q.substring(i+4));
    }
  } else if (service == 'route') {
    var el_fr = el('fr');
    var el_to = el('to');
    var fr = cleanString(el_fr.value);
    var to = cleanString(el_to.value);
    if (!fr) {
      errors.push('Please enter a From address');
      if (region)
	el_fr.focus();
    }
    if (!to) {
      errors.push('Please enter a To address');
      if (fr)
	el_to.focus();
    }
    if (fr && to) {
      var q = ['["', fr, '", "', to, '"]'].join('');
    }
  } else {
    errors.push('Unknown service: ' + service);
  }

  if (errors.length) {
    errors = ['<h2>Errors</h2><ul><li>', errors.join('</li><li>'),
	      '</li></ul>'].join('');
    setStatus('Error. See below for details.', 1);
    setResult(errors);
  } else {
    var url = ['http://', domain, '/',  
	       '?region=', region, 
	       '&q=', escape(q), 
	       '&async=1'].join('');
    //alert(url);
    doXmlHttpReq('GET', url, _callback);
  }
}


/* Callbacks */

/** 
 * Do stuff that's common to all callbacks in here
 */
function _callback(req)
{
  var result_set = {};
  var status = req.status;
  var response_text = req.responseText;
  //alert(response_text);
  if (status < 400)
    {
      if (start_ms)
	{
	  var elapsed = (new Date().getTime() - start_ms) / 1000.0;
	  setStatus(['Done. Took ', elapsed, ' second', 
		     (elapsed == 1.00 ? '' : 's'), '.'].join(''));
	}
      eval("result_set = " + response_text + ";");
      setResult(unescape(result_set.result_set.html));
      eval('_' + result_set.result_set.type + 'Callback')(status, result_set);
    }
  else
    {
      setStatus('Error. See below for details.', 1);
      setResult(response_text);
    }
}

function _geocodeCallback(status, result_set)
{
  geocodes = result_set.result_set.result;
  switch (status)
    {
    case 200: // A-OK, one match
      if (map)
	showGeocode(0, true);
      break;
    case 300:
      break;
    }
}
	
var colors = ['#0000ff', '#00ff00', '#ff0000', 
	      '#00ffff', '#ff00ff', '#ff8800',
	      '#000000', '#ffffff'];	
var color_index = 0;
var colors_len = colors.length;
function _routeCallback(status, result_set)
{
  var route = result_set.result_set.result;
  switch (status) 
    {
    case 200: // A-OK, one match
      if (map) {
	  var linestring = route.linestring;
	  var linestring_len = linestring.length;
	  var last_point_ix = linestring.length - 1;
	  var box = getBoxForPoints(linestring);	
	  var s_e_markers = placeMarkers([linestring[0],
					  linestring[last_point_ix]],
					 [start_icon, end_icon]);
	  var s_mkr = s_e_markers[0];
	  var e_mkr = s_e_markers[1];
	  var e_ord = linestring_len - 1;
	  GEvent.addListener(s_mkr, "click", function() { 
	    map.showMapBlowup(linestring[0]); 
	  });	           
	  GEvent.addListener(e_mkr, "click", function() { 
	    map.showMapBlowup(linestring[e_ord]); 
	  });			
	  centerAndZoomToBox(box);
	  drawPolyLine(linestring, colors[color_index++]);
	  if (color_index == colors_len)
	    color_index = 0;
	}
      break;			 
    case 300: // Multiple matches
      break;
    }
}


/* UI Manipulation */

function setStatus(content, error)
{
  if (error) 
    setElStyle('status', 'color', 'red');
  else 
    setElStyle('status', 'color', 'black');
  setIH('status', content.toString());
}

function setResult(content, error)
{
  if (error) 
    setElStyle('result', 'color', 'red');
  else 
    setElStyle('result', 'color', 'black');
  setIH('result', content.toString());
}

function setRouteField(fr_or_to, value)
{
  eval([fr_or_to, ' = "', value, '";'].join(''));
  setElV(fr_or_to, value);
}


/* Map */

function setElVToMapLonLat(id)
{
  if (!map) 
    return;
  var lon_lat = map.getCenterLatLng();
  var x = Math.round(lon_lat.x * 1000000) / 1000000;
  var y = Math.round(lon_lat.y * 1000000) / 1000000;
  setElV(id, "lon=" + x + ", " + "lat=" + y);
}

function _clearMap()
{  
  if (map) 
    {
      map.clearOverlays();
      for (var reg_key in regions)
	_showRegionOverlays(regions[reg_key], true);
    }
}

function resizeMap() 
{
  var margin = 5;
  var win_height = getWindowHeight();
  var height = win_height - elOffset('map') - margin;
  if (height >= 0)
    {
      el('map').style.height = height + 'px';
      if (map)
	map.onResize();
    }
  height = win_height - elOffset('result') - margin;
  if (height >= 0)
    el('result').style.height =  height + 'px'; 
}

function showGeocode(index, open_info_win)
{
  var geocode = geocodes[index];
  var html = unescape(geocode.html);
  setResult(html);
  if (map) 
    {
      var point = {'x': geocode.x, 'y': geocode.y};
      if (!geocode.marker) {
	geocode.marker = placeMarkers([point])[0];
	GEvent.addListener(geocode.marker, "click", function() {
	  map.openInfoWindowHtml(point, html); 
	});
      }
      if (open_info_win)
	{
	  map.centerAndZoom(point, 3);
	  map.openInfoWindowHtml(point, html);
	}
    }
}


/* Regions */

function selectRegion(region)
{
  if (!region.bounds)
    region = regions[region] || regions.all;

  setStatus(region.subheading);
  document.title = 'byCycle - Bicycle Trip Planner - ' + region.heading;

  if (map)
    {
      _zoomToRegion(region);
      if (region.all)
	{
	  var reg;
	  for (var reg_key in regions)
	    {
	      reg = regions[reg_key];
	      _initRegion(reg);
	      _showRegionOverlays(reg);
	    }
	}
      else
	{
	  _initRegion(region);
	  _showRegionOverlays(region);
	}
    }
}

function _initRegion(region)
{
  var bounds = region.bounds;
  var center = region.center;
  var dimensions = region.dimensions;
  var linestring = region.linestring;

  if (!center)
    {
      center = getCenterOfBox(bounds);
      region.center = center;
    }

  if (!dimensions)
    {
      dimensions = getBoxDimensions(bounds) ;
      region.dimensions = dimensions;
    }      

  if (!linestring)
    {
      var minX = bounds['minX']; var maxY = bounds['maxY'];
      var maxX = bounds['maxX']; var minY = bounds['minY']; 
      var tl = {x: minX, y: maxY};
      var tr = {x: maxX, y: maxY};
      var br = {x: maxX, y: minY};
      var bl = {x: minX, y: minY};
      var linestring = [tl, tr, br, bl, tl];
      region.linestring = linestring;
    }
}

function _zoomToRegion(region)
{
  centerAndZoomToBox(region.bounds, 
		     region.center, 
		     region.dimensions);
}

function _showRegionOverlays(region, use_cached)
{
  if (region.all)
    return;

  var marker = region.marker;
  var line = region.line;
  
  if (!marker)
    {
      icon = new GIcon();
      icon.image = "images/x.png";
      icon.iconSize = new GSize(17, 19);
      icon.iconAnchor = new GPoint(9, 10);
      icon.infoWindowAnchor = new GPoint(9, 10);
      icon.infoShadowAnchor = new GPoint(9, 10);
      region.marker = placeMarker(region.center, icon);
      GEvent.addListener(region.marker, "click", function() { 
			   var id = region.id;
			   var sel = el('region');
			   for (var i = 0; i < sel.length; ++i)
			     {
			       var opt = sel.options[i];
			       if (opt.value == id)
				 {
				   sel.selectedIndex = i;
				   selectRegion(id);
				   break;
				 }
			     }
			 });
    } 
  else if (use_cached)
    {
      map.addOverlay(region.marker);
    }
  
  if (!line)
    region.line = drawPolyLine(region.linestring); 
  else if (use_cached)
    map.addOverlay(region.line);
}

