# Geocode Service Module

class GeocodeError(Exception):
    def __init__(self, desc=''): 
        if desc: self.description = desc
        else: self.description = 'Geocode Error'

    def __str__(self): return self.description

class AddressNotFoundError(GeocodeError):
    def __init__(self, address=''):
        desc = 'Could not find address `%s`' % address
        GeocodeError.__init__(self, desc=desc)
                
class MultipleMatchingAddressesError(GeocodeError):
    def __init__(self, geocodes=[]):
        self.geocodes = geocodes
        desc = 'Multiple matching addresses found'
        GeocodeError.__init__(self, desc=desc)

class InputError(GeocodeError):
    def __init__(self, errors=[]):
        desc = '<br/>'.join(errors)
        GeocodeError.__init__(self, desc=desc)

 
def get(region='', q='', **params):
    """Get the geocode of the address, according to the data mode.
    
    @param region Either the name of a region mode OR a mode object. In the
           first case a mode will be instantiated to geocode the address; in
           the second the object will be used directly.
    @param q An address string that can be geocoded by the mode
    @return A list of geocodes for the inaddr
    
    """
    # Check input
    errors = []

    try:
        region.geocode
    except AttributeError:    
        region_is_object = False
        region = region.strip().lower()
    else:
        region_is_object = True
    if not region:
        errors.append('Region required')
        
    inaddr = q.strip().lower()
    if not q:
        errors.append('Address required')

    if errors: raise InputError(errors)

    # If region is a string (i.e., it's not an object) instantiate a new data mode
    # based on the string
    if not region_is_object:
        path = 'byCycle.tripplanner.model.%s'
        region = __import__(path % region, globals(), locals(), ['']).Mode()

    # Get geocode(s)
    geocodes = region.geocode(q)    
    len_geocodes = len(geocodes)
    if len_geocodes == 0:
        raise AddressNotFoundError(q)
    elif len_geocodes > 1:
        raise MultipleMatchingAddressesError(geocodes)
    else:
        return geocodes


if __name__ == "__main__":
    import time
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
         ('300 main',
          ),
         
         'portland':
         # Portland
         ('37800 S Hwy 213 Hwy, Clackamas, OR 97362',
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
          'W Burnside St, Portland, OR 97204 & NW 3rd Ave, Portland, OR 97209',
          'Burnside St, Portland, & 3rd Ave, Portland, OR 97209',
          '300 main',
          '300 bloofy lane',
         ),
        }

    i = 1
    for region in ('portlandor',):
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
