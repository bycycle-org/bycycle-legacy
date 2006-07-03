/**
 * byCycle namespace
 */
var byCycle = (function() {
  var debug = 1;
  var base_url = location.href.split('?')[0];
  var domain = base_url.split('/')[2];

  var _public = {
    debug: debug,

    local: 1,

    no_map: 1,

    // The URL minus the query string
    base_url: base_url,
    
    // Just the domain part of the URL
    domain: domain,

    log: function() {
      if (arguments.length < 1) return;
      var msgs = [];
      for (var i = 0; i < arguments.length; ++i) {
	msgs.push(arguments[i]);
      }
      var msg = msgs.join('\n');
      if (msg) {
	alert(msg);
      }
    }
  }

  if (debug) {
    MochiKit.LoggingPane.createLoggingPane();
    _public.log = MochiKit.Logging.log;
  }

  return _public;
})();

