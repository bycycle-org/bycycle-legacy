/* User interface */

var _services = ['search', 'route'];
var _service_data = {'search': ['q', 'Search'],
		     'route': ['fr', 'Find Route']};
var _default_service = 'search';
var _service = _default_service;
var _webservice = '';

var disclaimer = '\
    <div class="disclaimer">\
        No warranty of any kind, either expressed or implied, \
        is given in regard to any route directions or other information presented here. \
        User assumes all risk of use.\
    </div>';


function ui__init__()
{
  _el('q').focus();
}


function _selectInput(service, focus) {
  if (!service && !_service_data[service]) 
    {
      service = _default_service;
    }
  var sd = _service_data[service];
  var next_service, link_el, input_el;
  for (var i = 0; i < _services.length; i++) 
    {
      next_service = _services[i];
      // Set the link style
      link_el = _el(next_service + '_link');
      link_el.className = (next_service == service) ? 'selected' : '';
      // Hide or  show the input section
      input_el = _el(next_service + '_input');
      input_el.style.display = (next_service == service) ? '' : 'none';
    }
  _setElV('find_button', sd[1]);
  if (focus == true) 
    {
      _el(sd[0]).focus();
    } 
  else if (focus) 
    {
      _el(focus).focus();
    }
  _service = service;
}


function _showInputSection(service) { _el(service+'_link').onclick(); }


function _setResult(msg, error)
{
  if (error) _setElStyle('result', 'color', 'red');
  else _setElStyle('result', 'color', 'black');
  _setIH('result', msg.toString());
}


function _clearResult() { _setResult(''); }


/**
 * @param alt_service An alternate service to use, instead of the globally set one
 */
var start_ms;
function _find(alt_service)
{
  start_ms = new Date().getTime();

  //_setElStyle('welcome', 'display', 'none');
  _setResult('Processing. Please wait...');
  
  if (alt_service) service = alt_service;
  else service = _service;
  
  if (map) 
    map.closeInfoWindow();

  var q = _elV('q');
  var fr_to;
  var query_str = '';
  
  // See if search query is for a route (if it has " to " in between 
  if (service == 'search') 
    {
      var words = _trim(q).split(/\s+to\s+/i);
      if (words.length > 1) 
	{
	  service = 'route';
	  fr_to = [];
	  for (var i = 0; i < words.length; ++i)
	    fr_to.push(words[i]);
	}
    }

  if (service == 'route')     
    {
      _setResult('Finding route. Please wait...');
      _webservice = 'route';
      if (!fr_to)
	{
	  // Found fr/to in route boxes
	  var fr = _elV('fr');
	  var to = _elV('to');
	  if (fr && to) 
	    fr_to = [fr, to];
	}
      if (fr_to) 
	{
	  // Found fr/to in search box ("A to B")
	  _setElV('fr', fr_to[0]);
	  _setElV('to', fr_to[1]);
	  for (var i = 0; i < fr_to.length; ++i) 
	    fr_to[i] = escape(_cleanString(fr_to[i].replace('"', "'")));
	  query_str = 'q=["' + fr_to.join('","') + '"]&dmode=' + _elV('dmode') + '&tmode=bike';
	}
      _showInputSection('route');
    } 
  else if (service == 'search') 
    {
      _webservice = 'geocode';
      if (q) query_str = 'q=' + escape(_cleanString(q)) + '&dmode=' + _elV('dmode');
    } 
  else if (service == 'feedback') 
    {
      _webservice = 'feedback';
      var feedback = _elV('feedback');
      if (!feedback) return;
      var data = 
	'{"q":"'      + _elV('q')     + '",' +
	' "fr":"'     + _elV('fr')    + '",' + 
	' "to":"'     + _elV('to')    + '",' +
	' "dmode":"'  + _elV('dmode') + '",' + 
	' "result":"' + _elV('result')  + '"}';
      query_str = 'feedback=' + escape(_cleanString(feedback, true)) + '&data=' + escape(data);    
    } 
  else 
    {
      _setResult('Unknown service: ' + service);
      return;
    }

  if (!query_str) 
    {
      var msg = ['<b>More input required.</b><br/>'];
      if (service == 'search') 
	{
	  msg.push(' Missing address or route query.<br/>');
	} 
      else if (service == 'route') 
	{
	  if (!_elV('fr')) msg.push(' Missing from address.<br/>');
	  if (!_elV('to')) msg.push(' Missing to address.<br/>');
	}
      _setResult(msg.join(''));
    } 
  else 
    {
      var url = ['http://', domain, '/', dir, 'webservices/', _webservice, 
		 '?', query_str].join('');
      //alert(url);
      doXmlHttpReq('GET', url, _callback);
    }
}


