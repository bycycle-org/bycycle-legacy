#!/home/u6/bycycle/bin/python -OO


import cgi, os, sys, urllib


def _main():
    try:
        # Get the CGI vars and put them into a standard dict
        cgi_vars = cgi.FieldStorage()
        params = {}
        for param in cgi_vars.keys():
            param = ' '.join(param.split())
            val = ' '.join(cgi_vars.getvalue(param, '').split())
            # params are allowed to start with bycycle prefix (namespace)
            if param.startswith('bycycle_'):
                param = '_'.join(param.split('_')[1:])
            params[param] = val

        # Process query and get result
        params['method'] = os.environ['REQUEST_METHOD']
        status, response_text, params = _processQuery(**params)

        # Transform result to output format
        O = _makeOutput(status, response_text, **params)
        content_type, status, content = O

        # Deliver result to client
        _printrn('Content-type: %s' % content_type)        
        _printrn('Status: %s' % status)
        _printrn()
        sys.stdout.write(content)
    except Exception, e:
        import traceback
        sys.stderr = sys.stdout
        print 'Content-type: text/html\r\n\r'
        print
        print '<html><head><title>'
        print e
        print '</title>'
        print '</head><body>'
        print '<h1>TRACEBACK</h1>'
        print '<pre>'
        traceback.print_exc()
        print '</pre>'
        print '</body></html>'
    

def _processQuery(method='get', **params):    
    from byCycle.lib import wsrest

    params['region'] = _getRegion(**params)

    # Analyze the query to determine the service and prepare the query for 
    # the service.
    A = _analyzeQuery(**params)
    params['service'], params['q'], params['fr'], params['to'] = A
    service = params['service']

    # Import web service module
    import_path = 'byCycle.tripplanner.webservices.%s'

    if service is None:
        status = 200
        response_text = None
    else:
        module = __import__(import_path % service, globals(), locals(), [''])
        class_ = service.title()

        # Create web service object
        # E.g., if mod is geocode & class is Geocode, then this is equivalent
        # geocode.Geocode(**params)
        ws_obj = getattr(module, class_)(**params)

        # Process the query according to the request method
        try:
            response_text = getattr(ws_obj, method)()
        except wsrest.MethodNotAllowedError, exc:
            status = exc.status
            response_text = exc.reason + ' (%s)' % method
            #req.allow_methods(exc.getAllowMethods(ws_obj))
        except wsrest.MultipleChoicesError, exc:
            status = exc.status
            response_text = exc.choices
        except wsrest.RestError, exc:
            status = exc.status
            response_text = exc.reason
        except Exception, exc:
            status = 500
            response_text = str(exc)
        else:
            status = 200
    
    return status, response_text, params


def _analyzeQuery(q=None, fr=None, to=None, **params):
    if q is fr is to is None:
        service = None
    
    # If query has params fr and to and not q, it is a route query
    if q is None and fr is not None and to is not None:
        service = 'route'
        q = [fr, to]

    # If param q contains the substring " to " between two other substrings OR
    # if param q is a list (or a string repr of a list) with at least two
    # items, query is for a route
    try:
        service
    except NameError:
        try:
            words = eval(q)
        except:
            import re
            sRe = '\s+to\s+'
            oRe = re.compile(sRe, re.I)
            try:
                words = re.split(oRe, q)
            except TypeError:
                words = None
        if isinstance(words, list) and len(words) > 1:
            service = 'route'    
            q = words
            fr = q[0]
            to = q[1]

    # If we can't determine q is a route query, assume it's a geocode query
    try:
        service
    except NameError:
        service = 'geocode'

    return service, q, fr, to


def _makeOutput(status, response_text, format='html', **params):
    import simplejson

    if response_text is not None:
        if status < 400:
            result_set = eval(response_text)
            type_ = result_set['result_set']['type']
            callback = '_%sCallback' % type_
            html = eval(callback)(status, result_set, **params)
            result_set['result_set']['html'] = urllib.quote(html)
            response_text = simplejson.dumps(result_set)
        else:
            response_text = '<h2>Error</h2>%s' % response_text

    if format == 'json':
        content_type = 'text/plain'
        content = response_text or ''
    elif format == 'html':
        content_type = 'text/html'

        template = 'tripplanner.html'
        
        if response_text is None:
            result = _getWelcomeMessage(template)
        elif status >= 400:
            result = response_text or 'Unknown Error'

        q = params['q']
        if isinstance(q, list):
           params['q'] = ' to '.join(q) 

        params['http_status'] = status
        params['response_text'] = response_text
        params['regions_opt_list'] = _makeRegionsOptionList(**params)
        params['result'] = result
        
        for p in params:
            if params[p] is None:
                params[p] = ''
                
        template_file = open(template)
        content = template_file.read() % params
        template_file.close()
    return content_type, status, content
    

