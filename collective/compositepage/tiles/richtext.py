# -*- encoding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.textfield import RichText
from plone.app.textfield.interfaces import ITransformer
from .base import IBaseTileSchema
from .base import BasePersistentTile
from .. import _


class IRichTextTileSchema(IBaseTileSchema):
    text = RichText(title=_(u'Text'))


class RichTextTile(BasePersistentTile):
    index = ViewPageTemplateFile('templates/richtext.pt')

    def text_output(self, fname='text'):
        text = ''
        if self.data[fname]:
            transformer = ITransformer(self.context, None)
            if transformer is not None:
                text = transformer(self.data[fname], 'text/x-html-safe')
        return text
