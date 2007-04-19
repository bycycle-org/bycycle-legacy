"""$Id$

Portland, OR Bicycle Travel Mode. 11/07/2005.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>

All rights reserved.

TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION

1. The software may be used and modified by individuals for noncommercial, 
private use.

2. The software may not be used for any commercial purpose.

3. The software may not be made available as a service to the public or within 
any organization.

4. The software may not be redistributed.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
from byCycle.model import portlandor


FASTER, SHORTER, FLATTER, SAFER, DEFAULT = range(5)

# bikemode of "x" means avoid segment
mu = None
mm = None
lt = None
mt = None
ht = None
ca = None   # bikemode "ca" OR primary road (1300)
cca = None  # state highway
ccca = None # freeway
xxx = 1000  # avoid
# bike lane
blt = None
bmt = None
bht = None
bca = None
bcca = None
bccca = None 
# no bike mode
no_bm_lt = None
no_bm_mt = None
no_bm_ht = None
no_bm_ca = None
no_bm_cca = None
no_bm_ccca = None

            
class Mode(portlandor.Mode):
    def __init__(self, tmode='bicycle', pref='', **kwargs):
        """

        @param pref A string containing the user's simple preference option.
               Can be one of default, flatter, safer, shorter, or faster.

        """
        portlandor.Mode.__init__(self)
        self.pref = (pref == '') or eval(pref.upper())
        self.pct_slopes = [p*.01 for p in
                           (0,    0.65, 1.8, 3.7, 7,  12, 21,  500)]
        self.mph_up     =  (12.5, 11,   9.5, 7.5, 5,  3,  2.5, 2.5)
        self.mph_down   =  (12.5, 14,   17,  21,  26, 31, 32,  32)

        global mu, mm, lt, mt, ht, ca, cca, ccca, xxx
        global blt, bmt, bht, bca, bcca, bccca
        global no_bm_lt, no_bm_mt, no_bm_ht, no_bm_ca, no_bm_cca, no_bm_ccca
        if self.pref == SAFER:
            mu = .85
            mm = .9
            lt = 1
            mt = 2
            ht = 4
            ca = xxx
            cca = xxx
            ccca = xxx
            # bike lane
            blt = .75
            bmt = 1
            bht = 2
            bca = xxx
            bcca = xxx
            bccca = xxx
            # no bike mode
            mult = 3
            no_bm_lt = blt * mult
            no_bm_mt = bmt * mult
            no_bm_ht = bht * mult
            no_bm_ca = xxx
            no_bm_cca = xxx
            no_bm_ccca = xxx
        else:
            mult = 2
            mu = .85
            mm = .9
            lt = 1
            mt = 1.17
            ht = 1.33            
            ca = 2.67
            cca = 10
            ccca = 100
            # bike lane
            blt = .75
            bmt = .875
            bht = 1
            bca = 2
            bcca = 3
            bccca = 4 
            # no bike mode
            mult = 2
            no_bm_lt = blt * mult
            no_bm_mt = bmt * mult
            no_bm_ht = bht * mult
            no_bm_ca = bca * mult
            no_bm_cca = bcca * mult
            no_bm_ccca = bccca * mult
            
            
    def getEdgeWeight(self, v, edge_attrs, prev_edge_attrs):
        """Calculate weight for edge given it & last crossed edge's attrs."""
        length = edge_attrs[self.indices['length']] * self.int_decode
        code = edge_attrs[self.indices['code']]
        bikemode = edge_attrs[self.indices['bikemode']]
        slope = edge_attrs[self.indices['abs_slp']] * self.int_decode
        upfrac = edge_attrs[self.indices['up_frac']] * self.int_decode
        downfrac = 1 - upfrac
        node_f_id = edge_attrs[self.indices['node_f_id']]
        streetname_id = edge_attrs[self.indices['streetname_id']]
        #cpd = edge_attrs[self.indices['cpd']]
 
        # -- Calculate base weight of edge (in hours)
        
        # Length of segment that is uphill in from => to direction
        up_len = length * upfrac

        # Length of segment that is downhill in from => to direction
        down_len = length * (1.0 - upfrac)

        # Swap uphill and downhill lengths when traversing segment to => from
        if v != node_f_id:
            up_len, down_len = down_len, up_len

        # Based on the slope, calculate the speed of travel uphill and downhill
        # (up_spd & down_spd)
        if slope <= 0:
            up_spd = self.mph_up[0]
            down_spd = self.mph_down[0]
        elif slope >= self.pct_slopes[-1]:
            # Slope is past end
            pct_past_end = slope / self.pct_slopes[-2]
            up_spd = self.mph_up[-1] / pct_past_end     #slower
            down_spd = self.mph_down[-1] * pct_past_end #faster
        else:
            for i, u in enumerate(self.pct_slopes[1:]):
                if slope <= u:
                    l = self.pct_slopes[i]
                    break
            pct_past_l = (slope - l) / (u - l)
            mph_up_i, mph_up_j = self.mph_up[i], self.mph_up[i+1]
            up_spd = mph_up_i - (mph_up_i - mph_up_j) * pct_past_l
            mph_down_i, mph_down_j = self.mph_down[i], self.mph_down[i+1]
            down_spd = mph_down_i + (mph_down_j - mph_down_i) * pct_past_l

        # Based on uphill length and speed, calculate time to traverse uphill
        # part of segment
        up_time = up_len / up_spd
        # Likewise for downhill part of segment
        down_time = down_len / down_spd
        # Add those together for estimated total time to traverse segment
        hours = up_time + down_time

        # -- Adjust weight based on user preference
        
        if bikemode:
            # Adjust bike network street
            if   bikemode == 't':          hours *= mu
            elif bikemode == 'p':          hours *= mm
            elif bikemode == 'b':
                # Adjust bike lane for traffic (est. from st. type)
                if   code in (1500, 1521): hours *= blt    #lt
                elif code == 1450:         hours *= bmt    #mt
                elif code == 1400:         hours *= bht    #ht
                elif code == 1300:         hours *= bca    #ca
                elif 1200 <= code < 1300:  hours *= bcca   #ca+
                elif 1100 <= code < 1200:  hours *= bccca  #ca++
                else:                      hours *= xxx    #?          
            elif bikemode == 'l':          hours *= lt
            elif bikemode == 'm':          hours *= mt
            elif bikemode == 'h':          hours *= ht
            elif bikemode == 'c':          hours *= ca
            elif bikemode == 'x':          hours *= xxx
        else:
            # Adjust normal (i.e., no bikemode) street based on traffic
            # (est. from st. type)
            if code == 3200:                 hours *= mu
            elif code in (3230, 3240, 3250): hours *= mm
            else:
                if code in (1500, 1521):     hours *= no_bm_lt
                elif code == 1450:           hours *= no_bm_mt
                elif code == 1400:           hours *= no_bm_ht
                elif code == 1300:           hours *= no_bm_ca
                elif 1200 <= code < 1300:    hours *= no_bm_cca
                elif 1100 <= code < 1200:    hours *= no_bm_ccca
                else:                        hours *= xxx


        # Penalize edge if it has different street name from previous edge
        try:
            prev_ix_sn = prev_edge_attrs[self.indices['streetname_id']]
            if streetname_id != prev_ix_sn:
                hours += .0027777  # 10 seconds
        except TypeError:
            pass        

        return hours
