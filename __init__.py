import os.path as ospath

# Add your install path to this list
paths = (# Typical UNIX installation
         '/usr/local/lib/python2.4/site-packages/byCycle/',
         '/usr/lib/python2.4/site-packages/byCycle/',

         '/home/u6/bycycle/lib/python2.4/site-packages/byCycle/',

         # Typical  Windows installation
         'C:/Python24/Lib/site-packages/byCycle/',
         'D:/Python24/Lib/site-packages/byCycle/'
         'E:/Python24/Lib/site-packages/byCycle/'
        )

for path in paths:
    if ospath.exists(path):
        install_path = path
        break

