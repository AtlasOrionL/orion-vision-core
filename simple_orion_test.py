#!/usr/bin/env python3
"""
🚀 SIMPLE ORION TEST
Basit Orion entegrasyon testi
"""

import sys
import os
from pathlib import Path

# Proje root'unu sys.path'e ekle
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

def main():
    print("🚀 ORION VISION CORE - SIMPLE TEST")
    print("="*50)
    
    # 1. Config test
    try:
        from orion_config_manager import get_config
        config = get_config()
        print(f"✅ Config loaded: {config.server.host}:{config.server.port}")
        print(f"✅ Ollama: {config.ollama.base_url}")
        print(f"✅ Default model: {config.ollama.default_model}")
    except Exception as e:
        print(f"❌ Config failed: {e}")
        return
    
    # 2. Runner service test
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "src" / "jobone" / "vision_core"))
        from runner_service import app, OLLAMA_BASE_URL, DEFAULT_MODEL
        print(f"✅ Runner service loaded")
        print(f"✅ FastAPI app: {app.title}")
    except Exception as e:
        print(f"❌ Runner service failed: {e}")
        return
    
    # 3. Ollama test
    try:
        import httpx
        import asyncio
        
        async def test_ollama():
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    response = await client.get("http://localhost:11434/api/tags")
                    if response.status_code == 200:
                        data = response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        print(f"✅ Ollama connected: {models}")
                        return True
                    else:
                        print(f"⚠️ Ollama status: {response.status_code}")
                        return False
            except Exception as e:
                print(f"⚠️ Ollama not available: {e}")
                return False
        
        ollama_ok = asyncio.run(test_ollama())
        
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
    
    # 4. Start simple server
    print("\n🌐 Starting simple server test...")
    try:
        import uvicorn
        
        print(f"🚀 Server ready at: http://{config.server.host}:{config.server.port}")
        print("📚 API docs at: /docs")
        print("🏥 Health check at: /api/health")
        print("💬 Chat API at: /api/chat/send")
        print("\n✅ All systems ready!")
        print("🎯 Use Ctrl+C to stop")
        
        # Start server
        uvicorn.run(
            app,
            host=config.server.host,
            port=config.server.port,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed: {e}")

if __name__ == "__main__":
    main()
