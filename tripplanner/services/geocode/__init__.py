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

 
def get(input):
    """Get the geocode of the address, according to the data mode.
    
    @param inaddr -- An address string that can be geocoded by the mode
    @param mode -- Either the name of a mode OR a mode object. In the first
                   case a mode will be instantiated to geocode the address; in
                   the second the object will be used directly.
    @return -- A list of geocodes for the inaddr
    
    """
    # Check input
    errors = []

    try:
        val = input['q'].strip().lower()
        if not val: raise ValueError
    except (KeyError, ValueError):
        errors.append('Please enter an address.')
    else:
        inaddr = val

    try:
        try:
            val = input['dmode']
            val = val.strip().lower()
        except AttributeError:
            pass
        else:
            if not val: raise ValueError
    except (KeyError, ValueError):
        errors.append('Please select a region.')
    else:
        mode = val

    if errors: raise InputError(errors)

    # See if mode is object (has geocode attr) or string (no geocode attr)
    # If string, instantiate a new data mode object based on the string
    try:
        mode.geocode
    except AttributeError:
        path = 'byCycle.tripplanner.model.%s'
        mode = __import__(path % mode, globals(), locals(), ['']).Mode()

    # Get geocode(s)
    geocodes = mode.geocode(inaddr)    
    len_geocodes = len(geocodes)
    if len_geocodes == 0: raise AddressNotFoundError(inaddr)
    elif len_geocodes > 1: raise MultipleMatchingAddressesError(geocodes)
    else: return geocodes


if __name__ == "__main__":
    import time
    A = (#' ',
         # Milwaukee
        '37800 S Hwy 213 Hwy, Clackamas, OR 97362',
         '0 w hayes ave',
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
         # Portland
         #4550 ne 15',
         #4408 se stark',
         #4408 se stark, or',
         #4408 se stark, wi',
         #4408 se stark st oregon 97215',
         #44th and stark',
         #3 and main oregon',
         #3rd & main 97024',
         #(-122.67334, 45.523307)',
         #W Burnside St, Portland, OR 97204 & NW 3rd Ave, Portland, OR 97209',
         #Burnside St, Portland, & 3rd Ave, Portland, OR 97209',
         #'300 main',
         #'300 bloofy lane'
         )

    i = 1
    I = {'q': None, 'dmode': 'metro'}
    for a in A:
        I['q'] = a
        st = time.time()
        try:
            geocodes = get(I)
        except AddressNotFoundError, e:
            print i, a
            print e
            raise
        except MultipleMatchingAddressesError, e:
            print i, a
            print e
            for code in e.geocodes: print '    %s' % code
        except Exception, e:
            print e
            raise
        else:
            print i, a
            print '    %s' % geocodes[0]
        i+=1
        tt = time.time() - st
        print '    %.2f seconds' % tt 
