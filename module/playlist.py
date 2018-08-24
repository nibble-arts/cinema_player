import ConfigParser, os, time
from os.path import isfile
from response import Response


class Playlist:

	playlist = None
	filename = ""

	def __init__(self):

		self.playlist = ConfigParser.ConfigParser()
		self.playlist.add_section("list")
		self.playlist.add_section("options")

		self.playlist.set("options", "autoplay", "false")
		self.playlist.set("options", "stop_at_end", "false")
		self.playlist.set("options", "screensaver", "")


	# set/get playlist name
	def name(self, filename):

		if filename:
			self.filename = filename

		else:
			return self.filename


	# load playlist file
	def load(self, file = False):

		# use current file
		if not file:
			file = self.filename

		# file exists -> load
		if os.path.isfile(file):

			self.filename = file

			self.__init__()
			self.playlist.read(file)


	# write playlist to pass or current path
	def write(self, path = False):

		# write to new file position
		if not path:
			path = self.filename

		self.playlist.write(path)


	# get option from ṕlaylist
	def option(self, option_name):

		for opt in self.playlist.items("options"):

			if opt[0] == option_name:
				return opt[1]


		return False


	# list playlist content
	def list(self):

		response = Response()

		# sort by number
		playlist = self.playlist.items("list")

		response.set("playlist", [b for a,b in playlist]) #sorted((tup[0], tup) for tup in playlist)]
		response.set("file", self.filename)
		response.set("cmd", "playlist")

		response.set("autoplay", self.playlist.get("options", "autoplay"))
		response.set("stop_at_end", self.playlist.get("options", "stop_at_end"))
		response.set("screensaver", self.playlist.get("options", "screensaver"))
		
		return response


	# add/append video to playlist
	def add(self, file, pos = False):

		# check for file 
		if os.path.isfile(file):
			# add at position
			if pos != False:

				pass

			# append entry
			else:

				nr = time.time()
				print str(nr)
				self.playlist.set("list", str(nr), file)

		return self.list()


	# remove video from playlist by id
	def remove(self, pos):

		self.playlist.remove_option("list", str(pos))

		for video in reversed(self.playlist.items("list")):

			if int(pos) > int(video[0]):

				self.playlist.set("list", str(int(video[0]) - 1), video[1])

		# write altered list
		self.write()

		return self.list()