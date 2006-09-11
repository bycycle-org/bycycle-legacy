/** $Id: ajax.js 190 2006-08-16 02:29:29Z bycycle $
 *
 * A few simple functions for doing RPC via XMLHttpRequest.
 * 
 * Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>
 * 
 * All rights reserved.
 * 
 * TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION
 * 
 * 1. The software may be used and modified by individuals for noncommercial, 
 * private use.
 * 
 * 2. The software may not be used for any commercial purpose.
 * 
 * 3. The software may not be made available as a service to the public or within 
 * any organization.
 * 
 * 4. The software may not be redistributed.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */
var is_ajax_enabled = isAjaxEnabled();

function isAjaxEnabled() {
	if (createXmlHttpReq()) return true;
	else return false;
}

function createXmlHttpReq() {
    try {
        return new window.ActiveXObject("Microsoft.XMLHTTP");
    } catch (e) {
        try {
            return new window.XMLHttpRequest();
        } catch (e) { return null; }
    }
}

function doXmlHttpReq(method, url, callback) {
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
