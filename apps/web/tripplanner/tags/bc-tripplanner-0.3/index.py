#!/home/u2/bycycle/bin/python -OO
"""$Id: index.py 190 2006-08-16 02:29:29Z bycycle $

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
try:
    if __name__ == '__main__':
        import os
        os.environ['PYTHON_EGG_CACHE'] = '/home/u2/bycycle/.python-eggs'
        import tripplanner
        tripplanner.TripPlanner().run()
except:
    """ Output an error page with traceback, etc """
    print 'Content-type: text/html\r\n\r'

    import cgi
    import sys
    import traceback
        
    print '<h2>An Internal Error Occurred!</h2>'
    print '<i>Runtime Failure Details:</i><p>'
    
    t, val, tb = sys.exc_info()
    print '<p>Exception = ', t, '<br/>'
    print 'Value = ', val, '\n', '<p>'
    
    print '<i>Traceback:</i><p>'
    tbf = traceback.format_tb(tb)
    print '<pre>'
    for item in tbf:
        outstr = item.replace('<', '&lt;')
        outstr = outstr.replace('>', '&gt;')
        outstr = outstr.replace('\n', '\n')
        print outstr, '<br/>'
    print '</pre>'
    print '</p><p>'
    
    cgi.print_environ()
    print '<br/><br/>'

