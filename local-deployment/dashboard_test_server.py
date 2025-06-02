#!/usr/bin/env python3
"""
Simple test server for Orion Vision Core dashboard testing
"""

import json
import random
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Mock data
mock_agents = [
    {
        "agent_id": "comm_agent_1",
        "config": {
            "name": "Communication Agent 1",
            "description": "Handles inter-agent communication"
        },
        "status": "running",
        "metrics": {
            "uptime": 3600,
            "messages_processed": 150,
            "llm_calls": 25
        }
    },
    {
        "agent_id": "task_orchestrator",
        "config": {
            "name": "Task Orchestrator",
            "description": "Manages and distributes tasks"
        },
        "status": "running",
        "metrics": {
            "uptime": 3500,
            "messages_processed": 89,
            "llm_calls": 12
        }
    }
]

class OrionTestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if path == '/':
            response = {"message": "Orion Test Server Running", "status": "ok"}
        elif path == '/agents':
            # Simulate some variation in metrics
            for agent in mock_agents:
                agent["metrics"]["messages_processed"] += random.randint(0, 5)
                agent["metrics"]["llm_calls"] += random.randint(0, 2)
                agent["metrics"]["uptime"] += 5
            response = mock_agents
        elif path.startswith('/agents/') and path.endswith('/status'):
            agent_id = path.split('/')[2]
            agent = next((a for a in mock_agents if a["agent_id"] == agent_id), None)
            response = agent if agent else {"error": "Agent not found"}
        elif path == '/llm/test':
            responses = [
                "Hello! I'm working perfectly and ready to assist with any tasks.",
                "System status: All components operational. LLM integration successful.",
                "Greetings from the Orion Vision Core! All systems are functioning optimally.",
                "LLM test successful. Ready for advanced agent communication protocols."
            ]
            response = {
                "status": "success",
                "llm_response": random.choice(responses),
                "timestamp": datetime.now().isoformat()
            }
        elif path == '/health':
            response = {"status": "healthy", "timestamp": datetime.now().isoformat()}
        else:
            response = {"error": "Not found"}

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if path.startswith('/agents/') and path.endswith('/message'):
            agent_id = path.split('/')[2]
            response = {
                "status": "message_sent",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            response = {"error": "Not found"}

        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server():
    server = HTTPServer(('localhost', 8003), OrionTestHandler)
    print("🚀 Starting Orion Test Server...")
    print("📊 Dashboard: http://localhost:8080/web_dashboard.html")
    print("🔗 API: http://localhost:8003")
    print("✅ Server running on port 8003")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
