<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml">
  
  
  <head>
    <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=iso-8859-1"/>
    <title>byCycle.org - Bicycle Trip Planner/Route Finder</title>
    
    <meta name="keywords" content="bicycle, bike, bicycle trip planner, bicycle route finder, bike trip planner, bike route finder, bicycle route, bicycle trip, bike route, bike trip, bicycle routing, bike routing, maps, bicycle maps, bike maps, bicycle advocacy, community, sustainability, portland, oregon, milwaukee, wisconsin"/>
    <meta name="description" content="byCycle.org Bicycle Trip Planner -- A web-based, interactive, bicycle trip planner (route finder) for the Portland, Oregon, Milwaukee, Wisconsin, and, soon, other regions."/>
    
    <link rel="stylesheet" href="/css/base.css" type="text/css"/>
    <!--[if IE]>
      <link rel="stylesheet" href="/css/base_ie.css" type="text/css"/>
    <![endif]-->

    <script type="text/javascript" src="/js/MochiKit/MochiKit.js"></script>
    <script type="text/javascript" src="/js/util.js"></script>
    <script type="text/javascript" src="/js/bycycle.js"></script>
  </head>
  

  <body>


    <% c.poo %>


    <!-- Header -->
    <div id="header" class="page_section">
      <table>
	<tbody>
	  <tr>
	    <td>
	      <div id="title">
		<a href="http://www.bycycle.org/" title="byCycle.org Home Page">byCycle.org</a>&nbsp;-&nbsp;<a href="http://tripplanner.bycycle.org/">Bicycle Trip Planner</a>&nbsp;-&nbsp;<span id="active_region">All Regions</span>
	      </div>
	    </td>
	    <td>
	      <div id="about">
		<a href="http://byCycle.org/tripplanner/">About</a>
	      </div>
	    </td>
	  </tr>
	</tbody>
      </table>
    </div>
    <!-- End Header -->


    <!-- Input -->
    <div id="input" class="tab_pane">


      <div class="tab_labels page_section">
	<div class="clear"></div>
	<ul>
	  <li class="tab_label selected">
	    <a href="" onclick="return false;" 
	       title="Search the Map for an Address or Route">Search Map</a>
	  </li>
	  <li class="tab_label">
	    <a href="" onclick="return false;" 
	       title="Find a Route (Get Directions)">Find Route</a>
	  </li>
	  <li class="tab_label">
	    <a href="" onclick="return false;" 
	       title="Change the Active Geographic Region">Change Region</a>
	  </li>
	  <li class="tab_label">
	    <a href="" onclick="return false;" 
	       title="Show Trip Planner Help">Show Help</a>
	  </li>
	  <li class="tab_label">
	    <a href="" onclick="return false;" 
	       title="Send Us Your Comments, Questions, and Suggestions">Send Feedback</a>
	  </li>
	</ul>
	<div class="clear"></div>
      </div>


      <div class="tab_contents page_section">


	<div class="tab_content">
	  <!-- Query Form -->
	  <form id="query_form" method="get" action="" onsubmit="return false;">
	    <div>
	      <input id="q" name="q" type="text" value="<% c.q %>" title="Address/intersection or route" tabindex="1"/>
	      <input name="qb" type="submit" value="Search" title="Click to search" tabindex="9"/>
	      <div class="input_label">
		Enter an address or intersection -OR- pick a location from the map.
	      </div>
	    </div>
	  </form>
	  <!-- End Query Form --> 
	</div>
	
	
	<div class="tab_content" style="display: none;">
	  <!-- Route Form-->
	  <form id="route_form" method="get" action="" onsubmit="return false;">
	    <div>
	      <input id="fr" name="fr" type="text" value="<% c.fr %>" title="Start address/intersection" tabindex="4"/>
	      <a id="swap_fr_and_to" href="" onclick="return false;" 
		 title="Swap From and To Locations" tabindex="5"
		 ><img src="images/swapfrto.png" alt="-" width="20" height="14"/></a>
	      <input id="to" name="to" type="text" value="<% c.to %>" title="End address/intersection" tabindex="6"/>
	      <select id="pref" name="pref" tabindex="8">
		<option value="">- Route Type -</option>
		<option value="">Normal</option>
		<option value="safer">Safer</option>
	      </select>
	    </div>
	    <div class="input_label">
	      Enter your start and end addresses/intersections, select a route type (optional), and set your region.
	    </div>
	  </form>
	  <!-- End Route Form -->
	</div>

	
	<div class="tab_content" style="display: none;">
	  <!-- Region Form -->
	  <form id="region_form" method="get" action="" onsubmit="return false;">
	    <div>
	      <select id="region" name="region" class="region" title="Set the Active Region and Zoom In to It" tabindex="7">
		<option value="">- Regions -</option>
		<option value="">All Regions</option>
		<option value="portlandor">Portland, OR</option>
		<option value="milwaukeewi">Milwaukee, WI</option>
		<option value="pittsburghpa">Pittsburgh, PA</option>
	      </select>
	      <input id="change_region_button" name="rb" type="submit" value="Change Region"/>
	    </div>
	    <div class="input_label">
	      Select a new geographic region from the list. This will focus the map on the region and you won't have to type the city &amp; state or zip code for addresses you enter.
	    </div>
	  </form>
	  <!-- End Region Form -->
	</div>
      </div>
    </div>
    <!-- End Input -->

	      
    <!-- Content -->
    <div id="content" class="page_section">
      <table>
	<tbody>
	  <tr>


	    <!-- Display Area -->
	    <td>
	      <div id="display">
		<div id="info">
		  <p style="margin-top: 0;">
		    Welcome to the <a href="http://www.bycycle.org/" title="byCycle.org Home Page">byCycle.org</a> bicycle trip planner. 
		  </p>

		  <p>
