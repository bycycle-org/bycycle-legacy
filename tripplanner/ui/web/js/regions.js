var regions = 
  {

    all: 
    {
      'id': 'all',
      
      'heading': 'All Regions',
      
      'subheading': 'Welcome to the <a href="http://www.bycycle.org/" title="byCycle Home Page">byCycle</a> interactive bicycle trip planner, version 0.3.5 beta.',
      
      'bounds': new GLatLngBounds(new GLatLng(40.362070, -123.485755),
				  new GLatLng(45.814153, -79.866439)),
      
      'all': true
    }, 
    
    portlandor: 
    {
      'id': 'portlandor',
      
      'heading': 'Portland, OR',
      
      'subheading': 'Developed in cooperation with <a href="http://www.metro-region.org/">Metro</a>.',
      
      'bounds': new GLatLngBounds(new GLatLng(44.885219, -123.485755),
				  new GLatLng(45.814153, -121.649618))
    },
    
    milwaukeewi:
    {
      'id': 'milwaukeewi',
      
      'heading': 'Milwaukee, WI',
      
      'subheading': 'Developed in cooperation with the <a href="http://www.bfw.org/">Bicycle Federation of Wisconsin</a>.',
      
      'bounds': new GLatLngBounds(new GLatLng(42.842059, -88.069888), 
				  new GLatLng(43.192647, -87.828241)),
      
      'img_src': 'bfw_logo.gif',
      'img_width': 70,
      'img_height': 71,
      'href': 'http://www.bfw.org/'
    },
    
    
    pittsburghpa:
    {
      'id': 'pittsburghpa',
      
      'heading': 'Pittsburgh, PA',
      
      'subheading': 'Developed in cooperation with Jessi.',
      
      'bounds': new GLatLngBounds(new GLatLng(40.362070, -80.088957),
				  new GLatLng(40.500887, -79.866439))
    }
  };
