# -*- encoding: utf-8 -*-

from zope import schema
from zope.security import checkPermission
from zope.component import queryMultiAdapter

from z3c.form.browser.checkbox import CheckBoxFieldWidget

from plone import tiles
from plone.autoform import directives as form
from plone.supermodel import model
# from plone.i18n.normalizer import idnormalizer
from plone.namedfile import field as namedfile
from plone.i18n.normalizer import idnormalizer

from .widgets import ImageFieldWidget
from .. import _


class IBaseTileSchema(model.Schema):
    """ basic tile schema
    """

    title = schema.TextLine(
        title=_(u'Box title'),
        required=True,
    )

    show_title = schema.Bool(
        title=_(u'Show title?'),
        default=False,
    )

    form.widget(predefined_style=CheckBoxFieldWidget)
    predefined_style = schema.List(
        title=_(u'Predefined style'),
        value_type=schema.Choice(
            vocabulary='compositepage.tiles_predefined_styles'
        ),
        required=False,
    )

    form.widget(background_image=ImageFieldWidget)
    background_image = namedfile.NamedBlobImage(
        title=_(u"Background image"),
        description=_(u"An image that will be used "
                      u"as background for the block."),
        required=False,
    )

    width = schema.TextLine(
        title=_(u'Custom width'),
        description=_(u'Include unit of measure, eg: 200px or 20em'),
        default=u'',
        required=False,
    )

    height = schema.TextLine(
        title=_(u'Custom height'),
        description=_(u'Include unit of measure, eg: 200px or 20em'),
        default=u'',
        required=False,
    )

    extra_inline_style = schema.TextLine(
        title=_(u'Extra inline style'),
        description=_(u'Some extra style you want to add to the block. '
                      u'PLEASE, use this field wisely.'),
        default=u'',
        required=False,
    )

    padding = schema.TextLine(
        title=_(u'Custom padding'),
        description=_(u'You can provide padding for all the 4 sides. '
                      u'If you provide only 1 measure (eg: "1em") '
                      u'this will be applied for every side . '
                      u'If you provide 2 measures (eg: "1em 0.5em") '
                      u'the former will be applied top and bottom, '
                      u'the latter will be applied to left and right.'
                      u'If you specify separated measures for every side '
                      u'(eg: "1em 0.5em 0.2em 2em") they will be applied '
                      u'clockwise: "$top $right $bottom $left". '
                      u'NOTE: CSS padding affects width and height '
                      u'so you\'ll have to tweak the those measures if needed.'
                      ),
        default=u'',
        required=False,
    )

    model.fieldset('images',
                   label=_(u"Images"),
                   fields=['background_image',
                           ])

    model.fieldset('block_styles',
                   label=_(u"Block styles"),
                   fields=['predefined_style',
                           'height',
                           'width',
                           'padding',
                           'extra_inline_style',
                           ])


class BasePersistentTile(tiles.PersistentTile):

    @property
    def computed_id(self):
        return idnormalizer.normalize(self.title)

    def can_modify(self):
        return checkPermission('cmf.ModifyPortalContent',
                               self.context)

    @property
    def edit_url(self):
        return "./@@edit-tile/{0}/{1}".format(self.__name__, self.id)

    @property
    def delete_url(self):
        return "./@@delete-tile/{0}/{1}".format(self.__name__, self.id)

    @property
    def title(self):
        return self.data['title']

    def Title(self):  # noqa
        """ needed for @@images scale tag traversal
            (uses the title of the tile for the image tag title)
        """
        return self.title

    @property
    def show_title(self):
        return self.data['show_title']

    @property
    def height(self):
        return self.data['height']

    @property
    def width(self):
        return self.data['width']

    def download_url(self, fname):
        """ convenience method to get url for traversing to file fields
        Resulting url is the same of what you can get view ZPT like this:
        ${context/absolute_url}/${view/__name__}/${view/id}/@@download/$fname
        """
        if fname not in self.data:
            return ''
        url = '/'.join([
            self.context.absolute_url(),
            '@@download-file',
            self.id + ':' + fname
        ])
        return url

    @property
    def scales(self):
        """ looks like we cannot traverse to @@images view,
        but getting the adapter works fine so...
        """
        scales = queryMultiAdapter((self, self.request), name="images")
        return scales

    def scale(self, fname, **kw):
        """ convenience method to get a scale for an image.
        You can then use it in templates like:
            <img tal:replace="structure python: view.scale(fieldname).tag()" />
        """
        return self.scales.scale(fname, **kw)

    def css_class(self):
        styles = list(self.data.get('predefined_style') or [])
        styles.append(self.__name__.replace('.', '-'))
        if not self.data.get('background_image'):
            # we assume every bg predef style ends w/ '-bg'
            if not [x for x in styles if x.endswith('-bg')]:
                styles.append('no-background-image')
        return ' '.join(styles)

    def forced_styles(self):
        styles = ''
        for i in ('width', 'height', 'padding'):
            if self.data.get(i):
                styles += '{0}:{1};'.format(i, self.data.get(i))
        if self.data.get('background_image'):
            url = self.download_url('background_image')
            styles += ''.join([
                'background-image:url({0});'.format(url),
                'background-repeat:no-repeat;',
                'background-position:top left;',
            ])
        if self.data.get('extra_inline_style'):
            styles += self.data.get('extra_inline_style').lstrip(';')
        return styles
