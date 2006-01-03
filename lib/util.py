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
def getMostFrequentInList(lst):
    """Get the list item that occurs most often."""
    cnt = {}
    lst = [i for i in lst if i]
    for i in lst: cnt[i]=cnt.get(i, 0) + 1
    C = [None] + sorted(cnt.keys(), key=cnt.get)
    return C[-1]


