# ****************************************************
# * This file is part of the Cinema Player scripts
# *
# * It is provided as is unter the
# * GNU GENERAL PUBLIC LICENSE Version 3
# *
# * @author	  Thomas Winkler <thomas.winkler__at__iggmp.net>
# * @Version   1.0
# * @copyright 2018
# ****************************************************

from mplayer_control.player import Player
import time
import atexit

class Video:

	player = None
	lasttime = 0
	
	# create video with parameters
	def __init__(self, file, position, crop):

		self.player = Player(debug=False)
		self.file = file

		# set options
		self.player.add_command_option(option='-osdlevel', value='0')
		self.player.add_command_option(option='-nolirc')
		#self.player.add_command_option(option='-rootwin')
		self.player.add_command_option(option='-fs')
		self.player.add_command_option(option='-geometry', value=position)
		self.player.add_command_option(option='-vf', value='crop='+crop)

		# create player process
		self.player.create_new_process()


	# start video
	def play (self):
		if isinstance(self.player, Player):
			self.player.loadfile('"'+self.file+'"')


	# pause / resume video
	def pause (self):
		if isinstance(self.player, Player):
			self.player.pause()


	# stop video
	def stop (self):
		if isinstance(self.player, Player):
			self.player.stop()


	# seek position
	def seek (self, pos):
		return self.player.seek(float(pos), 1)


	def volume (self, volume):
		return self.player.volume(int(volume))


	def get_volume (self):
		return self.player.properties.volume


	# get length of video in seconds
	def length(self):
		if isinstance(self.player, Player):
			return self.player.get_time_length()


	# gete play position in seconds
	def get_time_pos(self):
		if isinstance(self.player, Player):

			self.lasttime = self.player.properties.time_pos
			return self.player.properties.time_pos


	# get play position as percentage (0-100)
	def get_percent_pos(self):
		if isinstance(self.player, Player):

			self.lasttime = self.player.properties.time_pos
			return self.player.properties.percent_pos


	# get file name
	def get_file_name(self):
		if isinstance(self.player, Player):
			# if hasattr(self.player, "properties"):

			# filename unavailabe -> kill player process
			if (self.player.properties.filename == 'PROPERTY_UNAVAILABLE'):
				self.quit()

			else:
				return self.file
#				return self.player.properties.filename


	# get player status
	def status(self):

		if not isinstance(self.player, Player):
			return "stop"


		if self.lasttime == self.player.properties.time_pos:
			return "pause"
		else:
			return "play"


	# quit player
	def quit(self):
		if isinstance(self.player, Player):
			self.player.quit()
			self.player.kill_process()

		self.player = None
