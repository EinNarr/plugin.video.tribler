import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import json
import requests

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

class Torrent(object):
	def __init__(self, api_port=8085):
		self.api_port = api_port
		
	def recommanded_torrents(self):
		limit = 9
		from resources.lib.module.perform_request import request_random_torrents
		torrent_list = request_random_torrents(8085, limit)

		for torrent_info in torrent_list:
			name = torrent_info.get('name')
			info_hash = torrent_info.get('infohash')
			self.addDirectoryItem(name, 'start-download&info-hash=%s&name=%s' % (info_hash, name), 'recommanded.png', 'DefaultMovies.png')

		self.endDirectory()

	def open_channel(self, channel_id, name):
		from resources.lib.module.perform_request import request_channel_torrents
		torrent_list = request_channel_torrents(8085, channel_id)

		self.addDirectoryItem(33001, 'subscribe&channel-id=%s&name=%s' % (channel_id, name), 'recommanded.png', 'DefaultMovies.png')

		for torrent_info in torrent_list:
			name = torrent_info.get('name')
			if name=='Unknown name' or name=='Unnamed torrent':
				continue
			info_hash = torrent_info.get('infohash')
			self.addDirectoryItem(name, 'torrent-action&info-hash=%s&name=%s' % (info_hash, name), 'recommanded.png', 'DefaultMovies.png')

		self.endDirectory()

	def torrent_action(self, info_hash, name):
		from resources.lib.module.utilities import get_string
		action = xbmcgui.Dialog().select(get_string(33004), [get_string(33005), get_string(33006), get_string(33007)])
		if   action == 0:
			from resources.lib.menu import download
			from resources.lib.module.perform_request import request_variables
			download.Download().start_download(info_hash, name, auto=True)
			video_port = request_variables(self.api_port).get('ports').get('video~port')
			Player = xbmc.Player()
			Player.play('http://localhost:%s/%s/%d' % (video_port, info_hash, 0))
		elif action == 1:
			from resources.lib.menu import download
			download.Download().start_download(info_hash, name)
		elif action == 2:
			from resources.lib.menu import download
			from resources.lib.module.perform_request import request_variables
			download.Download().start_download(info_hash, name)
			video_port = request_variables(self.api_port).get('ports').get('video~port')
			Player = xbmc.Player()
			Player.play('http://localhost:%s/%s/%d' % (video_port, info_hash, 0))
			

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