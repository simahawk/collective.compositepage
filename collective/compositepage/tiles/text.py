# -*- encoding: utf-8 -*-

from zope import schema

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.autoform import directives as form

from collective.z3cform.aceeditorwidget import AceEditorFieldWidget

from .base import IBaseTileSchema
from .base import BasePersistentTile
from ..utils import PTCompiler
from ..utils import logger
from .. import _


class ITextTileSchema(IBaseTileSchema):

    form.widget(text=AceEditorFieldWidget)
    text = schema.Text(
        title=_(u'Text')
    )


class TextTile(BasePersistentTile):
    index = ViewPageTemplateFile('templates/text.pt')

    pt_error = False

    def text_output(self):
        text = self.data['text']
        if not text:
            return ''
        try:
            compiler = PTCompiler(self.context, text)
            return compiler.compile(request=self.request)
        except Exception as e:
            self.pt_error = True
            logger.error('RAWTILE: ' + str(e))
            return str(e)
