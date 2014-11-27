from zope.lifecycleevent import ObjectAddedEvent
from zope.component import getUtility
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.lifecycleevent import ObjectCreatedEvent
from zope.event import notify
from z3c.form import button

from plone.uuid.interfaces import IUUIDGenerator
from plone.tiles.interfaces import ITileDataManager
from plone.app.tiles.browser.add import DefaultAddView
from plone.app.tiles.browser.add import DefaultAddForm

from .. import _


class TilesAddForm(DefaultAddForm):

    def get_tile(self):
        typeName = self.tileType.__name__

        # Traverse to a new tile in the context, with no data
        return self.context.restrictedTraverse(
            '@@%s/%s' % (typeName, self.tileId,))

    def get_tile_url(self, tile=None):
        if not tile:
            tile = self.get_tile()
        return absoluteURL(tile, self.request)

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        typeName = self.tileType.__name__

        generator = getUtility(IUUIDGenerator)
        tileId = generator()

        # Traverse to a new tile in the context, with no data
        tile = self.context.restrictedTraverse(
            '@@%s/%s' % (typeName, tileId,))

        dataManager = ITileDataManager(tile)
        dataManager.set(data)

        # Look up the URL - we need to do this after we've set the data to
        # correctly account for transient tiles
        tileURL = absoluteURL(tile, self.request)

        notify(ObjectCreatedEvent(tile))
        notify(ObjectAddedEvent(tile, self.context, tileId))

        self.request.response.redirect(tileURL)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.context.absolute_url())

    def updateActions(self):
        super(TilesAddForm, self).updateActions()
        self.actions["save"].addClass("btn primary-btn")
        self.actions["cancel"].addClass("btn")


class TilesAddView(DefaultAddView):
    form = TilesAddForm

    # XXX: it removes some warnings
    def browserDefault(self):
        pass

    # XXX: it removes some warnings
    def publishTraverse(self, name):
        pass
