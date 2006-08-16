var regions = {
  
  all: 
  {
    id: 'all',
    
    heading: 'All Regions',
    
    subheading: 'Welcome to the <a href="http://www.bycycle.org/" title="byCycle Home Page">byCycle</a> interactive bicycle trip planner, version 0.3.5 beta.',
    
    bounds: {sw: {lat: 40.362070, lng: -123.485755},
	     ne: {lat: 45.814153, lng: -79.866439}},
    
    all: true
  }, 

  
  portlandor: 
  {
    id: 'portlandor',
    
    heading: 'Portland, OR',
    
    subheading: 'Developed in cooperation with <a href="http://www.metro-region.org/">Metro</a>.',
    
    bounds: {sw: {lat: 44.885219, lng: -123.485755},
	     ne: {lat: 45.814153, lng: -121.649618}}

    //center: new GLatLng(45.523127, -122.667761),

    //linestring: null,

    //line: null
  },

  
  milwaukeewi:
  {
    id: 'milwaukeewi',
    
    heading: 'Milwaukee, WI',
    
    subheading: 'Developed in cooperation with the <a href="http://www.bfw.org/">Bicycle Federation of Wisconsin</a>.',
    
    bounds: {sw: {lat: 42.842059, lng: -88.069888}, 
	     ne: {lat: 43.192647, lng: -87.828241}},
    
    img_src: 'bfw_logo.gif',
    img_width: 70,
    img_height: 71,
    href: 'http://www.bfw.org/'
  },
  
  
  pittsburghpa:
  {
    id: 'pittsburghpa',
    
    heading: 'Pittsburgh, PA',
    
    subheading: 'Developed in cooperation with Jessi.',
    
    bounds: {sw: {lat: 40.362070, lng: -80.088957},
	     ne: {lat: 40.500887, lng: -79.866439}}
  }

};
