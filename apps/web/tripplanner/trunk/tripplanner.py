"""$Id: tripplanner.py 190 2006-08-16 02:29:29Z bycycle $

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
import cgi
import os
import sys
import re
import datetime
import urllib
import simplejson
from byCycle.lib import wsrest


class TripPlanner(object):
    def run(self):
        self.host = os.environ['HTTP_HOST']

        try:
            # Get the CGI vars and put them into a standard dict
            cgi_vars = cgi.FieldStorage(keep_blank_values=1)
            params = {}
            for param in cgi_vars.keys():
                param = ' '.join(param.split())
                val = ' '.join(cgi_vars.getvalue(param, '').split())
                # params are allowed to start with bycycle prefix (namespace)
                if param.startswith('bycycle_'):
                    param = '_'.join(param.split('_')[1:])
                params[param] = val

            # Take note of which parameters were passed
            self.params_present = dict(zip(params.keys(), [True] * len(params)))

            # Process query and get result
            params['method'] = os.environ['REQUEST_METHOD']
            status, response_text, params = self.processQuery(**params)

            # Transform result to output format
            self.render(status, response_text, **params)
        except Exception, e:
            import traceback
            sys.stderr = sys.stdout
            print 'Content-type: text/html\r\n\r'
            print '\r'
            print '<html><head><title>'
            print e
            print '</title>'
            print '</head><body>'
            print '<h1>TRACEBACK</h1>'
            print '<pre>'
            traceback.print_exc()
            print '</pre>'
            print '</body></html>'


    def processQuery(self, method='get', **params):
        params['region'] = self.getRegion(**params)

        # Analyze the query to determine the service and prepare the query for
        # the service.
        A = self.analyzeQuery(**params)
        params['service'], params['q'], params['fr'], params['to'] = A
        service = params['service']

        # Base path to web services
        import_path = 'webservices.%s'

        if service is None:
            status = 200
            response_text = None
        else:
            # Import web service
            try:
                module = __import__(import_path % service,
                                    globals(), locals(), [''])
            except ImportError, e:
                status = 400
                response_text = 'Error importing %s service\n[%s]' % \
                                (service, e)
            else:
                class_ = service.title()

                # Create web service object
                # E.g., if mod is geocode & class is Geocode, then this is
                # equivalent to geocode.Geocode(**params)
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


    def analyzeQuery(self, service=None, q=None, fr=None, to=None, **params):
        """Look at query variables and decide what type of query was made."""
        q_pres = 'q' in self.params_present
        fr_pres = 'fr' in self.params_present
        to_pres = 'to'  in self.params_present
        region_pres = 'region' in self.params_present
        service_pres = 'service' in self.params_present
        if service == 'query' or (not service_pres and q_pres):
            # Service was specified as query OR it wasn't specified but q was
            #
            # If param q contains the substring " to " between two other
            # substrings
            # OR if param q is a string repr of a list with at least two items,
            # query is for a route
            try:
                words = eval(q)
            except:
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
            else:
                # q doesn't look like a route query; assume it's geocode query
                service = 'geocode'
        elif (service == 'route' or (not service_pres and not q_pres and fr_pres and to_pres)):
            # Service was specified as route OR it wasn't specified but both fr and to were
            #
            service = 'route'
            q = [fr or '', to or '']
        elif service_pres:
            # A service was specified
            pass
        else:
            service = None
        return service, q or '', fr or '', to or ''


    def render(self, status, response_text, format='html', **params):
        result_set = ''

        if response_text is not None:
            if status < 400:
                result_set = eval(response_text)
                type_ = result_set['result_set']['type']
                callback = getattr(self, '%sCallback' % type_)
                try:
                    html = callback(status, result_set, **params)
                except AttributeError:
                    html =  response_text
                #result_set['result_set']['html'] = html

        if format == 'json':
            content_type = 'text/plain'
            if status >= 400:
                content = simplejson.dumps({'error':
                                            response_text or 'Unknown Error'})
            else:
                result_set['result_set']['html'] = urllib.quote(html)
                content = simplejson.dumps(result_set)
        else:
            content_type = 'text/html'
            template_path = 'templates'

            template = os.path.join(template_path, 'tripplanner.html')

            if response_text is None:
                result = self.getWelcomeMessage(template)
            elif status >= 400:
                result = '<h2>Error</h2>%s' % (response_text.replace('\n',
                                                                     '<br/>')
                                               or 'Unknown Error')
            else:
                result_set['result_set']['html'] = html
                result = html

            params['notice_display'] = 'none'
            params['notice'] = ''

            q_pres = 'q' in self.params_present
            fr_pres = 'fr' in self.params_present
            to_pres = 'to'  in self.params_present
            region_pres = 'region' in self.params_present
            if fr_pres or to_pres:
                # Show route form when either of 'from' or 'to' is passed as a CGI parameter
                params['route_tab_class'] = 'selected'
                params['geocode_tab_class'] = ''

                # See if either or both 'from' and 'to' are missing OR blank
                if not (params['fr'] and params['to']):
                    # If either one is missing...
                    params['notice_display'] = 'block'
                    if not (params['fr'] or params['to']):
                        # If _both_ are missing
                        params['notice'] = 'Enter both your "from" and "to" addresses, then click the "Find Route" button.'
                    elif not params['fr']:
                        # If just 'from' is missing
                        params['notice'] = 'Enter your "from" address, then click the "Find Route" button.'
                    elif not params['to']:
                        # If just 'to' is missing
                        params['notice'] = 'Enter your "to" address, then click the "Find Route" button.'
            else:
                # Default: show geocode form
                params['geocode_tab_class'] = 'selected'
                params['route_tab_class'] = ''
                if q_pres and not params['q']:
                    # A blank search query was passed in the URL (i.e., ?q=)
                    params['notice_display'] = 'block'
                    params['notice'] = 'Enter something to search for, then click the "Find" button.'

            if (q_pres or fr_pres or to_pres) and (not region_pres or (region_pres and not params['region'])):
                # A query was passed in the URL but no region was specified
                params['notice_display'] = 'block'
                if params['notice']:
                    params['notice'] += '<br/>Also, you must select a region.'
                else:
                    params['notice'] = 'You must select a region.'

            q = params['q']
            if isinstance(q, list):
               params['q'] = ' to '.join(q)

            params['http_status'] = status
            params['response_text'] = urllib.quote(simplejson.dumps(result_set))
            params['regions_opt_list'] = self.makeRegionsOptionList(**params)
            params['result'] = result
            params['amount_options'] = """
            <option value="">[$$$]</option>
            <option value="2">$2</option>
            <option value="5">$5</option>
            <option value="10">$10</option>
            <option value="15">$15</option>
            <option value="20">$20</option>
            <option value="25">$25</option>
            <option value="30">$30</option>
            <option value="35">$35</option>
            <option value="40">$40</option>
            <option value="45">$45</option>
            <option value="50">$50</option>
            <option value="75">$75</option>
            <option value="100">$100</option>
            <option value="250">$250</option>
            <option value="500">$500</option>
            <option value="1000">$1000</option>
            <option value="other">Other</option>"""

            for p in params:
                if params[p] is None:
                    params[p] = ''

            template_file = open(template)
            content = template_file.read() % params
            template_file.close()

        # Send result to client
        self.write('Content-type: %s' % content_type)
        self.write('Status: %s' % status)
        self.write()
        self.write(content, None)


    ## Callbacks

    def getIdAddr(self, geocode):
        """Get the the edge or node ID type address for the given geocode. """
        type_ = geocode['type']
        if type_ == 'postal':
            id_addr = '%s+%s' % (geocode['number'], geocode['edge_id'])
        elif type_ == 'intersection':
            id_addr = geocode['node_id']
        return id_addr


    def geocodeCallback(self, status, result_set, region='', **params):
        geocodes = result_set['result_set']['result']

        html = '<div class="info_win">' \
               '  <h2 style="margin-top:0">Address</h2><p>%s</p><p>%s</p>' \
               '</div>'
        href = ' href="javascript:void(0);" '
        onclick = ' onclick="setVal(\'%s\', \'%%s\', \'%%s\'); el(\'route_link\').onclick();" '
        set = '<p>Set as <a %s %s>From</a> or ' \
              '<a %s %s>To</a> address for route</p>' % \
              (href, onclick % ('fr'),
               href, onclick % ('to'))

        if status == 200:    # A-OK, one match
            code = geocodes[0]
            disp_addr = code['address'].replace('\n', '<br/>')
            field_addr = code['address'].replace('\n', ', ')
            id_addr = self.getIdAddr(code)
            result = html % (disp_addr, set %
                             (id_addr, field_addr,
                              id_addr, field_addr))
            code['html'] = urllib.quote(result)
        elif status == 300:  # Multiple matches
            result = ['<h2>Multiple Matches Found</h2><ul class="mma_list">']
            for i, code in enumerate(geocodes):
                disp_addr = code['address'].replace('\n', '<br/>')
                field_addr = code['address'].replace('\n', ', ')
                id_addr = self.getIdAddr(code)
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


    def routeCallback(self, status, result_set, **params):
        route = result_set['result_set']['result']
        if status == 200:    # A-OK, one match
            result = self.makeDirectionsTable(route)
        elif status == 300:  # Multiple matches
            geocodes_fr = route['fr']['geocode']
            geocodes_to = route['to']['geocode']
            result = self.makeRouteMultipleMatchList(geocodes_fr, geocodes_to,
                                                 **params)
        return result


    def makeRouteMultipleMatchList(self, geocodes_fr, geocodes_to,
                                    region='', q='', fr='', to='', **params):
        result = ['<div id="mma"><h2>Multiple Matches Found</h2>']

        def makeDiv(fr_or_to, style):
            if fr_or_to == 'fr':
                heading = 'From Address:'
            else:
                heading = 'To Address:'
            result.append('<div id="mma_%s" style="display: %s;">'
                          '<h3>%s</h3>' %
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
                id_addr = self.getIdAddr(code)
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

    def getRegion(self, region='', **params):
        region = ''.join(region.split())
        region = region.replace(',', '')
        region = region.lower()
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

    def makeRegionsOptionList(self, region='', **params):
        """Create an HTML options list of regions.

        Set the selected region if we got here by
        http://tripplanner.bycycle.org/?region=x where x is the name of a region.

        @return An HTML options list of regions sorted by state, then area

        """
        region = region.strip().lower().replace(',', '')

        regions = {'or': ['portland',],
                   'wi': ['milwaukee',],
                   'pa': ['pittsburgh',],
                   #'wa': ['seattle',]
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


    def getWelcomeMessage(self, template):
        return '''
        <p style="margin-top:0;">
          The <a href="byCycle.org"
                 title="byCycle Home Page"
                 >byCycle.org</a>
          bicycle trip planner is under active development.
          Please <a href="http://bycycle.org/contact"
          title="Send us problem reports, comments, questions, and suggestions"
          >contact us</a> with any problems, comments, questions, or
          suggestions.
        </p>
        <p>
          If you find this site useful or would like help it improve, please
          consider <b><a href="http://bycycle.org/support#donate"
          target="_new">donating</a></b>. Any amount helps.
        </p>
        %s
        <p>
          &copy; 2006
          <a href="http://bycycle.org/"
             title="byCycle Home Page"
             >byCycle.org</a>
          <br/>
          Last modified: %s
          <br/>
        </p>
        ''' % (self.getDisclaimer(), self.getLastModified(template))
        return welcome_message


    def getDisclaimer(self):
        return '''
        <p>
          <b>Disclaimer</b>: As you are riding, please keep in mind that you
          don\'t <i>have</i> to
          follow the suggested route. <i>It may not be safe at any given
          point.</i> If you see what looks like an unsafe or undesirable
          stretch in the suggested route, you can decide to walk, ride on the
          sidewalk, or go a different way.
        </p>
        <p>
          Users should independently verify all information presented here.
          This service is provided <b>AS IS</b> with <b>NO WARRANTY</b> of any
          kind.
        </p>
        '''


    def getLastModified(self, file_name=''):
        """Get and format the last modified date of file_name."""
        stat = os.stat(file_name)
        last_modified = datetime.date.fromtimestamp(stat.st_mtime)
        last_modified = last_modified.strftime('%B %d, %Y')
        if last_modified[0] == '0':
            last_modified = last_modified[1:]
        return last_modified


    def makeDirectionsTable(self, route):
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

        table = '''
        <table class="summary">
            <tr>
              <td class="start">
                <h2><a href="javascript:void(0);" class="start"
                       onclick="showMapBlowup(0);">Start</a></h2>
              </td>
              <td class="start">%s</a>
              </td>
            </tr>
            <tr>
              <td class="end">
                <h2><a href="javascript:void(0);" class="end"
                       onclick="showMapBlowup(%s);">End</a></h2>
              </td>
              <td class="end">%s</td>
            </tr>
            <tr>
              <td class="total_distance"><h2>Distance</h2></td>
              <td>%s miles</td>
            </tr>
        </table>
        <table class="directions">
            %%s
        </table>
        ''' % (fr_addr, len(linestring) - 1, to_addr, distance)

        # Template for direction row
        d_row = '''
        <tr>
          <td class="count %s">
            <a href="javascript:void(0)"
               onclick="showMapBlowup(%s)">%s.</a>
          </td>
          <td class="turn %s">%s</td>
          <td class="direction %s">%s</td>
          <td class="segment_distance %s">%smi</td>
        </tr>
        '''

        # Direction rows
        row_class = 'a'
        last_i = len(directions)
        tab = '&nbsp;' * 4
        d_rows = []
        row_i = []
        i = 1
        for d in directions:
            turn = d['turn'].title()
            street = d['street']
            if isinstance(street, list):
                street = street[1]
            if i == 1:
                street = '%s toward %s' % (street, d['toward'])
            jogs = d['jogs']
            ls_index = d['ls_index']
            mi = d['distance']['mi']

            if turn.lower() == 'straight':
                turn = 'Becomes'

            row_i = [street]
            
            if jogs:
                row_i.append('<br/>%sJogs...' % tab)
                for j in jogs:
                    row_i.append('<br/>%s%s&middot; <i>%s</i> at %s' % \
                                 (tab, tab, j['turn'], j['street']))

            # Create row for direction
            d_rows.append(d_row % (
                row_class, ls_index, i,     # count
                row_class, turn,            # turn
                row_class, ''.join(row_i),  # direction
                row_class, mi               # segment distance
            ))

            row_class = ['a', 'b'][row_class == 'a']
            i += 1

        # Tack on last direction
        last_row = d_row  % (
            row_class, len(linestring) - 1, i, 
            row_class, 'End',
            row_class, '%s' % last_street, 
            row_class, mi
        )
        
        d_rows.append(last_row)

        table = table % ''.join([str(d) for d in d_rows])

        try:
            fr_id = '%s %s' % (fr['number'], fr['edge_id'])
        except KeyError:
            fr_id = fr['node_id']

        try:
            to_id = '%s %s' % (to['number'], to['edge_id'])
        except KeyError:
            to_id = to['node_id']

        reverse_div = '''
        <div id="reverse_div">
          <a href="javascript:void(0);"
             onclick="reverseDirections('%s', '%s');"
             >Reverse Directions</a>
        </div>''' % (to_id, fr_id)

        result = ''.join((reverse_div, table, self.getDisclaimer()))

        return result


    def write(self, content='', newline='\r\n'):
        sys.stdout.write('%s%s' % (content, newline or ''))
