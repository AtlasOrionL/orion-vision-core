#!/usr/bin/env python3
"""
🚀 Basic Orion API Server
Minimal HTTP server for VS Code Extension
"""

import http.server
import socketserver
import json
import time

class BasicHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "service": "Orion Vision Core API",
                "version": "1.0.0",
                "timestamp": time.time()
            }
            
            self.wfile.write(json.dumps(response).encode())
            print(f"✅ Health check OK")
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/ai/completion':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "result": "AI Response from Orion Vision Core",
                    "confidence": 0.85,
                    "suggestions": ["Test suggestion"],
                    "metadata": {"model": "orion-v1"}
                }
                
                self.wfile.write(json.dumps(response).encode())
                print(f"🤖 AI completion OK")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                print(f"❌ Error: {e}")
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    print(f"🚀 Starting server on port {PORT}")
    print(f"🔗 Health: http://localhost:{PORT}/api/health")
    
    with socketserver.TCPServer(("", PORT), BasicHandler) as httpd:
        httpd.serve_forever()
