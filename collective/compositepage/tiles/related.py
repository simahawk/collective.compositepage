#-*- coding: utf-8 -*-

from zope import schema
from zope.component import queryMultiAdapter
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder

import plone.api
from plone.memoize import view
from plone.autoform import directives as form
from plone.formwidget.contenttree import PathSourceBinder
from plone.formwidget.contenttree import ContentTreeFieldWidget

from .base import BasePersistentTile
from .base import IBaseTileSchema
from ..utils import is_collection
from ..utils import get_collection_query
from ..utils import to_portal_abs_path
from .. import _


class IRelatedContainerSchema(IBaseTileSchema):
    form.widget(source_context=ContentTreeFieldWidget)
    source_context = schema.Choice(
        title=_(u"Folder or collection"),
        # description=_(u""),
        required=False,
        source=PathSourceBinder(portal_type=('Folder', 'Collection'))
    )


class RelatedContainerTile(BasePersistentTile):

    ptype = 'Image'
    limit = 1
    items_search_depth = 1

    @property
    def ps(self):
        return queryMultiAdapter((self.context, self.request),
                                 name="plone_portal_state")

    @property
    def catalog(self):
        return plone.api.portal.get_tool("portal_catalog")

    @property
    def base_query(self):
        query = {
            'portal_type': self.ptype,
            'sort_on': 'getObjPositionInParent',
        }
        return query

    def get_container(self):
        if not self.data['source_context']:
            return None
        portal = self.ps.portal()
        path = to_portal_abs_path(portal, self.data['source_context'])
        # no security check here, we only need to check
        # if the container exists and get its path later
        # and it might be in private state, but we want
        # its contents nonetheless.
        container = portal.unrestrictedTraverse(path, None)
        return container

    @view.memoize
    def get_items(self):
        container = self.get_container()
        if container is None:
            return []
        query = self.base_query.copy()
        query['path'] = {
            'query': '/'.join(container.getPhysicalPath()),
            'depth': self.items_search_depth,
        }
        if is_collection(container):
            query.update(get_collection_query(container))

        # make sure we look only for our ctype!
        query['portal_type'] = self.ptype

        brains = self.catalog(query)[:self.limit]

        return brains


class IRelatedItemsSchema(IBaseTileSchema):

    related_items = RelationList(
        title=_(u'label_related_items',
                default=u'Related Items'),
        default=[],
        value_type=RelationChoice(
            title=u"Related",
            source=ObjPathSourceBinder()
        ),
        required=False,
    )
