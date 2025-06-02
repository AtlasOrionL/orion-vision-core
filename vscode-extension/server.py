#!/usr/bin/env python3
"""
Orion Vision Core VS Code Extension Server
Provides API endpoints for AI providers, terminal, and file system operations.
"""

import subprocess
import os
import sys
from datetime import datetime
from typing import List
import asyncio
from aiohttp import web, ClientSession
from aiohttp.web import Request, Response, json_response
from aiohttp_cors import setup as cors_setup, ResourceOptions
import logging

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Request counter for tracking
request_counter = 0

class OrionServer:
    def __init__(self):
        self.app = web.Application()
        self.setup_middleware()
        self.setup_cors()
        self.setup_routes()
        self.ollama_url = "http://localhost:11434"
        self.default_model = "llama3.2:1b"

    @web.middleware
    async def log_request_middleware(self, request, handler):
        """Log all incoming requests"""
        global request_counter
        request_counter += 1

        start_time = datetime.now()
        logger.info(f"🔄 [{request_counter}] {request.method} {request.path} - Started")

        try:
            response = await handler(request)
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ [{request_counter}] {request.method} {request.path} - {response.status} ({duration:.3f}s)")
            return response
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ [{request_counter}] {request.method} {request.path} - ERROR: {str(e)} ({duration:.3f}s)")
            raise

    def setup_middleware(self):
        """Setup middleware"""
        self.app.middlewares.append(self.log_request_middleware)
        
    def setup_cors(self):
        """Setup CORS for VS Code extension"""
        cors = cors_setup(self.app, defaults={
            "*": ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
    def setup_routes(self):
        """Setup API routes"""
        # Health check
        self.app.router.add_get('/api/health', self.health_check)
        
        # Provider endpoints
        self.app.router.add_get('/api/providers', self.get_providers)
        self.app.router.add_post('/api/providers/test', self.test_provider)
        
        # Chat endpoints
        self.app.router.add_post('/api/chat', self.chat)
        
        # Terminal endpoints
        self.app.router.add_post('/api/terminal/execute', self.execute_command)
        
        # File system endpoints
        self.app.router.add_get('/api/filesystem/list', self.list_directory)
        self.app.router.add_post('/api/filesystem/read', self.read_file)
        self.app.router.add_post('/api/filesystem/write', self.write_file)
        self.app.router.add_delete('/api/filesystem/delete', self.delete_file)

    async def health_check(self, request: Request) -> Response:
        """Health check endpoint"""
        try:
            # Test Ollama connection
            ollama_connected = await self.test_ollama_connection()
            
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0.0",
                "services": {
                    "chat": "active",
                    "terminal": "active",
                    "filesystem": "active",
                    "providers": "active",
                    "ollama": "connected" if ollama_connected else "disconnected"
                },
                "ollama": {
                    "url": self.ollama_url,
                    "default_model": self.default_model,
                    "connected": ollama_connected
                }
            }
            return json_response(health_data)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return json_response({"status": "error", "message": str(e)}, status=500)

    async def test_ollama_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            async with ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags", timeout=5) as response:
                    return response.status == 200
        except:
            return False

    async def get_providers(self, request: Request) -> Response:
        """Get available AI providers"""
        try:
            # Check Ollama models
            ollama_models = await self.get_ollama_models()
            
            providers = [
                {
                    "id": "ollama",
                    "name": "Ollama (Local)",
                    "type": "local",
                    "status": "connected" if ollama_models else "disconnected",
                    "models": ollama_models,
                    "default_model": self.default_model
                },
                {
                    "id": "openrouter",
                    "name": "OpenRouter",
                    "type": "cloud",
                    "status": "not_configured",
                    "models": [
                        "microsoft/wizardlm-2-8x22b",
                        "meta-llama/llama-3-8b-instruct:free"
                    ],
                    "default_model": "microsoft/wizardlm-2-8x22b"
                }
            ]
            
            return json_response({"providers": providers})
        except Exception as e:
            logger.error(f"Get providers failed: {e}")
            return json_response({"error": str(e)}, status=500)

    async def get_ollama_models(self) -> List[str]:
        """Get available Ollama models"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
        except Exception as e:
            logger.error(f"Failed to get Ollama models: {e}")
        return []

    async def test_provider(self, request: Request) -> Response:
        """Test provider connection"""
        try:
            data = await request.json()
            provider_id = data.get('provider_id')
            
            if provider_id == 'ollama':
                success = await self.test_ollama_connection()
                if success:
                    # Test with a simple prompt
                    test_response = await self.call_ollama("Hello, this is a test message.")
                    return json_response({
                        "success": True,
                        "message": "Ollama connection successful",
                        "test_response": test_response[:100] + "..." if len(test_response) > 100 else test_response
                    })
                else:
                    return json_response({"success": False, "message": "Ollama not available"})
            else:
                return json_response({"success": False, "message": "Provider not implemented"})
                
        except Exception as e:
            logger.error(f"Test provider failed: {e}")
            return json_response({"success": False, "message": str(e)}, status=500)

    async def call_ollama(self, prompt: str, model: str = None) -> str:
        """Call Ollama API"""
        try:
            if not model:
                model = self.default_model
                
            async with ClientSession() as session:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
                
                async with session.post(f"{self.ollama_url}/api/generate", 
                                      json=payload, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', 'No response')
                    else:
                        return f"Error: HTTP {response.status}"
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            return f"Error: {str(e)}"

    async def chat(self, request: Request) -> Response:
        """Chat endpoint"""
        try:
            data = await request.json()
            message = data.get('message', '')
            model = data.get('model', self.default_model)
            provider = data.get('provider', 'ollama')

            logger.info(f"💬 Chat request: provider={provider}, model={model}, message_length={len(message)}")
            logger.debug(f"💬 Chat message preview: {message[:100]}...")

            if provider == 'ollama':
                logger.info(f"🤖 Calling Ollama with model: {model}")
                response_text = await self.call_ollama(message, model)
                logger.info(f"✅ Ollama response received: {len(response_text)} characters")

                return json_response({
                    "response": response_text,
                    "model": model,
                    "provider": provider,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                logger.warning(f"❌ Unsupported provider: {provider}")
                return json_response({"error": "Provider not supported"}, status=400)

        except Exception as e:
            logger.error(f"❌ Chat failed: {e}")
            return json_response({"error": str(e)}, status=500)

    async def execute_command(self, request: Request) -> Response:
        """Execute terminal command (safe commands only)"""
        try:
            data = await request.json()
            command = data.get('command', '')
            
            # Security: Only allow safe commands
            safe_commands = ['ls', 'pwd', 'whoami', 'date', 'echo', 'cat', 'head', 'tail', 'wc', 'grep']
            command_parts = command.split()
            
            if not command_parts or command_parts[0] not in safe_commands:
                return json_response({
                    "success": False,
                    "error": "Command not allowed for security reasons",
                    "allowed_commands": safe_commands
                }, status=403)
            
            # Execute command
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=10, cwd='/tmp')
            
            return json_response({
                "success": True,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode,
                "command": command
            })
            
        except subprocess.TimeoutExpired:
            return json_response({"success": False, "error": "Command timeout"}, status=408)
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return json_response({"success": False, "error": str(e)}, status=500)

    async def list_directory(self, request: Request) -> Response:
        """List directory contents"""
        try:
            path = request.query.get('path', '/tmp')
            
            # Security: Restrict to safe directories
            safe_paths = ['/tmp', '/home', '/var/log']
            if not any(path.startswith(safe_path) for safe_path in safe_paths):
                return json_response({"error": "Path not allowed"}, status=403)
            
            if not os.path.exists(path):
                return json_response({"error": "Path does not exist"}, status=404)
            
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    stat = os.stat(item_path)
                    items.append({
                        "name": item,
                        "type": "directory" if os.path.isdir(item_path) else "file",
                        "size": stat.st_size if os.path.isfile(item_path) else None,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except:
                    continue
            
            return json_response({"success": True, "path": path, "items": items})

        except Exception as e:
            logger.error(f"List directory failed: {e}")
            return json_response({"error": str(e)}, status=500)

    async def read_file(self, request: Request) -> Response:
        """Read file contents"""
        try:
            data = await request.json()
            file_path = data.get('path', '')

            # Security checks
            if not file_path.startswith('/tmp/'):
                return json_response({"error": "File path not allowed"}, status=403)

            if not os.path.exists(file_path):
                return json_response({"error": "File does not exist"}, status=404)

            if not os.path.isfile(file_path):
                return json_response({"error": "Path is not a file"}, status=400)

            # Read file (limit size for security)
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024:  # 1MB limit
                return json_response({"error": "File too large"}, status=413)

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return json_response({
                "success": True,
                "content": content,
                "size": file_size,
                "path": file_path
            })

        except Exception as e:
            logger.error(f"Read file failed: {e}")
            return json_response({"error": str(e)}, status=500)

    async def write_file(self, request: Request) -> Response:
        """Write file contents"""
        try:
            data = await request.json()
            file_path = data.get('path', '')
            content = data.get('content', '')

            # Security checks
            if not file_path.startswith('/tmp/'):
                return json_response({"error": "File path not allowed"}, status=403)

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            file_size = os.path.getsize(file_path)

            return json_response({
                "success": True,
                "size": file_size,
                "path": file_path
            })

        except Exception as e:
            logger.error(f"Write file failed: {e}")
            return json_response({"error": str(e)}, status=500)

    async def delete_file(self, request: Request) -> Response:
        """Delete file"""
        try:
            data = await request.json()
            file_path = data.get('path', '')

            # Security checks
            if not file_path.startswith('/tmp/'):
                return json_response({"error": "File path not allowed"}, status=403)

            if not os.path.exists(file_path):
                return json_response({"error": "File does not exist"}, status=404)

            os.remove(file_path)

            return json_response({"success": True, "path": file_path})

        except Exception as e:
            logger.error(f"Delete file failed: {e}")
            return json_response({"error": str(e)}, status=500)

    async def start_server(self, host='localhost', port=8000):
        """Start the server"""
        logger.info(f"🚀 Starting Orion Vision Core Server on {host}:{port}")
        logger.info(f"🔗 Health check: http://{host}:{port}/api/health")
        logger.info(f"🤖 Ollama URL: {self.ollama_url}")

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info("✅ Server started successfully!")
        return runner

async def main():
    """Main function"""
    server = OrionServer()
    runner = await server.start_server()

    try:
        # Keep server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down server...")
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
