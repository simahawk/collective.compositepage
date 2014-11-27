#-*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabularyFactory

from plone.i18n.normalizer import idnormalizer

from .utils import get_composite_styles
from .utils import get_tiles_styles


class BaseVocabulary(object):
    implements(IVocabularyFactory)

    terms = []

    def __call__(self, context):
        terms = self.get_terms(context)
        return SimpleVocabulary(list(terms))

    def get_dict(self):
        return dict(self.terms)

    def get_terms(self, context):
        raise NotImplementedError()


class VocabFromDictRecords(BaseVocabulary):

    def get_records(self):
        raise NotImplementedError()

    def get_terms(self, context):
        for item in self.get_records():
            title = item['title']
            token = idnormalizer.normalize(title)
            value = item['css_class']
            yield SimpleTerm(value=value,
                             token=token,
                             title=title)


class CompositePredefinedStyles(VocabFromDictRecords):

    def get_records(self):
        return get_composite_styles()


class TilesPredefinedStyles(VocabFromDictRecords):

    def get_records(self):
        return get_tiles_styles()

