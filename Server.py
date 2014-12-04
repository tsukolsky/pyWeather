from DatabaseProvider import DatabaseProvider
from Communicator import Communicator
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer

DB_PRINT = True
def DEBUG(message):
    if DB_PRINT:
        print "Server: %s"%message
        
class PyWeatherServer():
    PORT = 6969
    def __init__(self):
        self.__handler = None
        self.__httpd = None
        
    def run(self):
        self.__handler = SimpleHTTPRequestHandler
        self.__httpd = TCPServer(("", PyWeatherServer.PORT), self.__handler)
        
        DEBUG("Run - Serving at port %d"%PyWeatherServer.PORT)
        self.__httpd.serve_forever()
        
        
if __name__ == "__main__":
    DEBUG("Creating server")
    server = PyWeatherServer()
    server.run()
