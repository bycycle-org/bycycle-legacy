/**
 * byCycle namespace
 */
NameSpace('byCycle', window, function() {
  // private:
  var prod_config = {
    local: 0,
    map_state: 1
  };

  var dev_config = {
    local: 1,
    map_state: 1
  };

  var noop = function() {};

  var console_debug = function() {
    console.debug.apply(console, arguments);
  }

  var hostname = location.hostname;
  var port = location.port;

  var makeParams = function () {
    var params = {};
    var query_string = window.location.search.substring(1);
    var pairs = query_string.split('&');
    for (var name_value, i = 0; i < pairs.length; ++i) {
      name_value = pairs[i].split('=');
      params[name_value[0]] = name_value[1];
    }
    return params;
  };

  // public:
  return {
    // `debug` is a global set in the template; it's value is passed from
    // Pylons as an attribute of the global `g`
    config: debug ? dev_config : prod_config,

    // Used to look Google API key in gmap.js and to make queries in ui.js
    domain: (port ? [hostname, port].join(':') : hostname),

    // URL query parameters as a Hash
    request_params: makeParams(),

    default_map_type: 'base',

    noop: noop,

    // Namespace for byCycle widgets
    widget: {},

    /**
     * Get value for variable from query string if possible, otherwise use the
     * global config value
     */
    getParamVal: function(var_name, func) {
      // Override config setting with query string setting
      var v = byCycle.request_params[var_name];
      if (typeof(v) == 'undefined') {
	   // Query string override not given; use config
        v = byCycle.config[var_name];
      } else if (typeof(func) == 'function') {
        // Process query string value with func, iff given
        v = func(v);
      }
      return v;
    },

    logDebug: (debug ? console_debug : noop)
  };
}());
