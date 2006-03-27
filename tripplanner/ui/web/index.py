import os
import datetime
import urllib
import simplejson
import byCycle


template = '%stripplanner/ui/web/tripplanner.html' % \
           byCycle.install_path


def index(req, **params):
    # - Normal request
    #   - No query string
    #     Return the template with default values
    
    #   - Query string, region only
    #     Return the template with default values, region selected

    #   - Query string
    #     Process the query
    #     Return the template with values filled in
    #     Move the map if there's not an error

    # - Asynchronous request
    #   - Query string
    #     Process the query
    #     Return processing results

    try:
        async = params['async'] == '1'
    except KeyError:
        async = False

    try:
        params['region'] = _getRegionForAlias(params['region'])
    except KeyError:
        pass

    if async:
        # Asynchronous request
        req.content_type = 'text/plain'
        
        response_text = _processQuery(req, params)
        status = req.status
        if req.status < 400:
            result_set = eval(response_text)
            type_ = result_set['result_set']['type']
            callback = '_%sCallback' % type_
            result = eval(callback)(req.status, result_set, **params)
            result_set['result_set']['html'] = urllib.quote(result)
            content = simplejson.dumps(result_set)
        else:
            content = '<h2>Error</h2>%s' % response_text
    else:
        # Normal request
        req.content_type = 'text/html'

        try:
            q = ' '.join(params['q'].split())
        except KeyError:
            status = ''
            response_text = ''
            q = ''
            fr = ''
            to = ''
            result = _getWelcomeMessage()
        else:
            fr = to = ''
            response_text = _processQuery(req, params)            
            status = req.status
            if req.status < 400:
                result_set = eval(response_text)
                type_ = result_set['result_set']['type']
                callback = '_%sCallback' % type_
                result = eval(callback)(req.status, result_set, **params)
                response_text = simplejson.dumps(response_text)
            else:
                result = '<h2>Error</h2>%s' % response_text
                                
        data = {
            'http_status': status,
            'response_text': response_text,
            'q': q,
            'fr': fr,
            'to': to,
            'regions_opt_list': _makeRegionsOptionList(**params),
            'result': result,
            }

        template_file = open(template)
        content = template_file.read() % data
        template_file.close()
    return content


def _processQuery(req, params, service=''):
    from byCycle.lib import wsrest

    # Normalize query
    params['q'] = ' '.join(params['q'].split()).lower()

    # Analyze the query to determine the service and prepare the query for the
    # service. If a service was explicitly given, use it; otherwise, use the
    # service determined by the semantic analysis.
    s = _analyzeQuery(params)
    service = service or s

    # Import web service module
    path = 'byCycle.tripplanner.webservices.%s'
    mod = __import__(path % service, globals(), locals(), [''])
    
    # Create web service object
    ws_obj = getattr(mod, service.title())(**params)

    # Process the query according to the request method
    method = req.method
    try:
        content = eval('ws_obj.%s' % method)()
    except wsrest.MethodNotAllowedError, exc:
        content = exc.reason + ' (%s)' % method
        req.allow_methods(exc.getAllowMethods(ws_obj))
    except wsrest.MultipleChoicesError, exc:
        content = exc.choices
    except wsrest.RestError, exc:
        content = exc.reason
    except Exception, exc:
        status = 500
        content = str(exc)
    else:
        status = 200

    try:
        req.status = status
    except NameError:
        req.status = exc.status
    
    return content


def _analyzeQuery(params):
    q = params['q']
    service = 'geocode'

    try:
        q = eval(q)
    except:
        words = q.split(' to ') 
        if len(words) > 1:
            service = 'route'
            q = words
    else:
        if isinstance(q, list):
            service = 'route'
           
    try:
        service = params['service']
    except KeyError:
        params['service'] = service

    params['q'] = q
    return service


## Callbacks

def _geocodeCallback(status, result_set, **params):
    geocodes = result_set['result_set']['result']
    if status == 200:    # A-OK, one match
        geocode = geocodes[0]
        addr = geocode['address'].replace('\n', '<br/>')
        field_addr = geocode['address'].replace('\n', ', ')
        href = ' href="javascript:void(0);" '        
        result = '<h2 style="margin-top:0">Address</h2><p>%s</p>' % addr
    elif status == 300:  # Multiple matches
        result = ['<h2>Multiple Matches Found</h2><ul>']
        for i, code in enumerate(geocodes):
            addr = code['address']
            result.append('<li>'
                          '  <a href="?region=%s&q=%s" '
                          '    onclick="_showGeocode(%s, 1); return false;"'
                          '    >%s</a>'
                          '</li>' %
                          (params['region'],
                           addr.replace('\n', ', ').replace(' ', '+'),
                           i,
                           addr.replace('\n', '<br/> ')))
        result.append('</ul>')
        result = ''.join(result)
    return result


def _routeCallback(status, result_set, **params):
    route = result_set['result_set']['result']
    if status == 200:    # A-OK, one match
        result = _makeDirectionsTable(route)
    elif status == 300:  # Multiple matches
        geocodes_fr = route['fr']['geocode']
        geocodes_to = route['to']['geocode']
        result = _makeRouteMultipleMatchList(geocodes_fr, geocodes_to, params)
    return result


