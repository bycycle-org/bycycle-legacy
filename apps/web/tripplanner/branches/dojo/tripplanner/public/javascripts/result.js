/**
 * Result Base Class
 *
 * ``id`` Unique ID for this result
 * ``result`` Object representing the result (Evaled JSON string)
 */
byCycle.UI.Result = function(id, result) {
  this.id = id;
  this.result = result;
  this.map = byCycle.UI.map;
  this.overlays = [];
};

byCycle.UI.Result.prototype = {
  remove: function() {
    Element.remove(this.id);
    for (var i = 0; i < this.overlays.length; ++i) {
       this.map.removeOverlay(this.overlays[i]);
    }
    delete byCycle.UI.results[this.id];
  }
}


