function echo(str) { document.write(str); }

function fixScroll() 
{
	var div = _el("content");
	var content = div.innerHTML;
	div.innerHTML = "<a id='fix_scroll' href=''></a>" + content;
	_el("fix_scroll").focus();
}

function _el(id) { return document.getElementById(id); }
function _elV(id) { return _el(id).value; }
function _setElV(id, val) { _el(id).value = val; }
function _setElStyle(id, style, value) { eval("_el(id).style."+style+"="+"'"+value+"'"); }

function _iH(id) { return _el(id).innerHTML; }
function _setIH(id, val) { _el(id).innerHTML = val; }
function _appendIH(id, val) { _el(id).innerHTML += val; }

function _swap(id_a, id_b) 
{
	// Swap the values of the two elements with the given IDs
	var av = _elV(id_a);
	_setElV(id_a, _elV(id_b));
	_setElV(id_b, av);
}

function _join(the_list, join_string)
{
	// Remove empty items and join the rest
	var new_list = [];
	if (!join_string) join_string = ' ';
	for (var i = 0; i < the_list.length; ++i) {
		word = the_list[i];
		if (word) new_list.push(word)
	}
	return new_list.join(join_string);
}
