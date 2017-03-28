import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import json
import requests

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

class Channel(object):
	def __init__(self, api_port=8085):
		self.api_port = api_port

	def discovered(self):
		from resources.lib.module.perform_request import request_discovered_channels
		channel_list = request_discovered_channels(self.api_port)

		for channel_info in channel_list:
			name = channel_info.get('name')
			channel_id = channel_info.get('dispersy_cid')
			subscribed = channel_info.get('subscribed')
			self.addDirectoryItem(name, 'open-channel&channel-id=%s&name=%s' % (channel_id, name), 'recommanded.png', 'DefaultMovies.png')

		self.endDirectory()

	def recommanded_channels(self):
		limit = 9
		from resources.lib.module.perform_request import request_recommanded_channels
		channel_list = request_recommanded_channels(self.api_port, limit)

		for channel_info in channel_list:
			name = channel_info.get('name')
			channel_id = channel_info.get('dispersy_cid')
			subscribed = channel_info.get('subscribed')
			self.addDirectoryItem(name, 'open-channel&channel-id=%s&name=%s' % (channel_id, name), 'recommanded.png', 'DefaultMovies.png')

		self.endDirectory()

	def subscriptions(self):
		from resources.lib.module.perform_request import request_subscribed_channels
		channel_list = request_subscribed_channels(self.api_port)

		for channel_info in channel_list:
			name = channel_info.get('name')
			channel_id = channel_info.get('dispersy_cid')
			subscribed = channel_info.get('subscribed')
			self.addDirectoryItem(name, 'open-channel&channel-id=%s&name=%s' % (channel_id, name), 'recommanded.png', 'DefaultMovies.png')

		self.endDirectory()

	def subscribe(self, channel_id, name):
		from resources.lib.module.perform_request import subscribe_channel
		status = subscribe_channel(self.api_port, channel_id, True)
		from resources.lib.module.utilities import show_notification
		if status == 200:
			show_notification(name, 'Subscribe successfully')
		else:
			subscribe_channel(self.api_port, channel_id, False)
			show_notification(name, 'Unsubscribe successfully')

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