The trip planner is under active development. Please <a href="http://www.bycycle.org/contact.html" title="Send us problem reports, comments, questions, and suggestions">contact us</a> with any problems, comments, questions, or suggestions.
		  </p>
		  
		  <p>
		    If you find this application useful or would like help it improve, please consider <a href="http://www.bycycle.org/support.html#donate" target="_new">donating</a>. Any amount helps. 
		  </p>
		  
		  <p>
		    Users should independently verify all information presented here. This service is provided <b>AS IS</b> with <b>NO WARRANTY</b> of any kind. 
		  </p>        
		</div>
		
		<div id="result"></div>

		<div id="help"></div>
		
		<div id="error"></div>
	      </div>
	    </td>
	    <!-- End Display Area -->
	    
	    
	    <!-- Map -->
	    <td>
	      <div id="map">
		<div id="map_msg" style="padding: 4px;">
		  Loading map...
		  <noscript>
		    <!-- TODO: Put a default static map here -->
		    <p>
		      To display a map here, JavaScript must be enabled in your browser. If you would like to view the map, please enable JavaScript and <a href="">try again</a>.
		    </p>
		    <p>
		      Note that you must have a relatively recent browser for the map to display. We test in Mozilla Firefox 1.5 on Linux, Mac OS X, and Windows; Safari on Mac OS X; and Internet Explorer 6 on Windows. Although we try our best to make the Trip Planner work the same in all of these browsers, we do the most testing with Firefox, and as a result it is the best choice for running the Trip Planner. Firefox is a great browser and we recommned trying it if you haven't already.
		    </p>
		    <p>
		      If you don't have one of the above browsers, you may want to leave JavaScript turned off. On the other hand, if you feel like experimenting, you can <a href="http://www.bycycle.org/contact.html">let us know</a> if the trip planner does or does not work in other browsers.
		    </p>
		  </noscript>
		</div>
	      </div>
	    </td>
	    <!-- End Map -->


	    <!-- Google Ads -->
	    <td>
	      <div id="google_ads">
		<div class="title_bar">
		  <a id="hide_ads" class="close_button" href="" onclick="return false;" title="Close Ad Window">X</a>
		</div>
		<script type="text/javascript">
		  google_ad_client = 'pub-6971619329897557';
		  google_ad_width = 120;
		  google_ad_height = 600;
		  google_ad_format = '120x600_as';
		  google_ad_type = 'text_image';
		  google_ad_channel = '';
		  google_color_border = 'FFFFFF'; //99b3cc'; //A7CC95';
		  google_color_bg = 'FFFFFF';
		  google_color_link = '000000';
		  google_color_text = '000000';
		  google_color_url = '4466DD';
		</script>
		<script type="text/javascript">
		if (!byCycle.debug) {
		  writeScript('http://pagead2.googlesyndication.com/pagead/show_ads.js');
		}
		</script>
	      </div>
	    </td>
	    <!-- End Google Ads -->
	    

	  </tr>
	</tbody>
      </table>
    </div>
    <!-- End Content -->


    <!-- Footer -->    
    <div id="footer" class="page_section">
      <table>
	<tbody>
	  <tr>
	    <td>
	      <div id="status">
		Welcome to the <a href="http://byCycle.org/">byCycle.org</a> <a href="http://TripPlanner.byCycle.org/">bicycle trip planner</a>.
	      </div>
	    </td>
	    <td>
	      <div id="copyright">
		&copy; 2006 <a href="http://byCycle.org/">byCycle.org</a>
	      </div>
	    </td>
	  </tr>
	</tbody>
      </table>
    </div>
    <!-- End Footer -->    


    <input type="hidden" id="http_status" name="http_status" value="<% c.http_status %>"/>
    <input type="hidden" id="response_text" name="response_text" value='<% c.response_text %>'/> 


    <script type="text/javascript" src="/js/ui.js"></script>
    <script type="text/javascript" src="/js/map.js"></script>
    <script type="text/javascript" src="/js/gmap.js"></script>
    <script type="text/javascript" src="/js/regions.js"></script>
    <script type="text/javascript">byCycle.UI.preload();</script>


  </body>
</html>
