/** $Id: regions.js 190 2006-08-16 02:29:29Z bycycle $
 *
 * Description goes here.
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
var regions = { 
  all: {
    id: 'all',
    
    heading: 'All Regions',
    
    subheading: 'Welcome to the <a href="http://bycycle.org/" title="byCycle Home Page">byCycle.org</a> interactive bicycle trip planner.',
    
    bounds: {
		sw: {lat: 40.362070, lng: -123.485755},
		ne: {lat: 45.814153, lng: -79.866439}
	},    
	
    all: true
  }, 

  
  portlandor: {
    id: 'portlandor',
    
    heading: 'Portland, OR',
    
    subheading: 'Developed in cooperation with <a href="http://www.metro-region.org/">Metro</a>.',
    
    bounds: {
		sw: {lat: 44.885219, lng: -123.485755},
		ne: {lat: 45.814153, lng: -121.649618}
	}
  },

  milwaukeewi: {
    id: 'milwaukeewi',
    
    heading: 'Milwaukee, WI',
    
    subheading: 'Developed in cooperation with the <a href="http://www.bfw.org/">Bicycle Federation of Wisconsin</a>.',
    
    bounds: {
		sw: {lat: 42.842059, lng: -88.069888}, 
		ne: {lat: 43.192647, lng: -87.828241}
	}
  }
};