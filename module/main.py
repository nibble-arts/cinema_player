from callbackserver import CallBackServer
from api import Api
import ConfigParser


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


def main():

	config = ConfigParser.ConfigParser()
	config.read('config/server.cfg')

	# get settings from the configuration file
	if config:

		api_cfg = dict(config.items('api'))
		host_cfg = dict(config.items('server'))

		# create api
		# apiName: http path to api
		# httpRoot: relative path to html files
		api_class = Api(api_cfg)

		# create web server
		# host_name, port, callback
		server = CallBackServer(host_cfg["host"], int(host_cfg["port"]), api_class)
		server.start()

	else:
		print("config/config.cfg not found")
		print("abort Cinema Player")
