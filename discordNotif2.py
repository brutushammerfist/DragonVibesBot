from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        
        print(self.path)
        #self.end_headers()
        
        if (query_components["hub.challenge"]) != None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(query_components["hub.challenge"].encode("UTF-8"))
            self.wfile.close()
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(("OK").encode("UTF-8"))
            self.wfile.close()
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode("UTF-8")
        body = json.loads(body)
        print(body)
        
httpd = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)

httpd.serve_forever()