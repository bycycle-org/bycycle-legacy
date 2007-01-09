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

    <script type="text/javascript">
      //<![CDATA[
      var debug = <% ['false', 'true'][bool(g.debug)] %>;
      //]]>
    </script>

    <!-- We want access to these JavaScripts during page load. Other JS imports
    at bottom of page. -->
    <% h.javascript_include_tag(builtins=True) %>
    <% h.javascript_include_tag('/js/bycycle.js') %>
    <% h.javascript_include_tag('/js/util.js') %>
  </head>


  <body>


% if g.debug:
    <div style="position: abosolute; top: 0; left: 0; background: white; border: 1px solid gray;">
      <% c.my_env %>
    </div>
% #if

    <div id="top" class="page_section">
      <table>
        <tbody>
          <tr>


            <td id="logo_cell">
              <div id="logo">
                <a href=""
                   title="byCycle Trip Planner"
                   ><img src="<% h.url_for('/images/logo.png') %>" width="93" height="66" /></a>
              </div>
            </td>


            <td style="padding: 0">
              <!-- Input -->
              <div id="input" class="tab_pane">


                <div class="tab_labels">
                  <div class="clear"></div>
                  <ul>
                    <li class="tab_label <% c.query_label_class %>">
                      <a id="query_label" href="<% h.url_for('/%s/query/' % c.region_key) %>"
                         name='query'
                         title="Search the Map for an Address or Route"
                         >Search Map</a>
                    </li>
                    <li class="tab_label <% c.route_label_class %>">
                      <a id="route_label" href="<% h.url_for('/%s/route/' % c.region_key) %>"
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
                      action="<% h.url_for('/%s/query/' % c.region_key) %>"
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
% if c.status:
                <% c.status %>
% else:
                Welcome to the
                <a href="http://byCycle.org/" title="byCycle Home Page"
                   >byCycle</a> bicycle trip planner.
% #if
              </div>
            </td>


            <td>
              <div id="links">
                <a id="bookmark" href="<% h.url_for('/') %>"
                   onclick="return false;"
                   title="Link to the current result &amp; view"
                   >Link to this page</a>
                |
                <a href="http://byCycle.org/tripplanner/help.html"
                   onclick=""
                   title="Go to Trip Planner help page"
                   >Help</a>
                |
                <a href="http://byCycle.org/contact.html"
                   onclick=""
                   title="Send us your comments, questions, suggestions, etc"
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
              <!-- Display Panel -->
              <div id="display">
                <div id="spinner" style="display: none;">
                  <img src="<% h.url_for('/images/spinner.gif') %>"
                       width="16" height="16"/>
                </div>

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
                       title="Donate"
                       target="_new"
                       >donating</a>.
                    Any amount helps.
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
              <!-- End Display Panel -->
            </td>


            <td>
              <div id="map_container">
                <div id="map_menu">
                  <!-- Region -->
                  <span id="regions_container">
                    <a id="change_region_link"
                       href="#change-region"
                       title="Change region"
                       onclick="Element.show('regions_window'); return false;"
                       >Region</a>:

                    <span id="active_region"><% region %></span>

                    <& /widgets/window.myt, id='regions_window',
                                            title='Change Region',
                                            display='none', toggleable=True,
                                            content=m.scomp('/region/_regions_form.myt') &>
                  </span>
                  <!-- End Region -->
                   |
                  <a href="#find-address-at-center"
                     title="Find address at center of map (red dot)"
                     onclick="byCycle.UI.findAddressAtCenter(); return false;"
                     >Find Address at Center</a>
                   |
                  <a href="#clear-map-and-results"
                     title="Clear all results and map"
                     onclick="byCycle.UI.clearResults(); return false;"
                     >Clear All...</a>
                </div>

                <div id="map_msg">
                  <noscript>
                    <!-- TODO: Put a non-JS map here (Yahoo?) -->
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
                      <a href="http://www.mozilla.com/">trying it</a> if you
                      haven't already.
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
                
                <!-- Map -->
                <div id="map" style="display: none;"></div>
                <!-- End Map -->

                <div id="center_marker" style="display: none;" width="0" height="0">
                  <div class="info_win">
                    <p>
                      <a href="#find-address-at-center"
                         title="Find address at center of map (red dot)"
                         onclick="byCycle.UI.findAddressAtCenter(); return false;"
                         >Find address of closest intersection</a>
                    </p>

                    <p>
                      Set as
                      <a href="#set-as-start"
                         onclick="byCycle.UI.s_el.value = byCycle.UI.map.getCenterString(); return false;"
                         ><i>start</i></a> or
                      <a href="#set-as-end"
                         onclick="byCycle.UI.e_el.value = byCycle.UI.map.getCenterString(); return false;"
                         ><i>end</i></a>
                      address for route
                    </p>
                  </div>
                </div>
              </div>
            </td>


            <td>
              <!-- Google Ads -->
              <%python> _window_content = h.javascript_include_tag('/js/ads.js') </%python>
              <& /widgets/window.myt, id='ads', title='', display='none',
                                      close_handler='byCycle.UI.hideAds()',
                                      content=_window_content &>
            </td>


          </tr>
        </tbody>
      </table>
    </div>
    <!-- End Content -->


% if g.debug:
    <& /widgets/window.myt, id='debug_window', toggleable=True,
                            closeable=False,
                            title='Debug Log', display='none',
                            content_style='height: 300px; overflow: auto;' &>
% #if


    <script type="text/javascript">
      //<![CDATA[
      byCycle.prefix = '<% h.url_for('/') %>';
      //]]>
    </script>

% for js in ('regions', 'map', 'gmap', 'ui'):
    <% h.javascript_include_tag('/js/%s.js' % js) %>
% #for

    <script type="text/javascript">
      //<![CDATA[
      byCycle.UI.beforeLoad();
      // Values calculated in the controller
      // Only set status when there's a result
      byCycle.UI.http_status = <% c.http_status or 'null' %>;
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
