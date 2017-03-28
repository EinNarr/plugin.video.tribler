import os
class VideoPlayer(object):
	def file_select(self, path, files)
		if os.path.isfile(path):
			return path
		largest_name = None
		largest_size = 0
		for file_info in files:
			size = file_info.get('size')
			if size>largest_size:
				largest_name = file_info.get('name')
				largest_size = size
		return path+'/'+name