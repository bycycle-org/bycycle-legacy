function echo(str) { document.write(str); }

function fixScroll() 
{
  var div = _el("content");
  var content = div.innerHTML;
  div.innerHTML = "<a id='fix_scroll' href=''></a>" + content;
  _el("fix_scroll").focus();
}

function _el(id) { return document.getElementById(id); }

function _elV(id) 
{ 
  var val = _el(id).value;
  return val;
}
function _setElV(id, val) { _el(id).value = val; }

function _elStyle(id, style) { return _el(id).style[style]; }
function _setElStyle(id, style, value) { eval("_el(id).style."+style+"="+"'"+value+"'"); }

function _iH(id) { return _el(id).innerHTML; }
function _setIH(id, val) { _el(id).innerHTML = val; }
function _appendIH(id, val) { _el(id).innerHTML += val; }

/**
 * Swap the values of the two elements with the given IDs.
 * @param id_a ID of element to swap
 * @param id_b ID of other element to swap
 */
function _swapElV(id_a, id_b) 
{
  var av = _elV(id_a);
  _setElV(id_a, _elV(id_b));
  _setElV(id_b, av);
}

/**
 * Remove leading and trailing whitespace from a string and
 * reduce internal runs of whitespace down to a single space.
 * @param the_string The string to clean
 * @param keep_newlines If this is set, reduce internal newlines to a single newline instead of a space
 * @return The cleaned string
 */
function _cleanString(the_string, keep_newlines)
{
  if (!the_string) return '';
  // Remove leading and trailing whitespace
  the_string = the_string.replace(/^\s+|\s+$/g, '');
  // Reduce internal whitespace
  if (keep_newlines)
    {
      the_string = the_string.replace(/[ \f\t\u00A0\u2028\u2029]+/, ' ');
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
 * Remove leading and trailing whitespace from a strin.g
 * @param the_string The string to trim
 * @return The trimmed string

 */
function _trim(the_string)
{
  return the_string.replace(/^\s+|\s+$/g, '');
}

/**
 * Join a list of strings, separated by the given string. Exclude any empty
 * strings. 
 * @param the_list The list to join
 * @param the_string The string to insert between each string in the list (default: ' ')
 * @return The joined string
 */
function _join(the_list, join_string)
{
  // Remove empty items and join the rest
  var new_list = [];
  if (!join_string) join_string = ' ';
  for (var i = 0; i < the_list.length; ++i) {
    word = the_list[i];
    if (word) new_list.push(word);
  }
  return new_list.join(join_string);
}
