#-*- coding: utf-8 -*-

import json

from zope import component

from Products.Five.browser import BrowserView

from ..interfaces import ILayoutManager


class View(BrowserView):

    def save(self):
        html = self.request.get('html')
        ILayoutManager(self.context).html(html)
        return json.dumps({
            'error': False,
            'message': ''
        })

    def revert(self):
        self.request.set('plone.app.blocks.disabled', True)
        html = ILayoutManager(self.context).old_version()
        return json.dumps({
            'error': False,
            'message': '',
            'content': html,
        })

    def available_tiles(self):
        tools = component.getMultiAdapter(
            (self.context, self.request),
            name='compositepage_tools'
        )
        return json.dumps({
            'error': False,
            'message': '',
            'tiles': tools.available_tiles()
        })

