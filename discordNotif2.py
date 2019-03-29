from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        content_length = int(self.headers['Content-Length'])
        get_data = self.rfile.read(content_length)
        
        print(get_data)
        
        if(get_data["hub.challenge"]) != None:
            self.send_response(200)
            self.wfile.write(get_data["hub.challenge"])
        else:
            self.send_response(200)
            self.wfile.write("OK")
        
    #def do_POST(self):
        
        
httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)

httpd.serve_forever()