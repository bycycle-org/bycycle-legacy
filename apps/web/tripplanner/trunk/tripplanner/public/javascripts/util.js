window.util = {
  keys: function (obj) {
    var keys = [];
    for (var key in obj) {
      keys.push(key);
    }
    return keys;
  },

  values: function (obj) {
    var values = [];
    for (var key in obj) {
      values.push(obj[key]);
    }
    return values;
  },

  items: function (obj) {
    var items = [];
    for (var key in obj) {
      items.push(obj[key]);
    }
    return items;
  },

  /** Script Functions **/

  writeScript: function(src, type) {
    type = type || 'text/javascript';
    document.write('<script src="' + src + '" type="' + type + '"></script>');
  },

  appendScript: function(src, type) {
    var script = document.createElement('script');
    script.type = type || 'text/javascript';
    script.src = src;
    document.body.appendChild(script);
  },

  /** String Functions **/

  /**
   * Remove leading and trailing whitespace from a string and
   * reduce internal runs of whitespace down to a single space.
   * @param the_string The string to clean
   * @param keep_newlines If this is set, reduce internal newlines to a single
   *        newline instead of a space
   * @return The cleaned string
   */
  cleanString: function(the_string, keep_newlines) {
    if (!the_string) { return ''; }
    // Remove leading and trailing whitespace
    the_string = the_string.replace(/^\s+|\s+$/g, '');
    // Reduce internal whitespace
    if (keep_newlines) {
      //the_string = the_string.replace(/[ \f\t\u00A0\u2028\u2029]+/, ' ');
      the_string = the_string.replace(/[^\n^\r\s]+/, ' ');
      the_string = the_string.replace(/\n+/g, '\n');
      the_string = the_string.replace(/\r+/g, '\r');
      the_string = the_string.replace(/(?:\r\n)+/g, '\r\n');
    } else {
      the_string = the_string.replace(/\s+/g, ' ');
    }
    return the_string;
  },

  /**
   * Remove leading and trailing whitespace from a string.
   *
   * @param the_string The string to trim
   * @return The trimmed string
   */
  trim: function(the_string) {
    return the_string.replace(/^\s+|\s+$/g, '');
  },

  /**
   * Join a list of strings, separated by the given string, excluding any empty
   * strings in the input list.
   *
   * @param the_list The list to join
   * @param the_string The string to insert between each string in the list
   *        (default: ' ')
   * @return The joined string
   */
  join: function(the_list, join_string) {
    join_string = join_string || ' ';
    var new_list = [];
    for (var i = 0; i < the_list.length; ++i) {
      word = _trim(the_list[i]);
      if (word) { new_list.push(word); }
    }
    return new_list.join(join_string);
  }
};


window.NameSpace = function (name, parent, definition) {
  var ns = definition || {};
  ns.__name__ = name;
  ns.__parent__ = parent;
  parent[name] = ns;
  return ns;
};


window.Class = function (namespace, name, base, definition) {
  base = base || Function;
  definition = definition || {};
  // Create the skeleton of the class. The statements in this function will
  // be called whenever ``new <namespace>.<name>`` is called (that is,
  // whenever an instance is created from the class.
  var cls = function () {
    this.superclass = cls.superclass;
    this.initialize.apply(this, arguments);
  };
  // Set "special" class attributes.
  cls.superclass = base.prototype;
  cls.__name__ = name;
  cls.__namespace__ = namespace;
  // Set class's initial attributes to base class's attributes.
  cls.prototype = {};
  for (var attr in base.prototype) {
    cls.prototype[attr] = base.prototype[attr];
  }
  // Add user-friendly default toString method.
  var default_string_value = ['<class ', name, '>'].join('');
  cls.prototype.toString = function () {
    return default_string_value;
  };
  cls.prototype.__class__ = cls;
  // Add class attributes, overriding base class attributes.
  for (var attr in definition) {
    cls.prototype[attr] = definition[attr];
  }
  // Ensure the class has an initialization method.
  var initialize = cls.prototype.initialize;
  cls.prototype.initialize = initialize || function () {};
  // Set the class's constructor to the function defined above.
  cls.prototype.constructor = cls;
  // Add the class to the specified namespace/namespace.
  namespace[name] = cls;
  // Added this because it might be useful in certain scenarios.
  return cls;
};
