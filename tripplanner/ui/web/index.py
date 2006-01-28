import os, datetime
import byCycle


region_aliases = {'milwaukee': 'milwaukeewi',
                  'metro': 'portlandor',
                  'portland': 'portlandor',
                  }


def index(region='', tmode='', q=''):
    region = region.strip().lower().replace(',', '')
    q = ' '.join(q.split())

    try:
        region = region_aliases[region]
    except KeyError:
        pass

    # Create an options list of regions, setting the selected region if we got
    # here by http://tripplanner.bycycle.org/x where x is the name of some
    # region
    region_option = '<option value="%s">%s</option>'
    region_option_selected = '<option value="%s" selected="selected">%s</option>'
    regions = {'wi': ['milwaukee',
                      ],
               'or': ['portland',
                      ],
               }
    states = regions.keys()
    states.sort()
    regions_option_list = []
    region_display = ''
    for state in states:
        areas = regions[state]
        #areas.sort()
        for area in areas:
            reg = '%s%s' % (area, state)
            if reg == region:
                opt = region_option_selected
                region_display = ' - %s, %s' % (area.title(), state.upper())
            else:
                opt = region_option 
            regions_option_list.append(opt % (reg, '%s, %s' % (area.title(),
                                                               state.upper())))
    regions_option_list = '\n'.join(regions_option_list)

    template = '%stripplanner/ui/web/tripplanner.html' % byCycle.install_path

    # Get and format the last modified date of the template
    stat = os.stat(template)
    last_modified = datetime.date.fromtimestamp(stat.st_mtime)
    last_modified = last_modified.strftime("%B %d, %Y")

    template_file = open(template)
    data = {'last_modified': last_modified,
            'regions_option_list': regions_option_list,
            'region': region_display,
            'q': q,
            'fr': '',
            'to': '',
            }

    result, fr_to = _processQuery(region, tmode, q)

    data['result'] = result

    if fr_to:
        q = ' to '.join(fr_to)
        data['q'] = q
        data['fr'], data['to'] = fr_to[:]

    content = template_file.read() % data
    template_file.close()
    return content


def _processQuery(region, tmode, q):
    if not q:
        result = '''
        <p>
        Welcome to the
        <a href="http://www.bycycle.org/" title="byCycle Home Page">byCycle</a> 
        <a href="http://www.bycycle.org/tripplanner"
           title="Information About the Trip Planner"
           >Trip Planner</a>.
        The Trip Planner is under active development and may have some issues.
        If you find a problem, please send us feedback by using the form on 
        <a href="http://www.bycycle.org/contact.html"
           title="Contact Us"
           >this page</a> or
        <a href="mailto:wyatt@bycycle.org">sending email</a>.
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
            result = '<h2>Address</h2><p>%s</p>' % str(address).replace('\n', '<br/>')
    return result, rq


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


if __name__ == '__main__':
    content = index(region='milwaukee', q='27th and lisbon')
    print content

    content = index(region='milwaukee', tmode='bike',
                    q='27th and lisbon to 35th and north')
    print content
