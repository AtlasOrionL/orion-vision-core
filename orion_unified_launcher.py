#!/usr/bin/env python3
"""
🚀 ORION VISION CORE - UNIFIED LAUNCHER
Tüm Orion bileşenlerini tek komutla başlatan birleşik launcher

Bu dosya şunları yapar:
1. Tüm Orion bileşenlerini koordine eder
2. Çakışmaları önler ve çözer
3. Sağlık kontrolü yapar
4. Web interface sağlar
5. Graceful shutdown yapar

Kullanım:
    python orion_unified_launcher.py
    python orion_unified_launcher.py --full    # Tüm bileşenler
    python orion_unified_launcher.py --minimal # Sadece core bileşenler
    python orion_unified_launcher.py --gui-only # Sadece GUI
"""

import sys
import os
import asyncio
import argparse
import signal
import time
from pathlib import Path

# Proje root'unu sys.path'e ekle
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Orion managers
from orion_config_manager import get_config
from orion_component_coordinator import get_coordinator

# FastAPI ve Uvicorn
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

class OrionUnifiedLauncher:
    """🚀 Orion Vision Core Unified Launcher"""
    
    def __init__(self, mode: str = "full"):
        self.mode = mode
        self.config = get_config()
        self.coordinator = get_coordinator()
        self.app = FastAPI(
            title="Orion Vision Core",
            description="🚀 AI-powered development assistant with advanced capabilities",
            version="1.0.0"
        )
        
        self.running = False
        self.setup_signal_handlers()
        self.setup_fastapi_app()
        
        # Mode-specific configuration
        self.configure_mode()
    
    def setup_signal_handlers(self):
        """Signal handler'ları kur"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def configure_mode(self):
        """Çalışma moduna göre konfigürasyon"""
        if self.mode == "minimal":
            # Sadece core bileşenler
            self.config.gui.enabled = False
            self.config.voice.enabled = False
            self.config.agents.enabled = False
            print("🔧 Minimal mode: Core components only")
            
        elif self.mode == "gui-only":
            # Sadece GUI bileşenler
            self.config.agents.enabled = False
            self.config.voice.enabled = False
            print("🖥️ GUI mode: Interface components only")
            
        elif self.mode == "full":
            # Tüm bileşenler
            print("🚀 Full mode: All components enabled")
        
        # Port çakışmalarını çöz
        self.config.resolve_port_conflicts()
    
    def setup_fastapi_app(self):
        """FastAPI uygulamasını kur"""
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Static files (VS Code extension assets)
        static_path = PROJECT_ROOT / "vscode-extension" / "out"
        if static_path.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        
        # Routes
        self.setup_routes()
    
    def setup_routes(self):
        """API route'larını kur"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """Ana sayfa"""
            return self.get_dashboard_html()
        
        @self.app.get("/api/status")
        async def get_status():
            """Sistem durumu"""
            return {
                "status": "running" if self.running else "stopped",
                "mode": self.mode,
                "timestamp": time.time(),
                "components": self.coordinator.get_component_status(),
                "config": {
                    "server": {
                        "host": self.config.server.host,
                        "port": self.config.server.port,
                        "debug": self.config.server.debug
                    },
                    "ollama": {
                        "enabled": self.config.ollama.enabled,
                        "url": self.config.ollama.base_url,
                        "model": self.config.ollama.default_model
                    },
                    "gui": {
                        "enabled": self.config.gui.enabled,
                        "streamlit_port": self.config.gui.streamlit_port
                    }
                }
            }
        
        @self.app.get("/api/health")
        async def health_check():
            """Sağlık kontrolü"""
            component_health = {}
            overall_healthy = True
            
            for name, status in self.coordinator.component_status.items():
                is_healthy = await self.coordinator._health_check_component(name)
                component_health[name] = {
                    "healthy": is_healthy,
                    "state": status.state.value,
                    "last_check": status.last_health_check
                }
                if not is_healthy and not self.coordinator.components[name].optional:
                    overall_healthy = False
            
            return {
                "healthy": overall_healthy,
                "components": component_health,
                "timestamp": time.time()
            }
        
        @self.app.post("/api/restart/{component_name}")
        async def restart_component(component_name: str):
            """Bileşeni yeniden başlat"""
            if component_name not in self.coordinator.components:
                raise HTTPException(status_code=404, detail="Component not found")
            
            try:
                await self.coordinator._restart_component(component_name)
                return {"message": f"Component {component_name} restarted successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/logs/{component_name}")
        async def get_component_logs(component_name: str, lines: int = 100):
            """Bileşen loglarını al"""
            log_file = Path(f"logs/{component_name}.log")
            if not log_file.exists():
                raise HTTPException(status_code=404, detail="Log file not found")
            
            try:
                with open(log_file, 'r') as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                return {
                    "component": component_name,
                    "lines": recent_lines,
                    "total_lines": len(all_lines)
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/config")
        async def get_config_info():
            """Konfigürasyon bilgilerini al"""
            return {
                "server": self.config.get_component_config("server"),
                "database": self.config.get_component_config("database"),
                "ollama": self.config.get_component_config("ollama"),
                "agents": self.config.get_component_config("agents"),
                "gui": self.config.get_component_config("gui"),
                "voice": self.config.get_component_config("voice"),
                "security": self.config.get_component_config("security")
            }
        
        @self.app.post("/api/config/{component}")
        async def update_config(component: str, updates: dict):
            """Konfigürasyonu güncelle"""
            try:
                self.config.update_component_config(component, updates)
                return {"message": f"Configuration for {component} updated successfully"}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    def get_dashboard_html(self) -> str:
        """Dashboard HTML'ini oluştur"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orion Vision Core Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                }}
                .header h1 {{
                    font-size: 3em;
                    margin: 0;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                .header p {{
                    font-size: 1.2em;
                    opacity: 0.9;
                }}
                .cards {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }}
                .card {{
                    background: rgba(255,255,255,0.1);
                    border-radius: 10px;
                    padding: 20px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                }}
                .card h3 {{
                    margin-top: 0;
                    color: #ffd700;
                }}
                .status {{
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin: 10px 0;
                }}
                .status-dot {{
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #4CAF50;
                }}
                .status-dot.error {{
                    background: #f44336;
                }}
                .status-dot.warning {{
                    background: #ff9800;
                }}
                .links {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                }}
                .link {{
                    display: block;
                    padding: 15px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 8px;
                    text-decoration: none;
                    color: white;
                    text-align: center;
                    transition: all 0.3s ease;
                }}
                .link:hover {{
                    background: rgba(255,255,255,0.2);
                    transform: translateY(-2px);
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    opacity: 0.7;
                }}
                .refresh-btn {{
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 10px;
                }}
                .refresh-btn:hover {{
                    background: #45a049;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Orion Vision Core</h1>
                    <p>AI-powered development assistant with advanced capabilities</p>
                    <p>Mode: <strong>{self.mode.upper()}</strong> | Port: <strong>{self.config.server.port}</strong></p>
                </div>
                
                <div class="cards">
                    <div class="card">
                        <h3>🤖 AI Services</h3>
                        <div class="status">
                            <div class="status-dot"></div>
                            <span>Ollama: {self.config.ollama.base_url}</span>
                        </div>
                        <div class="status">
                            <div class="status-dot"></div>
                            <span>Model: {self.config.ollama.default_model}</span>
                        </div>
                        <div class="status">
                            <div class="status-dot"></div>
                            <span>Chat API: Active</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>🖥️ System Services</h3>
                        <div class="status">
                            <div class="status-dot"></div>
                            <span>Terminal API: Active</span>
                        </div>
                        <div class="status">
                            <div class="status-dot"></div>
                            <span>File System API: Active</span>
                        </div>
                        <div class="status">
                            <div class="status-dot"></div>
                            <span>Health Check: Active</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>🔌 Integrations</h3>
                        <div class="status">
                            <div class="status-dot"></div>
                            <span>VS Code Extension: Ready</span>
                        </div>
                        <div class="status">
                            <div class="status-dot {'error' if not self.config.gui.enabled else ''}"></div>
                            <span>GUI: {'Enabled' if self.config.gui.enabled else 'Disabled'}</span>
                        </div>
                        <div class="status">
                            <div class="status-dot {'error' if not self.config.voice.enabled else ''}"></div>
                            <span>Voice: {'Enabled' if self.config.voice.enabled else 'Disabled'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🔗 Quick Links</h3>
                    <div class="links">
                        <a href="/docs" class="link">📚 API Documentation</a>
                        <a href="/api/status" class="link">📊 System Status</a>
                        <a href="/api/health" class="link">🏥 Health Check</a>
                        <a href="http://localhost:{self.config.gui.streamlit_port}" class="link" target="_blank">🖥️ Streamlit GUI</a>
                        <a href="/api/config" class="link">⚙️ Configuration</a>
                    </div>
                    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Status</button>
                </div>
                
                <div class="footer">
                    <p>Orion Vision Core v1.0.0 | Running since {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>🌟 AI-powered development assistant for the future</p>
                </div>
            </div>
            
            <script>
                // Auto-refresh every 30 seconds
                setTimeout(() => location.reload(), 30000);
                
                // Check component status
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {{
                        console.log('System Status:', data);
                    }})
                    .catch(error => console.error('Status check failed:', error));
            </script>
        </body>
        </html>
        """
    
    async def start(self):
        """Sistemi başlat"""
        try:
            print("🚀 Starting Orion Vision Core Unified System...")
            
            # Konfigürasyonu doğrula
            config_errors = self.config.validate_config()
            if config_errors:
                print("⚠️ Configuration warnings:")
                for error in config_errors:
                    print(f"  - {error}")
            
            # Konfigürasyon özetini göster
            self.config.print_config_summary()
            
            # Bileşenleri başlat
            success = await self.coordinator.start_all_components()
            if not success:
                print("❌ Failed to start components")
                return False
            
            self.running = True
            print("✅ Orion Vision Core started successfully!")
            print(f"🌐 Dashboard: http://{self.config.server.host}:{self.config.server.port}")
            print(f"📚 API Docs: http://{self.config.server.host}:{self.config.server.port}/docs")
            
            return True
            
        except Exception as e:
            print(f"❌ Startup failed: {e}")
            return False
    
    async def shutdown(self):
        """Sistemi kapat"""
        if not self.running:
            return
        
        print("🛑 Shutting down Orion Vision Core...")
        self.running = False
        
        # Bileşenleri kapat
        await self.coordinator.stop_all_components()
        
        print("✅ Orion Vision Core shutdown complete")
    
    async def run(self):
        """Ana çalıştırma döngüsü"""
        # Sistemi başlat
        success = await self.start()
        if not success:
            return
        
        # Uvicorn server'ı başlat
        config = uvicorn.Config(
            self.app,
            host=self.config.server.host,
            port=self.config.server.port,
            log_level=self.config.logging.level.lower(),
            reload=self.config.server.debug,
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        try:
            await server.serve()
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
        finally:
            await self.shutdown()

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="🚀 Orion Vision Core Unified Launcher")
    parser.add_argument("--mode", choices=["full", "minimal", "gui-only"], default="full",
                       help="Launch mode (default: full)")
    parser.add_argument("--port", type=int, help="Override server port")
    parser.add_argument("--host", help="Override server host")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Banner
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                  🚀 ORION VISION CORE                        ║
    ║                   Unified Launcher v1.0.0                   ║
    ║                                                              ║
    ║  🤖 AI Chat + 🖥️ Terminal + 📁 File System + 🔌 APIs        ║
    ║  🎤 Voice + 🖼️ GUI + 🤖 Agents + 🧠 Ollama                  ║
    ║                                                              ║
    ║  Tüm bileşenler çakışma olmadan birlikte çalışır!           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Launcher'ı oluştur
    launcher = OrionUnifiedLauncher(mode=args.mode)
    
    # Override configurations
    if args.port:
        launcher.config.server.port = args.port
    if args.host:
        launcher.config.server.host = args.host
    if args.debug:
        launcher.config.server.debug = True
        launcher.config.logging.level = "DEBUG"
    
    # Sistemi çalıştır
    try:
        asyncio.run(launcher.run())
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"❌ System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
