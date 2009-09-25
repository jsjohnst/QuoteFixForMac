"""
QuoteFix - a Mail.app plug-in to fix some annoyances when replying to e-mail

Version: $Rev: 17 $

"""
from    AppKit      import *
from    Foundation  import *
import  objc, re, random

MVMailBundle    = objc.lookUpClass('MVMailBundle')
DocumentEditor  = objc.lookUpClass('DocumentEditor')
ComposeBackEnd  = objc.lookUpClass('ComposeBackEnd')

isQuoteFixed = {}

import  random

def rlog(msg):
    NSLog("[%.4f] %s" % (random.random(), msg))

class MyDocumentEditor(DocumentEditor):

    __slots__ = ()

    def removeOldSignature(self, root, view):
        firstdiv    = root.getElementsByTagName_("div").item_(0)
        blockquotes = root.getElementsByTagName_("blockquote")
        for i in range(blockquotes.length()):
            blockquote = blockquotes.item_(i)
            # only find non-nested blockquotes (lowest quote level)
            if blockquote.parentNode() != firstdiv:
                continue
            # find BR nodes so we can match "<br>-- "
            brs = blockquote.getElementsByTagName_("br")
            for j in range(brs.length()):
                br = brs.item_(j)
                # again, not nested BR's
                if br.parentNode().parentNode() != blockquote:
                    continue
                # find next sibling
                sibling = br.nextSibling()
                # should be a text-node
                if sibling and sibling.nodeValue().startswith("-- "):
                    # remove all whitelines before old signature
                    while br.previousSibling().nodeName().lower() == 'br':
                        br = br.previousSibling()
                    # set selection range
                    domrange = view.selectedDOMRange()
                    domrange.setStartBefore_(br)
                    domrange.setEndAfter_(blockquote)
                    # create selection
                    view.setSelectedDOMRange_affinity_(domrange, 0)
                    # delete old signature
                    view.deleteSelection()
                    # move down a line
                    view.moveDown_(self)
                    # and insert a paragraph break
                    view.insertParagraphSeparator_(self)
                    # signal that we removed an old signature
                    return True
        return False

    def moveAboveNewSignature(self, root, view):
        # find new signature by ID
        divs = root.getElementsByTagName_("div")
        for i in range(divs.length()):
            div = divs.item_(i)
            if div.getAttribute_("id") != 'AppleMailSignature':
                continue
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
        return False

    def cleanupLayout(self, root):
        hasChanged = False
        # clean up empty lines at top of message
        body    = root.getElementsByTagName_("body").item_(0)
        node    = body.firstChild()
        while node and node.nodeName().lower() == 'br':
            body.removeChild_(node)
            node = body.firstChild()
            hasChanged = True
        # clean up linebreaks before first blockquote
        quote   = root.getElementsByTagName_("blockquote").item_(0)
        parent  = quote.parentNode()
        node    = quote.previousSibling()
        while node and node.nodeName().lower() == 'br':
            parent.removeChild_(node)
            node = quote.previousSibling()
            hasChanged = True
        # signal change
        return hasChanged

    def isLoaded(self):
        global isQuoteFixed
        isloaded = super(self.__class__, self).isLoaded()
        if isloaded and self not in isQuoteFixed:
            # grab composeView instance; this is the WebView which contains
            # the message editor
            composeView = objc.getInstanceVariable(self, 'composeWebView')
            # check for the right conditions
            if composeView and not composeView.isLoading() and composeView.isEditable():
                # move cursor to end of document
                composeView.moveToEndOfDocument_(self)
                # signal that this view was 'fixed', since this method gets
                # called repeatedly (can't use a new instance variable for
                # this since the Obj-C backend doesn't appreciate that)
                isQuoteFixed[self] = True
                # try to remove old signature and position cursor sanely
                try:
                    frame   = composeView.selectedFrame()
                    dom     = frame.DOMDocument()
                    root    = dom.documentElement()
                    if self.removeOldSignature(root, composeView) or self.moveAboveNewSignature(root, composeView):
                        # if we changed anything, reset the 'changed' state
                        # of the compose backend
                        self.backEnd().setHasChanges_(False)
                    if self.cleanupLayout(root):
                        self.backEnd().setHasChanges_(False)
                except Exception, e:
                    pass
        return isloaded

class QuoteFix(MVMailBundle):

    @classmethod
    def initialize (cls):
        MVMailBundle.registerBundle()
        MyDocumentEditor.poseAsClass_(DocumentEditor)
        #MyComposeBackEnd.poseAsClass_(ComposeBackEnd)
        NSLog("QuoteFix Plugin registered with Mail.app")
