from zope.interface import implements
from persistent import Persistent
from bycycle.tripplanner.interfaces import IRegion, IAd


class Region(Persistent):
   implements(IRegion)
   

class Ad(Persistent):
   implements(IAd)