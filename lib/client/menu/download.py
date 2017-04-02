#coding:utf-8
import os
import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import json
import requests

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

class Download(object):
    def __init__(self, api_port=8085):
        self.api_port = api_port

    def get_download_prefix(self, status):
        prefix = status
        if   status == 'DLSTATUS_ALLOCATING_DISKSPACE':
            prefix = '[ALLOCATING DISKSPACE]'
        elif status == 'DLSTATUS_WAITING4HASHCHECK':
            prefix = '[WAITING FOR HASHCHECK]'
        elif status == 'DLSTATUS_HASHCHECKING':
            prefix = '[HASHCHECKING]'
        elif status == 'DLSTATUS_DOWNLOADING':
            prefix = '[DOWNLOADING]'
        elif status == 'DLSTATUS_SEEDING':
            prefix = '[SEEDING]'
        elif status == 'DLSTATUS_STOPPED':
            prefix = '[STOPPED]'
        elif status == 'DLSTATUS_STOPPED_ON_ERROR':
            prefix = '[STOPPED ON ERROR]'
        elif status == 'DLSTATUS_METADATA':
            prefix ='[FETCHING INFORMATION]'
        elif status == 'DLSTATUS_CIRCUITS':
            prefix ='[BUILDING CIRCUITS]'
        return prefix

    def get_download_progress(self, progress):
        progress = progress*100
        if progress<10:
            return '[  %.1f%%]' % progress
        else:
            return '[%.1f%%]' % progress

    def downloads_all(self):
        from client.module.perform_request import request_downloads
        download_list = request_downloads(self.api_port)

        for download_info in download_list:
            name = download_info.get('name')
            status = download_info.get('status')
            info_hash = download_info.get('infohash')
            self.addDirectoryItem(self.get_download_prefix(status)+name, 'download-action&info-hash=%s&name=%s' % (info_hash, name), 'recommanded.png', 'DefaultMovies.png')

        self.endDirectory()

    def downloads_downloading(self):
        from client.module.perform_request import request_downloads
        download_list = request_downloads(self.api_port)

        for download_info in download_list:
            name = download_info.get('name')
            status = download_info.get('status')
            progress = download_info.get('progress')
            info_hash = download_info.get('infohash')
            if status=='DLSTATUS_DOWNLOADING':
                self.addDirectoryItem(self.get_download_progress(progress)+name, 'download-action&info-hash=%s&name=%s' % (info_hash, name), 'recommanded.png', 'DefaultMovies.png')

        self.endDirectory()

    def downloads_completed(self):
        from client.module.perform_request import request_downloads
        download_list = request_downloads(self.api_port)

        for download_info in download_list:
            name = download_info.get('name')
            status = download_info.get('status')
            if status=='DLSTATUS_SEEDING':
                destination = download_info.get('destination')
                name = download_info.get('name')
                target = destination + '/' + name
                info_hash = download_info.get('infohash')
                self.addDirectoryItem(name, 'download-action&info-hash=%s&name=%s' % (info_hash, name), 'recommanded.png', 'DefaultMovies.png')

        self.endDirectory()

    def downloads_active(self):
        from client.module.perform_request import request_downloads
        download_list = request_downloads(self.api_port)

        for download_info in download_list:
            name = download_info.get('name')
            status = download_info.get('status')
            info_hash = download_info.get('infohash')
            if not (status=='DLSTATUS_STOPPED' or status=='DLSTATUS_STOPPED_ON_ERROR'):
                self.addDirectoryItem(name, 'download-action&info-hash=%s&name=%s' % (info_hash, name), 'recommanded.png', 'DefaultMovies.png')

        self.endDirectory()

    def downloads_inactive(self):
        from client.module.perform_request import request_downloads
        download_list = request_downloads(self.api_port)

        for download_info in download_list:
            name = download_info.get('name')
            status = download_info.get('status')
            info_hash = download_info.get('infohash')
            if status=='DLSTATUS_STOPPED' or status=='DLSTATUS_STOPPED_ON_ERROR':
                self.addDirectoryItem(name, 'download-action&info-hash=%s&name=%s' % (info_hash, name), 'recommanded.png', 'DefaultMovies.png')

        self.endDirectory()

    def download_action(self, info_hash, name):
        from client.module.utilities import get_string
        from client.module.perform_request import request_downloads
        from client.module.perform_request import request_variables

        download_list = request_downloads(self.api_port)

        for download_info in download_list:
            if download_info.get('infohash') == info_hash:
                break

        status = download_info.get('status')
        download_stopped = False
        if status=='DLSTATUS_STOPPED' or status=='DLSTATUS_STOPPED_ON_ERROR':
            download_stopped = True

        if download_stopped:
            action = xbmcgui.Dialog().select(get_string(33004), [get_string(33120), get_string(33121), get_string(33122), get_string(33124), get_string(33125)])
        else:
            action = xbmcgui.Dialog().select(get_string(33004), [get_string(33120), get_string(33121), get_string(33123), get_string(33124), get_string(33125)])

        if   action == 0:
            file_names = []
            for file in download_info.get('files'):
                file_names.append(file.get('name'))
            file_id = xbmcgui.Dialog().select(get_string(33004), file_names)
            video_port = request_variables(self.api_port).get('ports').get('video~port')
            Player = xbmc.Player()
            Player.play('http://localhost:%s/%s/%d' % (video_port, info_hash, file_id))
        elif action == 1:
            self.download_info(info_hash, name)
        elif action == 2:
            if download_stopped:
                from client.module.perform_request import resume_download
                resume_download(self.api_port, info_hash)
            else:
                from client.module.perform_request import stop_download
                stop_download(self.api_port, info_hash)
        elif action == 3:
            pass
        elif action == 4:
            confirm = xbmcgui.Dialog().yesno(get_string(33126), get_string(33127))
            if confirm:
                remove_data = xbmcgui.Dialog().yesno(get_string(33126), get_string(33128))
                if remove_data:
                    pass
                else:
                    pass

    def download_info(self, info_hash, name):
        from client.module.utilities import get_string
        dialog_progress = xbmcgui.DialogProgress()
        dialog_progress.create(name)
        while not dialog_progress.iscanceled():
            from client.module.perform_request import request_downloads
            download_list = request_downloads(self.api_port)

            download_info = None
            for download_info in download_list:
                if download_info.get('infohash') == info_hash:
                    break

            progress         = download_info.get('progress')
            speed_up         = download_info.get('speed_up')
            speed_down         = download_info.get('speed_down')
            eta             = download_info.get('eta')
            filesize         = download_info.get('size')
            seeder             = download_info.get('num_seeds')
            leecher            = download_info.get('num_peers')
            destination        = download_info.get('destination')
            status             = download_info.get('status')

            eta             = int(eta)
            eta_dis            = ' (' + get_string(33109) + ': '
            if eta>=3155760000:
                eta_dis     = eta_dis + '> 1 century)'
            elif eta>=31536000:
                eta_dis     = eta_dis + '> 1 year)'
            elif eta>=2592000:
                eta_dis     = eta_dis + '%dm%dd%dh%dm%ds)' % ((eta/2592000), (eta%2592000/86400), (eta%86400/3600), (eta%3600/60), (eta%60))
            elif eta>=86400:
                eta_dis     = eta_dis + '%dd%dh%dm%ds)' % ((eta/86400), (eta%86400/3600), (eta%3600/60), (eta%60))
            elif eta>=3600:
                eta_dis     = eta_dis + '%dh%dm%ds)' % ((eta/3600), (eta%3600/60), (eta%60))
            elif eta>=60:
                eta_dis     = eta_dis + '%dm%ds)' % ((eta/60), (eta%60))
            elif eta>0:
                eta_dis     = eta_dis + '%ds)' % ((eta%60))
            else:
                eta_dis     = eta_dis + 'N/A)'
            if not status == 'DLSTATUS_DOWNLOADING':
                eta_dis     = ''

            progress_bar    = int(progress*100)

            progress_dis     = get_string(33101) + ':   ' + '%.1f' % (filesize*progress/1024/1024) + 'MB/' + '%.1f' % (filesize/1024/1024) + 'MB' + eta_dis

            speed_up_dis    = None
            if speed_up < 1024:
                speed_up_dis = '%.1f' % (speed_up) + 'B/s ↑ '
            elif speed_up < 1024*1024:
                speed_up_dis = '%.1f' % (speed_up/1024) + 'KB/s ↑ '
            else:
                speed_up_dis = '%.1f' % (speed_up/1024/1024) + 'MB/s ↑ '

            speed_down_dis    = None
            if speed_down < 1024:
                speed_down_dis = '%.1f' % (speed_down) + 'B/s ↓ '
            elif speed_down < 1024*1024:
                speed_down_dis = '%.1f' % (speed_down/1024) + 'KB/s ↓ '
            else:
                speed_down_dis = '%.1f' % (speed_down/1024/1024) + 'MB/s ↓ '

            health_dis        = ' (%d ' % seeder
            if seeder<2:
                health_dis    = health_dis + get_string(33104) + ', %d ' % leecher
            else:
                health_dis    = health_dis + get_string(33105) + ', %d ' % leecher
            if leecher<2:
                health_dis    = health_dis + get_string(33106) + ')'
            else:
                health_dis    = health_dis + get_string(33107) + ')'

            speed_dis        = get_string(33102) + ':   ' + speed_down_dis + '  ' + speed_up_dis + health_dis

            destination_dis = get_string(33103) + ':   ' + destination

            dialog_progress.update(progress_bar, progress_dis, speed_dis, destination_dis)

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

    def start_download(self, info_hash, name, auto=False):
        from client.module.setting import Setting
        setting = Setting(self.api_port)

        ask     = setting.ask_download_settings
        anon_hops = 0
        safe_seeding = 0
        if setting.anonymous_download:
            anon_hops = setting.default_hop
            safe_seeding = 1
        if setting.anonymous_seed:
            safe_seeding = 1
        destination = setting.download_direction

        if ask and not auto:
            from client.module.utilities import get_string
            dialog = xbmcgui.Dialog()
            destination = dialog.browse(3, get_string(33008), 'files', '', False, False, setting.download_direction)#no idea what the 3rd parameter is
            anony_mode = dialog.select(get_string(33009), [get_string(33010), get_string(33011), get_string(33012)])
            if   anony_mode == 0:
                anon_hops = setting.default_hop
                safe_seeding = 1
            elif anony_mode == 1:
                safe_seeding = 1
            elif anony_mode == 2:
                anon_hops = 0
                safe_seeding = 0

        from client.module.perform_request import start_download
        response = start_download(self.api_port, info_hash, name, anon_hops, safe_seeding, destination)

        status = response.status_code
        if status == 200:
            from client.module.utilities import show_notification
            show_notification(name, 'Download started')
        elif response.json().get('error').get('message') == u'This download already exists.':
            from client.module.utilities import show_warning
            show_warning(name, 'Download already exists')
        else:
            from client.module.utilities import show_error
            show_error('ERROR', 'Failed to start download')