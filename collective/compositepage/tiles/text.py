# -*- encoding: utf-8 -*-

from zope import schema

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from .base import IBaseTileSchema
from .base import BasePersistentTile
from ..utils import PTCompiler
from .. import _


class ITextTileSchema(IBaseTileSchema):

    text = schema.Text(
        title=_(u'Text')
    )


class TextTile(BasePersistentTile):
    index = ViewPageTemplateFile('templates/text.pt')

    def text_output(self):
        text = self.data['text']
        if not text:
            return ''
        compiler = PTCompiler(self.context, text)
        return compiler.compile(request=self.request)

