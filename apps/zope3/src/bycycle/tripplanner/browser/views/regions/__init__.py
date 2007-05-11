from zope.publisher.browser import BrowserView


class Index(BrowserView):

    def __call__(self):
          return self.index()


class Edit(BrowserView):

    def __call__(self):
          return self.index()
