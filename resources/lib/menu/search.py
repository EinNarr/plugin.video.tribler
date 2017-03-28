import json
import multiprocessing
import os
import random
import sys
import time

import requests

import xbmcplugin
import xbmcgui

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

class Search(object):

	def __init__(self, api_port, keyword, type=None):
		self.api_port = api_port
		self.keyword  = keyword
		self.type = type

		self.file_channel = os.path.join(os.path.dirname(__file__),'channel.result')
		self.file_torrent = os.path.join(os.path.dirname(__file__),'torrent.result')

		(self.results, self.sender) = multiprocessing.Pipe()

	def start_searching(self):
		from resources.lib.module.perform_request import request_search
		from resources.lib.module.utilities import get_string

		self.search_manager_thread = multiprocessing.Process(target=self.search_manager, args = (self, ))
		self.search_manager_thread.start()

		self.results.recv()#blocking, wait for the event channel. discarding the 1st message which is events_start

		request_search(self.api_port, self.keyword)

		dialog_progress = xbmcgui.DialogProgress()
		dialog_progress.create(get_string(33202))

		progress_bar = 0
		result_num = 0
		result_not_change = 0
		results_torrent = []
		results_channel = []

		while not dialog_progress.iscanceled():
			dialog_progress.update(progress_bar, '%d '%len(results_channel)+get_string(33203), '%d '%len(results_torrent)+get_string(33204), get_string(33205))
			time.sleep(0.06)
			if progress_bar < 99:
				progress_bar = progress_bar + random.randint(0, 1)

			while self.results.poll():
				result_not_change = 0
				result_num = result_num + 1
				result = self.results.recv()
				if   result.get('type') == 'search_result_torrent':
					results_torrent.append(result.get('event'))
				elif result.get('type') == 'search_result_channel':
					results_channel.append(result.get('event'))
			else:
				result_not_change = result_not_change + 1

			if result_not_change > 50:
				self.finish_searching()
				break

		while progress_bar <= 100:
			time.sleep(0.006)
			progress_bar = progress_bar + 1
			dialog_progress.update(progress_bar, '%d '%len(results_channel)+get_string(33203), '%d '%len(results_torrent)+get_string(33204), get_string(33205))

		with open(self.file_torrent, "w") as f:
			json.dump(results_torrent, f)
		with open(self.file_channel, "w") as f:
			json.dump(results_channel, f)
			
		dialog_progress.close()

	def channel_results(self):
		with open(self.file_channel, "r") as f:
			results_channel = json.load(f)
		for result in results_channel:
			name = result.get('result').get('name')
			channel_id = result.get('result').get('dispersy_cid')
			self.addDirectoryItem('[channel] '+name, 'open-channel&channel-id=%s&name=%s' % (channel_id, name), 'recommanded.png', 'DefaultMovies.png')
			
		self.endDirectory()

	def torrent_results(self):
		with open(self.file_torrent, "r") as f:
			results_torrent = json.load(f)
		for result in results_torrent:
			name = result.get('result').get('name')
			info_hash = result.get('result').get('infohash')
			self.addDirectoryItem('[%s] '%result.get('result').get('category')+name, 'torrent-action&info-hash=%s&name=%s' % (info_hash, name), 'recommanded.png', 'DefaultMovies.png')

		self.endDirectory()

	def all_results(self):
		with open(self.file_channel, "r") as f:
			results_channel = json.load(f)
		for result in results_channel:
			name = result.get('result').get('name')
			channel_id = result.get('result').get('dispersy_cid')
			self.addDirectoryItem('[channel] '+name, 'open-channel&channel-id=%s&name=%s' % (channel_id, name), 'recommanded.png', 'DefaultMovies.png')

		with open(self.file_torrent, "r") as f:
			results_torrent = json.load(f)
		for result in results_torrent:
			name = result.get('result').get('name')
			info_hash = result.get('result').get('infohash')
			self.addDirectoryItem('[%s] '%result.get('result').get('category')+name, 'torrent-action&info-hash=%s&name=%s' % (info_hash, name), 'recommanded.png', 'DefaultMovies.png')

		self.endDirectory()

	def finish_searching(self):
		self.search_manager_thread.terminate()

	def search_manager(self, parent):
		response = requests.get('http://localhost:%d/events' % self.api_port, stream=True)
		responser_iter = response.iter_lines()
		self.sender.send(json.loads(next(responser_iter)))
		for line in responser_iter:
			line = json.loads(line)
			if self.type:
				if line.get('type') != self.type or line.get('event').get('query') != self.keyword:
					continue
			elif line.get('type') != 'search_result_channel' and line.get('type') != 'search_result_torrent':
				continue
			self.sender.send(line)

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