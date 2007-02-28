/**
 * FixedPane -- A window-like pane that sits in a fixed position.
 *
 * A pane instance has a title on top and can be open, collapsed, or closed.
 */
byCycle.widget.FixedPane = Class.create();
byCycle.widget.FixedPane.prototype = {

  // Default properties
  open: true,
  collapsible: true,
  closeable: true,

  /**
   * @param dom_node The DOM container for this control
   */
  initialize: function (dom_node, opts) {
    this.dom_node = $(dom_node);
    this.title_bar = this.dom_node.getElementsByClassName('title-bar')[0];
    this.title = this.title_bar.getElementsByClassName('title')[0].innerHTML;
    var content_pane = this.dom_node.getElementsByClassName('content-pane')[0];
    this.header = content_pane.getElementsByClassName('header')[0];
    this.body = content_pane.getElementsByClassName('body')[0];
    this.footer = content_pane.getElementsByClassName('footer')[0];
    this.content_pane = content_pane;
    this._create_controls();
    !this.open && this.content_pane.hide();
  },

  _create_controls: function () {
    byCycle.logDebug('Creating fixed pane controls...');
    if (!(this.collapsible || this.closeable)) return;

    // Create and append the control bar
    this.control_bar = document.createElement('div');
    this.control_bar.addClassName('control-bar');
    this.title_bar.appendChild(this.control_bar);

    if (this.collapsible) {
      byCycle.logDebug('Creating _ control...');
      this._add_button('toggle', 'Hide window content', '_', this.on_collapse);
    }
    
    if (this.closeable) {
      byCycle.logDebug('Creating X control...');
      this._add_button('close', 'Close window', 'X', this.on_close);
    }
  },

  _add_button: function (href, title, text, func) {
    var a = document.createElement('a');
    a.addClassName('button');
    a.href = href;
    a.title = title;
    a.innerHTML = text;
    Event.observe(a, 'click', func.bindAsEventListener(this));
    this.control_bar.appendChild(a);
  },

  on_collapse: function (event) {
    event && Event.stop(event);
    this._run_listeners('collapse');
    this.content_pane.toggle();
  },

  on_close: function (event) {
    event && Event.stop(event);
    this._run_listeners('close');
    this.dom_node.remove();
  },

  // TODO: Refactor to Widget superclass
  register_listeners: function (event_name /*, funcs */) {
    var listeners = this._get_listeners(event_name);
    for (var i = 1; i < arguments.length; ++i) {
      listeners.push(arguments[i]);
    }
  },

  _get_listeners: function (event_name) {
    var list_name = ['on', event_name, 'listeners'].join('_');
    var listeners = this[list_name];
    if (typeof listeners == 'undefined') {
      this[list_name] = [];
      listeners = this[list_name];
    }
    return listeners;
  },

  _run_listeners: function (event_name) {
    var listeners = this._get_listeners(event_name);
    if (listeners.length) {
      var self = this;
      listeners.each(function (h) { h(self); });
    }
  }
};
