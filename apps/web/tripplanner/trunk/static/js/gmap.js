/** $Id: gmap.js 190 2006-08-16 02:29:29Z bycycle $
 *
 * This module contains variables and functions relating to the Google Map. It 
 * should be considered an extension of the ui module.
 * 
 * Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>
 * 
 * All rights reserved.
 * 
 * TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION
 * 
 * 1. The software may be used and modified by individuals for noncommercial, 
 * private use.
 * 
 * 2. The software may not be used for any commercial purpose.
 * 
 * 3. The software may not be made available as a service to the public or within 
 * any organization.
 * 
 * 4. The software may not be redistributed.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */
var map;

var center_marker;
var center_point; 
var center_marker_html = [
  '<div class="info_win">',
	'<p>',
	  '<a href="javascript:void(0);" onclick="setElVToMapLonLat(\'q\'); doFind(\'geocode\');">Find address of closest intersection</a>',
	'</p>',
	'<p>Set as ',
	  '<a href="javascript:void(0);" onclick="setElVToMapLonLat(\'fr\'); input_tabs.set(\'activeIndex\', 1);">From</a> ',
	  'or ',
	  '<a href="javascript:void(0);" onclick="setElVToMapLonLat(\'to\'); input_tabs.set(\'activeIndex\', 1);">To</a> ',
	  'address for route',
	'</p>',
  '</div>'].join('');

// Start and end markers for routes
var base_icon;
var start_icon;
var end_icon;


function mapLoad() {
  var bRet = true;
  if (GBrowserIsCompatible()) {
    mapCreate();
    bRet = true;
  } else {
    setIH('map', [
	  '<p style="margin:10px;">',
		'Your browser doesn\'t seem to meet the requirements for using this application.',
		'The following browsers are currently supported and are all free to download ',
		'(<a href="http://www.mozilla.com/">Firefox</a> is an excellent choice):',
	  '</p>',
	  '<ul>',
		 '<li><a href="http://www.microsoft.com/windows/ie/downloads/default.asp">IE</a> 5.5+ (Windows)</li>',
		 '<li><a href="http://www.mozilla.com/">Firefox</a> 0.8+ (Windows, Mac, Linux)</li>',
		 '<li><a href="http://www.apple.com/safari/download/">Safari</a> 1.2.4+ (Mac)</li>',
		 '<li><a href="http://channels.netscape.com/ns/browsers/download.jsp">Netscape</a> 7.1+ (Windows, Mac, Linux)</li>',
		 '<li><a href="http://www.mozilla.org/products/mozilla1.x/">Mozilla</a> 1.4+ (Windows, Mac, Linux)</li>',
		 '<li><a href="http://www.opera.com/download/">Opera</a> 7.5+ (Windows, Mac, Linux)</li>',
	  '</ul>'].join(''));
    bRet = False;
  }
  return bRet;
}


function mapCreate() {
  map = new GMap2(el('map'));

  map.setCenter(new GLatLng(0, 0), 2);
  
  map.addControl(new GLargeMapControl());
  map.addControl(new GMapTypeControl());
  map.addControl(new GScaleControl());
  
  map.addControl(new GOverviewMapControl());
  var overview = document.getElementById('map_overview');
  document.getElementById('map').appendChild(overview);
 
  new GKeyboardHandler(map);

  var icon = new GIcon();
  icon.image = 'static/images/reddot15.png';
  icon.iconSize = new GSize(15, 15);
  icon.iconAnchor = new GPoint(7, 7);

  GEvent.addListener(map, 'moveend', function() {
    if (center_marker)
      map.removeOverlay(center_marker);
    var center = map.getCenter();
    center.x = Math.round(center.x * 1000000) / 1000000;
    center.y = Math.round(center.y * 1000000) / 1000000;
    center_marker = new GMarker(center, icon);
    map.addOverlay(center_marker);
    GEvent.clearListeners(center_marker, 'click');
    GEvent.addListener(center_marker, 'click', function() {
      map.openInfoWindowHtml(center, center_marker_html);
    });
  });
  
  GEvent.addListener(map, 'maptypechanged', function() {
    var map_type = map.getCurrentMapType();
    if (map_type.onChangeTo) {
      map_type.onChangeTo();
    }
  });
  
  GEvent.addListener(map, 'click', function() {
    map.closeInfoWindow();
  });
  
  base_icon = new GIcon();
  base_icon.shadow = 'static/images/shadow50.png';
  base_icon.iconSize = new GSize(20, 34);
  base_icon.shadowSize = new GSize(37, 34);
  base_icon.iconAnchor = new GPoint(9, 34);
  base_icon.infoWindowAnchor = new GPoint(9, 2);
  base_icon.infoShadowAnchor = new GPoint(18, 25);
  
  start_icon = new GIcon(base_icon);
  start_icon.image = 'static/images/dd-start.png';
  
  end_icon = new GIcon(base_icon);
  end_icon.image = 'static/images/dd-end.png';
}

