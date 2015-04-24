# -*- coding: utf-8 -*-

from zope import schema
from zope.component import queryMultiAdapter
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder

import plone.api
from plone.memoize import view
from plone.autoform import directives as form
from plone.formwidget.contenttree import UUIDSourceBinder
from plone.formwidget.contenttree import ContentTreeFieldWidget

from .base import BasePersistentTile
from .base import IBaseTileSchema
from ..utils import is_collection
from ..utils import get_collection_query
from .. import _


class IRelatedContainerSchema(IBaseTileSchema):
    form.widget(source_context=ContentTreeFieldWidget)
    source_context = schema.Choice(
        title=_(u"Folder or collection"),
        # description=_(u""),
        required=False,
        source=UUIDSourceBinder(portal_type=('Folder', 'Collection'))
    )

    form.widget(related_types=CheckBoxFieldWidget)
    related_types = schema.List(
        title=_(u"Types to list"),
        description=_(u'This may have no effect '
                      U'if you are linking collections.'),
        required=False,
        value_type=schema.Choice(
            title=u"Multiple",
            vocabulary='plone.app.vocabularies.UserFriendlyTypes'
        )
    )
    limit = schema.Int(
        title=_(u'Limit'),
        default=10,
        required=True,
    )
    subfolders = schema.Bool(
        title=_(u'Look into subfolders too?'),
        default=False,
    )


class RelatedContainerTile(BasePersistentTile):

    ptype = 'Image'
    limit = 1
    filtering_keys = ()

    @property
    def items_search_depth(self):
        subfolders = self.data['subfolders']
        if subfolders:
            return -1
        return 1

    @property
    def ps(self):
        return queryMultiAdapter((self.context, self.request),
                                 name="plone_portal_state")

    @property
    def catalog(self):
        return plone.api.portal.get_tool("portal_catalog")

    def prepare_filters(self, request):
        res = {}
        for k in self.filtering_keys:
            if k in request:
                res[k] = request.get(k)
        return res

    @property
    def base_query(self):
        ptypes = self.data['related_types'] or self.ptype
        query = {
            'portal_type': ptypes,
            'sort_on': 'effective',
            'sort_order': 'reverse',
        }
        parent_request = self.request.get('PARENT_REQUEST')
        if parent_request and self.filtering_keys:
            # we are in subrequest! just get any possibile
            # filtering here from parent request qstring
            query.update(self.prepare_filters(parent_request))
        return query

    @view.memoize
    def get_container(self):
        if not self.data['source_context']:
            return None
        # portal = self.ps.portal()
        # path = to_portal_abs_path(portal, self.data['source_context'])
        # no security check here, we only need to check
        # if the container exists and get its path later
        # and it might be in private state, but we want
        # its contents nonetheless.
        # container = portal.unrestrictedTraverse(path, None)
        brain = self.catalog(UID=self.data['source_context'])
        container = brain and brain[0] or None
        return container

    @view.memoize
    def get_items(self):
        container = self.get_container()
        if container is None:
            return []
        query = self.base_query.copy()
        path = container.getPath()
        query['path'] = {
            'query': path,
            'depth': self.items_search_depth,
        }
        if is_collection(container):
            query.pop('path')
            query.update(get_collection_query(container))
        brains = self.catalog(query)
        limit = self.data['limit'] or self.limit
        if limit:
            brains = brains[:limit]

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
