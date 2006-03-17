/* User Interface */


/* Data dictionary */

// User data
var q;
var fr;
var to;

// Result data
var result_set;
var geocodes;

// Map data
var center;

var start_ms;


/* Functions */

function doFind()
{
  start_ms = new Date().getTime();
  _setResult('Processing. Please wait<blink>...</blink>');
  
  if (map)
    map.closeInfoWindow();

  var el_region = el('region');
  var region = el_region.value;
  var el_q = el('q');
  var q = _trim(el_q.value, true);
  var errors = [];
  
  if (!q)
    {
      errors.push('Missing address or route <a href="javascript:void(0);" onclick="el(\'q\').focus();"><i>query</i></a>');
      el_q.focus();
    }
  
  if (!region)
    {
      errors.push('No <a href="javascript:void(0);" onclick="el(\'region\').focus();"><i>region</i></a> selected');
      el_region.focus();
    }

  if (errors.length) 
    {
      errors = ['<h2>Errors</h2><ul><li>', errors.join('</li><li>'),
		'</li></ul>'].join('');
      _setResult(errors);
    } 
  else 
    {
      var url = ['http://', domain, '/', dir, 
		 '?region=', region, '&tmode=bike&q=', 
		 escape(q), 
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
  if (status < 400)
    {
      eval("result_set = " + response_text + ";");
      eval('_' + result_set.result_set.type + 'Callback')(status, result_set);
      if (start_ms)
	_setIH('elapsed_time', 
	       ((new Date().getTime() - start_ms) / 1000.0) + 's');
      var result = result_set.result_set.html;
    }
  else
    {
      var result = response_text;
    }
  if (result)
    _setResult(result);
}

function _geocodeCallback(status, result_set)
{
  geocodes = result_set['result_set']['result'];
  switch (status)
    {
    case 200: // A-OK, one match
      if (map)
	{
	  _showGeocode(0, true);
	}
      break;
    case 300:
      if (map)
	{
	  for (var i = 0; i < geocodes.length; ++i)
	    _showGeocode(i, false);
	}
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
  fr = route.fr.original;
  to = route.to.original;
  switch (status)
    {
    case 200: // A-OK, one match
      if (map) 
	{
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
	  GEvent.addListener(s_mkr, "click", function() 
			     { 
			       map.showMapBlowup(linestring[0]); 
			     });	           
	  GEvent.addListener(e_mkr, "click", function() 
			     { 
			       map.showMapBlowup(linestring[e_ord]); 
			     });			
	  centerAndZoomToBox(box);
	  if (color_index == colors_len) color_index = 0;
	  drawPolyLine(linestring, colors[color_index++]);
	}
      break;			 
    case 300: // Multiple matches
      break;
    }
}


/* UI Manipulation */

function _setResult(content, error)
{
  if (error) 
    _setElStyle('result', 'color', 'red');
  else 
    _setElStyle('result', 'color', 'black');
  _setIH('result', content.toString());
}

function _setRouteFieldToAddress(fr_or_to, address)
{
  eval([fr_or_to, ' = "', address, '";'].join(''));
  _setElV('q', [fr, '\nTO\n', to].join(''));
}

function swapFromAndTo()
{
  var temp = fr;
  fr = to;
  to = temp;
  _setElV('q', [fr, '\nTO\n', to].join(''));
}


/* Map */

function _setElVToMapLonLat(id)
{
  if (!map) return;
  var lon_lat = map.getCenterLatLng();
  var x = Math.round(lon_lat.x * 1000000) / 1000000;
  var y = Math.round(lon_lat.y * 1000000) / 1000000;
  _setElV(id, "lon=" + x + ", " + "lat=" + y);
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
  var height = win_height - _getOffset('map') - margin;
  if (height >= 0)
    {
      el('map').style.height = height + 'px';
      if (map)
	map.onResize();
    }
  height = win_height - _getOffset('result') - margin;
  if (height >= 0)
    el('result').style.height =  height + 'px'; 
}

function _getOffset(id)
{
  var offset = 0;
  for (var e = el(id); e != null; e = e.offsetParent) 
    offset += e.offsetTop;
  return offset;
}

function _showGeocode(index, open_info_win)
{
  if (map) 
    {
      var geocode = geocodes[index];
      var point = {'x': geocode.x, 'y': geocode.y};
      var html = ['<div style="width:250px;">', 
		  geocode.address, 
		  '</div>'].join('');
      var geocode_marker = placeMarkers([point])[0];
      GEvent.addListener(geocode_marker, "click", 
			 function() { map.openInfoWindowHtml(point, html); });
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

//   var img_src = region.img_src;
//   var reg_logo = el('region_logo');
//   var reg_link = el('region_link');
//   if (img_src) 
//     {
//       reg_logo.src = 'images/' + img_src;
//       reg_logo.width = region.img_width;
//       reg_logo.height = region.img_height;
//       reg_link.href = region.href;
//     }
//   else 
//     {
//       reg_logo.src = '';
//       reg_logo.width = 0;
//       reg_logo.height = 0;
//       reg_link.href = '';
//    }

  //el('region_heading').innerHTML = region.heading;
  el('status').innerHTML = region.subheading;
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

