import time, os, sys
import urlparse
import mimetypes
import posixpath
from urlparse import parse_qs
urlparse.parse_qs = parse_qs
from os import listdir
from os.path import isfile, isdir, join

import ConfigParser

import json

from play import Play 
from response import Response
from playlist import Playlist

# ****************************************************
# * This file is part of the Cinema Player scripts
# *
# * It is provided as is unter the
# * GNU GENERAL PUBLIC LICENSE Version 3
# *
# * @author   Thomas Winkler <thomas.winkler__at__iggmp.net>
# * @Version   1.0
# * @copyright 2018
# ****************************************************


# API class to access data from ajax calls or act as an simple webserver.
#
#   call main() with the http url
#       If the http path matches the given api path, the api method is called
#       in all other cases the request is used to access the html pages in the defined subdirectory

class Api:

    api_name = ""
    html_root = ""
    path = ""
    query = ""
    basePath = ""

    current_dir = None
    response = None
    player = None

    player_cfg = None
    playlist = None

    screensaver = False
    screensaver_file = ""
    enable_screensaver = False

    video_types = ["mp4", "mpeg", "mov"]
    pl_types = ["playlist"]


    # create an api/html object
    #    options{"url": calling http_url, "api_name": page name for api calls, "html_root": root path for html pages}
    def __init__(self, options):

        self.player_cfg = ConfigParser.ConfigParser()
        self.player_cfg.read('config/player.cfg')

        self.screensaver_file = self.player_cfg.get("player", "screensaver")
        self.enable_screensaver = self.player_cfg.getboolean("player", "enable_screensaver")


       # load playlist
        self.playlist = Playlist()
#        self.playlist.name(options["playlist"])
#        self.playlist.load()


        # get player settings from the configuration file
        if not self.player_cfg:
            print "no player configuration found"
            sys.exit()


        # init variables
        self.basePath = os.path.dirname("..")

        self.api_name = options["api_name"]
        self.html_root = options["html_root"]
        self.current_dir = options["base_dir"]


        # create response object
        self.response = Response()


    #==========================================================
    # write player configuration file
    def writeplayer(self):

        with open('config/player.cfg', 'wb') as configfile:
            print "write config"
            self.player_cfg.write(configfile)


    #==========================================================
    # call api or html pages, depending on the page path
    def get(self, url):

        self.__create_query(url)

        # redirect to api interface
        if self.path == self.api_name:
            return self.api()

        # redirect to html pages
        else:
            return self.html()


    #==========================================================
    # call api or html pages, depending on the page path
    def post(self, url):

        self.__create_query(url)

        # redirect to api interface
        if self.path == self.api_name:
            return self.api()

        # redirect to html pages
        else:
            return self.html()



    #==========================================================
    # check for valid video formats
    def file_type(self, file, types):

        if os.path.splitext(file)[1][1:] in types:
            return True

        return False


    #==========================================================
    # get video file information from config file
    def read_info(self, file):

        response = Response()
        audio = Response()
        video = Response()

        response.set("file", file)

        # add video file cfg data
        filename = os.path.splitext(file)[0]

        if os.path.isfile(filename + ".cfg"):

            self.info = ConfigParser.ConfigParser()
            self.info.read(filename + ".cfg")

            # collect video data
            for info in self.info.items("video"):
                video.set(info[0], info[1])

            #collect audio data
            for info in self.info.items("audio"):
                audio.set(info[0], info[1])

            response.set("audio", audio)
            response.set("video", video)

        return response


    def get_files(self, dir, types):
        return [f for f in listdir(self.current_dir) if (isfile(join(self.current_dir, f)) and self.file_type(f, types) == True and not f.startswith("."))]

    def get_dirs(self, dir):
        return [f for f in listdir(self.current_dir) if (isdir(join(self.current_dir, f)) and not f.startswith("."))]





    #==========================================================
    #==========================================================
    # playback control

    # start playback of file
    def play(self, filename):

        # stop existing player
        self.stop()

        # create new player
        self.player = Play(filename, self.player_cfg)
        self.player.play()

        self.response.set("file", filename)


    # stop playback
    def stop(self):

        self.screensaver = False

        if isinstance(self.player, Play):

            self.player.quit()
            self.player = None;

            # call autoplay on stopping
