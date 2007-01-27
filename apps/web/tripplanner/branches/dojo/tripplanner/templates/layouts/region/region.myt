<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:v="urn:schemas-microsoft-com:vml">


  <head>


    <meta http-equiv="Content-Type"
          content="application/xhtml+xml; charset=utf-8" />

    <meta name="keywords"
          content="bicycle, bike, bicycle trip planner, bicycle route finder, bike trip planner, bike route finder, bicycle route, bicycle trip, bike route, bike trip, bicycle routing, bike routing, maps, bicycle maps, bike maps, bicycle advocacy, community, sustainability, portland, oregon, milwaukee, wisconsin" />

    <meta name="description"
          content="byCycle.org Bicycle Trip Planner -- A web-based, interactive, bicycle trip planner (route finder) for the Portland, Oregon, Milwaukee, Wisconsin, and, soon, other regions." />


    <title>byCycle.org - Bicycle Trip Planner - <% region %></title>


    <% h.stylesheet_link_tag('/css/base.css') %>
    <!--[if IE]>
      <% h.stylesheet_link_tag('/css/base_ie.css') %>
    <![endif]-->
    <% h.stylesheet_link_tag('/css/%s.css' % c.region_key) %>


    <script type="text/javascript">
      //<![CDATA[
      // Global setup
      var debug = <% ['false', 'true'][bool(g.debug)] %>;
      var djConfig = {
        isDebug: debug
      };
      byCycle_prefix = '<% h.url_for('/') %>';
      //]]>
    </script>

    <% h.javascript_include_tag('/js/dojo/dojo.js') %>

    <script type="text/javascript">
      //<![CDATA[
      dojo.require('dojo.event.*');
      dojo.require('dojo.io.*');
      dojo.require('dojo.widget.*');
      dojo.require('dojo.widget.LayoutContainer');
      dojo.require('dojo.widget.TabContainer');
      dojo.require('dojo.widget.SplitContainer');
      dojo.require('dojo.widget.ContentPane');
      dojo.require('dojo.html.display');
      dojo.require('dojo.dom');
      dojo.require("dojo.debug.console");
      //]]>
    </script>

    <% h.javascript_include_tag('/js/bycycle.js') %>
    <% h.javascript_include_tag('/js/util.js') %>
    <% h.javascript_include_tag('/widget/FixedPane.js') %>


  </head>


  <body>


    <div id="loading">
      <h1>byCycle.org Bicycle Trip Planner</h1>
      <h2>Loading. Please wait...</h2>
      <p id="loading_status"></p>
    </div>


    <!-- Root Container -->
    <div id="root_container" dojoType="LayoutContainer">


      <!-- Top Container -->
      <div id="top_container" dojoType="LayoutContainer" layoutAlign="top">


        <!-- Logo Pane -->
        <div id="logo_pane" dojoType="ContentPane" layoutAlign="left">
          <a href=""
             title="byCycle Trip Planner"
             ><img src="<% h.url_for('/images/logo.png') %>"
                   width="93" height="66" /></a>
        </div>
        <!-- End Logo Pane -->


        <!-- Input Container -->
        <div id="input_container" dojoType="TabContainer" layoutAlign="client">


          <!-- Query Pane -->
          <div id="query_pane" dojoType="ContentPane" label="Search Map">
            <form
              id="query_form"
              action="<% h.url_for('/%s/query/' % c.region_key) %>"
              method="get"
              onsubmit="byCycle.UI.runQuery(this); return false;">

              <div>
                <input
                  id="q" name="q" type="text" value="<% c.q %>"
                  title="Enter an address or route" tabindex="1" />
                <input
                  name="commit" type="submit" value="Search Map"
                  title="Click to search the map" tabindex="2" />
              </div>

              <div class="input_label">
                Enter an address or intersection -OR- pick a location
                from the map.
              </div>
            </form>
          </div>
          <!-- Query Pane -->


          <!-- Route Pane -->
          <div id="route_pane" dojoType="ContentPane" label="Find Route">
            <form
              id="route_form"
              action="<% h.url_for('/%s/route/' % c.region_key) %>"
              method="get"
              onsubmit="new byCycle.UI.RouteQuery(this).run(); return false;">

              <div>
                <!-- This is laid out like this intentionally to
                control the display of these elements. -->
                <input
                  id="s" name="s"
                  type="text"
                  value="<% c.s %>"
                  title="Enter start address"
                  tabindex="4"
                /><a
                    id="swap_s_and_e"
                    href="#swap-start-and-end"
                    onclick="return false;"
                    title="Swap start and end addresses"
                    tabindex="5"
                  ><img
                      src="<% h.url_for('/images/swapfrto.png') %>"
                      alt="&lt;>"
                      width="24"
                      height="14"
                    /></a><input
                  id="e" name="e"
                  type="text"
                  value="<% c.e %>"
                  title="Enter end address"
                  tabindex="6"
                />

                <% route_pref %>
                <input name="commit" type="submit" value="Find Route"
                       title="Click to find a route" tabindex="9" />
              </div>

              <div class="input_label">
                Enter your start and end addresses and, optionally,
                select a route type.
              </div>
            </form>
          </div>
          <!-- End Route Pane -->


        </div>
        <!-- End Input Container -->


      </div>
      <!-- End Top Container -->


      <!-- Content Pane -->
      <div id="content_pane" dojoType="LayoutContainer" layoutAlign="client">


        <!-- Bar -->
        <div id="bar" dojoType="LayoutContainer" layoutAlign="top">


          <!-- Status -->
          <div id="status_pane" dojoType="ContentPane" layoutAlign="client">
            <div id="spinner" style="display: none;">
              <img src="<% h.url_for('/images/spinner.gif') %>"
                   width="16" height="16" />
            </div>

            <div id="status">
