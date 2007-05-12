def encode_pairs(pairs):
    """Encode a set of lat/long pairs.

    ``pairs``
        A list of lat/long pairs ((lat, long), ...)
        Note carefully that the order is latitude, longitude

    return
        An encoded string representing all pairs

    Example::

        >>> pairs = ((38.5, -120.2), (43.252, -126.453), (40.7, -120.95))
        >>> encode_pairs(pairs)
        '_p~iF~ps|U_c_\\\\fhde@~lqNwxq`@'

    """
    result = []
    lat_prev, long_prev = 0, 0
    for pair in pairs:
        encoded_val, lat_prev = encode(pair[0], lat_prev)
        result.append(encoded_val)
        encoded_val, long_prev = encode(pair[1], long_prev)
        result.append(encoded_val)
    result = ''.join(result)
    return result

def encode(x, prev_int):
    """Encode a single latitude or longitude.
    
    ``x``
        The latitude or longitude to encode
        
    ``prev_int``
        The int value of the previous latitude or longitude
        
    Return the encoded value and its int value, which is used
        
    Example::
    
        >>> x = -179.9832104
        >>> encoded_x, prev = encode(x, 0)
        >>> encoded_x
        '`~oia@'
        >>> prev
        -17998321
        >>> x = -120.2
        >>> encode(x, prev)
        ('al{kJ', -12020000)
    
    """
    int_value = int(x * 1e5)
    res = int_value - prev_int
    res = res << 1
    if res < 0:
        res = ~res
    chunk = res
    res = []
    # while there are more than 5 bits left (that aren't all 0)...
    while chunk >= 32:  # 32 == 0xf0 == 100000
        res.append(chunk & 31)  # 31 == 0x1f == 11111
        chunk = chunk >> 5
    res = [(c | 0x20) for c in res]
    res.append(chunk)
    res = [(i + 63) for i in res]
    res = [chr(i) for i in res]
    res = ''.join(res)
    return res, int_value

def test_encode_negative():
    f = -179.9832104
    assert encode(f, 0)[0] == '`~oia@'
    
    f = -120.2
    assert encode(f, 0)[0] == '~ps|U'

def test_encode_positive():
    f = 38.5
    assert encode(f, 0)[0] == '_p~iF'

def test_encode_one_pair():
    pairs = [(38.5, -120.2)]
    expected_encoding = '_p~iF~ps|U'
    assert encode_pairs(pairs) == expected_encoding

def test_encode_pairs():
    pairs = (
        (38.5, -120.2),
        (40.7, -120.95),
        (43.252, -126.453),
        (40.7, -120.95),
    )
    expected_encoding = '_p~iF~ps|U_ulLnnqC_mqNvxq`@~lqNwxq`@'
    assert encode_pairs(pairs) == expected_encoding
    
    pairs = (
        (37.4419, -122.1419),
        (37.4519, -122.1519),
        (37.4619, -122.1819),
    )
    expected_encoding = 'yzocFzynhVq}@n}@o}@nzD'
    assert encode_pairs(pairs) == expected_encoding    
