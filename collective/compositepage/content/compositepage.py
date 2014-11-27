# -*- encoding: utf-8 -*-

from zope.interface import implementer

from plone.dexterity.content import Container

from ..interfaces import ICompositePage


@implementer(ICompositePage)
class CompositePage(Container):
    pass
