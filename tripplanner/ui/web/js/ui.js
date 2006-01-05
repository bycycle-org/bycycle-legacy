/* User interface */

var _services = ['route', 'search'];
var _default_service = 'search';
var _service = _default_service;
var _webservice = '';
var default_fields_to_focus = {'route': 'fr',
	                           'search': 'q'};
var default_result = '\
    <b>Welcome to the <a href="/" title="byCycle Home Page">byCycle</a> \
    <a href="http://tripplanner.bycycle.org/" title="Information About the Trip Planner">Trip Planner</a>.</b>\
    <div class="disclaimer">\
        No warranty of any kind, either expressed or implied, is given in regard to any route directions or other information presented here. User assumes all risk of use.\
    </div>';


function ui__init__()
{
    _reset();
    _el('q').focus();
}


function _selectInput(service, focus) {
	if (!service) { service = _default_service; }
	for (var i = 0; i < _services.length; i++) {
		var next_service = _services[i];
		var link_el = _el(next_service + '_link');
		var input_el = _el(next_service + '_input');
		link_el.className = (next_service == service) ? 'selected' : '';
		input_el.style.display = (next_service == service) ? '' : 'none';
	}
	if (focus == true) {
		_el(default_fields_to_focus[service]).focus();
	} else if (focus) {
	   _el(focus).focus();
	}
	_service = service;
}


function _showInputSection(service) { _el(service+'_link').onclick(); }


function _setStatus(msg, error)
{
	if (error) _setElStyle('status', 'color', 'red');
	else _setElStyle('status', 'color', 'black');
	_setIH('status', msg);
}


function _clearStatus() { _setIH('status', ''); }


/**
 * @param alt_service An alternate service to use, instead of the globally set one
 */
function _find(alt_service)
{
	_setStatus('Processing. Please wait...');
	
	if (alt_service) service = alt_service;
	else service = _service;
	
	if (map) map.closeInfoWindow();
	var q = _elV('q');
	var query_str = '';

	// See if search query is for a route
	if (service == 'search') {
		var fr_to = null;
		var tos = [' to ', ' TO ', ' To ', ' tO '];
		for (var i = 0; i < tos.length; ++i) {
			fr_to = q.split(tos[i]);
			if (fr_to.length >= 2) break;
		}
	}

	if (service == 'route' ||
		(service == 'search' && (fr_to.length >= 2))) {
		_setStatus('Finding route. Please wait...');
		_webservice = 'route';
		if (service == 'route') {
			var fr_to = null;
			var fr = _elV('fr');
			var to = _elV('to');
			if (fr && to) fr_to = [fr, to];
		}
		if (fr_to) {
			for (var i = 0; i < fr_to.length; ++i) fr_to[i] = fr_to[i].replace('"', "'");
			query_str = 'q=["' + escape(fr_to.join('","')) + '"]&tmode=bike';
		}
		_setElV('fr', fr_to[0]);
		_setElV('to', fr_to[1]);
		_showInputSection('route');
	} else if (service == 'search') {
		_webservice = 'geocode';
		if (q) query_str = 'q=' + escape(q);
	} else {
		_setStatus('Unknown service: ' + service);
		return;
	}

	if (!query_str) {
		var msg = 'More input required.';
		if (service == 'search') {
		  msg += ' Missing address or route query.';
		} else if (service == 'route') {
		  if (!_elV('fr')) msg += ' Missing from address.';
		  if (!_elV('to')) msg += ' Missing to address.';
		}
		_setStatus(msg);
	} else {
        var url = 'http://' + domain + '/tripplanner/webservices/' + _webservice + 
	              '/?' + query_str + '&dmode=' + _elV('dmode');
	    //echo(url);
        doXmlHttpReq('GET', url, _callback);
	}
}



/* Callbacks */

var geocodes;
//var geocode_marker;


/** 
 * Do stuff that's common to all callbacks in here
 */