## Callbacks

def _getIdAddr(geocode):
    type_ = geocode['type']
    if type_ == 'postal':
        id_addr = '%s+%s' % (geocode['number'], geocode['edge_id']) 
    elif type_ == 'intersection':
        id_addr = geocode['node_id']    
    return id_addr


def _geocodeCallback(status, result_set, region='', **params):
    geocodes = result_set['result_set']['result']
    
    html = '<div class="info_win">' \
           '  <h2 style="margin-top:0">Address</h2><p>%s</p><p>%s</p>' \
           '</div>'
    href = ' href="javascript:void(0);" '
    onclick = ' onclick="setVal(\'%s\', \'%%s\', \'%%s\')" '
    set = '<p>Set as <a %s %s>From</a> or ' \
          '<a %s %s>To</a> address for route</p>' % \
          (href, onclick % ('fr'),
           href, onclick % ('to'))
    
    if status == 200:    # A-OK, one match
        code = geocodes[0]
        disp_addr = code['address'].replace('\n', '<br/>')
        field_addr = code['address'].replace('\n', ', ')
        id_addr = _getIdAddr(code)
        result = html % (disp_addr, set %
                         (id_addr, field_addr,
                          id_addr, field_addr))
        code['html'] = urllib.quote(result)        
    elif status == 300:  # Multiple matches
        result = ['<h2>Multiple Matches Found</h2><ul class="mma_list">']
        for i, code in enumerate(geocodes):
            disp_addr = code['address'].replace('\n', '<br/>')
            field_addr = code['address'].replace('\n', ', ')
            id_addr = _getIdAddr(code)
            code['html'] = urllib.quote(html %
                                        (disp_addr, set %
                                         (id_addr, field_addr,
                                          id_addr, field_addr)))
            result.append('<li>'
                          '  %s<br/>'
                          '  <a href="javascript:void(0);"'
                          '     onclick="if (map) '
                          'map.setCenter(new GLatLng(%s, %s)); '
                          'return false;"'
                          '>Show on map</a>'
                          '  &middot;'
                          '  <a href="?region=%s&q=%s"'
                          '     onclick="showGeocode(%s, true); '
                          'return false;"'
                          '>Select</a>'
                          '</li>' % (disp_addr,
                                     code['y'], code['x'],
                                     region,
                                     id_addr,
                                     i)
                          )
        result.append('</ul>')
        result = '\n'.join(result)
    return result


def _routeCallback(status, result_set, **params):
    route = result_set['result_set']['result']
    if status == 200:    # A-OK, one match
        result = _makeDirectionsTable(route)
    elif status == 300:  # Multiple matches
        geocodes_fr = route['fr']['geocode']
        geocodes_to = route['to']['geocode']
        result = _makeRouteMultipleMatchList(geocodes_fr, geocodes_to,
                                             **params)
    return result


def _makeRouteMultipleMatchList(geocodes_fr, geocodes_to,
                                region='', q='', fr='', to='', **params):
    result = ['<div id="mma"><h2>Multiple Matches Found</h2>']

    def makeDiv(fr_or_to, style):
        if fr_or_to == 'fr':
            heading = 'From Address:'
        else:
            heading = 'To Address:'
        result.append('<div id="mma_%s" style="display: %s;"><h3>%s</h3>' % \
                      (fr_or_to, style, heading))

    def makeList(fr_or_to, q, geocodes, find):
        result.append('<ul class="mma_list">')
        if fr_or_to == 'fr':
            q_temp = '%%s+to+%s' % q[1]
        else:
            q_temp = '%s+to+%%s' % q[0]
        for code in geocodes:
            addr = code['address']
            disp_addr = addr.replace('\n', '<br/>')
            field_addr = addr.replace('\n', ', ')
            id_addr = _getIdAddr(code)
            q = (q_temp % id_addr)
            result.append('<li>'
                          '  %s<br/>'
                          '  <a href="javascript:void(0);"'
                          '     onclick='
                          '"if (map) map.setCenter(new GLatLng(%s, %s)); '
                          'return false;"'
                          '>Show on map</a>'
                          '  &middot;'
                          '  <a href="?region=%s&q=%s"'
                          '     onclick="%s return false;"'
                          '     >Select</a>'
                          '</li>' % (disp_addr,
                                     code['y'], code['x'],
                                     region,
                                     q,
                                     find % (id_addr, field_addr))
                          )
        result.append('</ul></div>')

    if geocodes_fr:
        find = "setVal('fr', '%s', '%s'); "
        if geocodes_to:
            find += "el('mma_fr').style.display = 'none'; " \
                    "el('mma_to').style.display = 'block'; "
        else:
            find += "doFind('route'); "
        makeDiv('fr', 'block')
        makeList('fr', q, geocodes_fr, find)

    if geocodes_to:
        find = "setVal('to', '%s', '%s'); doFind('route'); "
        if geocodes_fr:
            style = 'none'
        else:
            style = 'block'
        makeDiv('to', style)
        makeList('to', q, geocodes_to, find)
      
    result.append('</div>')
    return ''.join(result)


