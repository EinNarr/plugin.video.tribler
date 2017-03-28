import os
import sys
import time
import urlparse

import xbmcaddon

from requests.exceptions import ConnectionError
from os.path import join, abspath, dirname

from resources.lib.module.setting import Setting

args = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action 		= args.get('action')
channel_id 	= args.get('channel-id')
info_hash 	= args.get('info-hash')
name 		= args.get('name')
keyword		= args.get('keyword')

API_PORT = 8085

setting = None

# import xbmc
# xbmc.log('python %s $' % join(xbmcaddon.Addon().getAddonInfo('path'), 'service.py'))
path = xbmcaddon.Addon().getAddonInfo('path')

while not setting:
	try:
		setting = Setting(API_PORT)
	except:
		os.system('python %s/service.py $' % path)
		# time.sleep(3)

if action == None:
	from resources.lib.menu import navigator
	navigator.Navigator().root()

elif action == 'recommanded':
	from resources.lib.menu import navigator
	navigator.Navigator().recommanded()

elif action == 'discovered':
	from resources.lib.menu import channel
	channel.Channel().discovered()

elif action == 'my-channel':
	from resources.lib.menu import navigator
	navigator.Navigator().my_channel()

elif action == 'subscriptions':
	from resources.lib.menu import channel
	channel.Channel().subscriptions()

elif action == 'downloads':
	from resources.lib.menu import navigator
	navigator.Navigator().downloads()

elif action == 'downloads-all':
	from resources.lib.menu import download
	download.Download().downloads_all()

elif action == 'downloads-downloading':
	from resources.lib.menu import download
	download.Download().downloads_downloading()

elif action == 'downloads-completed':
	from resources.lib.menu import download
	download.Download().downloads_completed()

elif action == 'downloads-active':
	from resources.lib.menu import download
	download.Download().downloads_active()

elif action == 'downloads-inactive':
	from resources.lib.menu import download
	download.Download().downloads_inactive()

elif action == 'search':
	from resources.lib.menu import navigator
	navigator.Navigator().search(API_PORT)

elif action == 'settings':
	setting.open_settings()

elif action == 'recommanded-torrents':
	from resources.lib.menu import torrent
	torrent.Torrent().recommanded_torrents()

elif action == 'recommanded-channels':
	from resources.lib.menu import channel
	channel.Channel().recommanded_channels()

elif action == 'search-all':
	from resources.lib.menu import search
	search.Search(API_PORT, keyword).all_results()

elif action == 'search-channels':
	from resources.lib.menu import search
	search.Search(API_PORT, keyword).channel_results()

elif action == 'search-torrents':
	from resources.lib.menu import search
	search.Search(API_PORT, keyword).torrent_results()

elif action == 'open-channel':
	from resources.lib.menu import torrent
	torrent.Torrent().open_channel(channel_id, name)

elif action == 'subscribe':
	from resources.lib.menu import channel
	channel.Channel().subscribe(channel_id, name)

elif action == 'torrent-action':
	from resources.lib.menu import torrent
	torrent.Torrent().torrent_action(info_hash, name)

elif action == 'download-action':
	from resources.lib.menu import download
	download.Download().download_action(info_hash, name)

elif action == 'start-download':
	from resources.lib.menu import download
	download.Download().start_download(info_hash, name)