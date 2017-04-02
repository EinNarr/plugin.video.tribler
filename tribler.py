import sys
import urlparse
import paths

from client.module.setting import Setting

args = dict(urlparse.parse_qsl(sys.argv[2].replace('?', '')))

action = args.get('action')
channel_id = args.get('channel-id')
info_hash = args.get('info-hash')
name = args.get('name')
keyword = args.get('keyword')

API_PORT = 8085

setting = None

# import xbmc
# xbmc.log('python %s $' % join(xbmcaddon.Addon().getAddonInfo('path'), 'service.py'))

while not setting:
    setting = Setting(API_PORT)


if action == None:
    from client.menu import navigator
    navigator.Navigator().root()

elif action == 'recommanded':
    from client.menu import navigator
    navigator.Navigator().recommanded()

elif action == 'discovered':
    from client.menu import channel
    channel.Channel().discovered()

elif action == 'my-channel':
    from client.menu import navigator
    navigator.Navigator().my_channel()

elif action == 'subscriptions':
    from client.menu import channel
    channel.Channel().subscriptions()

elif action == 'downloads':
    from client.menu import navigator
    navigator.Navigator().downloads()

elif action == 'downloads-all':
    from client.menu import download
    download.Download().downloads_all()

elif action == 'downloads-downloading':
    from client.menu import download
    download.Download().downloads_downloading()

elif action == 'downloads-completed':
    from client.menu import download
    download.Download().downloads_completed()

elif action == 'downloads-active':
    from client.menu import download
    download.Download().downloads_active()

elif action == 'downloads-inactive':
    from client.menu import download
    download.Download().downloads_inactive()

elif action == 'search':
    from client.menu import navigator
    navigator.Navigator().search(API_PORT)

elif action == 'settings':
    setting.open_settings()

elif action == 'recommanded-torrents':
    from client.menu import torrent
    torrent.Torrent().recommanded_torrents()

elif action == 'recommanded-channels':
    from client.menu import channel
    channel.Channel().recommanded_channels()

elif action == 'search-all':
    from client.menu import search
    search.Search(API_PORT, keyword).all_results()

elif action == 'search-channels':
    from client.menu import search
    search.Search(API_PORT, keyword).channel_results()

elif action == 'search-torrents':
    from client.menu import search
    search.Search(API_PORT, keyword).torrent_results()

elif action == 'open-channel':
    from client.menu import torrent
    torrent.Torrent().open_channel(channel_id, name)

elif action == 'subscribe':
    from client.menu import channel
    channel.Channel().subscribe(channel_id, name)

elif action == 'torrent-action':
    from client.menu import torrent
    torrent.Torrent().torrent_action(info_hash, name)

elif action == 'download-action':
    from client.menu import download
    download.Download().download_action(info_hash, name)

elif action == 'start-download':
    from client.menu import download
    download.Download().start_download(info_hash, name)