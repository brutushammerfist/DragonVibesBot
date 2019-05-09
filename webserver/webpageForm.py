import http.server
import cgi
import base64
import json
import asyncio
import os
import threading
from urllib.parse import urlparse, parse_qs
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

"""
    Based upon work at https://gist.github.com/dragermrb/108158f5a284b5fba806
"""

class CustomServerHandler(http.server.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        #self.send_header('Content-type', 'application/json')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header(
            'WWW-Authenticate', 'Basic realm="Demo Realm"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        key = self.server.get_auth_key()

        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') == None:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'No auth header received'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            #self.send_response(200)
            #self.send_header('Content-type', 'text/html')
            #self.end_headers()

            getvars = self._parse_GET()

            base_path = urlparse(self.path).path
            print(base_path)
            if base_path == '/':
                with open("index.html", "r") as index:
                    response = index.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes(response, 'utf-8'))
            elif base_path.endswith(".mp3"):
                base_path = base_path[1:]
                print(base_path)
                if os.stat(base_path).st_size is not 0:
                    file = open(os.curdir + os.sep + base_path, "rb")
                    #file = open("." + base_path)
                    length = os.stat(base_path).st_size
                    data = file.read()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'audio/mpeg')
                    self.send_header('Content-Length', length)
                    self.end_headers()
                    self.wfile.write(data)
                    file.close()
            
        else:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'Invalid credentials'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

    def do_POST(self):
        key = self.server.get_auth_key()

        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') == None:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'No auth header received'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            postvars = self._parse_POST()
            getvars = self._parse_GET()

            response = {
                'path': self.path,
                'get_vars': str(getvars),
                'get_vars': str(postvars)
            }

            base_path = urlparse(self.path).path
            if base_path == '/path1':
                # Do some work
                pass
            elif base_path == '/path2':
                # Do some work
                pass

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        else:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'Invalid credentials'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        response = {
            'path': self.path,
            'get_vars': str(getvars),
            'get_vars': str(postvars)
        }

        self.wfile.write(bytes(json.dumps(response), 'utf-8'))

    def _parse_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(
                self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        return postvars

    def _parse_GET(self):
        getvars = parse_qs(urlparse(self.path).query)

        return getvars

class CustomHTTPServer(http.server.HTTPServer):
    key = ''

    def __init__(self, address, handlerClass=CustomServerHandler):
        super().__init__(address, handlerClass)

    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

    def get_auth_key(self):
        return self.key
        
"""
    Based upon work at https://github.com/dpallot/simple-websocket-server
"""

class SimpleEcho(WebSocket):
    def handleMessage(self):
        self.sendMessage(self.data)
        print(self.data)
        
    def handleConnected(self):
        print(self.address, 'connected')
        
    def handleClose(self):
        print(self.address, 'closed')
        
    def printBruh(self):
        print("Bruh")

if __name__ == '__main__':
    server = CustomHTTPServer(('0.0.0.0', 8080))
    
    secretsFile = open("secrets.json", "r")
    secrets = json.load(secretsFile)
    secretsFile.close()
    
    """def socketMain():
        socketServer = SimpleWebSocketServer('0.0.0.0', 8765, SimpleEcho)
        socketServer.serveforever()"""
    
    socketServer = SimpleWebSocketServer('0.0.0.0', 8765, SimpleEcho)
    
    socketThread = threading.Thread(target=socketServer.serveforever)
    socketThread.start()
    
    testThread = threading.Thread(target=socketServer.printBruh)
    testThread.start()
    
    server.set_auth('DracoAsier', secrets['dracoWebPass'])
    server.set_auth('BrutusHammerfist', secrets['brutWebPass'])
    #server.serve_forever()
    
    serverThread = threading.Thread(target=server.serve_forever())
    serverThread.start()