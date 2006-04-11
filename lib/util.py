"""
$$$
:File: util.py
:Description: Utility functions that don't fit anywhere else
:Author: Wyatt Baldwin
:Copyright: 2005 byCycle.org
:License: GPL
:Version: 0
:Date: 15 Aug 2005
$$$

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
ERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""

def getMostFrequentInList(the_list):
    """Get the list item that occurs most often."""
    cnt = {}
    the_list = [i for i in the_list if i]
    for i in the_list:
        cnt[i]=cnt.get(i, 0) + 1
    C = [None] + sorted(cnt.keys(), key=cnt.get)
    return C[-1]


def joinAttrs(attrs, join_string=' '):
    """Join the values in attrs, leaving out empty values."""
    if isinstance(attrs, dict):
        attrs = attrs.values()
    return join_string.join([str(a) for a in attrs if a])


def swapKeysAndValues(old_dict):
    """Make a new dict with keys and values in given dict swapped.

    In other words, make a new dict that has the keys of the old dict as the
    values and the respective values of the old dict as the keys to those
    values.

    """
    new_dict = {}
    for k in old_dict:
        new_dict[old_dict[k]] = k
    return new_dict
