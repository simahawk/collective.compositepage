# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__file__)

from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface
from zope.component import adapts
from zope import schema

from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList

from plone.supermodel import model
from plone.dexterity.interfaces import IDexterityContent
from plone.autoform.interfaces import IFormFieldProvider

from plone.formwidget.contenttree import ObjPathSourceBinder

from .. import _


class ILinkedResource(model.Schema):
    model.fieldset(
        'linked-resources',
        label=u"Linked resources",
        fields=[
            'remote_url',
            'related_resources',
            'related_resources_cta',
        ]
    )

    remote_url = schema.TextLine(
        title=_(u'Link'),
        description=_(u'Insert a link to an external resource, '
                      u'or relate an internal resource '
                      u'using "Linked resource" below.'),
        required=False,  # we can use also relatedItems
    )

    # form.widget(related_resource=ContentTreeFieldWidget)
    related_resources = RelationList(
        title=_(u"Linked resources"),
        required=False,
        value_type=RelationChoice(
            title=u"Multiple",
            source=ObjPathSourceBinder()
        )
    )
    related_resources_cta = schema.Text(
        title=_(u'Resources CTA'),
        description=_(u'Insert related resource call to actions options. '
                      u'Each line match a linked resource. '
                      u'You can provide them in the form '
                      u'`option:value, option2:value`.'
                      u'Valid options are: `label`, `css_class`., '),
        required=False,  # we can use also relatedItems
        default=u''
    )

alsoProvides(ILinkedResource, IFormFieldProvider)


class LinkedResource(object):
    implements(ILinkedResource)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context


# XXX 2014-04-08 there's no way to reach `resource_url` method on behavior
# and get the method from the object itself
# unless you get straight to the behavior itself.
# So, we prefer to relay on an adapter, also to ease customization.

class ILinkedResourceURLGetter(Interface):
    pass


class ResourceURLGetter(object):
    implements(ILinkedResourceURLGetter)
    adapts(ILinkedResource)

    def __init__(self, context):
        self.context = context

    def url(self):
        if self.context.remote_url:
            return self.context.remote_url
        res = self.resources()
        if len(res) == 1:
            return res[0]['url']
        return ''

    def remote_url(self):
        return self.context.remote_url

    def resources(self):
        res = []
        res_cta = self.parse_cta_options()
        for i, rel_value in enumerate(self.context.related_resources or []):
            obj = rel_value.to_object
            if obj is None:
                logger.warning('broken references')
                continue
            try:
                cta = res_cta[i]
            except IndexError:
                cta = {}
            # make sure we have defaults
            defaults = {
                'label': obj.Title(),
                'css_class': '',
            }
            for k, v in defaults.iteritems():
                if not cta.get(k):
                    cta[k] = v
            res.append({
                'cta': cta,
                'url': obj.absolute_url(),
                'obj': obj,
            })
        return res

    def parse_cta_options(self):
        opts = []
        for line in self.context.related_resources_cta.splitlines():
            if not line.strip():
                # empty line
                continue
            values = {}
            options = line.split(',')
            for opt in options:
                try:
                    k, v = opt.split(':')
                    values[k.strip()] = v.strip()
                except ValueError:
                    # wrong line formatting
                    continue
            if values:
                opts.append(values)
        return opts


