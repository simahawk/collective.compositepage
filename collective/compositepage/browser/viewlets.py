#-*- coding: utf-8 -*-

from zope.security import checkPermission

from plone.app.layout.viewlets import ViewletBase
from ..interfaces import ILayoutManager


class CompositeToolsViewlet(ViewletBase):
    """A simple viewlet which renders composite page tools
    """

    def tiles(self):
        manager = ILayoutManager(self.context)
        return manager.html()

    def can_modify(self):
        return checkPermission('cmf.ModifyPortalContent',
                               self.context)
