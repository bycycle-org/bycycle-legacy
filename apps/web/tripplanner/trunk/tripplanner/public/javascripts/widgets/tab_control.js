/**
 * Tabinator Tab control
 */
Class(byCycle.widget, 'TabControl', null, {
  /**
   * @param dom_node The DOM container (or its ID) for this Tab control
   */
  initialize: function(dom_node, initial_tab_id) {
    this.dom_node = $(dom_node);
    this.create_tabs();
    if (initial_tab_id) {
      this.select_by_id(initial_tab_id);
    } else {
      this.show(this.get_initial_tab());
    }
  },

  create_tabs: function() {
    // An individual Tab object. Contains tab id, button, link, and content.
    var tab;
    // All the Tabs in this Tab control (usually a DIV)
    var tabs = {};
    var tab_ids_in_order = [];
    // Get the Tab buttons (usually LIs)
    var tab_buttons = this.dom_node.find('.tab-buttons .tab-button');
    console.debug(tab_buttons)
    var self = this;
    // For each Tab button...
    $.each(tab_buttons, function (tab_button) {
      tab_button = $(tab_button);
      // ...get the link (A) inside the button
      var tab_link = tab_button.find('a');
      console.debug(tab_link);
      // ...see if the link has a Tab ID (href="#id")
      var tab_id = self.get_tab_id(tab_link);
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
        tab_ids_in_order.push(tab_id);
        tab_link.click(self.on_click)
        if (!self.first_tab) {
          self.first_tab = tab;
        }
      }
    });
    this.tabs = tabs;
    this.tab_ids_in_order = tab_ids_in_order;
  },

  on_click: function(event) {
    // Select tab on click event
    Event.stop(event);
    var tab_link = Event.findElement(event, 'a');
    this.select_by_id(tab_link.tab_id);
  },

  select: function(index) {
    // Select tab programatically by index
    if (index < 0) {
      // Allow indexing from end using negative index
      index = this.tab_ids_in_order.length + index
    }
    this.select_by_id(this.tab_ids_in_order[index]);
  },

  select_by_id: function(tab_id) {
    // Select tab programatically by ID
    $.each(util.values(this.tabs), function (tab) {
      $(tab).hide();
    });
    this.show(this.tabs[tab_id]);
  },

  hide: function(tab) {
    tab.button.removeClass('selected-tab-button');
    tab.content.removeClass('selected-tab-content');
    tab.content.addClass('tab-content');
  },

  show: function(tab) {
    tab.button.addClass('selected-tab-button');
    tab.content.addClass('selected-tab-content');
    tab.content.removeClass('tab-content');
  },

  /**
   * Return the tab ID for a link. The tab ID is the hash part of a URL.
   *
   * @param tab_link An <A>nchor DOM element (or any obj with href attribute).
   */
  get_tab_id: function(tab_link) {
    var id = tab_link.href.match(/#(\w.+)/);
    if (id) {
      return id[1];
    } else {
      return null;
    }
  },

  get_initial_tab: function() {
    var initial_tab;
    var initial_tab_id = this.get_tab_id(window.location);
    if (initial_tab_id) {
      initial_tab = this.tabs[initial_tab_id];
    }
    return initial_tab || this.first_tab;
  }
});
