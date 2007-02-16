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


street_types_ftoa = {'alley': 'aly', 'annex': 'anx', 'arcade': 'arc',
                     'avenue': 'ave', 'bayoo': 'byu', 'beach': 'bch',
                     'bend': 'bnd', 'bluff': 'blf', 'bluffs': 'blfs',
                     'bottom': 'btm', 'boulevard': 'blvd', 'branch': 'br',
                     'bridge': 'brg', 'brook': 'brk', 'brooks': 'brks',
                     'burg': 'bg', 'burgs': 'bgs', 'bypass': 'byp',
                     'camp': 'cp', 'canyon': 'cyn', 'cape': 'cpe',
                     'causeway': 'cswy', 'center': 'ctr', 'centers': 'ctrs',
                     'circle': 'cir', 'circles': 'cirs', 'cliff': 'clf',
                     'cliffs': 'clfs', 'club': 'clb', 'common': 'cmn',
                     'corner': 'cor', 'corners': 'cors', 'course': 'crse',
                     'court': 'ct', 'courts': 'cts', 'cove': 'cv',
                     'coves': 'cvs', 'creek': 'crk', 'crescent': 'cres',
                     'crest': 'crst', 'crossing': 'xing', 'crossroad': 'xrd',
                     'curve': 'curv', 'dale': 'dl', 'dam': 'dm',
                     'divide': 'dv', 'drive': 'dr', 'drives': 'drs',
                     'estate': 'est', 'estates': 'ests', 'expressway': 'expy',
                     'extension': 'ext', 'extensions': 'exts', 'fall': 'fall',
                     'falls': 'fls', 'ferry': 'fry', 'field': 'fld',
                     'fields': 'flds', 'flat': 'flt', 'flats': 'flts',
                     'ford': 'frd', 'fords': 'frds', 'forest': 'frst',
                     'forge': 'frg', 'forges': 'frgs', 'fork': 'frk',
                     'forks': 'frks', 'fort': 'ft', 'freeway': 'fwy',
                     'garden': 'gdn', 'gardens': 'gdns', 'gateway': 'gtwy',
                     'glen': 'gln', 'glens': 'glns', 'green': 'grn',
                     'greens': 'grns', 'grove': 'grv', 'groves': 'grvs',
                     'harbor': 'hbr', 'harbors': 'hbrs', 'haven': 'hvn',
                     'heights': 'hts', 'highway': 'hwy', 'hill': 'hl',
                     'hills': 'hls', 'hollow': 'holw', 'inlet': 'inlt',
                     'island': 'is', 'islands': 'iss', 'isle': 'isle',
                     'junction': 'jct', 'junctions': 'jcts', 'key': 'ky',
                     'keys': 'kys', 'knoll': 'knl', 'knolls': 'knls',
                     'lake': 'lk', 'lakes': 'lks', 'land': 'land',
                     'landing': 'lndg', 'lane': 'ln', 'light': 'lgt',
                     'lights': 'lgts', 'loaf': 'lf', 'lock': 'lck',
                     'locks': 'lcks', 'lodge': 'ldg', 'loop': 'loop',
                     'mall': 'mall', 'manor': 'mnr', 'manors': 'mnrs',
                     'meadow': 'mdw', 'meadows': 'mdws', 'mews': 'mews',
                     'mill': 'ml', 'mills': 'mls', 'mission': 'msn',
                     'motorway': 'mtwy', 'mount': 'mt', 'mountain': 'mtn',
                     'mountains': 'mtns', 'neck': 'nck', 'orchard': 'orch',
                     'oval': 'oval', 'overpass': 'opas', 'park': 'park',
                     'parks': 'park', 'parkway': 'pkwy', 'parkways': 'pkwy',
                     'pass': 'pass', 'passage': 'psge', 'path': 'path',
                     'pike': 'pike', 'pine': 'pne', 'pines': 'pnes',
                     'place': 'pl', 'plain': 'pln', 'plains': 'plns',
                     'plaza': 'plz', 'point': 'pt', 'points': 'pts',
                     'port': 'prt', 'ports': 'prts', 'prairie': 'pr',
                     'radial': 'radl', 'ramp': 'ramp', 'ranch': 'rnch',
                     'rapid': 'rpd', 'rapids': 'rpds', 'rest': 'rst',
                     'ridge': 'rdg', 'ridges': 'rdgs', 'river': 'riv',
                     'road': 'rd', 'roads': 'rds', 'route': 'rte',
                     'row': 'row', 'rue': 'rue', 'run': 'run',
                     'shoal': 'shl', 'shoals': 'shls', 'shore': 'shr',
                     'shores': 'shrs', 'skyway': 'skwy', 'spring': 'spg',
                     'springs': 'spgs', 'spur': 'spur', 'spurs': 'spur',
                     'square': 'sq', 'squares': 'sqs', 'station': 'sta',
                     'stravenue': 'stra', 'stream': 'strm', 'street': 'st',
                     'streets': 'sts', 'summit': 'smt', 'terrace': 'ter',
                     'throughway': 'trwy', 'trace': 'trce', 'track': 'trak',
                     'trafficway': 'trfy', 'trail': 'trl', 'tunnel': 'tunl',
                     'turnpike': 'tpke', 'underpass': 'upas', 'union': 'un',
                     'unions': 'uns', 'valley': 'vly', 'valleys': 'vlys',
                     'viaduct': 'via', 'view': 'vw', 'views': 'vws',
                     'village': 'vlg', 'villages': 'vlgs', 'ville': 'vl',
                     'vista': 'vis', 'walk': 'walk', 'walks': 'walk',
                     'wall': 'wall', 'way': 'way', 'ways': 'ways',
                     'well': 'wl', 'wells': 'wls'}
street_types_atof = swapKeysAndValues(street_types_ftoa)
street_types_atof['pky'] = 'parkway'
