function echo(str) { document.write(str); }


function writeScript(src, type) {
  var type = type || 'text/javascript';
  document.write('<script src="' + src + '" type="' + type + '"></script>');
}

function appendScript(src, type) {
  var script = document.createElement('script');
  script.type = type || 'text/javascript';
  script.src = src;
  document.getElementsByTagName('head')[0].appendChild(script);
}


function fixScroll()  {
  var div = el("content");
  var content = div.innerHTML;
  div.innerHTML = "<a id='fix_scroll' href=''></a>" + content;
  el("fix_scroll").focus();
}


/* DOM */

function elTag(name)
{
  return document.getElementsByTagName(name);
}

function elTag0(name)
{
  return document.getElementsByTagName(name)[0];
}


/* Element */

function el(id)
{ 
  //GLog.write(id);
  return document.getElementById(id); 
}

function elV(id) 
{ 
  //GLog.write(id);
  return document.getElementById(id).value;
}

function setElV(id, val) 
{ 
  //GLog.write(id);
  document.getElementById(id).value = val; 
}

function elOffset(id)
{
  var offset = 0;
  for (var e = el(id); e != null; e = e.offsetParent) 
    offset += e.offsetTop;
  return offset;
}


/* Element Style */


/**
 * Get the value of an element's style
 * @param style_name The CSS name for the style to get the value of (for 
          standards-compliant browsers)
 * @param ie_style_name The mixed case name for the style to get the value of 
          (for IE when the style name has more than 1 word)
 */
function elStyle(id, style_name, ie_style_name)
{
  var el = document.getElementById(id);
  if (el.currentStyle) {
    return el.currentStyle[ie_style_name];
  } else if (document.defaultView.getComputedStyle) {
    var comp_style = document.defaultView.getComputedStyle(el, '');
    return comp_style.getPropertyValue(style_name);
  }
  return '';
}


/**
 * Set the value of an element's style
 * @param style_name The CSS name for style to set value of (mixed-case)
 * @param value The new value for the style (e.g., "5px")
 */
function setElStyle(id, style_name, value) 
{ 
  // use mixed case for style name
  document.getElementById(id).style[style_name] = value;
}




/* Inner HTML */

function iH(id) { return document.getElementById(id).innerHTML; }
function setIH(id, val) { document.getElementById(id).innerHTML = val; }
function appendIH(id, val) { document.getElementById(id).innerHTML += val; }


/**
 * Swap the values of the two elements with the given IDs.
 * @param id_a ID of element to swap
 * @param id_b ID of other element to swap
 */
function swapElV(id_a, id_b) 
{
  var av = elV(id_a);
  setElV(id_a, elV(id_b));
  setElV(id_b, av);
}


/* Misc */

function getWindowHeight() {
  if (window.self && self.innerHeight) {
    return self.innerHeight;
  }
  else if (document.documentElement && document.documentElement.clientHeight) {
    return document.documentElement.clientHeight;
  } else {
    return 0;
  }
}


/* String */


/**
 * Remove leading and trailing whitespace from a string and
 * reduce internal runs of whitespace down to a single space.
 * @param the_string The string to clean
 * @param keep_newlines If this is set, reduce internal newlines to a single newline instead of a space
 * @return The cleaned string
 */
function cleanString(the_string, keep_newlines)
{
  if (!the_string) 
    return '';
  // Remove leading and trailing whitespace
  the_string = the_string.replace(/^\s+|\s+$/g, '');
  // Reduce internal whitespace
  if (keep_newlines)
    {
      //the_string = the_string.replace(/[ \f\t\u00A0\u2028\u2029]+/, ' ');
      the_string = the_string.replace(/[^\n^\r\s]+/, ' ');
      the_string = the_string.replace(/\n+/g, '\n');
      the_string = the_string.replace(/\r+/g, '\r');
      the_string = the_string.replace(/(?:\r\n)+/g, '\r\n');
    }
  else
    {
      the_string = the_string.replace(/\s+/g, ' ');
    }
  return the_string;
}

/**
 * Remove leading and trailing whitespace from a string.
 *
 * @param the_string The string to trim
 * @return The trimmed string
 */
function trim(the_string)
{
  return the_string.replace(/^\s+|\s+$/g, '');
}

/**
 * Join a list of strings, separated by the given string, excluding any empty
 * strings in the input list. 
 *
 * @param the_list The list to join
 * @param the_string The string to insert between each string in the list (default: ' ')
 * @return The joined string
 */
function _join(the_list, join_string)
{
  join_string = join_string || ' ';
  var new_list = [];
  for (var i = 0; i < the_list.length; ++i) {
    word = _trim(the_list[i]);
    if (word) new_list.push(word);
  }
  return new_list.join(join_string);
}