/* Callbacks */

var geocodes;


/** 
 * Do stuff that's common to all callbacks in here
 */
function _callback(req)
{
  var result_set = {};
  var status = req.status;
  var reason = req.statusText;
  var status_msg = '';
  var error;
  var callback = eval('_'+_webservice+'Callback');
  
  if (status == 200 || status == 300) 
    {
      eval("result_set = " + req.responseText + ";");
    }
  
  var result = callback(status, result_set);
  var result_text = result['result_text'];
  error = result['error'];
  
  if (error) 
    {
      result_text = (result_text ? result_text : reason);
      status_msg += '<b>Error</b>'; 
    } 
  else 
    {
      status_msg += ((new Date().getTime() - start_ms) / 1000.0) + 's';
    }
  _setResult('<div>'+status_msg+'</div>' + result_text);
  return !error;
}


function _geocodeCallback(status, result_set)
{
  error = false;
  var result_text = '';
  switch (status)
    {
    case 200: // A-OK, one match
      geocodes = result_set['result_set']['result'];
      var geocode = geocodes[0];
      _showGeocode(0, true);
      result_text = _makeAddressFromGeocode(geocode, true);
      break;
    case 300: // Multiple matches
      geocodes = result_set['result_set']['result'];
      result_text = '<h3>Multiple Matches Found</h3><ul>';
      var href = ' href="javascript:void(0);" ';
      for (var i = 0; i < geocodes.length; ++i) 
	{
	  var code = geocodes[i];
	  var onclick = ' onclick="_showGeocode('+i+');" ';
	  var a = '<a'+href+onclick+'>'+_makeAddressFromGeocode(code, false, '<br/>')+'</a>';
	  result_text += '<li>'+a+'</li>';
	}
      result_text += '</ul>';
      break;
    case 400: // Input Error
    case 404: // Not found
    case 405: // Method not allowed (POST, etc)
    default: error = true;
    }
  return {'result_text': result_text, 'error': error};
}
	
var colors = ['#0000ff', '#00ff00', '#ff0000', 
	      '#00ffff', '#ff00ff', '#ff8800',
	      '#000000', '#ffffff'];	
