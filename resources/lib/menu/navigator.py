import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import json
import requests

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

class Navigator(object):
	def root(self):
		self.addDirectoryItem(32001, 'recommanded', 'recommanded.png', 'DefaultMovies.png')
		self.addDirectoryItem(32002, 'discovered', 'discovered.png', 'DefaultTVShows.png')
		# self.addDirectoryItem(32003, 'my-channel', 'discovered.png', 'DefaultTVShows.png')
		self.addDirectoryItem(32004, 'subscriptions', 'subscriptions.png', 'DefaultMovies.png')
		self.addDirectoryItem(32005, 'downloads', 'tools.png', 'DefaultAddonProgram.png')
		self.addDirectoryItem(32006, 'search', 'search.png', 'DefaultFolder.png')
		self.addDirectoryItem(32007, 'settings', 'settings.png', 'DefaultFolder.png')
		self.endDirectory()

	def recommanded(self):
		self.addDirectoryItem(32011, 'recommanded-torrents', 'trakt.png', 'DefaultMovies.png')
		self.addDirectoryItem(32012, 'recommanded-channels', 'trakt.png', 'DefaultMovies.png')
		self.endDirectory()

	def my_channel(self):
		self.endDirectory()

	def downloads(self):
		self.addDirectoryItem(32051, 'downloads-all', 'recommanded.png', 'DefaultMovies.png')
		self.addDirectoryItem(32052, 'downloads-downloading', 'recommanded.png', 'DefaultMovies.png')
		self.addDirectoryItem(32053, 'downloads-completed', 'recommanded.png', 'DefaultMovies.png')
		self.addDirectoryItem(32054, 'downloads-active', 'recommanded.png', 'DefaultMovies.png')
		self.addDirectoryItem(32055, 'downloads-inactive', 'recommanded.png', 'DefaultMovies.png')
		self.endDirectory()

	def search(self, api_port):	
		from resources.lib.module.utilities import get_string
		keyword = xbmcgui.Dialog().input(get_string(33201), type=xbmcgui.INPUT_ALPHANUM)
		if len(keyword)>0:
			from resources.lib.menu import search
			search.Search(api_port, keyword).start_searching()
			self.addDirectoryItem(32061, 'search-all&keyword=%s' % keyword, 'trakt.png', 'DefaultMovies.png')
			self.addDirectoryItem(32062, 'search-channels&keyword=%s' % keyword, 'trakt.png', 'DefaultMovies.png')
			self.addDirectoryItem(32063, 'search-torrents&keyword=%s' % keyword, 'trakt.png', 'DefaultMovies.png')
			self.endDirectory()

	def addDirectoryItem(self, name, query, thumb, icon, isFolder=True):
		if isinstance(name, int) :
			name = xbmcaddon.Addon().getLocalizedString(name).encode('utf-8')
		#thumb = os.path.join(artPath, thumb) if not artPath == None else icon
		url = '%s?action=%s' % (sysaddon, query)
		thumb = icon
		item = xbmcgui.ListItem(label=name)
		item.setArt({'icon': thumb, 'thumb': thumb})
		xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

	def endDirectory(self):
		xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)