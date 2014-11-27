#-*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.security import checkPermission
from zope import component

from plone.memoize import view
from plone.tiles.interfaces import ITileType


class View(BrowserView):

    def can_modify(self):
        return checkPermission('cmf.ModifyPortalContent',
                               self.context)

    @view.memoize
    def available_tiles(self):
        types = []
        for tiletype in self.get_registered_tile_types():
            types.append({
                'name': tiletype.__name__,
                'title': tiletype.title,
                'add_url': '{0}/{1}/{2}'.format(self.context.absolute_url(),
                                                '@@add-tile',
                                                tiletype.__name__)
            })
        return sorted(types, key=lambda x: x['title'])

    def get_registered_tile_types(self):
        prefix = 'compositepage.tiles'
        all_tiles = component.getAllUtilitiesRegisteredFor(ITileType)
        return [x for x in all_tiles
                if x.__name__.startswith(prefix)]


