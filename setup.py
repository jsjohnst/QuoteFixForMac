from    distutils.core import setup
import  py2app

plist = dict(NSPrincipalClass = 'QuoteFix')
setup(
    plugin  = [ 'QuoteFix.py' ],
    options = dict(py2app = dict(
        extension   = '.mailbundle',
        includes    = [ 'QFMenu', 'QFAlert' ],
        plist       = plist
    ))
)
