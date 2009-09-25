from    AppKit      import *
from    Foundation  import *
from    QFAlert     import *
import  objc

class QFMenu(NSObject):

    @classmethod
    def init(cls):
        # act as a singleton, since we only need to inject ourselves into
        # the main Mail menu once
        if '_instance' in cls.__dict__:
            self = cls._instance
            return self

        # create an instance
        self = cls._instance    = NSObject.init(cls.alloc())
        self.is_debugging       = False
        self.mainwindow         = NSApplication.sharedApplication().mainWindow()

        # check if menu should be displayed
        userdefaults = NSUserDefaults.standardUserDefaults()
        showDebugMenu   = userdefaults.boolForKey_('IncludeQuoteFixMenu')
        if not showDebugMenu:
            return self

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
            addItem("Debug", "debugItemChanged:", state = 0)
            addItem("Copy original contents to clipboard (for debugging)", "copyToClipboard:")
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

    def setHTML_(self, html):
        self.html       = html

    def debugItemChanged_(self, sender):
        sender.setState_(1 - sender.state())
        self.is_debugging = not self.is_debugging

    def isDebugging(self):
        return self.is_debugging

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
                'QuoteFix plug-in ($Rev: 23 $)',
                '''
For more information about this plug-in, please refer to its Google Code homepage at

http://code.google.com/p/quotefixformac/

This plug-in was written by Robert Klep (robert@klep.name).
''', alert_style = NSInformationalAlertStyle)
