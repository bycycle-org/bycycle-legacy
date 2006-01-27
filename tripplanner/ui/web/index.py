import os, datetime
import byCycle


region_aliases = {'milwaukee': 'milwaukeewi',
                  'metro': 'portlandor',
                  'portland': 'portlandor',
                  }


def index(region='', **params):
    region = region.lower().replace(',', '')

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
            }
    content = template_file.read() % data
    template_file.close()
    return content

