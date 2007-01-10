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
states_ftoa = {'alabama': 'al',
               'alaska': 'ak',
               'american samoa': 'as',
               'arizona': 'az',
               'arkansas': 'ar',
               'california': 'ca',
               'colorado': 'co',
               'connecticut': 'ct',
               'delaware': 'de',
               'district of columbia': 'dc',
               'federated states of micronesia': 'fm',
               'florida': 'fl',
               'georgia': 'ga',
               'guam': 'gu',
               'hawaii': 'hi',
               'idaho': 'id',
               'illinois': 'il',
               'indiana': 'in',
               'iowa': 'ia',
               'kansas': 'ks',
               'kentucky': 'ky',
               'louisiana': 'la',
               'maine': 'me',
               'marshall islands': 'mh',
               'maryland': 'md',
               'massachusetts': 'ma',
               'michigan': 'mi',
               'minnesota': 'mn',
               'mississippi': 'ms',
               'missouri': 'mo',
               'montana': 'mt',
               'nebraska': 'ne',
               'nevada': 'nv',
               'new hampshire': 'nh',
               'new jersey': 'nj',
               'new mexico': 'nm',
               'new york': 'ny',
               'north carolina': 'nc',
               'north dakota': 'nd',
               'northern mariana islands': 'mp',
               'ohio': 'oh',
               'oklahoma': 'ok',
               'oregon': 'or',
               'palau': 'pw',
               'pennsylvania': 'pa',
               'puerto rico': 'pr',
               'rhode island': 'ri',
               'south carolina': 'sc',
               'south dakota': 'sd',
               'tennessee': 'tn',
               'texas': 'tx',
               'utah': 'ut',
               'vermont': 'vt',
               'virgin islands': 'vi',
               'virginia': 'va',
               'washington': 'wa',
               'west virginia': 'wv',
               'wisconsin': 'wi',
               'wyoming': 'wy'}

states_atof = {'ak': 'alaska',
               'al': 'alabama',
               'ar': 'arkansas',
               'as': 'american samoa',
               'az': 'arizona',
               'ca': 'california',
               'co': 'colorado',
               'ct': 'connecticut',
               'dc': 'district of columbia',
               'de': 'delaware',
               'fl': 'florida',
               'fm': 'federated states of micronesia',
               'ga': 'georgia',
               'gu': 'guam',
               'hi': 'hawaii',
               'ia': 'iowa',
               'id': 'idaho',
               'il': 'illinois',
               'in': 'indiana',
               'ks': 'kansas',
               'ky': 'kentucky',
               'la': 'louisiana',
               'ma': 'massachusetts',
               'md': 'maryland',
               'me': 'maine',
               'mh': 'marshall islands',
               'mi': 'michigan',
               'mn': 'minnesota',
               'mo': 'missouri',
               'mp': 'northern mariana islands',
               'ms': 'mississippi',
               'mt': 'montana',
               'nc': 'north carolina',
               'nd': 'north dakota',
               'ne': 'nebraska',
               'nh': 'new hampshire',
               'nj': 'new jersey',
               'nm': 'new mexico',
               'nv': 'nevada',
               'ny': 'new york',
               'oh': 'ohio',
               'ok': 'oklahoma',
               'or': 'oregon',
               'pa': 'pennsylvania',
               'pr': 'puerto rico',
               'pw': 'palau',
               'ri': 'rhode island',
               'sc': 'south carolina',
               'sd': 'south dakota',
               'tn': 'tennessee',
               'tx': 'texas',
               'ut': 'utah',
               'va': 'virginia',
               'vi': 'virgin islands',
               'vt': 'vermont',
               'wa': 'washington',
               'wi': 'wisconsin',
               'wv': 'west virginia',
               'wy': 'wyoming'}


def statesToMySQL():
    import mode
    m = mode.Mode()
    Q = 'insert into states (code, state) values ("%s", "%s")'
    codes = states_atof.keys()
    codes.sort()
    for c in codes:
        m.executeQuery(Q % (c, states_atof[c]))
