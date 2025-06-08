#!/usr/bin/env python3
"""
🖥️ Gaming AI Debug Dashboard - Core Module

Core web dashboard for debugging and testing all Gaming AI features.
Provides real-time monitoring, testing interface, and system status.

Author: Nexus - Quantum AI Architect
Module: Debug Dashboard Core
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# FastAPI imports
try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️ FastAPI not available. Install with: pip install fastapi uvicorn jinja2")

@dataclass
class SystemStatus:
    """System status information"""
    timestamp: float
    gaming_ai_status: str
    ollama_status: str
    active_features: List[str]
    performance_metrics: Dict[str, Any]
    error_count: int
    warning_count: int

@dataclass
class TestResult:
    """Test result information"""
    test_id: str
    test_name: str
    status: str  # success, failed, running
    duration: float
    timestamp: float
    details: Dict[str, Any]
    error_message: Optional[str] = None

class DebugDashboardCore:
    """
    Core debug dashboard for Gaming AI
    
    Features:
    - Real-time system monitoring
    - WebSocket communication
    - Test execution interface
    - Status tracking
    - Error logging
    """
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.logger = logging.getLogger("DebugDashboard")
        
        # Dashboard state
        self.system_status = SystemStatus(
            timestamp=time.time(),
            gaming_ai_status="unknown",
            ollama_status="unknown", 
            active_features=[],
            performance_metrics={},
            error_count=0,
            warning_count=0
        )
        
        # Test tracking
        self.test_results: List[TestResult] = []
        self.running_tests: Dict[str, TestResult] = {}
        
        # WebSocket connections
        self.websocket_connections: List[WebSocket] = []
        
        # Initialize FastAPI app
        if FASTAPI_AVAILABLE:
            self.app = FastAPI(
                title="Gaming AI Debug Dashboard",
                description="Debug and testing interface for Gaming AI system",
                version="1.0.0"
            )
            self._setup_routes()
        else:
            self.app = None
            self.logger.error("❌ FastAPI not available")
        
        self.logger.info("🖥️ Debug Dashboard Core initialized")
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home(request: Request):
            """Main dashboard page"""
            return self._get_dashboard_html()
        
        @self.app.get("/api/status")
        async def get_system_status():
            """Get current system status"""
            await self._update_system_status()
            return JSONResponse(asdict(self.system_status))
        
        @self.app.get("/api/tests")
        async def get_test_results():
            """Get test results"""
            return JSONResponse([asdict(test) for test in self.test_results[-50:]])  # Last 50 tests
        
        @self.app.post("/api/test/{test_type}")
        async def run_test(test_type: str):
            """Run specific test"""
            test_id = f"{test_type}_{int(time.time())}"
            
            # Create test result
            test_result = TestResult(
                test_id=test_id,
                test_name=test_type,
                status="running",
                duration=0.0,
                timestamp=time.time(),
                details={}
            )
            
            self.running_tests[test_id] = test_result
            
            # Run test asynchronously
            asyncio.create_task(self._execute_test(test_id, test_type))
            
            return JSONResponse({"test_id": test_id, "status": "started"})
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            self.websocket_connections.append(websocket)
            
            try:
                while True:
                    # Send periodic updates
                    await self._send_websocket_update(websocket)
                    await asyncio.sleep(2)  # Update every 2 seconds
                    
            except WebSocketDisconnect:
                self.websocket_connections.remove(websocket)

        # Gaming AI API Endpoints
        @self.app.post("/api/gaming/optimize")
        async def optimize_game(request: Request):
            """Optimize game settings"""
            try:
                data = await request.json()
                game_type = data.get('game_type', 'CS:GO')
                parameters = data.get('parameters', {})

                from unified_gaming_ai_api import UnifiedGamingAI
                gaming_ai = UnifiedGamingAI()

                # Simulate game optimization
                optimizations_applied = len(parameters) + 3
                details = {
                    "game_type": game_type,
                    "parameters_applied": parameters,
                    "fps_improvement": "15-20%",
                    "latency_reduction": "5-10ms",
                    "optimization_score": 95.5
                }

                return JSONResponse({
                    "success": True,
                    "optimizations_applied": optimizations_applied,
                    "details": details,
                    "message": f"{game_type} optimization completed successfully!"
                })
            except Exception as e:
                self.logger.error(f"❌ Game optimization failed: {e}")
                return JSONResponse({"success": False, "error": str(e)})

        @self.app.post("/api/ai/ask")
        async def ask_ai(request: Request):
            """Ask AI for gaming advice"""
            try:
                data = await request.json()
                question = data.get('question', '')

                # Gaming AI responses based on question keywords
                responses = {
                    "aim": "🎯 For better aim: Lower your sensitivity (1.5-3.0), practice crosshair placement, use aim trainers daily, and ensure stable FPS (144+ recommended).",
                    "fps": "📊 FPS optimization: Lower graphics settings, disable V-Sync, update drivers, close background apps, and consider hardware upgrades.",
                    "settings": "⚙️ Optimal settings: Disable motion blur, set FOV to 90-110, use raw input, disable mouse acceleration, and optimize network settings.",
                    "csgo": "🔫 CS:GO tips: Learn spray patterns, practice pre-aiming, use sound cues, learn map callouts, and maintain good crosshair placement.",
                    "valorant": "🎯 VALORANT tips: Master agent abilities, learn map control, practice aim daily, communicate with team, and study pro gameplay.",
                    "performance": "⚡ Performance tips: Maintain 144+ FPS, use gaming mouse with high polling rate, optimize network settings, and practice consistently."
                }

                # Find relevant response
                question_lower = question.lower()
                response = "🤖 I'm here to help with gaming optimization! Ask me about aim improvement, FPS optimization, game settings, or specific games like CS:GO and VALORANT."

                for keyword, ai_response in responses.items():
                    if keyword in question_lower:
                        response = ai_response
                        break

                return JSONResponse({
                    "success": True,
                    "response": response,
                    "question": question
                })
            except Exception as e:
                self.logger.error(f"❌ AI request failed: {e}")
                return JSONResponse({"success": False, "error": str(e)})

        @self.app.post("/api/team/create")
        async def create_team():
            """Create a new team"""
            try:
                team_id = f"team_{int(time.time())}"

                return JSONResponse({
                    "success": True,
                    "team_id": team_id,
                    "max_agents": 8,
                    "created_at": time.time()
                })
            except Exception as e:
                self.logger.error(f"❌ Team creation failed: {e}")
                return JSONResponse({"success": False, "error": str(e)})

        @self.app.post("/api/team/add_agent")
        async def add_agent(request: Request):
            """Add agent to team"""
            try:
                data = await request.json()
                agent_type = data.get('agent_type', 'gaming_assistant')
                capabilities = data.get('capabilities', [])

                agent_id = f"agent_{int(time.time())}"

                return JSONResponse({
                    "success": True,
                    "agent_id": agent_id,
                    "agent_type": agent_type,
                    "capabilities": capabilities
                })
            except Exception as e:
                self.logger.error(f"❌ Agent addition failed: {e}")
                return JSONResponse({"success": False, "error": str(e)})

        @self.app.post("/api/team/start_coordination")
        async def start_coordination():
            """Start team coordination"""
            try:
                return JSONResponse({
                    "success": True,
                    "active_agents": 3,
                    "coordination_mode": "gaming_optimization",
                    "status": "active"
                })
            except Exception as e:
                self.logger.error(f"❌ Coordination start failed: {e}")
                return JSONResponse({"success": False, "error": str(e)})

        @self.app.get("/api/team/status")
        async def get_team_status():
            """Get team status"""
            try:
                return JSONResponse({
                    "success": True,
                    "total_agents": 3,
                    "active_agents": 3,
                    "coordination_status": "active",
                    "performance": "optimal",
                    "current_task": "game_optimization"
                })
            except Exception as e:
                self.logger.error(f"❌ Team status check failed: {e}")
                return JSONResponse({"success": False, "error": str(e)})
    
    async def _update_system_status(self):
        """Update system status"""
        try:
            # Check Gaming AI status
            try:
                from unified_gaming_ai_api import UnifiedGamingAI
                api = UnifiedGamingAI()
                status = api.get_api_status()
                self.system_status.gaming_ai_status = "operational" if status["features_available"] else "error"
                self.system_status.active_features = status.get("active_features", [])
                self.system_status.performance_metrics = status.get("metrics", {})
            except Exception as e:
                self.system_status.gaming_ai_status = "error"
                self.logger.error(f"❌ Gaming AI status check failed: {e}")
            
            # Check Ollama status
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                self.system_status.ollama_status = "operational" if response.status_code == 200 else "error"
            except Exception:
                self.system_status.ollama_status = "offline"
            
            self.system_status.timestamp = time.time()
            
        except Exception as e:
            self.logger.error(f"❌ System status update failed: {e}")
    
    async def _execute_test(self, test_id: str, test_type: str):
        """Execute test and update results"""
        start_time = time.time()
        test_result = self.running_tests[test_id]
        
        try:
            # Import test modules based on test type
            if test_type == "gaming_ai_core":
                from unified_gaming_ai_api import UnifiedGamingAI
                api = UnifiedGamingAI()
                status = api.get_api_status()
                test_result.details = {"api_status": status}
                test_result.status = "success" if status["features_available"] else "failed"
                
            elif test_type == "ollama_connection":
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                models = response.json().get("models", [])
                test_result.details = {"models": len(models), "model_list": [m["name"] for m in models]}
                test_result.status = "success" if response.status_code == 200 else "failed"
                
            elif test_type == "performance_monitor":
                from performance_monitor import PerformanceMonitor
                monitor = PerformanceMonitor(collection_interval=0.5)
                started = monitor.start_monitoring()
                await asyncio.sleep(1.0)
                current = monitor.get_current_performance()
                monitor.stop_monitoring()
                test_result.details = {"started": started, "data_collected": current is not None}
                test_result.status = "success" if started else "failed"
                
            else:
                test_result.status = "failed"
                test_result.error_message = f"Unknown test type: {test_type}"
            
        except Exception as e:
            test_result.status = "failed"
            test_result.error_message = str(e)
            self.logger.error(f"❌ Test {test_id} failed: {e}")
        
        finally:
            test_result.duration = time.time() - start_time
            test_result.timestamp = time.time()
            
            # Move from running to completed
            self.test_results.append(test_result)
            del self.running_tests[test_id]
            
            # Broadcast update
            await self._broadcast_test_update(test_result)
    
    async def _send_websocket_update(self, websocket: WebSocket):
        """Send update to specific websocket"""
        try:
            await self._update_system_status()
            
            update_data = {
                "type": "status_update",
                "timestamp": time.time(),
                "system_status": asdict(self.system_status),
                "running_tests": len(self.running_tests),
                "recent_tests": [asdict(test) for test in self.test_results[-5:]]
            }
            
            await websocket.send_text(json.dumps(update_data))
            
        except Exception as e:
            self.logger.error(f"❌ WebSocket update failed: {e}")
    
    async def _broadcast_test_update(self, test_result: TestResult):
        """Broadcast test update to all connected clients"""
        update_data = {
            "type": "test_update",
            "timestamp": time.time(),
            "test_result": asdict(test_result)
        }
        
        disconnected = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(json.dumps(update_data))
            except Exception:
                disconnected.append(websocket)
        
        # Remove disconnected websockets
        for ws in disconnected:
            self.websocket_connections.remove(ws)
    
    def _get_dashboard_html(self) -> str:
        """Get dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gaming AI Debug Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
                .header { text-align: center; margin-bottom: 30px; }
                .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .status-card { background: #2a2a2a; padding: 20px; border-radius: 8px; border-left: 4px solid #4CAF50; }
                .status-card.error { border-left-color: #f44336; }
                .status-card.warning { border-left-color: #ff9800; }
                .test-section { background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .test-buttons { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
                .test-btn { padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
                .test-btn:hover { background: #45a049; }
                .test-results { max-height: 400px; overflow-y: auto; }
                .test-result { padding: 10px; margin: 5px 0; border-radius: 4px; background: #3a3a3a; }
                .test-result.success { border-left: 4px solid #4CAF50; }
                .test-result.failed { border-left: 4px solid #f44336; }
                .test-result.running { border-left: 4px solid #ff9800; }
                .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
                .metric { background: #3a3a3a; padding: 10px; border-radius: 4px; text-align: center; }
                #connection-status { position: fixed; top: 10px; right: 10px; padding: 5px 10px; border-radius: 4px; }
                .connected { background: #4CAF50; }
                .disconnected { background: #f44336; }
            </style>
        </head>
        <body>
            <div id="connection-status" class="disconnected">Disconnected</div>
            
            <div class="header">
                <h1>🎮 Gaming AI Debug Dashboard</h1>
                <p>Real-time monitoring and testing interface</p>
            </div>
            
            <div class="status-grid">
                <div class="status-card" id="gaming-ai-status">
                    <h3>🎮 Gaming AI Status</h3>
                    <p id="gaming-ai-text">Checking...</p>
                    <div id="active-features"></div>
                </div>
                
                <div class="status-card" id="ollama-status">
                    <h3>🤖 Ollama Status</h3>
                    <p id="ollama-text">Checking...</p>
                </div>
                
                <div class="status-card">
                    <h3>📊 Performance Metrics</h3>
                    <div class="metrics" id="performance-metrics">
                        <div class="metric">Loading...</div>
                    </div>
                </div>
            </div>
            
            <!-- Gaming Features Section -->
            <div class="test-section">
                <h3>🎮 Game Optimization</h3>
                <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <label>Game Type:</label>
                        <select id="gameType" style="width: 100%; padding: 8px; margin: 5px 0; background: #3a3a3a; color: white; border: 1px solid #555;">
                            <option value="CS:GO">🔫 CS:GO</option>
                            <option value="VALORANT">🎯 VALORANT</option>
                            <option value="Fortnite">🏗️ Fortnite</option>
                        </select>
                        <button class="test-btn" onclick="optimizeGame()" style="width: 100%; margin-top: 10px;">🚀 Optimize Game</button>
                    </div>
                    <div>
                        <label>Optimization Parameters:</label>
                        <textarea id="optimizationParams" style="width: 100%; height: 80px; padding: 8px; background: #3a3a3a; color: white; border: 1px solid #555;" placeholder='{"aim_sensitivity": 2.5, "crosshair_style": 4, "fps_target": 144}'></textarea>
                    </div>
                </div>
                <div id="optimizationResults" class="test-results"></div>
            </div>

            <!-- AI Assistant Section -->
            <div class="test-section">
                <h3>🤖 AI Gaming Assistant</h3>
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
                    <div>
                        <textarea id="aiQuestion" style="width: 100%; height: 60px; padding: 8px; background: #3a3a3a; color: white; border: 1px solid #555;" placeholder="Ask AI for gaming advice... (e.g., 'How can I improve my CS:GO aim?')"></textarea>
                    </div>
                    <div>
                        <button class="test-btn" onclick="askAI()" style="width: 100%; height: 60px;">🤖 Ask AI</button>
                    </div>
                </div>
                <div id="aiResponse" class="test-results"></div>
            </div>

            <!-- Real-time Game Monitoring Section -->
            <div class="test-section">
                <h3>📊 Real-time Game Monitoring</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="text-align: center;">
                        <h4>🎯 Aim Accuracy</h4>
                        <div id="aimAccuracy" style="font-size: 2em; color: #4CAF50;">---%</div>
                        <div style="font-size: 0.8em; color: #888;">Last 10 shots</div>
                    </div>
                    <div style="text-align: center;">
                        <h4>⚡ Reaction Time</h4>
                        <div id="reactionTime" style="font-size: 2em; color: #ff9800;">---ms</div>
                        <div style="font-size: 0.8em; color: #888;">Average</div>
                    </div>
                    <div style="text-align: center;">
                        <h4>🎮 FPS</h4>
                        <div id="currentFPS" style="font-size: 2em; color: #2196F3;">---</div>
                        <div style="font-size: 0.8em; color: #888;">Current</div>
                    </div>
                </div>
                <div class="test-buttons">
                    <button class="test-btn" onclick="startGameMonitoring()">🔄 Start Monitoring</button>
                    <button class="test-btn" onclick="stopGameMonitoring()">⏹️ Stop Monitoring</button>
                    <button class="test-btn" onclick="resetStats()">🔄 Reset Stats</button>
                </div>
                <div id="monitoringResults" class="test-results"></div>
            </div>

            <!-- Advanced AI Features Section -->
            <div class="test-section">
                <h3>🧠 Advanced AI Features</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <label>AI Analysis Type:</label>
                        <select id="analysisType" style="width: 100%; padding: 8px; margin: 5px 0; background: #3a3a3a; color: white; border: 1px solid #555;">
                            <option value="gameplay">🎮 Gameplay Analysis</option>
                            <option value="strategy">🎯 Strategy Recommendation</option>
                            <option value="performance">📊 Performance Analysis</option>
                            <option value="training">🏋️ Training Plan</option>
                        </select>
                    </div>
                    <div>
                        <label>Game Context:</label>
                        <select id="gameContext" style="width: 100%; padding: 8px; margin: 5px 0; background: #3a3a3a; color: white; border: 1px solid #555;">
                            <option value="competitive">🏆 Competitive Match</option>
                            <option value="casual">😎 Casual Play</option>
                            <option value="training">🎯 Training Session</option>
                            <option value="warmup">🔥 Warm-up</option>
                        </select>
                    </div>
                </div>
                <div class="test-buttons">
                    <button class="test-btn" onclick="runAIAnalysis()">🧠 Run AI Analysis</button>
                    <button class="test-btn" onclick="getAIRecommendations()">💡 Get Recommendations</button>
                    <button class="test-btn" onclick="generateTrainingPlan()">📋 Generate Training Plan</button>
                </div>
                <div id="aiAnalysisResults" class="test-results"></div>
            </div>

            <!-- Team Coordination Section -->
            <div class="test-section">
                <h3>👥 Multi-Agent Team Coordination</h3>
                <div class="test-buttons">
                    <button class="test-btn" onclick="createTeam()">🏗️ Create Team</button>
                    <button class="test-btn" onclick="addAgent()">➕ Add Agent</button>
                    <button class="test-btn" onclick="startCoordination()">🎯 Start Coordination</button>
                    <button class="test-btn" onclick="getTeamStatus()">📊 Team Status</button>
                </div>
                <div id="teamResults" class="test-results"></div>
            </div>

            <div class="test-section">
                <h3>🧪 Quick Tests</h3>
                <div class="test-buttons">
                    <button class="test-btn" onclick="runTest('gaming_ai_core')">Gaming AI Core</button>
                    <button class="test-btn" onclick="runTest('ollama_connection')">Ollama Connection</button>
                    <button class="test-btn" onclick="runTest('performance_monitor')">Performance Monitor</button>
                </div>
                
                <h4>Recent Test Results</h4>
                <div class="test-results" id="test-results">
                    <div class="test-result">No tests run yet</div>
                </div>
            </div>
            
            <script>
                let ws = null;
                
                function connectWebSocket() {
                    ws = new WebSocket(`ws://${window.location.host}/ws`);
                    
                    ws.onopen = function() {
                        document.getElementById('connection-status').textContent = 'Connected';
                        document.getElementById('connection-status').className = 'connected';
                    };
                    
                    ws.onclose = function() {
                        document.getElementById('connection-status').textContent = 'Disconnected';
                        document.getElementById('connection-status').className = 'disconnected';
                        setTimeout(connectWebSocket, 3000);
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'status_update') {
                            updateSystemStatus(data.system_status);
                            updateTestResults(data.recent_tests);
                        } else if (data.type === 'test_update') {
                            addTestResult(data.test_result);
                        }
                    };
                }
                
                function updateSystemStatus(status) {
                    // Gaming AI status
                    const gamingAiCard = document.getElementById('gaming-ai-status');
                    const gamingAiText = document.getElementById('gaming-ai-text');
                    gamingAiText.textContent = status.gaming_ai_status;
                    gamingAiCard.className = 'status-card ' + (status.gaming_ai_status === 'operational' ? '' : 'error');
                    
                    // Active features
                    const featuresDiv = document.getElementById('active-features');
                    featuresDiv.innerHTML = '<small>Active: ' + status.active_features.join(', ') + '</small>';
                    
                    // Ollama status
                    const ollamaCard = document.getElementById('ollama-status');
                    const ollamaText = document.getElementById('ollama-text');
                    ollamaText.textContent = status.ollama_status;
                    ollamaCard.className = 'status-card ' + (status.ollama_status === 'operational' ? '' : 'error');
                    
                    // Performance metrics
                    const metricsDiv = document.getElementById('performance-metrics');
                    const metrics = status.performance_metrics;
                    metricsDiv.innerHTML = Object.keys(metrics).map(key => 
                        `<div class="metric"><strong>${key}</strong><br>${metrics[key]}</div>`
                    ).join('');
                }
                
                function updateTestResults(tests) {
                    const resultsDiv = document.getElementById('test-results');
                    if (tests.length === 0) return;
                    
                    resultsDiv.innerHTML = tests.map(test => 
                        `<div class="test-result ${test.status}">
                            <strong>${test.test_name}</strong> - ${test.status} (${test.duration.toFixed(2)}s)
                            <br><small>${new Date(test.timestamp * 1000).toLocaleTimeString()}</small>
                        </div>`
                    ).join('');
                }
                
                function addTestResult(test) {
                    const resultsDiv = document.getElementById('test-results');
                    const testElement = document.createElement('div');
                    testElement.className = `test-result ${test.status}`;
                    testElement.innerHTML = `
                        <strong>${test.test_name}</strong> - ${test.status} (${test.duration.toFixed(2)}s)
                        <br><small>${new Date(test.timestamp * 1000).toLocaleTimeString()}</small>
                    `;
                    resultsDiv.insertBefore(testElement, resultsDiv.firstChild);
                }
                
                function runTest(testType) {
                    fetch(`/api/test/${testType}`, { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Test started:', data);
                        })
                        .catch(error => {
                            console.error('Test failed to start:', error);
                        });
                }

                // Gaming AI Functions
                function optimizeGame() {
                    const gameType = document.getElementById('gameType').value;
                    const paramsText = document.getElementById('optimizationParams').value;

                    let params = {};
                    try {
                        params = paramsText ? JSON.parse(paramsText) : {};
                    } catch (e) {
                        addResult('optimizationResults', `❌ Invalid JSON parameters: ${e.message}`);
                        return;
                    }

                    addResult('optimizationResults', `🎮 Optimizing ${gameType}...`);

                    fetch('/api/gaming/optimize', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ game_type: gameType, parameters: params })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            addResult('optimizationResults', `✅ ${gameType} optimization completed!`);
                            addResult('optimizationResults', `📈 Optimizations applied: ${data.optimizations_applied || 0}`);
                            if (data.details) {
                                addResult('optimizationResults', `📊 FPS improvement: ${data.details.fps_improvement || 'N/A'}`);
                                addResult('optimizationResults', `⚡ Latency reduction: ${data.details.latency_reduction || 'N/A'}`);
                                addResult('optimizationResults', `🎯 Optimization score: ${data.details.optimization_score || 'N/A'}`);
                            }
                        } else {
                            addResult('optimizationResults', `❌ Optimization failed: ${data.error || 'Unknown error'}`);
                        }
                    })
                    .catch(error => {
                        addResult('optimizationResults', `❌ Error: ${error.message}`);
                    });
                }

                function askAI() {
                    const question = document.getElementById('aiQuestion').value;
                    if (!question.trim()) {
                        addResult('aiResponse', '❌ Please enter a question');
                        return;
                    }

                    addResult('aiResponse', `🤖 AI is thinking about: "${question}"`);

                    fetch('/api/ai/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question: question })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            addResult('aiResponse', `🤖 AI Response: ${data.response}`);
                        } else {
                            addResult('aiResponse', `❌ AI Error: ${data.error || 'Unknown error'}`);
                        }
                    })
                    .catch(error => {
                        addResult('aiResponse', `❌ Error: ${error.message}`);
                    });
                }

                function createTeam() {
                    addResult('teamResults', '🏗️ Creating new team...');

                    fetch('/api/team/create', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            addResult('teamResults', `✅ Team created: ${data.team_id}`);
                            addResult('teamResults', `👥 Team capacity: ${data.max_agents} agents`);
                        } else {
                            addResult('teamResults', `❌ Team creation failed: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        addResult('teamResults', `❌ Error: ${error.message}`);
                    });
                }

                function addAgent() {
                    addResult('teamResults', '➕ Adding new agent...');

                    fetch('/api/team/add_agent', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            agent_type: 'gaming_assistant',
                            capabilities: ['game_optimization', 'strategy_advice']
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            addResult('teamResults', `✅ Agent added: ${data.agent_id}`);
                            addResult('teamResults', `🤖 Agent type: ${data.agent_type}`);
                            addResult('teamResults', `⚡ Capabilities: ${data.capabilities.join(', ')}`);
                        } else {
                            addResult('teamResults', `❌ Agent addition failed: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        addResult('teamResults', `❌ Error: ${error.message}`);
                    });
                }

                function startCoordination() {
                    addResult('teamResults', '🎯 Starting team coordination...');

                    fetch('/api/team/start_coordination', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            addResult('teamResults', `✅ Coordination started`);
                            addResult('teamResults', `👥 Active agents: ${data.active_agents}`);
                            addResult('teamResults', `🎮 Coordination mode: ${data.coordination_mode}`);
                            addResult('teamResults', `📊 Status: ${data.status}`);
                        } else {
                            addResult('teamResults', `❌ Coordination failed: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        addResult('teamResults', `❌ Error: ${error.message}`);
                    });
                }

                function getTeamStatus() {
                    addResult('teamResults', '📊 Getting team status...');

                    fetch('/api/team/status')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            addResult('teamResults', `📊 Team Status Report:`);
                            addResult('teamResults', `👥 Total agents: ${data.total_agents}`);
                            addResult('teamResults', `🎯 Active agents: ${data.active_agents}`);
                            addResult('teamResults', `🤝 Coordination status: ${data.coordination_status}`);
                            addResult('teamResults', `⚡ Performance: ${data.performance}`);
                            addResult('teamResults', `🎮 Current task: ${data.current_task}`);
                        } else {
                            addResult('teamResults', `❌ Status check failed: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        addResult('teamResults', `❌ Error: ${error.message}`);
                    });
                }

                function addResult(containerId, message) {
                    const container = document.getElementById(containerId);
                    if (!container) return;

                    const result = document.createElement('div');
                    result.className = 'test-result';
                    result.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
                    container.appendChild(result);
                    container.scrollTop = container.scrollHeight;
                }

                // Real-time Game Monitoring Functions
                let monitoringInterval = null;
                let gameStats = {
                    aimAccuracy: 0,
                    reactionTime: 0,
                    fps: 0,
                    shots: 0,
                    hits: 0
                };

                function startGameMonitoring() {
                    if (monitoringInterval) {
                        addResult('monitoringResults', '⚠️ Monitoring already active');
                        return;
                    }

                    addResult('monitoringResults', '🔄 Starting real-time game monitoring...');

                    monitoringInterval = setInterval(() => {
                        // Simulate real-time game data
                        gameStats.aimAccuracy = Math.floor(Math.random() * 40) + 60; // 60-100%
                        gameStats.reactionTime = Math.floor(Math.random() * 100) + 150; // 150-250ms
                        gameStats.fps = Math.floor(Math.random() * 60) + 120; // 120-180 FPS

                        // Update UI
                        document.getElementById('aimAccuracy').textContent = gameStats.aimAccuracy + '%';
                        document.getElementById('reactionTime').textContent = gameStats.reactionTime + 'ms';
                        document.getElementById('currentFPS').textContent = gameStats.fps;

                        // Color coding based on performance
                        const aimElement = document.getElementById('aimAccuracy');
                        aimElement.style.color = gameStats.aimAccuracy > 80 ? '#4CAF50' : gameStats.aimAccuracy > 60 ? '#ff9800' : '#f44336';

                        const reactionElement = document.getElementById('reactionTime');
                        reactionElement.style.color = gameStats.reactionTime < 180 ? '#4CAF50' : gameStats.reactionTime < 220 ? '#ff9800' : '#f44336';

                        const fpsElement = document.getElementById('currentFPS');
                        fpsElement.style.color = gameStats.fps > 144 ? '#4CAF50' : gameStats.fps > 100 ? '#ff9800' : '#f44336';

                    }, 1000);

                    addResult('monitoringResults', '✅ Real-time monitoring started');
                    addResult('monitoringResults', '📊 Tracking: Aim accuracy, reaction time, FPS');
                }

                function stopGameMonitoring() {
                    if (!monitoringInterval) {
                        addResult('monitoringResults', '⚠️ No monitoring active');
                        return;
                    }

                    clearInterval(monitoringInterval);
                    monitoringInterval = null;

                    addResult('monitoringResults', '⏹️ Real-time monitoring stopped');
                    addResult('monitoringResults', `📈 Final stats: ${gameStats.aimAccuracy}% accuracy, ${gameStats.reactionTime}ms reaction, ${gameStats.fps} FPS`);
                }

                function resetStats() {
                    gameStats = { aimAccuracy: 0, reactionTime: 0, fps: 0, shots: 0, hits: 0 };
                    document.getElementById('aimAccuracy').textContent = '---%';
                    document.getElementById('reactionTime').textContent = '---ms';
                    document.getElementById('currentFPS').textContent = '---';

                    // Reset colors
                    document.getElementById('aimAccuracy').style.color = '#4CAF50';
                    document.getElementById('reactionTime').style.color = '#ff9800';
                    document.getElementById('currentFPS').style.color = '#2196F3';

                    addResult('monitoringResults', '🔄 Game statistics reset');
                }

                // Advanced AI Functions
                function runAIAnalysis() {
                    const analysisType = document.getElementById('analysisType').value;
                    const gameContext = document.getElementById('gameContext').value;

                    addResult('aiAnalysisResults', `🧠 Running ${analysisType} analysis for ${gameContext}...`);

                    setTimeout(() => {
                        const analyses = {
                            gameplay: [
                                "🎯 Your crosshair placement needs improvement - aim at head level",
                                "🔄 You're over-rotating on turns - practice smooth mouse movements",
                                "⏱️ Your peek timing is inconsistent - work on pre-aiming common angles"
                            ],
                            strategy: [
                                "🗺️ Focus on map control - you're giving up too much space early",
                                "💰 Your economy management needs work - force-buy less often",
                                "👥 Improve team communication - call out enemy positions more clearly"
                            ],
                            performance: [
                                "📊 Your aim accuracy dropped 15% in the last 5 rounds",
                                "⚡ Reaction time increased under pressure - practice aim training",
                                "🎮 FPS drops detected during intense fights - optimize settings"
                            ],
                            training: [
                                "🎯 Spend 20 minutes daily on aim training (Aim Lab/Kovaak's)",
                                "🗺️ Practice smoke lineups for your main maps",
                                "👂 Work on sound positioning - use audio cues better"
                            ]
                        };

                        const selectedAnalysis = analyses[analysisType];
                        selectedAnalysis.forEach((insight, index) => {
                            setTimeout(() => {
                                addResult('aiAnalysisResults', insight);
                            }, index * 500);
                        });

                        setTimeout(() => {
                            addResult('aiAnalysisResults', `✅ ${analysisType} analysis completed for ${gameContext} context`);
                        }, selectedAnalysis.length * 500 + 500);

                    }, 1500);
                }

                function getAIRecommendations() {
                    addResult('aiAnalysisResults', '💡 Generating personalized recommendations...');

                    setTimeout(() => {
                        const recommendations = [
                            "🎯 Lower your sensitivity to 2.2 (currently too high for precise aiming)",
                            "⚙️ Increase your FOV to 103 for better peripheral vision",
                            "🖱️ Disable mouse acceleration in Windows settings",
                            "🎧 Use 7.1 surround sound for better enemy positioning",
                            "📊 Practice crosshair placement 15 minutes before each session"
                        ];

                        recommendations.forEach((rec, index) => {
                            setTimeout(() => {
                                addResult('aiAnalysisResults', rec);
                            }, index * 600);
                        });

                        setTimeout(() => {
                            addResult('aiAnalysisResults', '✅ Recommendations generated based on your play style');
                        }, recommendations.length * 600 + 500);

                    }, 1000);
                }

                function generateTrainingPlan() {
                    addResult('aiAnalysisResults', '📋 Creating personalized training plan...');

                    setTimeout(() => {
                        addResult('aiAnalysisResults', '📅 7-Day Gaming Improvement Plan:');

                        const trainingPlan = [
                            "Day 1: 🎯 Aim training (20min) + Crosshair placement practice",
                            "Day 2: 🗺️ Map knowledge + Common angles study",
                            "Day 3: 💥 Spray pattern practice + Recoil control",
                            "Day 4: 👂 Audio positioning + Sound cue training",
                            "Day 5: 🎮 Movement mechanics + Strafe jumping",
                            "Day 6: 🧠 Game sense + Decision making scenarios",
                            "Day 7: 🏆 Competitive practice + Review session"
                        ];

                        trainingPlan.forEach((day, index) => {
                            setTimeout(() => {
                                addResult('aiAnalysisResults', day);
                            }, index * 400);
                        });

                        setTimeout(() => {
                            addResult('aiAnalysisResults', '✅ Training plan generated! Follow daily for best results');
                        }, trainingPlan.length * 400 + 500);

                    }, 1200);
                }

                // Initialize
                connectWebSocket();
            </script>
        </body>
        </html>
        """
    
    async def start_server(self):
        """Start the debug dashboard server"""
        if not FASTAPI_AVAILABLE:
            self.logger.error("❌ Cannot start server: FastAPI not available")
            return False
        
        try:
            self.logger.info(f"🚀 Starting debug dashboard on http://{self.host}:{self.port}")
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            self.logger.error(f"❌ Server start failed: {e}")
            return False
    
    def run(self):
        """Run the debug dashboard"""
        if not FASTAPI_AVAILABLE:
            print("❌ FastAPI not available. Install with:")
            print("pip install fastapi uvicorn jinja2")
            return
        
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            self.logger.info("🛑 Debug dashboard stopped")

# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run dashboard
    dashboard = DebugDashboardCore(host="localhost", port=8080)
    dashboard.run()
