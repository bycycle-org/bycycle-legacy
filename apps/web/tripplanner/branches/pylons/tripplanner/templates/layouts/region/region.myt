<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:v="urn:schemas-microsoft-com:vml">


  <head>
    <meta http-equiv="Content-Type"
          content="application/xhtml+xml; charset=utf-8" />
    <meta name="keywords" content="bicycle, bike, bicycle trip planner, bicycle route finder, bike trip planner, bike route finder, bicycle route, bicycle trip, bike route, bike trip, bicycle routing, bike routing, maps, bicycle maps, bike maps, bicycle advocacy, community, sustainability, portland, oregon, milwaukee, wisconsin" />
    <meta name="description"
          content="byCycle.org Bicycle Trip Planner -- A web-based, interactive, bicycle trip planner (route finder) for the Portland, Oregon, Milwaukee, Wisconsin, and, soon, other regions." />

    <title>byCycle.org - Bicycle Trip Planner - <% region %></title>

    <% h.stylesheet_link_tag('/css/base.css') %>
    <!--[if IE]>
      <% h.stylesheet_link_tag('/css/base_ie.css') %>
    <![endif]-->
    <% h.stylesheet_link_tag('/css/%s.css' % c.region_key) %>

    <!-- We want access to these JavaScripts during page load. Other JS imports
    at bottom of page. -->
    <% h.javascript_include_tag(builtins=True) %>
    <% h.javascript_include_tag('/js/util.js') %>
    <% h.javascript_include_tag('/js/bycycle.js') %>
  </head>


  <body>


  <% c.my_env %>


    <div id="top" class="page_section">
      <table>
        <tbody>
          <tr>


            <td id="logo_cell">
              <div id="logo">
                <a href="/"
                   title="byCycle Trip Planner"
                   ><img src="/images/logo.png" width="93" height="66" /></a>
              </div>
            </td>


            <td style="padding: 0">
              <!-- Input -->
              <div id="input" class="tab_pane">


                <div class="tab_labels">
                  <div class="clear"></div>
                  <ul>
                    <li class="tab_label <% c.query_label_class %>">
                      <a id="query_label" href="/<% c.region_key %>/query/"
                         name='query'
                         title="Search the Map for an Address or Route"
                         >Search Map</a>
                    </li>
                    <li class="tab_label <% c.route_label_class %>">
                      <a id="route_label" href="/<% c.region_key %>/route/"
                         name='route'
                         title="Find a Route (Get Directions)">Find Route</a>
                    </li>
                  </ul>
                  <div class="clear"></div>
                </div>


                <div class="tab_contents">


                  <div class="tab_content" style="<% c.query_tab_style %>">
                    <!-- Query Form -->
                    <form 
                      id="query_form"
                      action="/<% c.region_key %>/query"
                      method="get"
                      onsubmit="new byCycle.UI.SearchQuery(this).run(); return false;">
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


                  <div class="tab_content" style="<% c.route_tab_style %>">
                    <!-- Route Form-->
                    <form 
                      id="route_form"
                      action="/<% c.region_key %>/route"
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
                            href=""
                            onclick="return false;"
                            title="Swap start and end addresses"
                            tabindex="5"
                          ><img
                              src="/images/swapfrto.png"
                              alt="<>"
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
                    <!-- End Route Form -->
                  </div>


                </div>


              </div>
              <!-- End Input -->
            </td>


          </tr>
        </tbody>
      </table>
    </div>


    <div id="middle" class="page_section">
      <table>
        <tbody>
          <tr>


            <td>
              <div id="status">
                <% c.status or
                  'Welcome to the <a href="http://byCycle.org/">byCycle</a> bicycle trip planner.'
                %>
              </div>
            </td>


            <td>
              <div id="links">
                <!-- Region -->
                <span id="regions_container">
                  <b>Region:</b>
                  <span id="active_region"><% region %></span>
                  <a id="change_region_link" href="" 
                    onclick="return false;">change</a>
                  <div id="regions_window" class="window"
                       style="display: none;">
                    <div class="title_bar">
                      <table>
                        <tbody>
                          <tr>
                            <td class="l">Change Region</td>
                            <td class="r">
                              <a class="button" href=""
                                 onclick="Element.hide('regions_window'); return false;"
                                 >X</a>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    <div class="content_pane">
                      <!-- Render a partial, so to speak. -->
                      <& /region/_regions_form.myt &>
                    </div>
                  </div>
                </span>
                <!-- End Region -->
                |
                <a id="bookmark" href="/"
                   title="Link to the current result"
                   >Link to this page</a>
                |
                <a href="" onclick="return false;"
                   title="Show Trip Planner Help"
                   >Help</a>
                |
                <a href="" onclick="return false;"
                   title="Send Us Your Comments, Questions, and Suggestions"
                   >Feedback</a>
              </div>
            </td>


          </tr>
        </tbody>
      </table>
    </div>


    <!-- Content -->
    <div id="content" class="page_section">
      <table>
        <tbody>
          <tr>


            <td>
              <!-- Display Area -->
              <div id="display">
                <div id="info">
