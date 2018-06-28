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

	# create video with parameters
	def __init__(self, file, position, crop):

		# print "init player"

		self._player = Player(debug=False)
		self.file = file

		# set options
		self._player.add_command_option(option='-nolirc')
		self._player.add_command_option(option='-fs')
		self._player.add_command_option(option='-geometry', value=position)
		self._player.add_command_option(option='-vf', value='crop='+crop)

		# create player process
		self._player.create_new_process()
		pass

	# start video
	def play (self):
		if isinstance(self._player, Player):

			self._player.loadfile(self.file)
			pass

	# pause / resume video
	def pause (self):
		if isinstance(self._player, Player):
			self._player.pause()

	# stop video
	def stop (self):
		if isinstance(self._player, Player):
			self._player.stop()

	# get length of video in seconds
	def length(self):
		if isinstance(self._player, Player):
			return self._player.get_time_length()

	# gete play position in seconds
	def get_time_pos(self):
		if isinstance(self._player, Player):

			self._lasttime = self._player.properties.time_pos
			return self._player.properties.time_pos

	# get play position as percentage (0-100)
	def get_percent_pos(self):
		if isinstance(self._player, Player):

			self._lasttime = self._player.properties.time_pos
			return self._player.properties.percent_pos

	# get file name
	def get_file_name(self):
		if isinstance(self._player, Player):
			# if hasattr(self._player, "properties"):

			# filename unavailabe -> kill player process
			if (self._player.properties.filename == 'PROPERTY_UNAVAILABLE'):
				self.quit()

			else:
				return self._player.properties.filename

	# get player status
	def status(self):
		if not isinstance(self._player, Player):
			return "stop"

		if self._lasttime == self._player.properties.time_pos:
			return "pause"
		else:
			return "play"

	# quit player
	def quit(self):
		if isinstance(self._player, Player):
			self._player.quit()
			self._player.kill_process()

		self._player = None