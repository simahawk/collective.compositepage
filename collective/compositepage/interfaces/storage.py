#-*- coding: utf-8 -*-

from zope import interface


class ILayoutManager(interface.Interface):
    """ Storage manager for tiles layout
    """

    def html(html):
        """ store html
        """

    def old_version():
        """ return previous version
        """
