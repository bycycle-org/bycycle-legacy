/** byCycle namespace
 *
 * Depends on `util` module and defines JS-library-specific utility functions.
 */
NameSpace('APP', window, function() {
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
	  YAHOO.util.Connect.asyncRequest(
		'GET', APP.prefix + 'regions?format=json&wrap=off',
		{
		  success: function (response) {
			var result = YAHOO.lang.JSON.parse(response.responseText);

			APP.regions.initialize(result);
			if (APP.region_id) {
			  APP.region = APP.regions.regions[APP.region_id];
			} else {
			  APP.region_id = 'all';
			  APP.region = APP.regions[APP.region_id];
			}

			var map_state = util.getParamVal('map_state', function (ms) {
			  // Convert `map_state` param value to boolean.
			  return ms === '' || ms == '0' || ms == 'off';
			});
			var map_type_name = (util.getParamVal('map_type') || '');
			map_type_name = map_type_name.toLowerCase();
			map_type_name = map_type_name || APP.region.map_type;

			APP.UI.map_state = map_state;
			APP.UI.map_type = APP.Map.base;
			var url = [
			  APP.prefix, 'javascripts/',  map_type_name, '.js'].join('');
			YAHOO.util.Get.script(url, {
			  onSuccess: function () {
				APP.UI.map_type = APP.Map[map_type_name];
				APP.UI.onLoad();
			  }
			});
		  }
		}
	  );
	},

	/* Library specific utilities */

	el: function (id) {
	  return new YAHOO.util.Element(id);
	}
  };
}());