def _makeRouteMultipleMatchList(geocodes_fr, geocodes_to, params):
    region = params['region']
    result = ['<div id="mma"><h2>Multiple Matches Found</h2>']

    def makeDiv(fr_or_to, style):
        if fr_or_to == 'fr':
            heading = 'From Address:'
        else:
            heading = 'To Address:'
        result.append('<div id="mma_%s" style="display:%s;"><h3>%s</h3>' % \
                      (fr_or_to, style, heading))

    def makeList(fr_or_to, geocodes, find):
        result.append('<ul>')
        if fr_or_to == 'fr':
            q_temp = '%s to ' + params['q'][1]
        else:
            q_temp = params['q'][0] + ' to %s'
        for code in geocodes:
            addr = code['address']
            q = q_temp % addr.replace('\n', ', ')
            result.append('<li>'
                          '<a href="?region=%s&q=%s&tmode=bike">%s</a>'
                          '</li>' % 
                          (region,
                           q.replace(' ', '+'),
                           addr.replace('\n', '<br/>')))
        result.append('</ul></div>')
  
    if geocodes_fr:
        style = 'block'
        if geocodes_to:
            find = '_setElStyle(\'mma_fr\', \'display\', \'none\'); ' \
                   '_setElStyle(\'mma_to\', \'display\', \'block\')'
        else:
            find = 'doFind()'
        makeDiv('fr', style)
        makeList('fr', geocodes_fr, find)

    if geocodes_to:
        find = 'doFind()'
        if geocodes_fr:
            style = 'none'
        else:
            style = 'block'
        makeDiv('to', style)
        makeList('to', geocodes_to, find)
      
    result.append('</div>')
    return ''.join(result)


## Web Services

def geocode(req, **params):
    return _processQuery(req, params, 'geocode')


def route(req, **params):
    return _processQuery(req, params, 'route')


## Helpers

def _getRegionForAlias(alias):
    region_aliases = {'mil': 'milwaukeewi',
                      'milwaukee': 'milwaukeewi',
                      'metro': 'portlandor',
                      'por': 'portlandor',
                      'portland': 'portlandor',
                      }
    try:
        region = region_aliases[alias]
    except KeyError:
        return alias
    else:
        return region


## Output
    
def _makeRegionsOptionList(region='', **params):
    """Create an HTML options list of regions.

    Set the selected region if we got here by
    http://tripplanner.bycycle.org/?region=x where x is the name of a region.

    @return An HTML options list of regions sorted by state, then area
    
    """
    regions = {'or': ['portland',
                      ],
               'wi': ['milwaukee',
                      ],
               'pa': ['pittsburgh',
                      ],
               }

    states = regions.keys()
    states.sort()

    region = region.strip().lower().replace(',', '')

    region_opt = '<option value="%s">%s</option>'
    region_opt_selected = '<option value="%s" selected="selected">%s</option>'

    regions_opt_list = []
    region_heading = 'All Regions'

    for state in states:
        areas = regions[state]
        for area in areas:
            reg = '%s%s' % (area, state)
            if reg == region:
                opt = region_opt_selected
            else:
                opt = region_opt 
            regions_opt_list.append(opt % (reg, '%s, %s' %
                                           (area.title(),
                                            state.upper())))
            
    return ''.join(regions_opt_list)


def _getWelcomeMessage():
    welcome_message = '''
    <p style="margin-top:0;">
    The Trip Planner is under active development. Please
    <a href="http://www.bycycle.org/contact.html"
    title="Send us problem reports, comments, questions, and suggestions"
    >contact us</a>
    with any problems, comments, questions, or suggestions.
    </p>
    
    <p>
    Users should independently verify all information presented here. This service is provided AS IS with NO WARRANTY of any kind. 
    </p>
    
    <p>
    &copy; 2006 
    <a href="http://www.bycycle.org/" 
    title="byCycle Home Page"
    >byCycle.org</a>
    <br/>
    Last modified: %s
    <br/>
    </p>
    ''' % (_getLastModified(template))
    return welcome_message


def _getLastModified(file_name=''):
    """Get and format the last modified date of file_name."""
    stat = os.stat(file_name)
    last_modified = datetime.date.fromtimestamp(stat.st_mtime)
    last_modified = last_modified.strftime('%B %d, %Y')
    if last_modified[0] == '0':
        last_modified = last_modified[1:]
    return last_modified


