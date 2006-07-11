var prod_config = {
  debug: 0,
  local: 0,
  map_state: 1
};

var dev_config = {
  debug: 1,
  local: 1,
  map_state: 0
};


/**
 * byCycle namespace
 */
var byCycle = (function() {
  /* Config */
  var config = dev_config;

  /* Dynamically discovered config */
  var base_url = location.href.split('?')[0];
  var domain = base_url.split('/')[2];

  /* Query string config */
  var query_pairs = parseQueryString(window.location.search.substr(1));
  var map_state = query_pairs.map_state;
  var map_state = ((typeof(map_state) != 'undefined' && 
		    (map_state == '1' || map_state == 'on')) || 
		   config.map_state);
  
  var _public = {
    debug: config.debug,
    local: config.local,
    map_state: map_state,
    base_url: base_url,
    domain: domain,

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

