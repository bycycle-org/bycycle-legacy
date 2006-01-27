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
      author_email='wyatt.lee.baldwin@gmail.com',
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
                'tripplanner.model.milwaukeewi',
                'tripplanner.model.milwaukeewi.data',
                'tripplanner.model.portlandor',
                'tripplanner.model.portlandor.data',
                'tripplanner.services',
                'tripplanner.services.geocode',                
                'tripplanner.services.route',
                'tripplanner.ui',
                'tripplanner.ui.web',
                'tripplanner.webservices',
                ],
      )

