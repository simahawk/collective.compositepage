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

    @property
    def context_state(self):
        return self.context.restrictedTraverse('@@plone_context_state')

    def visible(self):
        """ make sure we make it visible only on view
        """
        return self.context_state.is_view_template()
