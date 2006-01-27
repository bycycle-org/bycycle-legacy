def milwaukee(**params):
    return index(region='milwaukee', **params)


def metro(**params):
    return index(region='metro', **params)
portland = metro


def index(region='', **params):
    import os, datetime
    import byCycle
    
    template = '%stripplanner/ui/web/tripplanner.tmpl' % byCycle.install_path

    # Create an options list of regions, setting the selected region if we got
    # here by http://tripplanner.bycycle.org/x where x is the name of some
    # region
    region_option = '<option value="%s">%s</option>'
    region_option_selected = '<option value="%s" selected="selected">%s</option>'
    regions_map = {'Milwaukee, WI': 'milwaukee',
                  'Portland, OR': 'metro'}
    regions = regions_map.keys()
    regions.sort()
    regions_option_list = []
    for r in regions:
        region_abbrev = regions_map[r]
        if region_abbrev == region:
            regions_option_list.append(region_option_selected%(region_abbrev, r))
        else:
            regions_option_list.append(region_option%(region_abbrev, r))
    regions_option_list = '\n'.join(regions_option_list)

    # Get the last modified date of the template
    stat = os.stat(template)
    last_modified = datetime.date.fromtimestamp(stat.st_mtime)
    last_modified = last_modified.strftime("%B %d, %Y")


    data = {'last_modified': last_modified,
            'regions_option_list': regions_option_list}

    template_file = open(template)
    result = template_file.read() % data
    template_file.close()
    return result

