# -*- coding: utf-8 -*-

from plone.indexer.decorator import indexer

from .behaviors.linkedresource import ILinkedResource
from .behaviors.linkedresource import ILinkedResourceURLGetter


@indexer(ILinkedResource)
def resource_url(obj):
    getter = ILinkedResourceURLGetter(obj)
    return getter.resource_url()


@indexer(ILinkedResource)
def resources(obj):
    getter = ILinkedResourceURLGetter(obj)
    return getter.resources()
