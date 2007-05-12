from zope.app.form.browser.editview import EditView
from zope.app.form.browser.add import AddView
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ListSequenceWidget, ObjectWidget

from bycycle.tripplanner.interfaces import IRegion, IAd
from bycycle.tripplanner.entities import Ad


_ad_widget = CustomWidgetFactory(ObjectWidget, Ad)
_ads_widget = CustomWidgetFactory(ListSequenceWidget, subwidget=_ad_widget)


class Add(AddView):
    __used_for__ = IRegion
    ads_widget = _ads_widget


class Edit(EditView):
    __used_for__ = IRegion
    ads_widget = _ads_widget
