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
unknown = None
portlandor = 'portlandor'
milwaukeewi = 'milwaukeewi'
pittsburghpa = 'pittsburghpa'

states_cities = {
    'or': {'columbia': portlandor,
           'washington': portlandor,
           'multnomah': portlandor,
           'portland': portlandor,
           'banks': portlandor,
           'vancouver': portlandor,
           'north plains': portlandor,
           'hillsboro': portlandor,
           'gresham': portlandor,
           'fairview': portlandor,
           'maywood park': portlandor,
           'forest grove': portlandor,
           'troutdale': portlandor,
           'beaverton': portlandor,
           'wood village': portlandor,
           'cornelius': portlandor,
           'hood river': portlandor,
           'milwaukie': portlandor,
           'clackamas': portlandor,
           'happy valley': portlandor,
           'tigard': portlandor,
           'gaston': portlandor,
           'yamhill': portlandor,
           'lake oswego': portlandor,
           'king city': portlandor,
           'sandy': portlandor,
           'johnson city': portlandor,
           'durham': portlandor,
           'tualitin': portlandor,
           'gladstone': portlandor,
           'west linn': portlandor,
           'rivergrove': portlandor,
           'oregon city': portlandor,
           'sherwood': portlandor,
           'wilsonville': portlandor,
           'estacada': portlandor,
           'canby': portlandor,
           'barlow': portlandor,
           'molalla': portlandor,
           'marion': portlandor,
           },
    
    'wi': {'bayside': milwaukeewi,
           'brown deer': milwaukeewi,
           'cudahy': milwaukeewi,
           'fox point': milwaukeewi,
           'franklin': milwaukeewi,
           'glendale': milwaukeewi,
           'greendale': milwaukeewi,
           'greenfield': milwaukeewi,
           'hales corners': milwaukeewi,
           'milwaukee': milwaukeewi,
           'oak creek': milwaukeewi,
           'river hills': milwaukeewi,
           'saint francis': milwaukeewi,
           'shorewood': milwaukeewi,
           'south milwaukee': milwaukeewi,
           'wauwatosa': milwaukeewi,
           'west allis': milwaukeewi,
           'west milwaukee': milwaukeewi,
           'whitefish bay': milwaukeewi,
    },

    'pa': {'pittsburgh': pittsburghpa
    },
    
    }

cities = {}
for state in states_cities:
    cities_in_state = states_cities[state]
    for city in cities_in_state:
        region = cities_in_state[city]
        if city in cities:
            cities[city].append(region)
        else:
            cities[city] = [region]

zip_codes = {
    97206: portlandor,
    97217: portlandor,
    }

region_aliases = {
    'mil': milwaukeewi,
    'milwaukee': milwaukeewi,
    'pgh': pittsburghpa,
    'metro': portlandor,
    'pdx': portlandor,
    'por': portlandor,
    'port': portlandor,
    'portland': portlandor,
    }

def getRegion(region):
    """Find the proper region name for the input region."""
    region = region.strip().lower()
    region = region.replace(',', '')
    region = ''.join(region.split())
    try:
        region = region_aliases[region]
    except KeyError:
        pass
    return region
