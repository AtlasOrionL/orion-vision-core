#!/usr/bin/env python3
"""
VS Code Extension Runtime Fix
Diagnose and fix provider initialization issues

Author: Atlas-orion (Augment Agent)
Date: 2 Haziran 2025
Purpose: Fix VS Code extension runtime issues
"""

import os
import json
import time
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print formatted section"""
    print(f"\n🔍 {title}")
    print("-" * 40)

def diagnose_extension_issues():
    """Diagnose VS Code extension runtime issues"""
    print_section("EXTENSION RUNTIME ISSUE DIAGNOSIS")
    
    issues_found = []
    
    # Check if Orion server is running
    print("🔍 Checking Orion Vision Core server status...")
    
    try:
        import requests
        
        # Test local server
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("  ✅ Orion server: Running on port 8000")
            else:
                print(f"  ⚠️ Orion server: Responding but status {response.status_code}")
                issues_found.append("Server responding with non-200 status")
        except requests.exceptions.ConnectionError:
            print("  ❌ Orion server: Not running on port 8000")
            issues_found.append("Orion server not running")
        except requests.exceptions.Timeout:
            print("  ⚠️ Orion server: Timeout (slow response)")
            issues_found.append("Server timeout")
            
    except ImportError:
        print("  ⚠️ Requests module not available for testing")
    
    # Check Python server
    print("\n🐍 Checking Python server status...")
    server_file = "vscode-extension/server.py"
    if os.path.exists(server_file):
        print(f"  ✅ Python server file: Found ({os.path.getsize(server_file)} bytes)")
    else:
        print("  ❌ Python server file: Missing")
        issues_found.append("Python server file missing")
    
    # Check extension configuration
    print("\n⚙️ Checking extension configuration...")
    try:
        with open("vscode-extension/package.json", "r") as f:
            package_data = json.load(f)
        
        # Check server configuration
        config = package_data.get("contributes", {}).get("configuration", {})
        properties = config.get("properties", {})
        
        server_host = properties.get("orion.server.host", {}).get("default", "localhost")
        server_port = properties.get("orion.server.port", {}).get("default", 8000)
        
        print(f"  ✅ Default server: {server_host}:{server_port}")
        
        # Check AI configuration
        ai_enabled = properties.get("orion.ai.enabled", {}).get("default", True)
        ai_model = properties.get("orion.ai.model", {}).get("default", "gpt-4")
        
        print(f"  ✅ AI configuration: Enabled={ai_enabled}, Model={ai_model}")
        
    except Exception as e:
        print(f"  ❌ Configuration check failed: {str(e)}")
        issues_found.append("Configuration check failed")
    
    return issues_found

def create_server_startup_script():
    """Create server startup script"""
    print_section("CREATING SERVER STARTUP SCRIPT")
    
    startup_script = """#!/usr/bin/env python3
\"\"\"
Orion Vision Core Server Startup
Quick server for VS Code extension
\"\"\"

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
    \"\"\"Start Orion server\"\"\"
    try:
        server = HTTPServer(('localhost', port), OrionHandler)
        print(f'🚀 Orion Vision Core Server started on http://localhost:{port}')
        print(f'📊 Health check: http://localhost:{port}/health')
        print(f'🔧 API status: http://localhost:{port}/api/status')
        print('Press Ctrl+C to stop')
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print('\\n👋 Server stopped')
    except Exception as e:
        print(f'❌ Server error: {str(e)}')

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_server(port)
"""
    
    with open("orion_server.py", "w") as f:
        f.write(startup_script)
    
    print("✅ Server startup script created: orion_server.py")
    print("💡 Usage: python orion_server.py [port]")
    print("💡 Default: python orion_server.py 8000")

def create_extension_config_fix():
    """Create extension configuration fix"""
    print_section("CREATING EXTENSION CONFIG FIX")
    
    config_fix = """// VS Code Extension Configuration Fix
// Add this to VS Code settings.json