#            self.autoplay()


    # autoplay screensaver or next playlist entry
    def autoplay(self):

        # check for screensaver file
        if not os.path.isfile(self.screensaver_file):
            self.screensaver_file = ""
            self.enable_screensaver = False

 
        # start screensaver if enabled
        if self.screensaver_file and self.enable_screensaver != False:
            self.play(self.screensaver_file)
            self.screensaver = True



    #==========================================================
    #==========================================================
    # call api interface
    def api(self):


        #==============================
        # reset response
        self.response.reset()


        #==============================
        # get file parameter
        if (self.query.get("file")):
            filepath = os.path.join(self.current_dir, self.query.get("file")[0])
        else:
            filepath = ""


        #====================================================
        # COMMANDS
        #
        # filesystem
        #   list:       list current directory
        #   cd:         change directory
        #   up:         move current directory up
        #
        # player/video
        #   status:     get player status
        #   fileinfo:   get video config file informations
        #   writeinfo:  write information to video config file
        #   play:       start playback of file
        #
        # playlist
        #   playlist:   get playlist
        #
        #
        # commands with active player
        #
        #   stop:       stop playback
        #   pause:      pause playback
        #   position:   get playback position
        #====================================================


        #==============================
        # cmd found
        if (self.query.get("cmd")):


            #==============================
            # status and command
            #==============================
            cmd = self.query.get("cmd")[0]
            self.response.set("cmd", cmd)


            # add status to response
            if isinstance(self.player, Play):
                # stop on status stop
                if self.player.status() == "stop":
                    self.stop()

                else:
                    self.response.set("status", str(self.player.status()))

            else:
                self.response.set("status", "stop")


            #==============================
            # list directory
            #==============================
            if (cmd == "list"):

                self.response.set("dirinfo", self.read_file_info())


            #==============================
            # change directory
            #   param: file
            #==============================
            if (cmd == "cd"):

                newDir = self.current_dir

                if (not self.current_dir.endswith("/")):
                    newDir = newDir + "/"

                self.current_dir = newDir + self.query.get("file")[0] + "/"

                self.response.set("dirinfo", self.read_file_info())


            #==============================
            # go directory up
            #==============================
            if (cmd == "up"):

                newDir = self.current_dir

                if (self.current_dir.endswith("/")):
                    newDir = self.current_dir[:-1]

                self.current_dir = '/'.join(newDir.split("/")[:-1])+'/'

                self.response.set("dirinfo", self.read_file_info())


            #==============================
            # get file informations file data
            #==============================
            if (cmd == "fileinfo"):
                self.response.set("fileinfo", self.read_info(filepath))


            #==============================
            # write
            #   param: file, video/audio parameters
            #==============================
            if (cmd == "writeinfo"):

                filename = os.path.splitext(filepath)[0] + ".cfg"

                video_info = ConfigParser.ConfigParser()

                video_info.add_section("video")
                video_info.add_section("audio")

                for val in self.query:
                    keyval = val.split("_")

                    if len(keyval) > 1:
                        video_info.set(keyval[0], keyval[1], self.query.get(val)[0])

                self.info = video_info

                with open(filename, "wb") as configfile:
                    video_info.write(configfile)

                self.response = self.read_info(filepath)


            #==============================
            # set/enable/disable screensaver autoplay
            #==============================
            if (cmd == "set_screensaver"):

                self.player_cfg.set("player", "screensaver", filepath)
                self.player_cfg.set("player", "enable_screensaver", False)

                self.screensaver_file = filepath
                self.enable_screensaver = False
                self.writeplayer()

            if (cmd == "enable_screensaver"):

                self.player_cfg.set("player", "enable_screensaver", True)

                self.enable_screensaver = True
                self.writeplayer()

            if (cmd == "disable_screensaver"):

                self.player_cfg.set("player", "enable_screensaver", False)

                self.enable_screensaver = False
                self.writeplayer()

            scr = Response()

            # add screensaver info
            scr.set("enable_screensaver", self.enable_screensaver)
            scr.set("screensaver", self.screensaver)
            scr.set("screensaver_file", self.screensaver_file)

            self.response.set("screensaver", scr)


            #==============================
            # get playlist
            #   param: none -> return playlist
            #   param: file -> load new playlist
            #==============================
            if (cmd == "playlist"):

                # if filepath: load new playlist
                if filepath:
                    self.playlist.name(filepath)
                    self.playlist.load()

                self.response = self.playlist.list()



            #==============================
            # add to active playlist
            #   param: file -> video filename
            #   param: pos -> position in the playlist
            #          if no position, append to end
            #==============================
            if (cmd == "addtoplaylist"):

                if filepath:

                    # add at position
                    if self.query.get("pos"):
                        self.response = self.playlist.add(filepath, self.query.get("pos")[0])

                    # append
                    else:
                        self.response = self.playlist.add(filepath)


            #==============================
            # removefromplaylist
            #   param: pos -> position of file
            #       to in the playlist to be removed
            #==============================
            if (cmd == "removefromplaylist"):

                self.response = self.playlist.remove(self.query.get("pos")[0])



            #====================================================
            #====================================================
            # start playback
            #====================================================
            #====================================================
            if (os.path.isfile(filepath)):

                # start playback if file exists
                if (cmd == "play"):
                    self.play(filepath)


            #====================================================
            # commands to active player
            #====================================================

            # player is active
            if isinstance(self.player, Play):

                # add playing filename
                self.response.set("file", self.player.get_file_name())
                self.response.set("time", self.player.position())
                self.response.set("volume", self.player.get_volume())

                #==============================
                # toggle pause/play 
                #==============================
                if (cmd == "pause"):
                    self.player.pause()


                #==============================
                # stop playback
                #==============================
                if (cmd == "stop"):
                    self.stop()


                #==============================
                # seek position
                #==============================
                if (cmd == "seek"):
                    self.player.seek(self.query.get("position")[0])


                #==============================
                # set volume
                #==============================
                if (cmd == "volume"):
                    self.player.volume(self.query.get("volume")[0])


            # no active player
            else:
                self.response.set("warning", "no player")
                self.response.set("time", 0)
                self.player = None

                self.autoplay()


        """Respond to a GET request."""

        return ({
            "code": 200,
            "content-type": "application/json",
            "response": self.response.render()
        })




    #==========================================================
    #==========================================================
    # call html pages
    def html(self):

        # no path, try index.html
        if (self.path == ""):
            self.path = "index.html"

        # add http base to path
        http_path = os.path.join(self.basePath, self.html_root)

        # get content type
        ctype = self.guess_type(self.path)

        # look for file and render
        if (os.path.isfile(os.path.join(http_path, self.path))):

            """Return page"""

            # copy html file to output
            html = open(os.path.join(http_path, self.path), "rb")
            response = html.read()
            html.close()

            return ({
                "code": 200,
                "content-type": ctype,
                "response": response
            })


        # no page found -> 404
        else:

            """Return 404 page"""

            # copy html file to output
            html = open(os.path.join(self.basePath, http_path, "404.html"), "rb")
            response = html.read()
            html.close()

            return ({
                "code": 404,
                "content-type": "text/html",
                "response": response
            })


    def __create_query(self, url):

        # remove leading /
        if (url.startswith("/")):
            url = url[1:]

        self.query = {}
        self.path = url.split("?")

        # has self.query -> parse self.query
        if (len(self.path) > 1):
            self.query = urlparse.parse_qs(self.path[1])


        # get path
        self.path = self.path[0]


    def read_file_info(self):

        dirinfo = Response()

        dirinfo.set("dir", self.current_dir)
        dirinfo.set("dirs", self.get_dirs(self.current_dir))
        dirinfo.set("files", self.get_files(self.current_dir, self.video_types))
#        dirinfo.set("playlist", self.playlist.list())
        dirinfo.set("pl_files", self.get_files(self.current_dir, self.pl_types))

        return dirinfo


    def guess_type(s, path):

        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.
        """

        base, ext = posixpath.splitext(path)

        if ext in s.extensions_map:
            return s.extensions_map[ext]

        ext = ext.lower()

        if ext in s.extensions_map:
            return s.extensions_map[ext]

        else:
            return s.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types

    extensions_map = mimetypes.types_map.copy()

    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })