#!/usr/bin/env python3
"""
🚀 Simple Orion Vision Core API Server
Basic HTTP server with API endpoints for VS Code Extension
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime
import time

class OrionAPIHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/health':
            self.send_health_response()
        elif self.path == '/api/status':
            self.send_status_response()
        elif self.path == '/api/extension/info':
            self.send_extension_info()
        else:
            self.send_404()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/ai/completion':
            self.handle_ai_completion()
        else:
            self.send_404()
    
    def send_health_response(self):
        """Send health check response"""
        response = {
            "status": "healthy",
            "service": "Orion Vision Core API",
            "version": "1.0.0",
            "timestamp": time.time()
        }
        self.send_json_response(response)
        print(f"✅ Health check requested at {datetime.now()}")
    
    def send_status_response(self):
        """Send system status response"""
        response = {
            "system": "Orion Vision Core",
            "status": "operational",
            "modules": {
                "ai_provider": "active",
                "deployment_manager": "active",
                "webview_provider": "active"
            },
            "uptime": time.time(),
            "version": "8.8.0"
        }
        self.send_json_response(response)
        print(f"📊 Status requested at {datetime.now()}")
    
    def send_extension_info(self):
        """Send extension info response"""
        response = {
            "extension": "Orion Vision Core VS Code Extension",
            "version": "1.0.0",
            "features": [
                "AI-powered code completion",
                "Smart code search", 
                "Deployment management",
                "Real-time monitoring"
            ],
            "endpoints": [
                "/api/health",
                "/api/ai/completion",
                "/api/status",
                "/api/extension/info"
            ]
        }
        self.send_json_response(response)
        print(f"ℹ️  Extension info requested at {datetime.now()}")
    
    def handle_ai_completion(self):
        """Handle AI completion requests"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            prompt = request_data.get('prompt', '')
            request_type = request_data.get('type', 'completion')
            
            print(f"🤖 AI Request: {request_type} - {prompt[:50]}...")
            
            # Generate response based on type
            if request_type == "completion":
                result = f"AI Code Completion for: {prompt}\n\n// Generated by Orion Vision Core\n// This is a simulated response"
            elif request_type == "search":
                result = f"Smart Search Results for: {prompt}\n\n1. Found relevant code patterns\n2. Suggested improvements\n3. Related documentation"
            elif request_type == "explanation":
                result = f"Code Explanation for: {prompt}\n\nThis code appears to be implementing functionality related to your query."
            elif request_type == "refactor":
                result = f"Refactoring Suggestions for: {prompt}\n\n1. Extract common functionality\n2. Improve naming conventions\n3. Add error handling"
            elif request_type == "debug":
                result = f"Debug Analysis for: {prompt}\n\n1. Check variable initialization\n2. Verify function parameters\n3. Add logging statements"
            else:
                result = f"AI Response for: {prompt}\n\nOrion Vision Core is processing your request..."
            
            response = {
                "result": result,
                "confidence": 0.85,
                "suggestions": [
                    "Consider adding error handling",
                    "Add unit tests for this functionality", 
                    "Document the API endpoints"
                ],
                "metadata": {
                    "processing_time": 0.5,
                    "model": "orion-vision-core-v1",
                    "request_type": request_type
                }
            }
            
            self.send_json_response(response)
            print(f"✅ AI Response generated successfully")
            
        except Exception as e:
            error_response = {
                "error": f"AI completion failed: {str(e)}",
                "status": "error"
            }
            self.send_json_response(error_response, status=500)
            print(f"❌ AI completion error: {str(e)}")
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        json_data = json.dumps(data, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_404(self):
        """Send 404 response"""
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"error": "Endpoint not found", "status": 404}
        json_data = json.dumps(response)
        self.wfile.write(json_data.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    
    print("🚀 Starting Orion Vision Core API Server...")
    print(f"📡 Server will be available at: http://localhost:{PORT}")
    print(f"🔗 Health check: http://localhost:{PORT}/api/health")
    print(f"🤖 AI completion: http://localhost:{PORT}/api/ai/completion")
    print(f"📊 System status: http://localhost:{PORT}/api/status")
    print(f"ℹ️  Extension info: http://localhost:{PORT}/api/extension/info")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    with socketserver.TCPServer(("", PORT), OrionAPIHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            httpd.shutdown()
