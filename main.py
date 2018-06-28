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

import time, os, sys
from os import listdir
from os.path import isfile, isdir, join
import BaseHTTPServer
import urlparse
from urlparse import parse_qs
urlparse.parse_qs = parse_qs
import json
import posixpath
import mimetypes


from module.play import Play 

#=========================================================
# start http server
#
# video play API
#=========================================================


HOST_NAME = 'localhost' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8000 # Maybe set this to 9000.
VIDEO_PATH = '/home/tom/Videos/'
HTTP_ROOT = 'html/'


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    _player = None
    _current_dir = VIDEO_PATH

    def do_HEAD(s):

        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):

        def _get_files(dir):
            return [f for f in listdir(MyHandler._current_dir) if (isfile(join(MyHandler._current_dir, f)) and not f.startswith("."))]

        def _get_dirs(dir):
            return [f for f in listdir(MyHandler._current_dir) if (isdir(join(MyHandler._current_dir, f)) and not f.startswith("."))]


        # print "GET"

        # get path
        uri = s.path

        # remove leading /
        if (uri.startswith("/")):
            uri = uri[1:]

        query = {}
        path = uri.split("?")

        # has query -> parse query
        if (len(path) > 1):
            query = urlparse.parse_qs(path[1])

        # get path
        path = path[0]


        #====================================================
        # api access
        # api?cmd=...&file=...
        if (len(query) and path == "api"):

            """Respond to a GET request."""
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()

            response = {}


            #==============================
            # file found
            if (query.get("file")):
                filepath = MyHandler._current_dir + query.get("file")[0]
            else:
                filepath = ""


            #====================================================
            # global commands

            #==============================
            # cmd found
            if (query.get("cmd")):

                cmd = query.get("cmd")[0]


                #==============================
                # list directory
                #==============================
                if (cmd == "list"):
                    response["dir"] = MyHandler._current_dir
                    # directory = os.listdir(MyHandler._current_dir)

                    files = _get_files(MyHandler._current_dir)
                    dirs = _get_dirs(MyHandler._current_dir)

                    response["files"] = files
                    response["dirs"] = dirs


                #==============================
                # change directory
                #==============================
                if (cmd == "cd"):

                    response["cmd"] = cmd
                    newDir = MyHandler._current_dir

                    if (not MyHandler._current_dir.endswith("/")):
                        newDir = newDir + "/"

                    MyHandler._current_dir = newDir + query.get("file")[0] + "/"

                    response["dir"] = MyHandler._current_dir
                    response["dirs"] = _get_dirs(MyHandler._current_dir)
                    response["files"] = _get_files(MyHandler._current_dir)


                #==============================
                # go directory up
                #==============================
                if (cmd == "up"):

                    newDir = MyHandler._current_dir

                    if (MyHandler._current_dir.endswith("/")):
                        newDir = MyHandler._current_dir[:-1]

                    MyHandler._current_dir = '/'.join(newDir.split("/")[:-1])+'/'

                    response["cmd"] = cmd
                    response["dir"] = MyHandler._current_dir
                    response["dirs"] = _get_dirs(MyHandler._current_dir)
                    response["files"] = _get_files(MyHandler._current_dir)
                    pass


                # #==============================
                # # status
                # #==============================
                if (cmd == "status"):
                    if isinstance(MyHandler._player, Play):
                        response["status"] = MyHandler._player.status()
                    else:
                        response["status"] = "stop"

                    response["cmd"] = "status"


                #==============================
                # start playback
                #==============================
                if (os.path.isfile(filepath)):


                    # start playback if file exists
                    if (cmd == "play"):

                        # stop existing player
                        if isinstance(MyHandler._player, Play):
                            MyHandler._player.quit()
                            MyHandler._player = None;


                        MyHandler._player = Play(filepath)
                        MyHandler._player.play()

                        response["cmd"] = "play"
                        response["file"] = MyHandler._player.get_file_name()


                #====================================================
                # commands to active player

                # player is active
                if isinstance(MyHandler._player, Play):

                    
                    # add playing filename
                    response["file"] = MyHandler._player.get_file_name()

                    #==============================
                    # toggle pause/play 
                    #==============================
                    if (cmd == "pause"):
                        MyHandler._player.pause()
                        response["cmd"] = "pause"

                    #==============================
                    # stop playback
                    #==============================
                    if (cmd == "stop"):
                        MyHandler._player.quit()
                        MyHandler._player = None;
                        response["cmd"] = "stop"

                    #==============================
                    # get position
                    #==============================
                    if (cmd == "position"):

                        response["cmd"] = "position"
                        response["time"] = MyHandler._player.position()


                # no active player
                else:
                    response["error"] = "no player"
                    MyHandler._player = None


                #================
                # print to console
#                print "cmd: "+cmd+" "

                # for key in response:
                #     if (key != "cmd"):

                #         if (type(response[key]) is str):
                #             print " "+key+"="+response[key]
                #             pass
                #         else:
                #             if (not response[key] == None):
                #                 print " "+key+"="+str.join(", ",response[key])
                #             pass


            s.wfile.write(json.dumps(response))
            pass


        #====================================================
        # page access
        else:

            # no path, try index.html
            if (path == ""):
                path = "index.html"

            # add http base to path
            http_path = HTTP_ROOT+path

            # get content type
            ctype = s.guess_type(path)

            # look for file and render
            if (os.path.isfile(http_path)):

                """Return index.html"""
                s.send_response(200)
                s.send_header("Content-type", ctype)
                s.end_headers()

                # copy html file to output
                html = open(http_path, "rb")
                s.wfile.write(html.read())
                html.close()
                pass

            # no page found -> 404
            else:

                """Return 404 page"""
                s.send_response(404)
                s.send_header("Content-type", "text/html")
                s.end_headers()

                # copy html file to output
                html = open(HTTP_ROOT + "404.html", "rb")
                s.wfile.write(html.read())
                html.close()
                pass




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





if __name__ == '__main__':

    server_class = BaseHTTPServer.HTTPServer

    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()

    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)