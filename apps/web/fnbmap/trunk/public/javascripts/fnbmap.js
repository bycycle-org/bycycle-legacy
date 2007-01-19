var FNBMap = (function() {
	var self = null;
    
	// public:
	return {
	    default_center: new GLatLng(45.5230067448621, -122.667846679688),
        default_zoom: 15,
        geocoder: null,
        	   
		on_load: function() {
			self = FNBMap;
			Event.observe(window, 'resize', self.on_resize);
			self.map_el = $('map');
			self.create_map();
			self.on_resize();
  			Event.observe(window, 'unload', self.on_unload);
  		},

		on_unload: function() {
		  GUnload();
		},
				
        on_resize: function() {  	
            var dims = Element.getDimensions(document.body);
            var pos = Position.cumulativeOffset(self.map_el);
            var height = dims.height - pos[1];
            dims = Element.getDimensions($('ft'));
            height = height - dims.height;
            self.map_el.style.height = height + 'px';
            self.map.checkResize();
            $('content').style.height = (height - 10) + 'px';
        },
    
        create_map: function() {
            // Create Google Map
            var map = new GMap2($('map'));
            map.setCenter(self.default_center, self.default_zoom);
            map.addControl(new GLargeMapControl());
            map.addControl(new GMapTypeControl());
            map.addControl(new GScaleControl());
            map.addControl(new GOverviewMapControl());
            new GKeyboardHandler(map);
            self.map = map;		    
        },
    
        /**
        * Find the smallest bounding box containing the points.
        */
        get_bounds_for_points: function(points) {
            var xs = [];
            var ys = [];
            for (var i = 0, p = null; i < points.length; ++i) {
                p = points[i];
                xs.push(p.lng());
                ys.push(p.lat());
            }
            var comp = function(a, b) { return a - b; };
            xs.sort(comp);
            ys.sort(comp);
            var bounds = new GLatLngBounds(new GLatLng(ys[0], xs[0]), new GLatLng(ys.pop(), xs.pop()))
            return bounds;
        },  					
	}
})();
