        names = ('address', 'start', 'end', 'num', 'id', 'region')
        N = '|;.join(names)
        expr = '(?P<name>(%s))\s*:\s*(?P<value>(?:\w+\s+)+)' % N
        matches = re.findall(expr, q + ' ')
        matches = [(m[0], m[1].strip()) for m in matches]
        matches = dict(matches)
        
        building_number = matches.get('num', None)
        network_id = matches.get('id', None)
        q_region = matches.get('region', None)        