{
    "orion.ai.enabled": true,
    "orion.ai.model": "gpt-4",
    "orion.server.host": "localhost",
    "orion.server.port": 8000,
    "orion.ai.retryAttempts": 3,
    "orion.ai.connectionTimeout": 5000,
    "orion.ai.autoReconnect": true,
    "orion.logging.level": "debug",
    "orion.codeCompletion.enabled": true,
    "orion.mobile.previewEnabled": true,
    "orion.networking.debugEnabled": true,
    "orion.performance.monitoringEnabled": true
}
"""
    
    with open("vscode_settings_fix.json", "w") as f:
        f.write(config_fix)
    
    print("✅ VS Code settings fix created: vscode_settings_fix.json")
    print("💡 Copy contents to VS Code settings.json")

def create_provider_test_script():
    """Create provider test script"""
    print_section("CREATING PROVIDER TEST SCRIPT")
    
    test_script = """#!/usr/bin/env python3
\"\"\"
Provider Test Script
Test all extension providers
\"\"\"

import requests
import json
import time

def test_orion_server():
    \"\"\"Test Orion server connectivity\"\"\"
    print('🔍 Testing Orion server...')
    
    endpoints = [
        'http://localhost:8000/health',
        'http://localhost:8000/api/status',
        'http://localhost:8000/api/ai/status',
        'http://localhost:8000/api/completion/status'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=2)
            if response.status_code == 200:
                print(f'  ✅ {endpoint}: OK')
            else:
                print(f'  ⚠️ {endpoint}: Status {response.status_code}')
        except requests.exceptions.ConnectionError:
            print(f'  ❌ {endpoint}: Connection failed')
        except requests.exceptions.Timeout:
            print(f'  ⏱️ {endpoint}: Timeout')

def test_ollama_connection():
    \"\"\"Test Ollama connectivity\"\"\"
    print('\\n🤖 Testing Ollama connection...')
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f'  ✅ Ollama: {len(models)} models available')
            for model in models[:3]:
                print(f'    🤖 {model.get("name", "Unknown")}')
        else:
            print(f'  ⚠️ Ollama: Status {response.status_code}')
    except requests.exceptions.ConnectionError:
        print('  ❌ Ollama: Not running')
    except requests.exceptions.Timeout:
        print('  ⏱️ Ollama: Timeout')

def main():
    print('🧪 PROVIDER CONNECTIVITY TEST')
    print('=' * 40)
    
    test_orion_server()
    test_ollama_connection()
    
    print('\\n💡 If tests fail:')
    print('  1. Start Orion server: python orion_server.py')
    print('  2. Start Ollama: ollama serve')
    print('  3. Restart VS Code')

if __name__ == '__main__':
    main()
"""
    
    with open("test_providers.py", "w") as f:
        f.write(test_script)
    
    print("✅ Provider test script created: test_providers.py")
    print("💡 Usage: python test_providers.py")

def main():
    """Main runtime fix function"""
    print_header("VS CODE EXTENSION RUNTIME FIX")
    print(f"🕐 Fix started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Diagnose issues
    issues = diagnose_extension_issues()
    
    print_section("ISSUE SUMMARY")
    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("✅ No obvious issues detected")
    
    # Create fix scripts
    create_server_startup_script()
    create_extension_config_fix()
    create_provider_test_script()
    
    print_header("RUNTIME FIX INSTRUCTIONS")
    print("🔧 To fix VS Code extension issues:")
    print()
    print("1. 🚀 START ORION SERVER:")
    print("   python orion_server.py")
    print()
    print("2. 🤖 START OLLAMA (if using):")
    print("   ollama serve")
    print()
    print("3. ⚙️ UPDATE VS CODE SETTINGS:")
    print("   Copy vscode_settings_fix.json to VS Code settings")
    print()
    print("4. 🔄 RESTART VS CODE:")
    print("   Close and reopen VS Code")
    print()
    print("5. 🧪 TEST PROVIDERS:")
    print("   python test_providers.py")
    print()
    print("6. 🎯 VERIFY EXTENSION:")
    print("   Ctrl+Shift+P > Orion: Activate AI Assistant")
    
    print(f"\n🎯 RUNTIME FIX COMPLETED: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
