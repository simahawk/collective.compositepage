#-*- coding: utf-8 -*-

from zope import annotation

from Products.Five.browser import BrowserView

from ..interfaces import ILayoutManager


class StorageView(BrowserView):

    def __call__(self):
        self.request.set('plone.app.blocks.disabled', True)
        html = ILayoutManager(self.context).html()
        anno = annotation.interfaces.IAnnotations(self.context)
        tiles = ['%s\n' % x for x in anno.keys() if 'tile' in x]
        return html.replace('<', '&lt;').replace('>', '&gt;') + \
            '<pre>' + '\n'.join(['\n'.join(tiles)]) + '</pre>'