## Helpers

def _getRegion(region='', **params):
    region_aliases = {'mil': 'milwaukeewi',
                      'milwaukee': 'milwaukeewi',
                      'metro': 'portlandor',
                      'por': 'portlandor',
                      'portland': 'portlandor',
                      }
    try:
        region = region_aliases[region]
    except KeyError:
        pass
    return region


## Output
    
def _makeRegionsOptionList(region='', **params):
    """Create an HTML options list of regions.

    Set the selected region if we got here by
    http://tripplanner.bycycle.org/?region=x where x is the name of a region.

    @return An HTML options list of regions sorted by state, then area
    
    """
    region = region.strip().lower().replace(',', '')

    regions = {'or': ['portland',
                      ],
               'wi': ['milwaukee',
                      ],
               'pa': ['pittsburgh',
                      ],
               }

    states = regions.keys()
    states.sort()

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


def _getWelcomeMessage(template):
    welcome_message = '''
    <p style="margin-top:0;">
    The Trip Planner is under active development. Please
    <a href="http://www.bycycle.org/contact.html"
    title="Send us problem reports, comments, questions, and suggestions"
    >contact us</a>
    with any problems, comments, questions, or suggestions.
    </p>
    
    <p>
    Users should independently verify all information presented here. This
    service is provided AS IS with NO WARRANTY of any kind. 
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
    import datetime
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
 
    fr_addr = str(fr_addr).replace('\n', '<br/>')
    to_addr = str(to_addr)
    last_street = to_addr.split('\n')[0]
    to_addr = to_addr.replace('\n', '<br/>')

    s_table = """
    <table id="summary">
        <tr>
          <td class="start">
            <h2><a href="javascript:void(0);" class="start"
                   onclick="showMapBlowup(0);">Start</a>
            </h2>
          </td>
          <td class="start">%s</a>
          </td>
        </tr>
        <tr>
          <td class="end">
            <h2><a href="javascript:void(0);" class="end"
                   onclick="showMapBlowup(%s);">End</a>
            </h2>
          </td>
          <td class="end">%s</td>
        </tr>
        <tr>
          <td class="total_distance"><h2>Distance</h2></td>
          <td>%s miles</td>
        </tr>
    </table>
    """ % (fr_addr, len(linestring) - 1, to_addr, distance)

    d_table = """
    <!-- Directions -->
    <table id="directions">%s</table>
    """

    d_row = """
    <tr>
      <td class="count %s">
        <a href="javascript:void(0)"
           onclick="showMapBlowup(%s)">%s.</a>
      </td>
      <td class="direction %s">%s</td>
    </tr>
    """               

    # Direction rows
    row_class = 'a'
    last_i = len(directions)
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

        d_rows.append(d_row % (row_class, ls_index, i, row_class,
                               ''.join(row_i)))
        del row_i[:]
        if row_class == 'a': row_class = 'b'
        else: row_class = 'a'
        i += 1

    last_row = d_row  % (row_class, len(linestring) - 1, i, row_class,
                         '<b>End</b> at <b>%s</b>' % last_street)
    d_rows.append(last_row)
    
    d_table = d_table % ''.join([str(d) for d in d_rows])
    return ''.join((s_table, d_table))            
        

def _printrn(print_me=''):
    sys.stdout.write('%s\r\n' % print_me)
        

if __name__ == '__main__':
    _main()
