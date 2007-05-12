from zope.interface import implements
from persistent import Persistent
from bycycle.tripplanner.interfaces import IAd


class Ad(Persistent):
   implements(IAd)
   title = u'Ad Title'
   content = u'Ad content'
   href = u'http://'
