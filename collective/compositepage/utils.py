#-*- coding: utf-8 -*-

import os
import logging

from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import aq_base

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest

from plone.registry.interfaces import IRegistry

from zope import component

from Products.ATContentTypes.interfaces import IATTopic
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.outputfilters.interfaces import IFilter
from plone.app.collection.interfaces import ICollection
from plone.app.querystring import queryparser


logger = logging.getLogger('collective.compositepage')


def to_portal_abs_path(portal, path):
    """ given portal and a path makes that path absolute
    """
    if not portal.id in path:
        portal_path = '/'.join(portal.getPhysicalPath())
        path = os.path.join(portal_path, path.strip('/'))
        path = path.strip('/')
        if isinstance(path, unicode):
            path = path.encode('utf8')
    return path


def get_records(key):
    res = []
    registry = getUtility(IRegistry)
    try:
        settings = registry[key].encode('utf-8')
    except Exception:
        msg = 'Missing "%s" in registry' % key
        logger.error(msg)
        return res

    for i, entry in enumerate(settings.splitlines()):
        if entry.strip():
            # non emtpy line
            try:
                css_class, title = entry.split('|')
                res.append({
                    'css_class': css_class,
                    'title': title,
                })
            except ValueError:
                msg = 'Error in %s settings. ' % key
                msg += 'Line %s: "%s"' % (i, entry)
                logger.error(msg)
    return res


def get_composite_styles():
    key = 'compositepage.compositepage_predefined_styles'
    return get_records(key)


def get_tiles_styles():
    key = 'compositepage.tiles_predefined_styles'
    return get_records(key)


def normalize(astring):
    return component.getUtility(IIDNormalizer).normalize(astring)


def is_collection(obj):
    """ return true if given obj is a plone collection
    """
    return IATTopic.providedBy(obj) or ICollection.providedBy(obj)


def parse_new_collection_query(context):
    """ given a new collection item returns its catalgo query
    """
    parse = queryparser.parseFormquery
    query = parse(context, context.getRawQuery())
    # sorting params do not come from query parsing
    if hasattr(context, 'sort_on'):
        query['sort_on'] = context.sort_on
    if hasattr(context, 'sort_reversed') and context.sort_reversed:
        query['sort_order'] = 'reverse'
    return query


def get_collection_query(obj):
    """ return collection's query params
    """

    if IATTopic.providedBy(obj):
        # old style collection
        return obj.buildQuery()

    if ICollection.providedBy(obj):
        # new style collection
        return parse_new_collection_query(obj)


def get_parent(obj):
    return aq_parent(aq_inner(obj))


class PTCompiler(object):
    """ PageTemplate compiler
    """

    def __init__(self, context, body):
        """
        @param `context`: current context
        @parem `body`: page template content
        """
        self.context = context
        self.body = body

    def compile(self, apply_filters=True, request=None, **kwargs):
        """ compiles page template.
        @param `apply_filters`: turns on/off html filtering
        You can pass extra arguments to compiler
        via `kwargs`.

        """
        if not self.body:
            return ''
        request = request or getRequest()
        pt = ZopePageTemplate(id='__%s_tal_body__' % self.context.id)
        pt.pt_edit(self.body, 'text/html')
        context = aq_inner(self.context)
        pt = aq_base(pt).__of__(context)
        # request is taken by acquisition
        compiled = pt(**kwargs)

        if isinstance(compiled, unicode):
            compiled = compiled.encode('utf-8')

        # trasform resolveuid link to absolute path
        if apply_filters:
            _filter = getMultiAdapter(
                (self.context, request),
                IFilter, name="resolveuid_and_caption")
            try:
                compiled = _filter(compiled)
            except AttributeError:
                # Something wrong happend
                # perhaps image scale doesn't exists
                pass
        return compiled.decode('utf-8')


class AttrDict(dict):
    """ a smarter dict
    """

    def __getattr__(self, k):
        return self[k]

    def __setattr__(self, k, v):
        self[k] = v
