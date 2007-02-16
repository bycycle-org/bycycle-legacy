"""$Id$

Description goes here.

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
from byCycle.util import swapKeysAndValues


directions_ftoa = {'north'     : 'n',
                   'south'     : 's',
                   'east'      : 'e',
                   'west'      : 'w',
                   'northeast' : 'ne',
                   'northwest' : 'nw',
                   'southeast' : 'se',
                   'southwest' : 'sw',
                   }
directions_atof = swapKeysAndValues(directions_ftoa)


directions_dtoa = {'0'   : 'n',
                   '180' : 's',
                   '90'  : 'e',
                   '270' : 'w',
                   '45'  : 'ne',
                   '315' : 'nw',
                   '135' : 'se',
                   '225' : 'sw',
                   }
directions_atod = swapKeysAndValues(directions_dtoa)


suffixes_ftoa = {'northbound': 'nb',
                 'southhbound': 'sb',
                 'eastbound': 'eb',
                 'westbound': 'wb',
                 }
suffixes_atof = swapKeysAndValues(suffixes_ftoa)
