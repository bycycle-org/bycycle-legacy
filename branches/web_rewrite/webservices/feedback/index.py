"""$Id$

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
#!/usr/local/bin/python2.4
# Feedback Web Service
from byCycle.lib import wsrest

class Feedback(wsrest.RestWebService):
    def __init__(self):
        wsrest.RestWebService.__init__(self)
             
    def GET(self):
        try:
            feedback = self.input['feedback']
            data = eval(self.input['data'])
        except Exception, e:
            raise
        else:
            import time
            now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            
            outdata = ['----------------------------------------',
                       now, '--Message', feedback, '--Fields']
            for k in data:
                outdata.append(k)
                if data[k]:
                    outdata.append('    %s' % data[k])
            outdata.append('\n')
            outdata = '\n'.join([str(d) for d in outdata])
            
            outfile = open('feedback', 'a')
            outfile.write(outdata)
            outfile.close()            
            result = wsrest.ResultSet('feedback', {'feedback': {}})
            return repr(result)

Feedback()
