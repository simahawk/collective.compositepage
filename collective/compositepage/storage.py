from persistent.dict import PersistentDict

from zope import interface
from zope import component
from zope import annotation

from .interfaces import IComposable
from .interfaces import ILayoutManager


KEY = 'collective.compositepage.layout'


class LayoutManager(object):
    interface.implements(ILayoutManager)
    component.adapts(IComposable)

    def __init__(self):
        # Does not expect argument as usual adapters
        # You can access annotated object through ``self.__parent__``
        # Let's use a PersistentDict since we do not know how it may evolve
        # and if we'll need more attributes to store.
        self._data = PersistentDict({'html': ''})
        self._old_data = PersistentDict({'html': ''})

    def html(self, html=None):
        current = self._data['html']
        if html is None:
            return current
        # else store a new value
        # but keep previous version
        self._old_data['html'] = current
        self._data['html'] = html

    def old_version(self):
        return self._data['html']


manager = annotation.factory(LayoutManager, key=KEY)
