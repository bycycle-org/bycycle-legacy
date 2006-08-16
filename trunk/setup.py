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
from distutils.core import setup
import sys

if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
    
setup(name='byCycle',
      description='byCycle Trip Planner',
      long_description='byCycle Trip Planner',
      author='Wyatt L. Baldwin',
      author_email='wyatt@byCycle.org',
      url='http://www.byCycle.org/',
      version='0.3alpha',
      classifiers=['Development Status - Alpha',
                   'License :: GPL for noncommercial use only',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Environment :: Console',
                   'Environment :: Web Environment',
                   ],
      packages=['lib',
                'tripplanner',
                'tripplanner.model',
                'tripplanner.model.tests',
                'tripplanner.model.milwaukeewi',
                'tripplanner.model.milwaukeewi.data',
                'tripplanner.model.portlandor',
                'tripplanner.model.portlandor.data',
                'tripplanner.model.pittsburghpa',
                'tripplanner.model.pittsburghpa.data',
                'tripplanner.services',
                'tripplanner.services.geocode',                
                'tripplanner.services.route',
                'tripplanner.ui',
                'tripplanner.ui.web',
                'tripplanner.webservices',
                ],
      )
