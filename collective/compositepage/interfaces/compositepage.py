#-*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface

from z3c.form.browser.radio import RadioFieldWidget
from plone.autoform import directives as form

from collective.compositepage import _


class IComposable(Interface):
    """ Objects marked with this interface
    gain composite tools and storage.
    This allow us to give composite tools features
    to objects that are not CompositePage.
    """


class ICompositePage(IComposable):

    show_title = schema.Bool(
        title=_(u'Show title?'),
        default=False,
    )

    show_description = schema.Bool(
        title=_(u'Show description?'),
        default=False,
    )

    centered_title = schema.Bool(
        title=_(u'Centered title?'),
        default=False,
    )

    form.widget(predefined_styles=RadioFieldWidget)
    predefined_styles = schema.List(
        title=_(u'Predefined style'),
        value_type=schema.Choice(
            vocabulary='compositepage.compositepage_predefined_styles'
        ),
        required=False,
    )

    custom_css = schema.Text(
        title=_(u'Custom CSS'),
        description=_(u'Add custom CSS rules to this page. '
                      u'PLEASE, use this field wisely!'),
        required=False,
    )
