var is_ajax_enabled = isAjaxEnabled();

function isAjaxEnabled()
{
	if (createXmlHttpReq()) return true;
	else return false;
}

function createXmlHttpReq()
{
    try {
        return new window.ActiveXObject("Microsoft.XMLHTTP");
    } catch (e) {
        try {
            return new window.XMLHttpRequest();
        } catch (e) { return null; }
    }
}

function doXmlHttpReq(method, url, callback)
{
    var req = createXmlHttpReq();
	if (!req) return;
	req.onreadystatechange = function()
	{
		if (req.readyState != 4) { return; }
		callback(req);
	};
	req.open(method, url, true);
	req.send(null);
}