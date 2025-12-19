from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time

class MockGumroadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Simple mock logic
        response = {}
        if "license_key=TEST-PRO-KEY" in post_data:
            response = {
                "success": True,
                "uses": 1,
                "purchase": {
                    "email": "test@example.com",
                    "created_at": "2023-01-01"
                }
            }
        else:
            response = {
                "success": False,
                "message": "Invalid license"
            }
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_mock_server(port=8000):
    server = HTTPServer(('localhost', port), MockGumroadHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server
