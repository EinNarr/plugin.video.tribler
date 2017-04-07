import json
import sys

import xbmcaddon

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

class Setting(object):
    def __init__(self, api_port):
        self.api_port = api_port

        self.load_from_server()

        self.load_from_ui()

    def load_from_ui(self):
        self.family_filter             = bool     (xbmcaddon.Addon().getSetting('filter.enable') == 'true')
        self.download_direction        = str     (xbmcaddon.Addon().getSetting('dllocation.path'))
        self.ask_download_settings     = bool    (xbmcaddon.Addon().getSetting('dllocation.ask') == 'true')
        self.anonymous_download        = bool    (xbmcaddon.Addon().getSetting('dlsetting.anony') == 'true')
        self.anonymous_seed            = xbmcaddon.Addon().getSetting('dlsetting.encrypt')
        self.watch_folder             = bool    (xbmcaddon.Addon().getSetting('wfolder.enable') == 'true')
        self.watch_folder_dir         = str    (xbmcaddon.Addon().getSetting('wfolder.path'))
        self.developer_mode            = bool    (xbmcaddon.Addon().getSetting('devmode.enable') == 'true')
        self.port                     = int    (xbmcaddon.Addon().getSetting('firewall.port'))
        self.lt_proxy_type             = int    (xbmcaddon.Addon().getSetting('tproxy.type'))
        self.lt_proxy_server         = str     (xbmcaddon.Addon().getSetting('tproxy.server'))
        self.lt_proxy_port             = str    (xbmcaddon.Addon().getSetting('tproxy.port'))
        self.lt_proxy_username         = str     (xbmcaddon.Addon().getSetting('tproxy.user'))
        self.lt_proxy_password         = str     (xbmcaddon.Addon().getSetting('tproxy.pass'))
        self.bandwidth_management     = bool    (xbmcaddon.Addon().getSetting('btfeature.utp') == 'true')
        self.bandwidth_connection    = int    (xbmcaddon.Addon().getSetting('btfeature.connect'))
        self.upload_limit             = int    (xbmcaddon.Addon().getSetting('bwlimit.upload'))
        self.download_limit         = int     (xbmcaddon.Addon().getSetting('bwlimit.download'))
        self.seeding_option         = int    (xbmcaddon.Addon().getSetting('seeding.option'))
        self.seeding_ratio             = float    (xbmcaddon.Addon().getSetting('seeding.ratio'))
        self.seeding_hour             = int    (xbmcaddon.Addon().getSetting('seeding.hour'))
        self.seeding_minute         = int    (xbmcaddon.Addon().getSetting('seeding.min'))
        self.exitnode                 = bool    (xbmcaddon.Addon().getSetting('anony.exitnode') == 'true')
        self.default_hop             = int    (xbmcaddon.Addon().getSetting('proxydl.speed')) + 1
        self.multichain             = bool    (xbmcaddon.Addon().getSetting('multichain.enable'))


    def load_from_server(self):
        from client.module.perform_request import load_settings
        settings_data = load_settings(self.api_port)

        TF = {True: 'true', False: 'false'}
        seeding_modes = {'forever': '0', 'time': '1', 'never': '2', 'ratio': '3'}

        xbmcaddon.Addon().setSetting('filter.enable',     TF[settings_data['general']['family_filter']])
        xbmcaddon.Addon().setSetting('dllocation.path', settings_data['downloadconfig']['saveas'])
        xbmcaddon.Addon().setSetting('wfolder.enable',     TF[settings_data['watch_folder']['enabled']])
        xbmcaddon.Addon().setSetting('wfolder.path',     settings_data['watch_folder']['watch_folder_dir'])
        xbmcaddon.Addon().setSetting('firewall.port',     str(settings_data['general']['minport']))
        xbmcaddon.Addon().setSetting('tproxy.type',     str(settings_data['libtorrent']['lt_proxytype']))
        if settings_data['libtorrent']['lt_proxyserver']:
            xbmcaddon.Addon().setSetting('tproxy.server', settings_data['libtorrent']['lt_proxyserver'][0])
            xbmcaddon.Addon().setSetting('tproxy.port', str(settings_data['libtorrent']['lt_proxyserver'][1]))
        else:
            xbmcaddon.Addon().setSetting('tproxy.server', '')
            xbmcaddon.Addon().setSetting('tproxy.port', '')
        if settings_data['libtorrent']['lt_proxyauth']:
            xbmcaddon.Addon().setSetting('tproxy.user', settings_data['libtorrent']['lt_proxyauth'][0])
            xbmcaddon.Addon().setSetting('tproxy.pass', settings_data['libtorrent']['lt_proxyauth'][1])
        else:
            xbmcaddon.Addon().setSetting('tproxy.user', '')
            xbmcaddon.Addon().setSetting('tproxy.pass', '')
        xbmcaddon.Addon().setSetting('btfeature.utp', TF[settings_data['libtorrent']['utp']])
        if settings_data['libtorrent']['max_connections_download'] == -1:
            xbmcaddon.Addon().setSetting('btfeature.connect', '0')
        else:
            xbmcaddon.Addon().setSetting('btfeature.connect', str(settings_data['libtorrent']['max_connections_download']))
        xbmcaddon.Addon().setSetting('bwlimit.upload', str(settings_data['Tribler']['maxuploadrate']))
        xbmcaddon.Addon().setSetting('bwlimit.download', str(settings_data['Tribler']['maxdownloadrate']))
        xbmcaddon.Addon().setSetting('seeding.option', seeding_modes[settings_data['downloadconfig']['seeding_mode']])
        xbmcaddon.Addon().setSetting('seeding.ratio', str(settings_data['downloadconfig']['seeding_ratio']))
        xbmcaddon.Addon().setSetting('seeding.hour', str(int(settings_data['downloadconfig']['seeding_time'])/60))
        xbmcaddon.Addon().setSetting('seeding.min', str(int(settings_data['downloadconfig']['seeding_time'])%60))
        xbmcaddon.Addon().setSetting('anony.exitnode', TF[settings_data['tunnel_community']['exitnode_enabled']])
        xbmcaddon.Addon().setSetting('proxydl.speed', str(settings_data['Tribler']['default_number_hops']-1))
        xbmcaddon.Addon().setSetting('multichain.enable', TF[settings_data['multichain']['enabled']])


    def save(self):
        settings_data = {'general': {}, 'Tribler': {}, 'downloadconfig': {}, 'libtorrent': {}, 'watch_folder': {},
                        'tunnel_community': {}, 'multichain': {}}
        settings_data['general']['family_filter']     = self.family_filter
        settings_data['downloadconfig']['saveas']     = self.download_direction

        settings_data['watch_folder']['enabled']    = self.watch_folder
        if settings_data['watch_folder']['enabled']:
            settings_data['watch_folder']['watch_folder_dir'] = self.watch_folder_dir

        settings_data['general']['minport'] = int(self.port)
        settings_data['libtorrent']['lt_proxytype'] = self.lt_proxy_type

        if len(self.lt_proxy_server) > 0 and len(self.lt_proxy_port) > 0:
            settings_data['libtorrent']['lt_proxyserver'] = [None, None]
            settings_data['libtorrent']['lt_proxyserver'][0] = self.lt_proxy_server
            settings_data['libtorrent']['lt_proxyserver'][1] = self.lt_proxy_port

        if len(self.lt_proxy_username) > 0 and len(self.lt_proxy_password) > 0:
            settings_data['libtorrent']['lt_proxyauth'] = [None, None]
            settings_data['libtorrent']['lt_proxyauth'][0] = self.lt_proxy_username
            settings_data['libtorrent']['lt_proxyauth'][1] = self.lt_proxy_password
        settings_data['libtorrent']['utp'] = self.bandwidth_management

        if self.bandwidth_connection == 0:
            self.bandwidth_connection = -1
        settings_data['libtorrent']['max_connections_download'] = self.bandwidth_connection

        settings_data['Tribler']['maxuploadrate'] = self.upload_limit
        settings_data['Tribler']['maxdownloadrate'] = self.download_limit

        seeding_modes = ['forever', 'time', 'never', 'ratio']
        selected_mode = seeding_modes[int(self.seeding_option)]

        settings_data['downloadconfig']['seeding_mode'] = selected_mode
        settings_data['downloadconfig']['seeding_ratio'] = self.seeding_ratio

        settings_data['downloadconfig']['seeding_time'] = self.seeding_hour*60+self.seeding_minute

        settings_data['tunnel_community']['exitnode_enabled'] = self.exitnode
        settings_data['Tribler']['default_number_hops'] = self.default_hop
        settings_data['multichain']['enabled'] = self.multichain

        from client.module.perform_request import save_settings
        save_settings(self.api_port, json.dumps(settings_data))

        return json.dumps(settings_data)

    def open_settings(self):
        # xbmcaddon.Addon().setSetting(id='filter.enable',     value='true')
        # from client.module.setting import Setting
        # settings = Setting().save()
        # xbmc.log(settings)
        # self.endDirectory()
        xbmcaddon.Addon().openSettings()
        self.load_from_ui()
        self.save()
        # xbmc.executebuiltin('Addon.OpenSettings(%s)' % id)