% if not c.info:
                  <p style="margin-top: 0;">
                    The trip planner is under active development. Please 
                    <a href="http://bycycle.org/contact.html" 
                       title="Send us problem reports, comments, questions, and suggestions"
                       >contact us</a> with any problems, comments, questions, 
                       or suggestions.
                  </p>
                  <p>
                    If you find this application useful or would like to 
                    contribute to its improvement, please consider 
                    <a href="http://bycycle.org/support.html#donate" 
                       target="_new">donating</a>. Any amount helps.
                  </p>
                  <p>
                    Users should independently verify all information presented
                    here. This service is provided <b>AS IS</b> with <b>NO 
                    WARRANTY</b> of any kind.
                  </p>
% #if
                </div>
                <div id="errors">
                  <% c.errors %>
                </div>
                <div id="results">
                  <% c.result %>
                </div>
                <div id="help">
                  <% c.help %>
                </div>
              </div>
              <!-- End Display Area -->
            </td>


            <td>
              <div id="map_msg">
                <noscript>
                  <!-- TODO: Put a default static map here -->
                  <p>
                    To display a map here, JavaScript must be enabled in your
                    browser. If you would like to view the map, please enable
                    JavaScript and <a href="">try again</a>.
                  </p>
                  <p>
                    Note that you must have a relatively recent browser for 
                    the map to display. We test in Mozilla Firefox 1.5 on 
                    Linux, Mac OS X, and Windows; Safari on Mac OS X; and 
                    Internet Explorer 6 on Windows. Although we try our 
                    best to make the Trip Planner work the same in all of 
                    these browsers, we do the most testing with Firefox, and 
                    as a result it is the best choice for running the Trip
                    Planner. Firefox is a great browser and we recommned 
                    trying it if you haven't already.
                  </p>
                  <p>
                    If you don't have one of the above browsers, you may want 
                    to leave JavaScript turned off. On the other hand, if you 
                    feel like experimenting, you can
                    <a href="http://bycycle.org/contact.html">let us know</a> 
                    if the trip planner does or does not work in other 
                    browsers.
                  </p>
                </noscript>
              </div>

              <div id="map_menu"><% map_menu %></div>

              <!-- Map -->
              <div id="map" style="display: none;"></div>
              <!-- End Map -->
            </td>


            <td>
              <!-- Google Ads -->
              <div id="ads" class="window" style="display: none;">
                <div class="title_bar">
                  <table>
                    <tbody>
                      <tr>
                        <td class="l"></td>
                        <td class="r">
                          <a id="hide_ads" class="button" href="" 
                            onclick="return false;" title="Close Ad Window"
                            >X</a>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="content_pane">
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
              </div>
              <!-- End Google Ads -->
            </td>


          </tr>
        </tbody>
      </table>
    </div>
    <!-- End Content -->


    <div id="debug_window" class="window" style="display: none; position: absolute; bottom: 0; right: 0; width: 300px; background: white;">
      <div class="title_bar">
        <table>
          <tbody>
            <tr>
              <td class="l">Debug Log</td>
              <td class="r">
                <a class="button" href="" 
                   onclick="Element.toggle('debug'); return false;" 
                   title="Show/Hide">#</a>
                <a class="button" href="" 
                   onclick="Element.hide('debug_window'); return false;" 
                   title="Close">X</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div id="debug" class="content_pane" 
           style="height: 300px; overflow: auto;">
      </div>
    </div>


% for js in ('regions', 'map', 'gmap', 'ui'):
    <% h.javascript_include_tag('/js/%s.js' % js) %>
% #for

    <script type="text/javascript">
      //<![CDATA[
      byCycle.UI.beforeLoad();
      // Values calculated in the controller
      byCycle.UI.http_status = <% c.http_status or 200 %>;
      byCycle.UI.region = '<% c.region_key or 'all' %>';
      byCycle.UI.service = '<% c.service_name or 'query' %>';
      //]]>
    </script>
  </body>
</html>


<%doc>
  This template automatically inherits from the autohandler as if we had this:
  <%inherit>
    inherit = 'autohandler'
  </%inherit>
</%doc>

<%args>
    region = 'All Regions'
    route_pref = None
    result = None
    map_menu = None
</%args>
