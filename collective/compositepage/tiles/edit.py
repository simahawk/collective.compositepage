from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify
from zope.traversing.browser.absoluteurl import absoluteURL

from z3c.form import button

from plone.tiles.interfaces import ITileDataManager
from plone.app.tiles.browser.edit import DefaultEditView
from plone.app.tiles.browser.edit import DefaultEditForm

from .. import _


class TilesEditForm(DefaultEditForm):

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
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        tile = self.get_tile()
        dataManager = ITileDataManager(tile)
        dataManager.set(data)

        tileURL = self.get_tile_url(tile)

        notify(ObjectModifiedEvent(tile))

        self.request.response.redirect(tileURL)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.get_tile_url())

    def updateActions(self):
        super(TilesEditForm, self).updateActions()
        self.actions["save"].addClass("btn primary-btn")
        self.actions["cancel"].addClass("btn")


class TilesEditView(DefaultEditView):
    form = TilesEditForm

    # XXX: it removes some warnings
    def browserDefault(self):
        pass

    # XXX: it removes some warnings
    def publishTraverse(self, name):
        pass
