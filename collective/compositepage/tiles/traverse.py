#-*- coding: utf-8 -*-

from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.annotation.interfaces import IAnnotations
from zope.publisher.interfaces import NotFound

from Products.Five.browser import BrowserView
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from plone.tiles.data import ANNOTATIONS_KEY_PREFIX


@implementer(IPublishTraverse)
class DownloadFile(BrowserView):

    tileId = None
    fieldName = None

    def publishTraverse(self, request, name):
        """ we expect name = tileid:fieldname
        """
        try:
            self.tileId, self.fieldName = name.split(':')
        except ValueError:
            pass
        return self

    def get_tile_data(self):
        annotations = IAnnotations(self.context)
        tile_data = annotations.get(
            '%s.%s' % (ANNOTATIONS_KEY_PREFIX, self.tileId),
            None
        )
        return tile_data

    def __call__(self):
        if self.tileId:
            tile_data = self.get_tile_data()
            if tile_data:
                field = tile_data.get(self.fieldName)
                if field:
                    set_headers(field, self.request.response,
                                filename=field.filename)
                else:
                    raise NotFound(self.context, self.tileId, self.request)
                return stream_data(field)


# TODO: traverse for scales
