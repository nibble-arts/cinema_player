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

from module.video import Video
import time
# run a video on two screens

class Play:

	def __init__(self, file):

		# position and crop parameters
		# position = x:y
		# crop = w:h:x:y
		position = "0:0"
		crop = "1920:1080:0:0"
		self.upper_video = Video(file, position, crop)

		# time.sleep(60)
#		position = "1920:0"
#		crop = "1920:1080:0:1080"
#		self.lower_video = Video(file, position, crop)
		pass

	def __del__(self):
		self.upper_video = None


	def play(self):
		self.upper_video.play()
#		self.lower_video.play()
		pass

	def pause(self):
		self.upper_video.pause()
#		self.lower_video.pause()
		pass

	def stop(self):
		self.upper_video.stop()
#		self.lower_video.quit()
		pass

	def quit(self):
		self.upper_video.quit()
#		self.lower_video.quit()
		pass

	def position(self):
		return self.upper_video.get_percent_pos()

	def get_file_name(self):
		return self.upper_video.get_file_name()