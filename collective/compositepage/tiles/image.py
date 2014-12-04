# -*- encoding: utf-8 -*-

from plone.app.textfield import RichText
from plone.supermodel import model

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from .related import RelatedContainerTile
from .related import IRelatedContainerSchema
from .richtext import RichTextTile
from .. import _


class IImageListingTile(IRelatedContainerSchema):

    model.fieldset(
        'top',
        label=u"Top",
        fields=[
            'top_text',
        ]
    )
    model.fieldset(
        'bottom',
        label=u"Bottom",
        fields=[
            'bottom_text',
        ]
    )

    top_text = RichText(
        title=_(u'Top text'),
        description=_(u'Text above image listing'),
        required=False,
    )

    bottom_text = RichText(
        title=_(u'Bottom text'),
        description=_(u'Text below image listing'),
        required=False,
    )


class ImageListingTile(RelatedContainerTile, RichTextTile):
    index = ViewPageTemplateFile('templates/imagelisting.pt')
    limit = 10

    @property
    def top_text(self):
        return self.data['top_text']

    @property
    def bottom_text(self):
        return self.data['bottom_text']
