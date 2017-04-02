import os
import sys
import xbmcaddon

ldir = os.path.join(xbmcaddon.Addon().getAddonInfo("path").decode("utf-8"), "lib")
sys.path.append(ldir)