var color_index = 0;
var colors_len = colors.length;
function _routeCallback(status, result_set)
{
  error = false;
  var result_text = '';
  switch (status)
    {
    case 200: // A-OK, one match
      var route = result_set['result_set']['result'];
      result_text = route['directions_table'];
      if (map) 
	{
	  var linestring = route['linestring'];
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
      var geocodes_fr = result_set['result_set']['result']['from'];
      var geocodes_to = result_set['result_set']['result']['to'];
      result_text = '<div id="mma">' +
	'<h3>Multiple Matches Found</h3>' +
	_makeRouteMultipleMatchList(geocodes_fr, geocodes_to) +
	'</div>';
      break;
    case 400: // Input Error
    case 404: // Not found
    case 405: // Method not allowed (POST, etc)
    default: error = true;
    }
  return {'result_text': result_text, 'error': error};
}


function _feedbackCallback(req)
{
  _setResult('Your feedback has been sent. Thanks.');
}


function _makeRouteMultipleMatchList(geocodes_fr, geocodes_to)
{
  var result = [];

  function makeDiv(fr_or_to, style)
  {
    var heading = (fr_or_to == 'fr' ? 'From' : 'To');
    result.push('<div id="mma_', fr_or_to, '" style="display:', style, ';"><h4>', heading, '</h4>');
  }

  function makeList(fr_or_to, geocodes, find)
  {
    var href = ' href="javascript:void(0);" ';    
    var onclick1 = ' onclick="_setElV(\'' + fr_or_to + '\', \'';
    var onclick2 = '\'); _showInputSection(\'route\'); ' + find + '" ';
    result.push('<ul>');
    
    var list;
    for (var i = 0; i < geocodes.length; ++i) 
      {
	addr = _makeAddressFromGeocode(geocodes[i], false, '\\n');
	list = ['<li>', '<a', href, onclick1, addr, onclick2, '>', addr.replace('\\n', '<br/>'), '</a>', '</li>'];
	result.push(list.join(''));
      }
    result.push('</ul></div>');
  }
  
  if (geocodes_fr.length)
    {
      var style = 'block';
      if (geocodes_to.length) 
	var find = '_setElStyle(\'mma_fr\', \'display\', \'none\'); _setElStyle(\'mma_to\', \'display\', \'block\');';
      else
	var find = '_find()';
      makeDiv('fr', style);
      makeList('fr', geocodes_fr, find);
    }

  if (geocodes_to.length)
    {
      var find = '_find()';
      if (geocodes_fr.length) 
	var style = 'none';
      else
	var style = 'block';
      makeDiv('to', style);
      makeList('to', geocodes_to, find);
    }
  return result.join('');
}


/**
 * Concatenate a geocode's address parts into a single string
 *
 * @param geocode A geocode object
 * @param show_lon_lat Flag indicating whether to show the geocode's long/lat as part of the address (default: false)
 * @param separator The separator that will go between the street, place, and long/lat (default: <br/>)
 */
function _makeAddressFromGeocode(geocode, show_lon_lat, separator)
{
  separator = separator || '<br/>';
  var type = geocode.type;
  var place; 
  var full_name;
  if (type == 'address') 
    {
      var st = geocode.street;
      place = geocode.place;
      full_name = _join([geocode.number.toString(), st.prefix, st.name, st.type, st.suffix]);
    } 
  else if (type == 'intersection') 
    {
      var st1 = geocode.street1;
      var st2 = geocode.street2;
      place = geocode.place1;
      full_name = [_join([st1.prefix, st1.name, st1.type, st1.suffix]),
		   _join([st2.prefix, st2.name, st2.type, st2.suffix])].join(' & ');
    }
  var zc = parseInt(place.zipcode);
  var city = place.city;
  var state = place.state_id;
  var address = [full_name, separator, 
		 city, (city ? ', ' : ''), 
		 state, (state ? ' ' : ''), 
		 zc || ''];
  if (show_lon_lat) address.push(separator, 'long: ', geocode.x, ', lat: ', geocode.y);
  return address.join('');
}

function _showGeocode(index, center)
{
  if (map) 
    {
      var geocode = geocodes[index];
      var point = {'x': geocode.x, 'y': geocode.y};
      var info_addr = _makeAddressFromGeocode(geocode, true);           // address for info win
      var field_addr = _makeAddressFromGeocode(geocode, false, '\\n');  // address for text field
      var href = ' href="javascript:void(0);" ';
      var html = ['<div style="width:250px;">',
		  '<b>Address</b><br/>',
		  info_addr, '<hr/>',
		  'Set as ',
		  '<a', href, ' onclick="_setRouteFieldToAddress(\'fr\', \'', field_addr, '\');">From</a> or ',
		  '<a', href, ' onclick="_setRouteFieldToAddress(\'to\', \'', field_addr, '\');">To</a> address for route<br/>',
		  '<input type="button" value="Find Route" onclick="_find(\'route\');" style="margin-top:4px;"/>',
		  '</div>'].join('');
      var geocode_marker = placeMarkers([point])[0];
      GEvent.addListener(geocode_marker, "click", function() { map.openInfoWindowHtml(point, html); });
      map.centerAndZoom(point, 3);
      map.openInfoWindowHtml(point, html);
    }
}

function _setRouteFieldToAddress(id, address)
{
  _selectInput('route', id == 'fr' ? 'to' : 'fr');
  _setElV(id, address);
}

function _clearMap()
{  
  if (map) 
    {
      map.clearOverlays();
      map.addOverlay(metro_line);
      map.addOverlay(milwaukee_line);
      for (var i = 0; i < region_markers.length; ++i)
	map.addOverlay(region_markers[i]);
    }
}

function _reset()
{
  _setElStyle('welcome', 'display', 'block');
  _setIH('fr', '');
  _setIH('to', '');
  _setIH('q', '');
  _clearMap();
}

function _setElVToAddress(id, address) 
{
  _setElV(id, address);
}

function _setElVToMapLonLat(id)
{
  if (!map) return;
  var lon_lat = map.getCenterLatLng();
  var x = Math.round(lon_lat.x * 1000000) / 1000000;
  var y = Math.round(lon_lat.y * 1000000) / 1000000;
  field = _setElV(id, "lon=" + x + ", " + "lat=" + y);
}

var _map_height = 300;
function _adjustMapHeight(taller_or_smaller)
{
  if (map) 
    {
      if (taller_or_smaller < 0)
	{
	  if (_map_height == 200) return;
	  _map_height -= 50;
	}
      else if (taller_or_smaller > 0)
	{
	  if (_map_height == 1200) return;
	  _map_height += 50;
	}
      var h = _map_height + 'px';
      _el('map').style.height = h;
      _el('result').style.height = h;
    }
}

function resizeMap() 
{
  var offset = 0;
  for (var elem = _el('map'); elem != null; elem = elem.offsetParent) 
    {
      offset += elem.offsetTop;
    }
  var height = getWindowHeight() - offset - 50;
  if (height >= 0) 
    {
      _el('map').style.height = height + 'px';
      _el('result').style.height = height + 'px';
      map.onResize();
    }
}
