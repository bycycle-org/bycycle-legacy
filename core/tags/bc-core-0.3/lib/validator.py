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
import re
import common

class Validator(object):
    """
    
    Note: All validation comparisons should be done in lowercase.

    """
    def __init__(self):
        pass

    
    # Validators -->
    
    def validateCrossStreets(self, crossStreets):
        """
        
        @param crossStreets -- a string of cross streets separated by
                               '&' or 'and' or 'AND'
                               
        """
        csStr = str(crossStreets)
        
        cs = csStr.split(' & ')
        if len(cs) != 2:
            cs = csStr.split(' and ')            
        if len(cs) != 2:
            cs = csStr.split(' AND ')
        if len(cs) == 2:
            a = cs[0]
            b = cs[1]
        else:
            return False 

        if not self.validateStreetName(a): return False
        if not self.validateStreetName(b): return False

        return True
    
    def validateStreetNumber(self, number):
        try: num = int(str(number))
        except Exception: return False 
        if num < 0 or num > 99999: return False
        return True

    def validateDirection(self, direction):
        dir = str(direction).strip().lower()
        if not (dir in common.directions_ttoa or \
                dir in common.directions_atot):
            return False
        return True

    def validateTurn(self, direction):
        dir = str(direction).strip().lower()
        if not (dir in common.turns_ttoa or \
                dir in common.turns_atot):
            return False
        return True    

    def validateStreetType(self, streetType):
        streetType = str(streetType).lower()
        if not (streetType in common.street_types_atot or \
                streetType in common.street_types_ttoa):
            return False
        return True
        
    def validateStreetName(self, streetName):
        name = str(streetName)
        words = name.split()
        if len(words) < 3 or \
               not (self.validateDirection(words[0]) and \
                    self.validateStreetType(words[-1])) or \
               re.search(common.disallowed_chars_re, name):
            return False
        return True

    def validateStreetAddress(self, streetAddress):
        address = str(streetAddress)
        words = address.split()
        if len(words) < 4 or \
               not (self.validateStreetNumber(words[0]) and \
                    self.validateStreetName(' '.join(words[1:]))):
            return False
        return True
    
    def validateGo(self, go):
        g = str(go).strip().lower()
        if g not in ("n", "y", "0", "1", "no", "yes"): return False
        return True
 
    def validateLongitude(self, longitude):
        try: long = float(str(longitude))
        except Exception: return False
        
        if long < -180.0 or long > 180.0: return False

        words = longitude.strip().split(".")
        if len(words[-1]) != common.lon_lat_fraction_len: return False

        return True

    def validateLatitude(self, latitude):
        try: lat = float(str(latitude))
        except Exception: return False
        
        if lat < -90.0 or lat > 90.0: return False

        words = latitude.strip().split(".")
        if len(words[-1]) != common.lon_lat_fraction_len: return False

        return True
    
    # <-- Validators


    # Fixer-uppers -->
    
    def fixupCrossStreets(self, crossStreets):
        csStr = str(crossStreets)
        
        cs = csStr.split('&')
        if len(cs) != 2:
            cs = csStr.split('and')            
        if len(cs) != 2:
            cs = csStr.split('AND')
        if len(cs) == 2:
            a = cs[0]
            b = cs[1]
        else:
            return '', '' 

        return ' & '.join((self.fixupStreetName(a), self.fixupStreetName(b)))
    
    def fixupStreetAddress(self, streetAddress):
        words = str(streetAddress).title().split()
        if len(words) < 2: return ''
        words[1] = self.fixupDirection(words[1])
        words[-1] = self.fixupStreetType(words[-1])
        return ' '.join(words)

    def fixupStreetName(self, streetName):
        words = str(streetName).title().split()
        if len(words) < 1: return ''
        words[0] = self.fixupDirection(words[0])
        words[-1] = self.fixupStreetType(words[-1])
        return ' '.join(words)

    def fixupStreetNumber(self, number):
        return str(number).strip()
    
    def fixupDirection(self, direction):
        d = str(direction).strip().lower()
        if dir in common.directions_ttoa: d = common.directions_ttoa[d]
        return d.upper()

    def fixupTurn(self, direction):
        d = str(direction).strip().lower()
        if dir in common.turns_ttoa: d = common.turns_ttoa[d]
        return d.upper()

    def fixupStreetType(self, streetType):
        st = str(streetType).strip().lower()
        if streetType in common.street_types_ttoa:
            streetType = common.street_types_ttoa[streetType]
        return streetType.upper()

    def fixupGo(self, go):
        g = str(go).strip().lower()
        if g in ("0", "no") : g = "n"
        elif g in ("1", "yes"): g = "y"
        return g.upper()
   
    def fixupLongitude(self, longitude):
        return str(longitude).strip()

    def fixupLatitude(self, latitude):
        return str(latitude).strip()
    
    # <-- Fixer-uppers
