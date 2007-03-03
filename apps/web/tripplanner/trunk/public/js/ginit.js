/** $Id: ginit.js 190 2006-08-16 02:29:29Z bycycle $
 *
 * This module initializes the interface.
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
var __debug__ = 1;
var local = 0;

// The base location (domain) of the web interface
var domain = location.href.split('/')[2];

// The URL minus the query string
var base_url = location.href.split('?')[0];

var urls_to_keys_map = {
  'tripplanner.bycycle.org':
  'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ8y5tnWrQRsyOlME1eHkOS3wQveBSeFCpOUAfP10H6ec-HcFWPgiJOCA',
  
  'dev.bycycle.org':
  'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQSskL_eAzZotWlegWekqLPLda0sxQZNf0_IshFell3z8qP8s0Car117A',
  
  'www.bycycle.org':
  'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ9bMyOoze7XFWIje4XR3o1o-U-cBTwScNT8SYtwSl70gt4wHCO-23Y3g',
  
  'bycycle.metro-region.org':
  'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhR7upyhxOh7UQa5Yu3ebGZe2uQ8SxRPJtyMUYYgIBQsAROpcOySx6G1RQ'
};

var api_key = urls_to_keys_map[domain]
if (api_key) {
  script('http://maps.google.com/maps?file=api&amp;v=2&amp;key=' + api_key);
}
