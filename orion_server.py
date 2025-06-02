#!/usr/bin/env python3
"""
Orion Vision Core Server Startup
Quick server for VS Code extension
"""

import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import time

# Add src to path
sys.path.insert(0, 'src')

class OrionHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'service': 'Orion Vision Core',
                'timestamp': time.time(),
                'version': '1.0.0'
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'ai_assistant': 'available',
                'code_completion': 'available',
                'smart_search': 'available',
                'providers': {
                    'ollama': 'checking...',
                    'openai': 'configured',
                    'claude': 'configured'
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'message': 'Orion Vision Core API',
                'endpoint': self.path,
                'method': 'GET',
                'status': 'success'
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'message': 'POST request received',
            'endpoint': self.path,
            'data_length': content_length,
            'status': 'success'
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def start_server(port=8000):
    """Start Orion server"""
    try:
        server = HTTPServer(('localhost', port), OrionHandler)
        print(f'🚀 Orion Vision Core Server started on http://localhost:{port}')
        print(f'📊 Health check: http://localhost:{port}/health')
        print(f'🔧 API status: http://localhost:{port}/api/status')
        print('Press Ctrl+C to stop')
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print('\n👋 Server stopped')
    except Exception as e:
        print(f'❌ Server error: {str(e)}')

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_server(port)
