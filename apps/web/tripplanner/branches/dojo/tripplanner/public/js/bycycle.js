$ = dojo.byId;

/**
 * byCycle namespace
 */
var byCycle = (function() {
  // private:
  var _prod_config = {
    local: 0,
    map_type: 'google',
    map_state: 1
  };

  var _dev_config = {
    local: 1,
    map_type: 'base',
    map_state: 1
  };

  var base_url = location.href.split('?')[0];
  var domain = base_url.split('/')[2];
  var index = 0;
  var colors = ['#fff', '#ccc'];

  var pairs = window.location.search.substr(1).split('&');
  var _query_pairs = {};
  for (var i = 0; i < pairs.length; ++i) {
    var name_value = pairs[i].split('=');
    _query_pairs[name_value[0]] = name_value[1];
  }

  var noop = function() {};

  // public:
  return {
    // `debug` is a global set in the template; it's value is passed from 
    // Pylons as an attribute of the global `g`
    config: debug ? _dev_config : _prod_config,
    base_url: base_url,
    domain: domain,
    prefix: byCycle_prefix,
    query_pairs: _query_pairs,
    default_map_type: 'base',

    noop: noop,
    
    /**
     * Get value for variable from query string if possible, otherwise use the
     * global config value
     */
    getParamVal: function(var_name, func) {
      var v = byCycle.query_pairs[var_name];
      if (typeof(v) == 'undefined') {
        v = byCycle.config[var_name];
      } else if (typeof(func) == 'function') {
        // Override config setting with query string setting
        v = func(v);
      }
      return v;
    },

    logDebug: (debug ? dojo.debug : noop),
  };
})();
