from    AppKit      import *
from    Foundation  import *
from    QFMenu      import *
from    QFAlert     import *
import  objc

class QFApp:

    def __init__(self, version):
        # set version
        self.version = version

        # store main window
        self.mainwindow = NSApplication.sharedApplication().mainWindow()

        # read user defaults
        userdefaults = NSUserDefaults.standardUserDefaults()

        # check if we're running in a different Mail version as before
        infodict    = NSBundle.mainBundle().infoDictionary()
        mailversion = infodict['CFBundleVersion']
        lastknown   = userdefaults.stringForKey_("QuoteFixLastKnownBundleVersion")
        if lastknown and mailversion != lastknown:
            QFAlert.showAlert(self,
                'QuoteFix plug-in',
                '''
The QuoteFix plug-in detected a different Mail.app version (perhaps you updated?).

If you run into any problems with regards to replying or forwarding mail, consider removing this plug-in (from ~/Library/Mail/Bundles/).

(This alert is only displayed once for each new version of Mail.app)
''', alert_style = NSInformationalAlertStyle)

        userdefaults.setObject_forKey_(mailversion, "QuoteFixLastKnownBundleVersion")

        # check if quotefixing should be turned on
        self.is_active = userdefaults.boolForKey_("QuoteFixDisabled") and False or True

        # check if debugging should be turned on
        self.is_debugging = userdefaults.boolForKey_("QuoteFixEnableDebugging") and True or False

        # check if menu should be injected
        self.menu = None
        try:
            # 'QuoteFixIncludeMenu' is new, 'IncludeQuoteFixMenu' is old
            # (but still supported)
            if userdefaults.boolForKey_('QuoteFixIncludeMenu') or userdefaults.boolForKey_('IncludeQuoteFixMenu'):
                self.menu = QFMenu.alloc().initWithApp_(self)
                self.menu.inject()
        except:
            if self.isDebugging():
                QFAlert.showException(self)

    def setHTML(self, html):
        if self.menu:
            self.menu.setHTML(html)

    def isDebugging(self):
        return self.is_debugging

    def setIsDebugging(self, debugging):
        self.is_debugging = debugging

    def isActive(self):
        return self.is_active

    def setIsActive(self, active):
        self.is_active = active

    def window(self):
        return self.mainwindow
