import os
from lxml import html
from zope.event import notify

from OFS.event import ObjectWillBeRemovedEvent
from zope.lifecycleevent import ObjectRemovedEvent
from zope.lifecycleevent import ObjectModifiedEvent

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.tiles.data import ANNOTATIONS_KEY_PREFIX
from plone.app.tiles import browser
from plone.app.tiles.browser.traversal import DeleteTile as BaseView


class DeleteTile(BaseView):

    index = ViewPageTemplateFile(
        os.path.join(
            os.path.dirname(browser.__file__),
            'delete.pt'
        )
    )

    def __call__(self):
        # Delete tile from template
        tile_data = self.annotations.get(
            '%s.%s' % (ANNOTATIONS_KEY_PREFIX, self.tileId),
            None
        )

        if tile_data and tile_data.get('column'):
            column = tile_data['column']
            element = html.fromstring(getattr(self.context, column))
            for tile_div in element:
                tile_url = tile_div.attrib['data-tile']
                if self.tileId in tile_url:
                    element.remove(tile_div)
                    break
            setattr(self.context, column, html.tostring(element))

        tile_url = tile_url.replace('./', '')
        tile = self.context.restrictedTraverse(tile_url)
        notify(ObjectWillBeRemovedEvent(tile, self.context, self.tileId))

        index = super(DeleteTile, self).__call__()

        notify(ObjectRemovedEvent(tile, self.context, self.tileId))
        notify(ObjectModifiedEvent(self.context))

        return index
