import requests

def request_channel_torrents(api_port, channel_id):
	response = requests.get('http://localhost:%d/channels/discovered/%s/torrents' % (api_port, channel_id))
	torrent_list = response.json().get('torrents')
	return torrent_list

def request_random_torrents(api_port, limit):
	response = requests.get('http://localhost:%d/torrents/random' % (api_port))
	torrent_list = response.json().get('torrents')
	return torrent_list

def request_discovered_channels(api_port):
	response = requests.get('http://localhost:%d/channels/discovered' % api_port)
	channel_list = response.json().get('channels')
	return channel_list

def request_recommanded_channels(api_port, limit):
	response = requests.get('http://localhost:%d/channels/popular' % api_port)
	channel_list = response.json().get('channels')
	return channel_list

def request_subscribed_channels(api_port):
	response = requests.get('http://localhost:%d/channels/subscribed' % api_port)
	channel_list = response.json().get('subscribed')
	return channel_list

def request_variables(api_port):
	response = requests.get('http://localhost:%d/variables' % api_port)
	variables = response.json().get('variables')
	return variables

def request_downloads(api_port):
	response = requests.get('http://localhost:%d/downloads?get_peers=1&get_pieces=1' % api_port)
	download_list = response.json().get('downloads')
	return download_list

def subscribe_channel(api_port, channel_id, subscribe):
	if subscribe:
		response = requests.put	('http://localhost:%d/channels/subscribed/%s' % (api_port, channel_id))
	else:
		response = requests.delete('http://localhost:%d/channels/subscribed/%s' % (api_port, channel_id))
	status = response.status_code
	return status

def start_download(api_port, info_hash, name, anon_hops, safe_seeding, destination):
	download_uri = ('magnet:?xt=urn:btih:%s&dn=%s' % (info_hash, name)).encode('utf-8')
	response = requests.put('http://localhost:%d/downloads' % api_port, 'anon_hops=%d&safe_seeding=%d&destination=%s&uri=%s' % 
		(anon_hops, safe_seeding, destination, download_uri))
	return response

def resume_download(api_port, info_hash):
	response = requests.patch('http://localhost:%d/downloads/%s' % (api_port, info_hash), 'state=resume')
	return response

def stop_download(api_port, info_hash):
	response = requests.patch('http://localhost:%d/downloads/%s' % (api_port, info_hash), 'state=stop')
	return response

def save_settings(api_port, settings_data):
	import xbmc
	response = requests.post('http://localhost:%d/settings' % api_port, settings_data)
	xbmc.log(str(response.json().get('modified')))
	return response

def load_settings(api_port):
	response = requests.get('http://localhost:%d/settings' % api_port)
	settings = response.json().get('settings')
	return settings

def request_search(api_port, keyword):
	response = requests.get('http://localhost:%d/search?q=%s' % (api_port, keyword))
	return response