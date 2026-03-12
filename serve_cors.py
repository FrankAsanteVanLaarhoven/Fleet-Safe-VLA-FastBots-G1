import http.server
import socketserver

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    port = 8080
    with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
        print(f"Serving at port {port} with CORS enabled")
        httpd.serve_forever()
