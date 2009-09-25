"""
QuoteFix - a Mail.app plug-in to fix some annoyances when replying to e-mail

Version: $Rev: 24 $
"""

from    AppKit          import *
from    Foundation      import *
from    QFMenu          import *
from    QFAlert         import *
import  objc, re, random, traceback

MVMailBundle        = objc.lookUpClass('MVMailBundle')
MailDocumentEditor  = objc.lookUpClass('MailDocumentEditor')

isQuoteFixed    = {}

import  random

def nslog(msg):
    NSLog("[%.4f] %s" % (random.random(), msg))

class QFMailDocumentEditor(MailDocumentEditor):

    __slots__ = ()

    def removeOldSignature(self, root, view):
        # grab first blockquote (if any)
        blockquote  = root.firstDescendantBlockQuote()
        if not blockquote:
            return False

        # find BR nodes so we can match "<br>-- "
        nodes   = []
        brs     = blockquote.getElementsByTagName_("br")
        nodes  += [ brs.item_(j) for j in range(brs.length()) ]
        divs    = blockquote.getElementsByTagName_("div")
        nodes  += [ divs.item_(j) for j in range(divs.length()) ]
        for node in nodes:
            # pick nodes with a quotelevel of 1 (in the first reply)
            if node.quoteLevel() != 1:
                continue

            # take stringvalue and innerHTML to check for signatures
            sv = node.stringValue() or ""
            ih = node.innerHTML()   or ""

            # check nodes
            if node.nodeName().lower() == 'div':
                if not ih.startswith("--&nbsp;") and not sv.startswith("-- "):
                    continue
            elif node.nodeName().lower() == 'br':
                node = node.nextSibling()
                if not node or not (node.stringValue() or "").startswith("-- "):
                    continue

            # set selection range
            domrange = view.selectedDOMRange()
            domrange.setStartBefore_(node)
            domrange.setEndAfter_(blockquote)

            # create selection
            view.setSelectedDOMRange_affinity_(domrange, 0)

            # delete old signature
            view.deleteSelection()

            # move down a line
            view.moveDown_(self)

            # and insert a paragraph break
            view.insertParagraphSeparator_(self)

            # remove empty lines
            blockquote.removeStrayLinefeeds()

            # signal that we removed an old signature
            return True

        return False

    def moveAboveNewSignature(self, dom, view):
        # find new signature by ID
        div = dom.getElementById_("AppleMailSignature")
        if not div:
            return False

        # set selection range
        domrange = view.selectedDOMRange()
        domrange.selectNode_(div)

        # create selection
        view.setSelectedDOMRange_affinity_(domrange, 0)

        # move up (positions cursor above signature)
        view.moveUp_(self)

        # and insert a paragraph break
        view.insertParagraphSeparator_(self)

        # signal that we removed an old signature
        return True

    def cleanupLayout(self, root):
        # clean up stray linefeeds
        root.getElementsByTagName_("body").item_(0).removeStrayLinefeeds()

        # clean up linebreaks before first blockquote
        blockquote  = root.firstDescendantBlockQuote()
        if not blockquote:
            return True
        parent      = blockquote.parentNode()
        node        = blockquote.previousSibling()
        while node and node.nodeName().lower() == 'br':
            parent.removeChild_(node)
            node = blockquote.previousSibling()

        return True

    def isLoaded(self):
        global isQuoteFixed

        # call superclass method first
        isloaded = super(self.__class__, self).isLoaded()
        if not isloaded:
            return isloaded

        # check if this message was already quotefixed
        if self in isQuoteFixed:
            return isloaded

        # check for the right kind of message:
        #   messagetype == 1 -> reply           (will  be fixed)
        #   messagetype == 2 -> reply to all    (will  be fixed)
        #   messagetype == 3 -> forward         (will  be fixed)
        #   messagetype == 4 -> is draft        (won't be fixed)
        #   messagetype == 5 -> new message     (won't be fixed)
        if self.messageType() not in [1, 2, 3]:
            return isloaded

        # grab composeView instance (this is the WebView which contains the
        # message editor) and check for the right conditions
        composeView = objc.getInstanceVariable(self, 'composeWebView')
        if not composeView or composeView.isLoading() or not composeView.isEditable():
            return isloaded

        # move cursor to end of document and signal that this view was
        # 'fixed', since this method gets called repeatedly (can't use
        # a new instance variable for this since the Obj-C backend doesn't
        # appreciate that)
        composeView.moveToEndOfDocument_(self)
        isQuoteFixed[self] = True

        # get menu instance
        menu = QFMenu.init()

        # perform some more modifications
        try:
            backend = self.backEnd()
            message = backend.message()
            is_rich = backend.containsRichText()
            frame   = composeView.mainFrame()
            dom     = frame.DOMDocument()
            root    = dom.documentElement()

            # send original HTML to menu for debugging
            menu.setHTML_(root.innerHTML())

            # start cleaning up
            if self.removeOldSignature(root, composeView) or self.moveAboveNewSignature(dom, composeView):
                # if we changed anything, reset the 'changed' state of the
                # compose backend
                self.backEnd().setHasChanges_(False)
            if self.cleanupLayout(root):
                self.backEnd().setHasChanges_(False)
        except Exception, e:
            if menu.isDebugging():
                QFAlert.showException(self)
            pass
        return isloaded

class QuoteFix(MVMailBundle):

    @classmethod
    def initialize(cls):
        MVMailBundle.registerBundle()
        QFMailDocumentEditor.poseAsClass_(MailDocumentEditor)
        QFMenu.init()
        NSLog("QuoteFix Plugin ($Rev: 24 $) registered with Mail.app")
