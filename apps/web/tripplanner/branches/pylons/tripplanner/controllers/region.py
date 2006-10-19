from tripplanner.lib.base import *
from byCycle.model import regions
from tripplanner.controllers.view import ViewController


class RegionController(ViewController):

    def show(self, region, service):
        """Show template for ``region``.

        Routes
        ------
        /
        /region

        """
        # Region not given in URL path; see if it's given as a query param
        if region is None:
            region = request.params.get('region', None)
            if region is not None:
                redirect_to('/%s' % region)

        # Get region key for region
        try:
            region_key = regions.getRegionKey(region)
        except ValueError:
            # Bad/unknown region
            # TODO: Show an error instead of just showing all regions
            region_key = 'all'
            c.error = 'Unknown region: %s' % region

        service = service or 'query'
        service = ''.join(service.strip().split()).lower()

        c.region_key = region_key
        c.service = service

        # Determine which input form should be shown
        style = 'display: none;'
        if service in ('address', 'geocode', 'query'):
            # show query by hiding route
            c.route_tab_style = style
            c.query_label_class = 'selected'
        elif service == 'route':
            # show route by hiding query
            c.query_tab_style = style
            c.route_label_class = 'selected'

        c.region_options = self._makeRegionOptions(region_key)
        return render_response('/region/%s.myt' % region_key)

    def _makeRegionOptions(self, region=''):
        """Make HTML options list with ``region`` selected, if ``region``.

        ``region`` `string` -- A valid region key or "all".

        """
        options = []
        option = '<option value="%s"%s>%s</option>'
        regions = {
            'or': ['portland',],
            'wi': ['milwaukee',],
            'wa': ['seattle',],
        }
        states = regions.keys()
        states.sort()
        for state in states:
            areas = regions[state]
            areas.sort()
            for area in areas:
                _r = '%s%s' % (area, state)
                text = '%s, %s' % (area.title(), state.upper())
                value = ''.join(text.split())
                if _r == region:
                    selected = ' selected="selected"'
                else:
                    selected = ''
                options.append(option % (_r, selected, text))
        return '\n'.join(options)
