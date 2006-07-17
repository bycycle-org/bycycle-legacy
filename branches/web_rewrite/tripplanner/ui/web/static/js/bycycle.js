var _prod_config = {
  debug: 0,
  local: 0,
  map_type: 'Google',
  map_state: 1
};

var _dev_config = {
  debug: 1,
  local: 1,
  map_type: 'Base',
  map_state: 1
};


/**
 * byCycle namespace
 */
var byCycle = (function() {
  var config = _dev_config;
  var base_url = location.href.split('?')[0];
  var domain = base_url.split('/')[2];
  
  var _public = {
    config: config,
    debug: config.debug, // expose directly for convenience
    base_url: base_url,
    domain: domain,
    query_pairs: parseQueryString(window.location.search.substr(1)),
    default_map_type: 'Base',

    /**
     * Get value for variable from query string if possible, otherwise use the
     * global config value
     */
    getVal: function(var_name, func) {
      var v = byCycle.query_pairs[var_name];
      if (typeof(v) == 'undefined') {
	v = byCycle.config[var_name];
      } else if (typeof(func) == 'function') {
	// Override config setting with query string setting
	logDebug('Overriding config', var_name);
	v = func(v);
      }
      return v;
    },

    logInfo: function() {
      if (arguments.length < 1) return;
      var msgs = [];
      for (var i = 0; i < arguments.length; ++i) {
	msgs.push(arguments[i]);
      }
      var msg = msgs.join('\n');
      if (msg) {
	alert(msg);
      }
    },

    logDebug: function() {
      // TODO: Send email to admin?
    }
  };

  if (config.debug) {
    //MochiKit.LoggingPane.createLoggingPane();
    _public.logInfo = MochiKit.Logging.log;
    _public.logDebug = MochiKit.Logging.logDebug;
  }

  return _public;
})();

