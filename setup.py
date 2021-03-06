from    distutils.core import setup
import  py2app, sys, os, commands

# determine version from latest revision
svnversion = commands.getoutput("svnversion -n")
if ':' in svnversion:
    dummy, svnversion = svnversion.split(":")
if svnversion[-1] in [ 'M', 'S' ]:
    svnversion = svnversion[:-1]

setup(
    plugin      = [ 'QuoteFix.py' ],
    version     = svnversion,
    description = "QuoteFix for Mac is a Mail.app plugin",
    options     = dict(py2app = dict(
        extension   = '.mailbundle',
        includes    = [ 'QFApp', 'QFMenu', 'QFAlert' ],
        plist       = dict(
            NSPrincipalClass                    = 'QuoteFix',
            CFBundleIdentifier                  = 'name.klep.mail.QuoteFix',
            NSHumanReadableCopyright            = '(c) 2009, Robert Klep, robert@klep.name',
            SupportedPluginCompatibilityUUIDs   = [
                # 10.6
                '225E0A48-2CDB-44A6-8D99-A9BB8AF6BA04', # Mail 4.0
                'B3F3FC72-315D-4323-BE85-7AB76090224D', # Message.framework 4.0
                # 10.6.1
                '99BB3782-6C16-4C6F-B910-25ED1C1CB38B',
                '2610F061-32C6-4C6B-B90A-7A3102F9B9C8',
            ]
        )
    ))
)
