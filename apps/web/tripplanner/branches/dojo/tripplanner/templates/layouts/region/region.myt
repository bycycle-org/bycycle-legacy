<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">


<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml">


  <head>
    <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" />

    <meta name="author" value="Wyatt Baldwin, wyatt@byCycle.org" />

    <meta name="keywords" content="bicycle, bike, bicycle trip planner, bicycle route finder, bike trip planner, bike route finder, bicycle route, bicycle trip, bike route, bike trip, bicycle routing, bike routing, maps, bicycle maps, bike maps, bicycle advocacy, community, sustainability, portland, oregon, milwaukee, wisconsin" />

    <meta name="description" content="byCycle.org Bicycle Trip Planner -- A web-based, interactive, bicycle trip planner (route finder) for the Portland, Oregon, Milwaukee, Wisconsin, and, soon, other regions." />

    <title>byCycle.org - Bicycle Trip Planner - ${c.region}</title>

    ${h.stylesheet_link_tag('base.css')}
    <!--[if IE]>${h.stylesheet_link_tag('base_ie.css')}<![endif]-->

    <script type="text/javascript" >
      //<![CDATA[
      // Global setup
      var debug = ${'true' if bool(g.debug) else 'false'};
      byCycle_prefix = '${h.url_for('/')}';
      //]]>
    </script>

    ${h.javascript_include_tag(builtins=True)}
    ${h.javascript_include_tag('bycycle', 'util')}
  </head>


  <body>


	<!-- Header -->
    <div id="header">


      <!-- Masthead -->
      <div id="masthead">
        <div id="logo">
          <a href="http://bycycle.org/" title="byCycle.org Home Page">
            ${h.image_tag('http://tripplanner.bycycle.org/static/images/logo.png', title='byCycle.org Home Page', width=150, height=40, alt='byCycle.org')}
          </a>
        </div>
        <div id="app_name">
          ${h.link_to('Bicycle Trip Planner', h.url_for('/'), title='byCycle.org Bicycle Trip Planner')}
        </div>
        <div id="version">
          <a href="http://en.wikipedia.org/wiki/Development_stage#Beta" title="Beta?">beta</a>
        </div>
      </div>
      <!-- End Masthead -->


      <!-- Input Container -->
      <div id="input_container" class="tab-control">


        <!-- Input Tab Buttons -->
        <ul id="input_tab_buttons" class="tab-buttons">
		  <!-- <li>s have class `tab-button` -->
		  ${self.make_tab_buttons('search-the-map', 'find-a-route')}
        </ul>
        <!-- End Input Tab Buttons -->


		<!-- End Input Tab Contents -->
        <div id="input_tab_contents" class="tab-contents">


          <!-- Query Pane -->
          <div id="search-the-map" class="tab-content">
            ${h.form(h.url_for('/%s' % c.region_key), method='get', id='query_form')}
              <div>
		  		${h.text_field('q', id='q', value=c.q, title='Enter an address or route', tabindex='1')}
				${h.submit(value='Search Map', title='Click to search the map', tabindex='2')}
              </div>
              <div class="input_label">
                Enter an address or intersection -OR- pick a location from the map.
              </div>
            ${h.end_form()}
          </div>
          <!-- Query Pane -->


          <!-- Route Pane -->
          <div id="find-a-route" class="tab-content">
            ${h.form(h.url_for('/%s/route' % c.region_key), method='get', id='route_form')}
              <div>
				${h.text_field('s', id='s', value=c.s, title='Enter start address', tabindex='3')}<a
				  id="swap_s_and_e"
				  href="#swap-start-and-end"
				  onclick="return false;"
				  title="Swap start and end addresses"
				  tabindex="4"
				>${h.image_tag('swapfrto.png', alt='&lt;&rt;', width='24', height=14)}</a>${h.text_field('e', id='e', value=c.e, title='Enter end address', tabindex='5')}

				${c.route_pref}
				${h.submit(value='Find Route', title='Click to find a route', tabindex='9')}
              </div>

              <div class="input_label">
                Enter your start and end addresses and, optionally, select a route type.
              </div>
            ${h.end_form()}
          </div>
          <!-- End Route Pane -->


        </div>
		<!-- End Input Tab Contents -->


      </div>
      <!-- End Input Container -->


      <div class="clear"></div>
    </div>
    <!-- End Header -->


    <!-- Bar -->
    <div id="bar">


      <div id="status">
		% if c.status:
		  ${c.status}
		% else:
		  Welcome to the
		  <a href="http://bycycle.org/"
			 title="byCycle Home Page (opens in new window)"
			 target="byCyle_window"
			 >byCycle</a> bicycle trip planner.
	  </div>


      <!-- Links -->
      <div id="links">
        <a id="bookmark" href="${h.url_for('/')}"
          title="Link to the current result &amp; view"
          >Link to this page</a>
        |
        <a href="http://bycycle.org/projects/trip-planner/help"
           title="Trip Planner help page (opens in new window)"
           target="byCyle_window"
           >Help</a>
        |
        <a href="http://bycycle.org/contact"
           title="Send us your comments, questions, suggestions, etc (opens in new window)"
           target="byCyle_window"
           >Feedback</a>
      </div>
      <!-- End Links -->


      <div class="clear"></div>
    </div>
    <!-- End Bar -->


    <!-- Content -->
    <div id="content">


      <!-- Column A -->
      <div id="col-a">


        <div id="spinner" class="spinner" style="display: none;">
          ${h.image_tag('spinner.gif', width=16, height=16)}
        </div>


        <!-- Message Pane -->
        <div id="message_pane">
          <div id="info_pane">
			% if c.info:
  			  ${c.info}
			% else:
			  <p class="first_p">
				The trip planner is under active development. Please
				<a href="http://www.bycycle.org/contact"
				   title="Send us problems, comments, questions, &amp; suggestions (opens in new window)"
				   target="byCyle_window"
				   >contact us</a>
				   with any problems, comments, questions, or suggestions.
			  </p>

			  <p>
				If you find this application useful or would like to contribute to its improvement, please consider
				<a href="http://bycycle.org/support/donate"
				   title="Support byCycle (opens in new window)"
				   target="byCyle_window">donating</a>,
				<a href="http://bycycle.org/support/buy-stuff"
				   title="Buy byCycle stuff"
				   target="byCyle_window">buying byCycle apparel or other items</a>, or
				<a href="http://bycycle.org/support/get-involved"
				   title="Get Involved"
				   target="byCyclewindow">getting involved</a>.
			  </p>

			  <p>
				Users should independently verify all information presented here. This
				service is provided <b>AS IS</b> with <b>NO WARRANTY</b> of any kind.
				<em>Please be careful out there.</em>
			  </p>
			% endif
		  </div>
          <div id="error_pane">${c.errors}</div>
          <div id="help_pane"></div>
        </div>
        <!-- End Message Pane -->


        <!-- Result Pane -->
        <div id="result_pane">
          <ul id="location_list" class="result_list"></ul>
          <ul id="route_list" class="result_list"></ul>
        </div>
        <!-- End Result Pane -->


      </div>
      <!-- End Column A -->


      <!-- Column B -->
      <div id="col-b">


        <!-- Map Menu -->
        <div id="map_menu">
          Region:
          <select id="regions" name="region">
            <option value="all">All Regions</option>
            ${h.options_for_select(c.region_options, selected=c.region_key)}
          </select>
          Map Mode:
          <select id="map_mode">
            <option value="">Default</option>
			<option value="identifyIntersection">Identify Intersection</option>
			<option value="identifyStreet">Identify Street</option>
          </select>
          <a href="#clear-map-and-results"
             title="Clear all results and map"
			 onclick="byCycle.UI.clearResults(); return false;"
			 >Clear All</a>
        </div>
        <!-- End Map Menu -->


        <!-- Map -->
        <div id="map_pane">
          <div id="map_message" style="display: none; padding: 5px;">
            You will need to update to a recent version of Internet Explorer, Firefox, or Safari to view the map.
          </div>
        </div>
        <!-- End Map -->


      </div>
      <!-- End Column B -->


      <div class="clear"></div>
    </div>
    <!-- End Content -->


    <!-- Footer -->
    <div id="footer">
      &nbsp;&copy; 2004 - 2007 <a href="http://byCycle.org/" title="byCycle Home Page">byCycle.org</a>
      &middot;
      Hosted by <a href="http://www.metro-region.org/">Metro</a>
    </div>
    <!-- End Footer -->


    <!-- Loading -->
    <div id="loading" style="display: none;">
      <h2>
        <div class="spinner">
          ${h.image_tag('spinner.gif', width=16, height=16)}
        </div>
        Loading. Please wait...
      </h2>
      <p id="loading_status"></p>
    </div>
    <!-- End Loading -->


    <!-- Ads -->
    <div id="ads">
      <div id="ad_title_bar">
        <a href="" id="hide_ads_button" title="Hide Ads">Hide Ads</a>
      </div>
      ${h.javascript_include_tag('ads')}
    </div>
    <!-- End Ads -->


	<% js_files = ('regions', 'map', 'gmap', 'ui', 'query', 'result', 'widgets/tabinator') %>
    ${h.javascript_include_tag(*js_files)}


    <script type="text/javascript">
      //<![CDATA[
      // Set up for initialization
      byCycle.UI.beforeLoad();
      // Values calculated in the controller
      // Only set status when there's a result
      byCycle.UI.http_status = ${c.http_status};
      byCycle.UI.region = '${c.region_key}';
      byCycle.UI.service = '${c.service}';
      byCycle.UI.query = '${c.q}';
      //]]>
    </script>


	<!-- TODO: Maybe we could get this dynamically the first time it's needed? -->
	<%include file="/_center_marker.html" />


  </body>
</html>
