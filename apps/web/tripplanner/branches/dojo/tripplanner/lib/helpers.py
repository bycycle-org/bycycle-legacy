"""
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from webhelpers import *
from pylons.helpers import log
from pylons.i18n import get_lang, set_lang


def if_ie(content, join_string=''):
    return join_string.join(('<!--[if IE]>', content, '<![endif]-->'))
