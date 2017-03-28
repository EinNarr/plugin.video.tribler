import sys

import xbmcaddon
import xbmcgui

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

class SubscribeListItem(xbmcgui.ListItem):
	def _init_(self, subscribed):
		xbmcgui.ListItem._init_(self)

		self.subscribed 		= subscribed
		self.subscribe_str		= xbmcaddon.Addon().getLocalizedString(33001).encode('utf-8')
		self.unsubscribe_str	= xbmcaddon.Addon().getLocalizedString(33002).encode('utf-8')
		
		if subscribed:
			self.setLabel(self.unsubscribe_str)
		else:
			self.setLabel(self.subscribe_str)

	def.toggle(self)
		self.subscribed = not self.subscribed
		if subscribed:
			self.setLabel(unsubscribe_str)
		else:
			self.setLabel(subscribe_str)


class ChannelListItem(xbmcgui.ListItem):
	def _init_(self, api_port, channel_id, subscribed):
		pass

class TorrentListItem(xbmcgui.ListItem):
	def _init_(self):
		pass

class DownloadListItem(xbmcgui.ListItem):
	def _init_(self):
		pass