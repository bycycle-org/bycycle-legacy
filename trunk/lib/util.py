"""$Id$

Utility functions that don't fit anywhere else.

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
