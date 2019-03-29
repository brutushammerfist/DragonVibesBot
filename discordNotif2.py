from http.server import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        
        self.end_headers()
        
        if (query_components["hub.challenge"]) != None:
            self.send_response(200)
            self.wfile.write(query_components["hub.challenge"])
        else:
            self.send_response(200)
            self.wfile.write("OK")
        
    #def do_POST(self):
        
        
httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)

httpd.serve_forever()