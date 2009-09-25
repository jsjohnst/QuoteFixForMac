from    AppKit      import *
from    Foundation  import *
from    QFAlert     import *
import  objc

class QFMenu(NSObject):

    def initWithApp_(self, app):
        self            = super(QFMenu, self).init()
        if self is None : return None
        self.app        = app
        self.mainwindow = NSApplication.sharedApplication().mainWindow()
        return self

    def inject(self):
        # yes, show menu
        try:
            # necessary because of the menu callbacks
            self.retain()

            # insert an item into the Mail menu
            newmenu     = NSMenu.alloc().initWithTitle_('QuoteFix Plug-in')

            # helper function
            def addItem(title, selector, state = None):
                item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, selector, "")
                item.setTarget_(self)
                if state != None:
                    item.setState_(state)
                newmenu.addItem_(item)

            # add a couple of useful items to the menu
            addItem("QuoteFix is %s" % (self.app.isActive() and "enabled" or "disabled"), "onOffItemChanged:", state = self.app.isActive())
            addItem("Debug", "debugItemChanged:", state = self.app.isDebugging())
            addItem("Copy original contents to clipboard", "copyToClipboard:")
            newmenu.addItem_(NSMenuItem.separatorItem())
            addItem("About...", "aboutItemSelected:")

            # add menu to the Mail menu
            newitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("QuoteFix Plug-in", None, "")
            newitem.setSubmenu_(newmenu)

            appmenu = NSApplication.sharedApplication().mainMenu().itemAtIndex_(0).submenu()
            appmenu.insertItem_atIndex_(NSMenuItem.separatorItem(), 1)
            appmenu.insertItem_atIndex_(newitem, 2)

        except Exception, e:
            raise e
        return self

    def setHTML(self, html):
        self.html = html

    def debugItemChanged_(self, sender):
        sender.setState_(1 - sender.state())
        self.app.setIsDebugging(sender.state())

    def onOffItemChanged_(self, sender):
        self.app.setIsActive(not self.app.isActive())
        sender.setTitle_("QuoteFix is %s" % (self.app.isActive() and "enabled" or "disabled"))
        sender.setState_(self.app.isActive())

    def copyToClipboard_(self, sender):
        if not self.html:
            return
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.declareTypes_owner_([ NSStringPboardType ], None)
        pasteboard.setString_forType_(self.html, NSStringPboardType)
        NSSound.soundNamed_("Pop").play()

    def window(self):
        return self.mainwindow

    def aboutItemSelected_(self, sender):
        QFAlert.showAlert(self,
                'QuoteFix plug-in (version %s)' % self.app.version,
                '''
For more information about this plug-in, please refer to its Google Code homepage at

http://code.google.com/p/quotefixformac/

This plug-in was written by Robert Klep (robert@klep.name).
''', alert_style = NSInformationalAlertStyle)
