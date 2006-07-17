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