function _callback(req)
{
	var start_time = new Date();
	var result_set = {};
	var status = req.status;
	var reason = req.statusText;
	var status_msg = '';
	var error;
    var callback;
    
	if (status == 200 || status == 300) {
		eval("result_set = " + req.responseText + ";");
		//map.removeOverlay(geocode_marker);
	}
    
    callback = eval('_'+_webservice+'Callback');    
    result = callback(status, result_set);
    result_text = result['result_text'];
    error = result['error'];
    
	if (error) {
	   result_text = 'Error: ' + (result_text ? result_text : reason);
       status_msg += '!'; 
	} else {
	   status_msg += 'Done. Took ' + ((new Date() - start_time) / 1000.0) + ' seconds.';
    }
	_setStatus(status_msg, error);
	_setIH('result', result_text);
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
			_showGeocode(0, true);
			result_text = _makeAddressFromGeocode(geocodes[0], true);
			break;
		case 300: // Multiple matches
		    geocodes = result_set['result_set']['result'];
			result_text = '<b><big>Multiple Matches Found</big></b><br/><ul>';
			var href = ' href="javascript:void(0);" ';
			for (var i = 0; i < geocodes.length; ++i) {
				var code = geocodes[i];
				var onclick = ' onclick="_showGeocode('+i+');" ';
				var a = '<a'+href+onclick+'>'+_makeAddressFromGeocode(code, false, ', ')+'</a>';
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
	
	
function _routeCallback(status, result_set)
{
    error = false;
    var result_text = '';
	switch (status)
	{
		case 200: // A-OK, one match
			var route = result_set['result_set']['result'];
			result_text = route['directions_table'];
	        if (map) {
	           var linestring = route['linestring'];
	           var linestring_len = linestring.length;
    		   var box = getBoxForPoints(linestring);	
	           var s_e_markers = placeMarkers([linestring[0],
	                                          linestring[linestring_len-1]],
	      			                          [start_icon, end_icon]);
	           var s_mkr = s_e_markers[0];
               var e_mkr = s_e_markers[1];
	           var e_ord = linestring_len - 1;
	           GEvent.addListener( s_mkr, "click", function() { showMapBlowupAlongRoute(linestring[0]); } );	           
        	   GEvent.addListener( e_mkr, "click", function() { showMapBlowupAlongRoute(linestring[e_ord]); } );			
	           centerAndZoomToBox(box);
			   drawPolyLine(linestring);
			}
			break;			 
		case 300: // Multiple matches
		    var geocodes_f = result_set['result_set']['result']['from'];
		    var geocodes_t = result_set['result_set']['result']['to'];
		    result_text = '<div id="mma">' +
		                      '<b><big>Multiple Matches Found</big></b><br/>' +
		                       _makeRouteMultipleMatchList(geocodes_f, geocodes_t, 'fr') +
		                       _makeRouteMultipleMatchList(geocodes_f, geocodes_f, 'to') +
		                  '</div>';
			break;
		case 400: // Input Error
		case 404: // Not found
		case 405: // Method not allowed (POST, etc)
		default: error = true;
	}
	return {'result_text': result_text, 'error': error};
}

function _makeRouteMultipleMatchList(geocodes_f, geocodes_t, fr_or_to)
{
    fr_or_to == 'fr' ? geocodes = geocodes_f : geocodes = geocodes_t;
    if (!geocodes) return '';
    
    var result = '<div id="mma_'+fr_or_to+'" ';
    
    if (fr_or_to == 'fr') {
        result += '><b>From:</b><br/>';
    	// Do find after selection of end address, if end address had multiple matches in addition to from address
        if (geocodes_t) {
            var find = '_setElStyle(\'mma_fr\', \'display\', \'none\'); ' +
                       '_setElStyle(\'mma_to\', \'display\', \'block\');';
        } else {
            var find = '_find();'
        }
    } else {
        if (geocodes_f) result += 'style="display:none"';
        result += '><b>To:</b><br/>';
        var find = '_find()';
    }

    var href = ' href="javascript:void(0);" ';    
    var onclick1 = ' onclick="_setElV(\'' + fr_or_to + '\', \'';
    var onclick2 = '\'); _showInputSection(\'route\'); ' + find + '" ';
    result += '<ul>';
	for (var i = 0; i < geocodes.length; ++i) {
	   var code = geocodes[i];
	   var addr = _makeAddressFromGeocode(code, false, ', ');
	   var onclick = onclick1 + addr + onclick2;
	   var a = '<a'+href+onclick+'>'+addr+'</a>';
	   result += '<li>'+a+'</li>';
	}
	result += '</ul></div>';
	return result;
}


function _makeAddressFromGeocode(geocode, show_lon_lat, separator)
{
	if (!separator) separator = '<br/>';  // separates street, place, and long/lat
	var type = geocode.type;
	var place; 
	var full_name;
	if (type == 'address') {
		var st = geocode.street;
		place = geocode.place;
		full_name = geocode.number + ' ' + _join([st.prefix, st.name, st.type, st.suffix]);				  
	} else if (type == 'intersection') {
		var st1 = geocode.street1;
		var st2 = geocode.street2;
		place = geocode.place1;
		full_name = _join([st1.prefix, st1.name, st1.type, st1.suffix]) + ' & ' +
			        _join([st2.prefix, st2.name, st2.type, st2.suffix])
	}
	var zc = place.zipcode == '0' ? '' : place.zipcode;
	var address = full_name + separator + place.city + ', ' + place.id_state  + ' ' + zc;	  
	if (show_lon_lat)	address += separator + 'long: ' + geocode.x + ', lat: ' + geocode.y;
	return address;
}

function _showGeocode(index, center)
{
	var geocode = geocodes[index];
	var point = {'x': geocode.x, 'y': geocode.y};
	var waddr = _makeAddressFromGeocode(geocode, true);         // address for info win
	var faddr = _makeAddressFromGeocode(geocode, false, ', ');  // address for text field
	var href = ' href="javascript:void(0);" ';
	var html = '<div style="width:250px;">' +
			     '<b>Address</b><br/>' +
				 waddr + '<br/>' +
				 'Get directions: ' +
				 '<a'+href+' onclick="_setRouteFieldToAddress(\'fr\', \''+faddr+'\');">From</a> &middot; ' +
				 '<a'+href+' onclick="_setRouteFieldToAddress(\'to\', \''+faddr+'\');">To</a>' +
			   '</div>';
	if (map) {
	   var geocode_marker = placeMarkers([point])[0];
	   GEvent.addListener(geocode_marker, "click",
		      			  function() { map.openInfoWindowHtml(point, html); });
       if (center) map.centerAtLatLng(point);
	   map.openInfoWindowHtml(point, html);
    }
}

function _setRouteFieldToAddress(id, address)
{
    _selectInput('route', id == 'fr' ? 'to' : 'fr');
	_setElV(id, address);
}

function _reset()
{  
    _clearStatus();
    _setIH('result', default_result);
    if (map) map.clearOverlays();
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
