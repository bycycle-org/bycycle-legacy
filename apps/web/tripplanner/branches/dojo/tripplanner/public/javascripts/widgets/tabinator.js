/**
 * Tabinator Tab control
 */
var Tabinator = Class.create();
Tabinator.prototype = {
  /**
   * @param tab_control The DOM container (or its ID) for this Tab control 
   */
  initialize: function(tab_control) {
    this.tab_control = $(tab_control);
    this.tabs = this.createTabs();
    this.show(this.getInitialTab());
  },
  
  createTabs: function() {
    // An individual Tab object. Contains tab id, button, link, and content.
    var tab;
    // All the Tabs in this Tab control (usually a DIV)
    var tabs = {};
    // Get the Tab buttons (usually LIs)
    var tab_buttons = this.tab_control.getElementsByClassName('tab-buttons')[0];
    tab_buttons = tab_buttons.getElementsByClassName('tab-button');
    // For each Tab button...
    tab_buttons.each((function (tab_button) {
      // ...get the link (A) inside the button
      var tab_link = tab_button.getElementsByTagName('a')[0];
      // ...see if the link has a Tab ID (href="#id")
      var tab_id = this.get_tab_id(tab_link);
      // ...and if it does...
      if (tab_id) {
        // ...add a new Tab to this Tab control
        tab = {};
        tab.id = tab_id;
        tab.button = tab_button;
        tab.link = tab_link;
        // When the Tab is clicked, we use this ID to dereference the Tab 
        // object in this Tab control's set of Tabs
        tab.link.tab_id = tab_id;
        // DOM element containing this Tab's content
        tab.content = $(tab_id);
        tabs[tab_id] = tab;
        Event.observe(tab_link, 'click', this.activate.bindAsEventListener(this));
        if (!this.first_tab) {
          this.first_tab = tab;
        }
      }
    }).bind(this));
    return $H(tabs);
  },
  
  activate: function(event) {
    Event.stop(event);
    // Hide all tabs
    this.tabs.values().each(this.hide.bind(this));
    // Activate selected tab
    var tab_link = Event.findElement(event, 'a');
    this.show(this.tabs[tab_link.tab_id]);
  },
  
  hide: function(tab) {
    tab.button.removeClassName('selected-tab-button');
    tab.content.removeClassName('selected-tab-content');
  },
  
  show: function(tab) {
    tab.button.addClassName('selected-tab-button');
    tab.content.addClassName('selected-tab-content');
  },

  /**
   * Return the tab ID for a link. The tab ID is the hash part of a URL.
   *
   * @param tab_link An <A>nchor DOM element
   */
  get_tab_id: function(tab_link) {
    byCycle.logDebug(tab_link);
    var id = tab_link.href.match(/#(\w.+)/);
    if (id) {
      return id[1];
    } else {
      return null;
    }
  },
      
  getInitialTab: function() {
    var initial_tab;
    var initial_tab_id = this.get_tab_id(window.location);
    if (initial_tab_id) {
      initial_tab = this.tabs[initial_tab_id];
    }
    return initial_tab || this.first_tab;
  }
};
