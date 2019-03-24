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

from video import Video
import time, sys, ast
# run a video on two screens


class Play:

	screens = {}

	def __init__(self, file, config):

		self.master = config.get('player', 'master')
		screen_config = dict(config.items('screens'))

		# initialize screens
		for scr in screen_config:

			scr_cfg = ast.literal_eval(screen_config[scr])

			position = scr_cfg['position']
			crop = scr_cfg['crop']

			self.screens[scr] = Video(file, position, crop)

		# position and crop parameters
		# position = x:y
		# crop = w:h:x:y
		# position = "0:0"
		# crop = "1920:1080:0:0"
		# self.upper_video = Video(file, position, crop)

		# time.sleep(60)
		# position = "1920:0"
		# crop = "1920:1080:0:1080"
		# self.lower_video = Video(file, position, crop)
		pass

	def __del__(self):

		self.screens = {}

	def play(self):

		for screen in self.screens:
			self.screens[screen].play()

	def pause(self):
		for screen in self.screens:
			self.screens[screen].pause()

	def stop(self):

		for screen in self.screens:
			self.screens[screen].stop()

	def seek(self, pos):
		for screen in self.screens:
			self.screens[screen].seek(pos)

	def volume(self, volume):
		return self.screens[self.master].volume(volume)

	def get_volume(self):
		return self.screens[self.master].get_volume()

	def quit(self):
		for screen in self.screens:
			self.screens[screen].quit()

	def status(self):
		return self.screens[self.master].status()

	def position(self):
		return self.screens[self.master].get_percent_pos()

	def time(self):
		return self.screens[self.master].get_time_pos()

	def length(self):
		return self.screens[self.master].get_length()

	def get_file_name(self):
		return self.screens[self.master].get_file_name()