def _makeDirectionsTable(route):
##    route = {'from':       {'geocode': fcode, 'original': fr},
##             'to':         {'geocode': tcode, 'original': to},
##             'linestring': [],
##             'directions': [],
##             'directions_table': '',
##             'distance':   {},
##             'messages': []
##            }

    distance = route['distance']['mi']
    fr = route['fr']['geocode']
    fr_addr = fr['address']
    to = route['to']['geocode']
    to_addr = to['address']
    directions = route['directions']
    linestring = route['linestring']
 
    fr_point = linestring[0]
    to_point = linestring[-1]

    fr_addr = str(fr_addr).replace('\n', '<br/>')
    to_addr = str(to_addr).replace('\n', '<br/>')

    s_table = """
    <table id='summary'>
        <tr>
          <td class='start'>
            <h2><a href='javascript:void(0);' class='start'
                   onclick="map.showMapBlowup(%s)">Start</a>
            </h2>
          </td>
          <td class='start'>%s</a>
          </td>
        </tr>
        <tr>
          <td class='end'>
            <h2><a href='javascript:void(0);' class='end'
                   onclick="map.showMapBlowup(%s)">End</a>
            </h2>
          </td>
          <td class='end'>%s</td>
        </tr>
        <tr>
          <td class='total_distance'><h2>Distance</h2></td>
          <td>%s miles</td>
        </tr>
    </table>
    """ % (fr_point, fr_addr, to_point, to_addr, distance)

    d_table = """
    <!-- Directions -->
    <table id='directions'>%s</table>
    """

    d_row = """
    <tr>
      <td class='count %s'>
        <a href='javascript:void(0)'
           onclick="map.showMapBlowup(%s)">%s.</a>
      </td>
      <td class='direction %s'>%s</td>
    </tr>
    """               

    # Direction rows
    row_class = 'a'
    last_i = len(directions)
    last_street = to_addr.split('\n')[0]
    tab = '&nbsp;' * 4
    d_rows = []
    row_i = []
    i = 1
    for d in directions:
        turn = d['turn']
        street = d['street']
        toward = d['toward']
        jogs = d['jogs']
        ls_index = d['ls_index']
        mi = d['distance']['mi']

        row_i = []

        if turn == 'straight':
            prev = street[0]
            curr = street[1]
            row_i.append('%s <b>becomes</b> %s' % (prev, curr))
        else:
            if i == 1:
                cmd = 'Go'
                on = 'on'
                onto = '<b>%s</b>' % street
            else:
                cmd = 'Turn'
                on = 'onto'
                onto = '<b>%s</b>' % street
            row_i.append('%s <b>%s</b> %s %s' % (cmd, turn, on, onto))

        if not toward:
            if i == last_i:
                toward = last_street
            else:
                toward = '?'
        row_i.append(' toward %s -- %smi' % (toward, mi))

        if d['bikemode']:
            row_i.append(' [%s]' % ', '.join([bm for bm in d['bikemode']]))

        if jogs:
            row_i.append('<br/>%sJogs...' % tab)
            for j in jogs:
                row_i.append('<br/>%s%s&middot; <i>%s</i> at %s' % \
                             (tab, tab, j['turn'], j['street']))

        d_rows.append(d_row % (row_class, linestring[ls_index], i,
                               row_class, ''.join(row_i)))
        del row_i[:]
        if row_class == 'a': row_class = 'b'
        else: row_class = 'a'
        i += 1

    last_row = d_row  % (row_class, linestring[-1], i, row_class,
                         '<b>End</b> at <b>%s</b>' % last_street)
    d_rows.append(last_row)
    
    d_table = d_table % ''.join([str(d) for d in d_rows])
    return ''.join((s_table, d_table))            
        

## Testing
    
if __name__ == '__main__':
    import sys

    
    class Req(object):
        def __init__(self):
            self.content_type = ''
            self.headers_out = {}


    P = [
        {'region': 'portlandor',
         'tmode': 'bike',
         'q': '300 main to 4807 se kelly'
         },

        {'region': 'milwaukee',
          'q': '27th and lisbon'
          },
         
         {'region': 'portlandor',
          'tmode': 'bike',
          'q': '4807 se kelly to 45th and kelly'
          },
         
         {'region': 'milwaukeewi',
          'tmode': 'bike',
          'q': '35th and north to 27th and lisbon'
          },
         ]


    print
    def runTest(func):
        print 'Running %s tests' % len(P)
        errs = []
        show_content = 1
        for i, params in enumerate(P):
            try:
                content = func(show_content=show_content, **params)
            except Exception, exc:
                content = ''
                errs.append((i+1, exc))
                char = '-'
                raise
            else:
                char = '+'
            if show_content:
                print content
                print
            else:
                sys.stdout.write(char)
                sys.stdout.flush()
                
        print '\nDone'
        if errs:
            print 'Errors'
        for i, e in errs:
            if e:
                print '%s) %s' % (i, e)
        print

        
    ## "CGI" test function

    def doRequest(show_content=False, **params):
        req = Req()
        req.method = 'GET'
        content = index(req, **params)
        if show_content:
            print req.content_type
            print req.headers_out
            print req.status
            #print req.reason
        return content
    runTest(doRequest)


    ## Web Services test function
    
    def doRequest(service=None, show_content=False, **params):
        req = Req()
        req.method = 'GET'
        params['async'] = '1'
        content = index(req, **params)
        if show_content:
            print req.content_type
            print req.headers_out
            print req.status
        return content
    runTest(doRequest)



