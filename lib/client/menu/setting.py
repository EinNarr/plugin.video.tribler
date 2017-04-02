import os,sys,urlparse

import xbmcaddon, xbmcgui, xbmcplugin


sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

class settings:
    def openSettings(query=None, id=addonInfo('id')):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        execute('Addon.OpenSettings(%s)' % id)
        c, f = query.split('.')
        execute('SetFocus(%i)' % (int(c) + 100))
        execute('SetFocus(%i)' % (int(f) + 200))
