/**
 * byCycle namespace
 */
var byCycle = (function() {
  // private:
  var prod_config = {
    local: 0,
    map_type: 'google',
    map_state: 1
  };

  var dev_config = {
    local: 1,
    map_type: 'base',
    map_state: 1
  };

  var base_url = location.href.split('?')[0];
  var domain = base_url.split('/')[2];
  var query_pairs = (window.location.search.substr(1)).toQueryParams();
  
  var noop = function() {};

  // public:
  return {
    // `debug` is a global set in the template; it's value is passed from 
    // Pylons as an attribute of the global `g`
    config: debug ? dev_config : prod_config,
    
    base_url: base_url,
    domain: domain,
    
    // Prefix for when app is mounted at other than root (/)
    prefix: byCycle_prefix,
    
    // URL query parameters as a Hash
    query_pairs: query_pairs,

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

    logDebug: (debug ? console.log : noop),
  };
})();
