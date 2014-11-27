# -*- encoding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from .base import IBaseTileSchema
from .base import BasePersistentTile
from .. import _


DEFAULT_WIDTH = 470
DEFAULT_HEIGHT = 269


class IVideoTileSchema(IBaseTileSchema):

    head_title = schema.TextLine(
        title=_(u'Head'),
        required=True,
    )

    text = schema.Text(
        title=_(u'Text'),
        required=True,
    )

    video_url = schema.TextLine(
        title=_(u'Youtube video embed URL'),
        description=_(u'Provide the embed URL and not the standard video URL. '
                      u'You can find it in "share"->"embed" option '
                      u'below the player on youtube.'),
        required=True,
    )

    width = schema.Int(
        title=_(u'Width'),
        default=DEFAULT_WIDTH,
        required=True,
    )

    height = schema.Int(
        title=_(u'Height'),
        default=DEFAULT_HEIGHT,
        required=True,
    )

    video_position = schema.Choice(
        title=_(u'Video position'),
        vocabulary=SimpleVocabulary([
            SimpleTerm(u'right', u'right', u'Right'),
            SimpleTerm(u'left', u'left', u'Left'),
        ]),
        required=False,
        default=u'right',
    )


class VideoTile(BasePersistentTile):
    index = ViewPageTemplateFile('templates/video.pt')

    @property
    def head_title(self):
        return self.data['head_title']

    @property
    def text(self):
        return self.data['text']

    @property
    def video_url(self):
        return self.data['video_url']

    @property
    def height(self):
        return self.data['height']

    @property
    def width(self):
        return self.data['width']

    def css_class(self):
        res = super(VideoTile, self).css_class()
        leadimage = self.data.get('video_position') or 'right'
        return res + ' ' + 'video-' + leadimage
