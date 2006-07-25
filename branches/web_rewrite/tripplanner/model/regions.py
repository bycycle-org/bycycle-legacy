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
    'metro': portlandor,  
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
