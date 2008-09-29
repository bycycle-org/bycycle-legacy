/**
 * Result Base Class
 *
 * ``id`` Unique ID for this result
 * ``result`` Object representing the result (Evaled JSON string)
 * ``service`` Service type for the result (i.e., where the result came from)
 */
Class(byCycle.UI, 'Result', null, {
  initialize: function(id, result, service) {
    this.id = id;
    this.result = result;
    this.service = service;
    this.map = byCycle.UI.map;
    this.overlays = [];
  },

  addOverlay: function(overlay) {
    this.overlays.push(overlay);
  },

  remove: function() {
    // Remove LI container
    $j(this.id).parent().remove();
    // Remove map overlays
    var overlay;
    for (var i = 0; i < this.overlays.length; ++i) {
      this.map.removeOverlay(this.overlays[i]);
    }
    // Remove this from results list
    delete byCycle.UI.results[this.service][this.id];
  }
});
