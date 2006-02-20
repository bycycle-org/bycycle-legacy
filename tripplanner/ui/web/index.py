import os, datetime
import byCycle


def index(region='', tmode='', q='', **params):
    region = region.strip().lower().replace(',', '')
    region = _getRegionForAlias(region)
    q = ' '.join(q.split())
    
    # Create an options list of regions, setting the selected region if we got
    # here by http://tripplanner.bycycle.org/x where x is the name of some
    # region (list is sorted by state, then area)
    region_opt = '<option value="%s">%s</option>'
    region_opt_selected = '<option value="%s" selected="selected">%s</option>'
    regions = {'wi': ['milwaukee',
                      ],
               'or': ['portland',
                      ],
               }
    states = regions.keys()
    states.sort()
    regions_opt_list = []
    region_heading = 'All Regions'
    for state in states:
        areas = regions[state]
        #areas.sort()
        for area in areas:
            reg = '%s%s' % (area, state)
            if reg == region:
                opt = region_opt_selected
                region_heading = '%s, %s' % (area.title(), state.upper())
            else:
                opt = region_opt 
            regions_opt_list.append(opt % (reg, '%s, %s' %
                                           (area.title(),
                                            state.upper())))
    regions_opt_list = '\n'.join(regions_opt_list)

    template = '%stripplanner/ui/web/tripplanner.html' % byCycle.install_path

    # Get and format the last modified date of the template
    stat = os.stat(template)
    last_modified = datetime.date.fromtimestamp(stat.st_mtime)
    last_modified = last_modified.strftime('%d %b %Y')
    if last_modified[0] == '0':
        last_modified = last_modified[1:]

    template_file = open(template)
    data = {'q': q,
            'fr': '',
            'to': '',
            'regions_opt_list': regions_opt_list,
            'region_heading': region_heading,
            'last_modified': last_modified,
            }

    result, fr_to = _doQuery(region, tmode, q)

    data['result'] = result

    if fr_to:
        q = ' to '.join(fr_to)
        data['q'] = q
        data['fr'], data['to'] = fr_to[:]

    content = template_file.read() % data
    template_file.close()
    return content


def _doQuery(region, tmode, q):
    if not q:
        result = '''
<p style="margin-top: 0;">
  Welcome to the
  <a href="http://www.bycycle.org/"
    title="byCycle Home Page"
    >byCycle</a> 
  <a href="http://www.bycycle.org/tripplanner"
    title="Information about the Trip Planner"
    >Trip Planner</a>,
  an interactive trip planning application that aims to help encourage
  bicycling and other alternative modes of transportation. The Trip Planner is
  under active development. If you find a problem or have any comments,
  questions, or suggestions, please
  <a href="http://www.bycycle.org/contact.html"
    title="Contact us"
    >contact us</a>.
</p>

<p>
  The Trip Planner is being developed in cooperation with the following
  organizations that provide data and other support to the project:
  <ul>
    <li>
      <a href="http://www.metro-region.org/">Metro</a> in the 
      <a href="http://tripplanner.bycycle.org/?region=PortlandOR"
        >Portland, OR</a>, area
    </li>
    <li>    
      <a href="http://www.bfw.org/">Bicycle Federation of Wisconsin</a> in the 
      <a href="http://tripplanner.bycycle.org/?region=MilwaukeeWI"
        >Milwaukee, WI</a>, area
    </li>
  </ul>
</p>

<p>
  Although every reasonable effort is being made to provide accurate and
  useful routes and other information, no guarantee can be made in regard to
  such accuracy or usefulness. Users are advised to independently verify any
  information presented here and are encouraged to 
  <a href="http://www.bycycle.org/contact.html"
    title="Send us your feedback"
    >provide feedback</a>. 
</p>
'''
        rq = None
    else:
        rq = _isRouteQuery(q)
        if rq:
            from byCycle.tripplanner.services import route
            route = route.get(region=region, tmode=tmode, q=rq)
            result = route['directions_table']
        else:
            from byCycle.tripplanner.services import geocode
            geocodes = geocode.get(region=region, q=q)
            address = geocodes[0]
            result = '<h2>Address</h2><p>%s</p>' % \
                     str(address).replace('\n', '<br/>')
    return result, rq


## Web Services

def geocode(req, **params):
    return _doWebServiceQuery(req, 'geocode', **params)


def route(req, **params):
    return _doWebServiceQuery(req, 'route', **params)


def _doWebServiceQuery(req, service, **params):
    try: 
        from mod_python import apache
    except ImportError:
        pass
    from byCycle.lib import wsrest

    params['region'] = _getRegionForAlias(params['region'])
        
    # Import correct web service module
    path = 'byCycle.tripplanner.webservices.%s'
    mod = __import__(path % service, globals(), locals(), [''])
    # Create web service object
    obj = getattr(mod, service.title())(**params)
    
    method = req.method
    try:
        content = eval('obj.%s' % method)()
    except wsrest.MethodNotAllowedError, exc:
        content = exc.reason + ' (%s)' % method
        req.allow_methods(exc.getAllowMethods(self))
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
    
    req.content_type = 'text/plain'
    return content


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


def _isRouteQuery(q):
    fr_to = q.lower().split(' to ')
    if len(fr_to) > 1:
        return fr_to
    try:
        fr_to = eval(q)
    except:
        pass
    else:
        if isinstance(fr_to, list) and len(fr_to) > 1:
            return fr_to
    return None


## Testing
    
if __name__ == '__main__':
    import sys

    
    class Req(object):
        def __init__(self):
            self.content_type = ''
            self.headers_out = {}


    P = [{'service': geocode,
          'region': 'milwaukee',
          'q': '27th and lisbon'
          },
         
         {'service': route,
          'region': 'milwaukeewi',
          'tmode': 'bike',
          'q': "['35th and north', '124 and county line']"
          },
         
         {'service': route,
          'region': 'milwaukeewi',
          'tmode': 'bike',
          'q': "['35th and north', '27th and lisbon']"
          },
         ]


    print
    def runTest(func):
        print 'Running %s tests' % len(P)
        errs = []
        show_content = False
        for i, params in enumerate(P):
            try:
                content = func(show_content=show_content, **params)
            except Exception, exc:
                content = ''
                errs.append((i+1, exc))
                char = '-'
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
        return index(**params)
    runTest(doRequest)


    ## Web Services test function
    
    def doRequest(service=None, show_content=False, **params):
        req = Req()
        req.method = 'GET'
        content = service(req, **params)
        if show_content:
            print req.content_type
            print req.headers_out
            print req.status
            #print req.reason
        return content
    runTest(doRequest)



