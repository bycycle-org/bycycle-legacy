/** byCycle namespace
 *
 * Depends on `util` module and defines JS-library-specific utility functions.
 */
NameSpace('app', window, function() {
  var prod_config = {
    local: 0,
    map_state: 1
  };

  var dev_config = {
    local: 1,
    map_state: 1
  };

  return {
    // `debug` is a global set in the template; it's value is passed from
    // Pylons as an attribute of the global `g`.
    config: debug ? dev_config : prod_config,

    onLoad: function () {
      // Do region-dependent initialization, which includes initializing the
      // main UI module.
      var url = app.prefix + 'regions?format=json&wrap=off';
      YAHOO.util.Connect.asyncRequest('GET', url, {
        success: function (response) {
          var result = YAHOO.lang.JSON.parse(response.responseText);

          app.regions.initialize(result);
          if (app.region_id) {
            app.region = app.regions.regions[app.region_id];
          } else {
            app.region_id = 'all';
            app.region = app.regions[app.region_id];
          }

          var map_state = util.getParamVal('map_state', function (ms) {
            // Convert `map_state` param value to boolean.
            return ms === '' || ms == '0' || ms == 'off';
          });
          var map_type_name = (util.getParamVal('map_type') || '');
          map_type_name = map_type_name.toLowerCase();
          map_type_name = map_type_name || app.region.map_type;

          app.ui.map_state = map_state;
          app.ui.map_type = app.Map.base;
          var url = [app.prefix, 'javascripts/',  map_type_name, '.js'].join('');
          YAHOO.util.Get.script(url, {
            onSuccess: function () {
              app.ui.map_type = app.Map[map_type_name];
              app.ui.onLoad();
            }
          });
        }
      });
    },

    /* Library specific utilities */

    el: function (id) {
      return new Element(id);
    }
  };
}());
