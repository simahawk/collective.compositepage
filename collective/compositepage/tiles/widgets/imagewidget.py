#-*- coding: utf-8 -*-

from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer, implements
from zope.interface import Interface
from plone.namedfile.interfaces import INamedImageField
from plone.formwidget.namedfile.widget import NamedImageWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget

from collective.compositepage.interfaces import ILayer


class IImageWidget(Interface):
    pass


class ImageWidget(NamedImageWidget):

    implements(IImageWidget)

    klass = u'named-image-widget allowDefault'

    @property
    def image_url(self):
        form = self.form
        if not hasattr(form, 'tileType'):
            # subform
            form = form.parentForm

        tile_url = '@@%s/%s' % (form.tileType.__name__,
                                form.tileId)
        tile = form.context.restrictedTraverse(tile_url)
        scale = None
        if tile.data[self.field.__name__]:
            scales = queryMultiAdapter((tile, self.request), name="images")
            scale = scales.scale(self.field.__name__)
        return scale and scale.url or ''


@implementer(IFieldWidget)
@adapter(INamedImageField, ILayer)
def ImageFieldWidget(field, request):
    return FieldWidget(field, ImageWidget(request))
