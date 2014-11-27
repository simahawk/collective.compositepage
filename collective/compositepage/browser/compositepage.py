#-*- coding: utf-8 -*-

from time import time

from Products.Five.browser import BrowserView
from Products.ResourceRegistries.tools.packer import CSSPacker

from plone.memoize import ram
from plone.uuid.interfaces import IUUID

from ..interfaces import ILayoutManager


REFRESH_INTERVAL = 1800


def minify_css(content, mode='full'):
    return CSSPacker(mode).pack(content)


def _css_cachekey(method, self):
    """
    """
    key = hash((
        IUUID(self.context),
        self.context.modified(),
        time() // REFRESH_INTERVAL,
    ))
    return key


class View(BrowserView):

    def tiles(self):
        manager = ILayoutManager(self.context)
        return manager.html()

    @property
    def css_class(self):
        styles = list(self.context.predefined_styles or [])
        return ' '.join(styles)

    @ram.cache(_css_cachekey)
    def custom_css(self):
        if self.context.custom_css:
            return minify_css(self.context.custom_css)
        return ''

