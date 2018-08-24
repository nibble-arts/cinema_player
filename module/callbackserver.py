import time, os, sys, socket, fcntl, struct
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

# The ApiServer class provides a simple http server with access to an
#   api or html pages
#
# It is licenced under the GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#
# @author       Thomas Winkler
# @version      1.0
# @copyright    2018

#==========================================================
# create a http handler

class HttpHandler(BaseHTTPRequestHandler):


    def do_HEAD(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()


    def do_GET(self):

        response = self.server.callback.get(self.path)

        self.send_response(response["code"])
        self.send_header("Content-type", response["content-type"])
        self.end_headers()

        self.wfile.write(response["response"])


#==========================================================
# A http server using a callback class for GET requests

class CallbackHttpServer(HTTPServer):

    def __init__(self, host, RequestHandlerClass, callback):

        HTTPServer.__init__(self, host, RequestHandlerClass, bind_and_activate=True)
        self.callback = callback


#==========================================================
# The server main class
#   Call with the server_name, server_port and a callback class
#
#   The callback class has to have a get() method, which is called at eatch get/post access

class CallBackServer:

    def __init__(self, server_name, port, callback):

        self.server_name = server_name
        self.port = port
        self.callback = callback

        self.source = "http://" + self.server_name# + ":" + str(self.port)


    # start the web server
    # terminate with keyboard interrupt
    def start(self):

        print "Wait for network connection"
        self.wait_for_internet_connection()

#        print self.get_ip_address('lo')
#        print self.get_ip_address('eth0')

        server = CallbackHttpServer((self.server_name, self.port), HttpHandler, self.callback)

        print time.asctime(), "Server Starts - %s:%s" % (self.server_name, self.port)
        try:
            server.serve_forever()

        except KeyboardInterrupt:
            pass

        server.server_close()
        print time.asctime(), "Server Stops - %s:%s" % (self.server_name, self.port)



    # wait for ethernet connection
    def wait_for_internet_connection(self):

        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind((self.server_name,self.port))
                s.close()
                return

            except:
                pass
