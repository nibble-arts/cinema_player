# ****************************************************
# * The class geathers data as key->value pairs
# *		can render it in diferent formats
# *
# * It is provided as is unter the
# * GNU GENERAL PUBLIC LICENSE Version 3
# *
# * @author   Thomas Winkler <thomas.winkler__at__iggmp.net>
# * @Version   1.0
# * @copyright 2018
# ****************************************************


import json


class Response:

	res = {}
	output_format = ''


	# create result object
	def __init__(self):
		self.reset()
		self.output_format = "json"
		pass


	# reset response
	def reset(self):
		self.res = {}
		self.output_format = ''


	# set result value
	def set(self, type, value):

		# append Response object as type
		if isinstance(value, Response):
			self.res[type] = value.get()

		else:
			self.res[type] = value


	def get(self, type = False):

		if not type:
			return self.res

		else:
			return self.res[type];


	# get the format
	#  if output_format != '', set value and return it
	def format(self, output_format=''):

		if output_format:
			self.output_format = output_format

		return self.output_format


	# render result to format
	def render(self):

		output = json.dumps(self.res) #, ensure_ascii=False, encoding='utf8'

		return output