function makeBikeLayer(zoom_levels) {
  var domain = 'mica.metro-region.org';
  var transparent_png = 'http://' + domain + '/bycycle/images/transparent.png';
  var copyrights = new GCopyrightCollection('&copy; <a href="http://www.metro-region.org/">Metro</a>');

  var wms_url = [
	'http://', domain, 
	'/cgi-bin/mapserv-postgis?map=/var/www/html/bycycle/bycycle.map&'].join('');
  
  var layers = 'pirate_network,county_lines';
  var tile_size = 256;
  var tile_size_less_one = tile_size - 1;
  var img_format = 'image/png';
  var srs = "EPSG:4326";
  var se, nw;
  var min_zoom = 9;
  var url = [wms_url,
	"SERVICE=WMS",
	"&VERSION=1.1.1",
	"&REQUEST=GetMap",
	"&LAYERS=", layers,
	"&STYLES=",
	"&FORMAT=", img_format,
	"&BGCOLOR=0xFFFFFF",
	"&TRANSPARENT=TRUE",
	"&SRS=", srs,
	"&WIDTH=", tile_size,
	"&HEIGHT=", tile_size].join('');

  var pdx_bounds = regions.portlandor.bounds;
  var pdx_sw = pdx_bounds.sw;
  var pdx_ne = pdx_bounds.ne;
  var bounds = new GLatLngBounds(new GLatLng(pdx_sw.lat, pdx_sw.lng), 
								 new GLatLng(pdx_ne.lat, pdx_ne.lng));

  var projection = new GMercatorProjection(zoom_levels);
  
  // FIXME: Why is this named with XXX?
  projection.XXXtileCheckRange = function(tile,  zoom,  tile_size) {
    var x = tile.x * tile_size;
    var y = tile.y * tile_size;
    var sw_point = new GPoint(x, y + tile_size_less_one);
    var ne_point = new GPoint(x + tile_size_less_one, y);
    sw = this.fromPixelToLatLng(sw_point, zoom);
    ne = this.fromPixelToLatLng(ne_point, zoom );
    var tile_bounds = new GLatLngBounds(sw, ne);
    if (tile_bounds.intersects(bounds)) {
      return true;
    } else {
      return false;
    }      
  };

  var layer = new GTileLayer(copyrights, 0, zoom_levels - 1);
  
  layer.getTileUrl = function(tile, zoom) {
    projection.XXXtileCheckRange(tile, zoom, tile_size);
    if (zoom < min_zoom) {
      var tile_url = transparent_png;
    } else {
      var bbox = [sw.lng(), sw.lat(), ne.lng(), ne.lat()].join(',');
      var tile_url = [url, "&BBOX=", bbox].join('');	
    }
    return tile_url;
  };

  layer.isPng = function() { 
    return true; 
  };

  layer.getOpacity = function() { 
    return .625; 
  };

  return new GTileLayerOverlay(layer);
}

function drawPolyLine(points, color, weight, opacity) {
  var line = new GPolyline(points, color, weight, opacity);
  map.addOverlay(line);
  return line;
}


function placeMarker(point, icon) {
  var marker = new GMarker(point, icon);
  map.addOverlay(marker);
  return marker;
}

/**
 * Put some markers on the map
 * @param points An array of GPoints
 * @param icons An array of GIcons (optional)
 */
function placeMarkers(points, icons) {
  var markers = [];
  var len = points.length;
  if (icons) {
    for (var i = 0; i < len; ++i) {
      var marker = new GMarker(points[i], icons[i]);
      markers.push(marker);
      map.addOverlay(marker);
    }
  } else {
    for (var i = 0; i < len; ++i) {
      var marker = new GMarker(points[i]);
      markers.push(marker);
      map.addOverlay(marker);
    }
  }
  return markers;
}


function showMapBlowup(index)  {
  map.showMapBlowup(linestring[index]);
}


function getBoundsForPoints(points) {
  var min_x = 180;
  var max_x = -180;
  var min_y = 90;
  var max_y = -90;
  for (var i = 0; i < points.length; i++) {
    var p = points[i];
    var x = p.x;
    var y = p.y;
    min_x = x < min_x ? x : min_x;
    max_x = x > max_x ? x : max_x;
    min_y = y < min_y ? y : min_y;
    max_y = y > max_y ? y : max_y;
  }
  return new GLatLngBounds(new GLatLng(min_y, min_x),
			   new GLatLng(max_y, max_x));
}


function getCenterOfBounds(bounds) {
  var sw = bounds.getSouthWest();
  var ne = bounds.getNorthEast();
  var lon = (sw.lng() + ne.lng()) / 2.0;
  var lat = (sw.lat() + ne.lat()) / 2.0;
  return new GLatLng(lat, lon);
}


function centerAndZoomToBounds(bounds, center) {
  var center = center || getCenterOfBounds(bounds);
  map.setCenter(center, map.getBoundsZoomLevel(bounds));
}
