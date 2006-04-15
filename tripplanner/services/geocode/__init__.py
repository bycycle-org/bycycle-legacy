# Geocode Service Module

from byCycle.tripplanner.model import mode

class GeocodeError(Exception):
    def __init__(self, desc=''): 
        if desc: self.description = desc
        else: self.description = 'Geocode Error'

    def __str__(self): return self.description

class AddressNotFoundError(GeocodeError):
    def __init__(self, address=''):
        desc = 'Unable to find address "%s"' % address
        GeocodeError.__init__(self, desc=desc)
                
class MultipleMatchingAddressesError(GeocodeError):
    def __init__(self, geocodes=[]):
        self.geocodes = geocodes
        desc = 'Multiple matches found'
        GeocodeError.__init__(self, desc=desc)

class InputError(GeocodeError):
    def __init__(self, errors=[]):
        desc = '<br/>'.join(errors)
        GeocodeError.__init__(self, desc=desc)

 
def get(sOrOMode='', q='', **params):
    """Get the geocode of the address, according to the data mode.
    
    @param string|object sOrOMode Either the name of a region mode OR a mode
           object. In the first case a mode will be instantiated to geocode the
           address; in the second the object will be used directly.
    @param q An address string that can be normalized & geocoded in the mode
    @return A list of geocodes for the inaddr

    TODO: Raise exception when no geocodes instead of returning empty list
    
    
    """
    # Check input
    errors = []

    if not sOrOMode:
        errors.append('Please select a region')
            
    inaddr = q.strip().lower()
    if not q:
        errors.append('Address required')

    if errors:
        raise InputError(errors)

    if not isinstance(sOrOMode, mode.Mode):
        path = 'byCycle.tripplanner.model.%s'
        oMode = __import__(path % sOrOMode, globals(), locals(), ['']).Mode()
    else:
        oMode = sOrOMode

    # Get geocode(s)
    # TODO: Fix this so this module is truly a service and the service part
    # of it isn't all mixed up in the model
    geocodes = region.geocode(q)    
    len_geocodes = len(geocodes)
    if len_geocodes == 0:
        raise AddressNotFoundError(q)
    elif len_geocodes > 1:
        raise MultipleMatchingAddressesError(geocodes)
    else:
        return geocodes


if __name__ == "__main__":
    # TODO: Create unit tests!!!!
    
    import sys
    import time

    try:
        region, q = sys.argv[1].split(',')
    except IndexError:
        A = {#' ',
            # Milwaukee
            'milwaukeewi':
            ('0 w hayes ave',
             'lon=-87.940407, lat=43.05321',
             'lon=-87.931137, lat=43.101234',
             'lon=-87.934399, lat=43.047126',
             '125 n milwaukee',
             '125 n milwaukee milwaukee wi',
             '27th and lisbon',
             '27th and lisbon milwaukee',
             '27th and lisbon milwaukee, wi',
             'lon=-87.961178, lat=43.062993',
             'lon=-87.921953, lat=43.040791',
             'n 8th st & w juneau ave, milwaukee, wi ',
             '77th and burleigh',
             '2750 lisbon',
             '(-87.976885, 43.059544)',
             'lon=-87.946243, lat=43.041669',
             '124th and county line',
             '124th and county line wi',
             '5th and center',
             '6th and hadley',
             ),
            
            'portlandor':
            ('lon=-120.432129, lat=46.137977',
             'lon=-120.025635, lat=45.379161',
             '300 main',
             '37800 S Hwy 213 Hwy, Clackamas, OR 97362',
                        '4550 ne 15',
             '633 n alberta',
             '4408 se stark',
             '4408 se stark, or',
             '4408 se stark, wi',
             '4408 se stark st oregon 97215',
             '44th and stark',
             '3 and main oregon',
             '3rd & main 97024',
             '(-122.67334, 45.523307)',
             'W Burnside St, Portland, OR 97204 & ' \
             'NW 3rd Ave, Portland, OR 97209',
             'Burnside St, Portland, & 3rd Ave, Portland, OR 97209',
             '300 main',
             '300 bloofy lane',
             ),
            }
    else:
        A = {region: (q,)}

    i = 1
    for region in A:
        print
        print 'Data region: %s' % region
        print '------------------------------'
        for q in A[region]:
            st = time.time()
            try:
                geocodes = get(region=region, q=q)
            except AddressNotFoundError, e:
                print i, q
                print e
            except MultipleMatchingAddressesError, e:
                print i, q
                print e
                for code in e.geocodes:
                    print '%s' % code
            except Exception, e:
                print e
                raise
            else:
                print i, q
                print '%s' % geocodes[0]
            i+=1
            tt = time.time() - st
            print '%.2f seconds' % tt 
            print