% if c.status:
              <% c.status %>
% else:
              Welcome to the
              <a href="http://www.bycycle.org/"
                 title="byCycle Home Page (opens in new window)"
                 target="byCyle_window"
                 >byCycle</a> bicycle trip planner.
% #if
            </div>
          </div>
          <!-- End Status -->


          <!-- Links -->
          <div id="links" dojoType="ContentPane" layoutAlign="right">
            <a id="bookmark" href="<% h.url_for('/') %>"
               onclick="return false;"
               title="Link to the current result &amp; view"
               target="byCyle_window"
               >Link to this page</a>
            |
            <a href="http://www.bycycle.org/tripplanner/help"
               onclick=""
               title="Trip Planner help page (opens in new window)"
               target="byCyle_window"
               >Help</a>
            |
            <a href="http://www.bycycle.org/contact"
               onclick=""
               title="Send us your comments, questions, suggestions, etc (opens in new window)"
               target="byCyle_window"
               >Feedback</a>
          </div>
          <!-- End Links -->


        </div>
        <!-- End Bar -->


        <!-- Split -->
        <div dojoType="SplitContainer"
             layoutAlign="client"
             orientation="horizontal"
             sizerWidth="10">


          <!-- Display Container -->
          <div id="display_container" dojoType="LayoutContainer" sizeShare="20">


            <!-- Message Pane -->
            <div id="message_pane" dojoType="ContentPane" layoutAlign="top">

              <!-- Info -->
              <div id="info_pane">
% if not c.info:
                <& /default_info.html &>
% #if
              </div>
              <!-- End Info -->

              <div id="error_pane"><% c.errors %></div>
              <div id="help_pane"></div>
            </div>
            <!-- End Message Pane -->


            <!-- Result Container -->
            <div id="result_container" dojoType="TabContainer" 
                 layoutAlign="client">

              <div id="location_list_pane" dojoType="ContentPane"
                   label="Locations">
                <ul id="location_list" class="result_list"></ul>
              </div>

              <div id="route_list_pane" dojoType="ContentPane"
                   label="Routes">
                <ul id="route_list" class="result_list"></ul>
              </div>

            </div>
            <!-- End Result Container -->


          </div>
          <!-- End Display Container -->


          <!-- Map Container -->
          <div id="map_container" dojoType="LayoutContainer" sizeShare="80">

            <!-- Map Menu -->
            <div id="map_menu" dojoType="ContentPane" layoutAlign="top">

              Region:
              <select id="regions" name="region">
                <option value="all">All Regions</option>
                <% c.region_options %>
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

              <& /_center_marker.html &>

            </div>
            <!-- End Map Menu -->


            <!-- Map -->
            <div id="map_pane" dojoType="ContentPane" layoutAlign="client">
            </div>
            <!-- End Map -->


          </div>
          <!-- End Map Container -->


        </div>
        <!-- End Split -->


      </div>
      <!-- End Content Pane -->


    </div>
    <!-- End Root Container -->


    <% h.javascript_include_tag('/js/regions.js') %>
    <% h.javascript_include_tag('/js/map.js') %>
    <% h.javascript_include_tag('/js/gmap.js') %>
    <% h.javascript_include_tag('/js/ui.js') %>
    <% h.javascript_include_tag('/js/result.js') %>

    <script type="text/javascript">
      //<![CDATA[
      // Set up for initialization
      byCycle.UI.beforeLoad();
      // Values calculated in the controller
      // Only set status when there's a result
      byCycle.UI.http_status = <% c.http_status or 'null' %>;
      byCycle.UI.region = '<% c.region_key or 'all' %>';
      byCycle.UI.service = '<% c.service_name or 'query' %>';
      byCycle.UI.query = '<% c.service_name or 'null' %>';
      //]]>
    </script>


  </body>


</html>


<%args>
    region = 'All Regions'
    route_pref = None
    result = None
    map_menu = None
</%args>
