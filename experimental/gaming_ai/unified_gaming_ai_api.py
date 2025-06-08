#!/usr/bin/env python3
"""
🔗 Unified Gaming AI API - Advanced Feature Integration

Complete unified API integrating all Gaming AI features with Ollama.

Sprint 4 - Task 4.5: Advanced Feature Integration
- Unified API for all features
- Ollama AI model integration
- Feature compatibility matrix
- Comprehensive integration testing

Author: Nexus - Quantum AI Architect
Sprint: 4.5 - Advanced Gaming Features
"""

import time
import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings

# Import all Gaming AI modules
try:
    from game_optimizations import GameOptimizations, GameType
    from performance_monitor import PerformanceMonitor, AlertLevel
    from multi_agent_coordinator import MultiAgentCoordinator, StrategyType
    from team_behaviors import TeamBehaviors, TeamBehaviorType
    GAMING_AI_MODULES_AVAILABLE = True
except ImportError as e:
    GAMING_AI_MODULES_AVAILABLE = False
    warnings.warn(f"🔗 Gaming AI modules import failed: {e}", ImportWarning)

# Ollama integration
try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    warnings.warn("🤖 Ollama integration requires requests library", ImportWarning)

class APIFeature(Enum):
    """Available API features"""
    GAME_OPTIMIZATION = "game_optimization"
    PERFORMANCE_MONITORING = "performance_monitoring"
    MULTI_AGENT_COORDINATION = "multi_agent_coordination"
    TEAM_BEHAVIORS = "team_behaviors"
    AI_ASSISTANCE = "ai_assistance"

class IntegrationLevel(Enum):
    """Integration levels"""
    BASIC = "basic"
    ADVANCED = "advanced"
    FULL = "full"
    AI_ENHANCED = "ai_enhanced"

@dataclass
class APIRequest:
    """Unified API request"""
    request_id: str
    feature: APIFeature
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    ai_assistance: bool = False
    timestamp: float = field(default_factory=time.time)

@dataclass
class APIResponse:
    """Unified API response"""
    request_id: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    ai_insights: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class FeatureCompatibility:
    """Feature compatibility information"""
    feature_a: APIFeature
    feature_b: APIFeature
    compatibility_level: IntegrationLevel
    shared_data: List[str] = field(default_factory=list)
    integration_points: List[str] = field(default_factory=list)

class UnifiedGamingAI:
    """
    Unified Gaming AI API
    
    Features:
    - Unified interface for all Gaming AI features
    - Ollama AI model integration
    - Cross-feature data sharing
    - Intelligent feature coordination
    - Real-time performance optimization
    """
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.logger = logging.getLogger("UnifiedGamingAI")
        self.ollama_host = ollama_host
        
        # Initialize all Gaming AI modules
        self.game_optimizer = None
        self.performance_monitor = None
        self.multi_agent_coordinator = None
        self.team_behaviors = None
        
        if GAMING_AI_MODULES_AVAILABLE:
            self._initialize_gaming_modules()
        
        # API state management
        self.active_sessions = {}  # session_id -> session_data
        self.feature_states = {    # feature -> state
            "game_optimization": {"active": True, "current_game": None},
            "performance_monitoring": {"active": False, "monitoring": False},
            "multi_agent_coordination": {"active": False, "agents": 0},
            "team_behaviors": {"active": True, "teams": 0}
        }
        self.shared_context = {}   # Cross-feature shared data
        
        # Feature compatibility matrix
        self.compatibility_matrix = self._build_compatibility_matrix()
        
        # Performance tracking
        self.api_metrics = {
            "requests_processed": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "ai_assisted_requests": 0
        }
        
        self.logger.info("🔗 Unified Gaming AI API initialized")
    
    def _initialize_gaming_modules(self):
        """Initialize all Gaming AI modules"""
        try:
            # Game Optimizations
            self.game_optimizer = GameOptimizations()
            self.game_optimizer.integrate_game_optimizers()
            
            # Performance Monitor
            self.performance_monitor = PerformanceMonitor(collection_interval=0.5)
            
            # Multi-Agent Coordinator
            self.multi_agent_coordinator = MultiAgentCoordinator(max_agents=8)
            
            # Team Behaviors
            self.team_behaviors = TeamBehaviors()
            
            self.logger.info("✅ All Gaming AI modules initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Gaming AI modules initialization failed: {e}")
    
    def _build_compatibility_matrix(self) -> Dict[str, FeatureCompatibility]:
        """Build feature compatibility matrix"""
        matrix = {}
        
        # Game Optimization + Performance Monitoring
        matrix["game_optimization_performance_monitoring"] = FeatureCompatibility(
            feature_a=APIFeature.GAME_OPTIMIZATION,
            feature_b=APIFeature.PERFORMANCE_MONITORING,
            compatibility_level=IntegrationLevel.FULL,
            shared_data=["game_type", "performance_metrics", "optimization_results"],
            integration_points=["real_time_optimization", "performance_feedback"]
        )

        # Multi-Agent + Team Behaviors
        matrix["multi_agent_coordination_team_behaviors"] = FeatureCompatibility(
            feature_a=APIFeature.MULTI_AGENT_COORDINATION,
            feature_b=APIFeature.TEAM_BEHAVIORS,
            compatibility_level=IntegrationLevel.FULL,
            shared_data=["agent_list", "team_composition", "coordination_state"],
            integration_points=["team_coordination", "behavior_execution"]
        )

        # Performance Monitoring + Multi-Agent
        matrix["performance_monitoring_multi_agent_coordination"] = FeatureCompatibility(
            feature_a=APIFeature.PERFORMANCE_MONITORING,
            feature_b=APIFeature.MULTI_AGENT_COORDINATION,
            compatibility_level=IntegrationLevel.ADVANCED,
            shared_data=["agent_performance", "system_metrics"],
            integration_points=["performance_optimization", "agent_health_monitoring"]
        )

        # Game Optimization + Team Behaviors
        matrix["game_optimization_team_behaviors"] = FeatureCompatibility(
            feature_a=APIFeature.GAME_OPTIMIZATION,
            feature_b=APIFeature.TEAM_BEHAVIORS,
            compatibility_level=IntegrationLevel.ADVANCED,
            shared_data=["game_context", "team_strategy"],
            integration_points=["game_specific_behaviors", "strategy_optimization"]
        )
        
        return matrix
    
    async def process_request(self, request: APIRequest) -> APIResponse:
        """Process unified API request"""
        start_time = time.time()
        
        try:
            self.logger.info(f"🔗 Processing request: {request.feature.value}.{request.action}")
            
            # Update metrics
            self.api_metrics["requests_processed"] += 1
            if request.ai_assistance:
                self.api_metrics["ai_assisted_requests"] += 1
            
            # Route request to appropriate handler
            if request.feature == APIFeature.GAME_OPTIMIZATION:
                response_data = await self._handle_game_optimization(request)
            elif request.feature == APIFeature.PERFORMANCE_MONITORING:
                response_data = await self._handle_performance_monitoring(request)
            elif request.feature == APIFeature.MULTI_AGENT_COORDINATION:
                response_data = await self._handle_multi_agent_coordination(request)
            elif request.feature == APIFeature.TEAM_BEHAVIORS:
                response_data = await self._handle_team_behaviors(request)
            elif request.feature == APIFeature.AI_ASSISTANCE:
                response_data = await self._handle_ai_assistance(request)
            else:
                raise ValueError(f"Unknown feature: {request.feature}")
            
            # Add AI insights if requested
            ai_insights = None
            if request.ai_assistance and OLLAMA_AVAILABLE:
                ai_insights = await self._get_ai_insights(request, response_data)
            
            # Create response
            execution_time = time.time() - start_time
            response = APIResponse(
                request_id=request.request_id,
                success=True,
                data=response_data,
                ai_insights=ai_insights,
                execution_time=execution_time
            )
            
            # Update metrics
            self.api_metrics["successful_requests"] += 1
            self._update_response_time_metric(execution_time)
            
            # Update shared context
            self._update_shared_context(request, response_data)
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Request processing failed: {e}")
            
            self.api_metrics["failed_requests"] += 1
            
            return APIResponse(
                request_id=request.request_id,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def _handle_game_optimization(self, request: APIRequest) -> Dict[str, Any]:
        """Handle game optimization requests"""
        if not self.game_optimizer:
            raise RuntimeError("Game optimizer not available")
        
        action = request.action
        params = request.parameters
        
        if action == "detect_game":
            process_name = params.get("process_name", "")
            window_title = params.get("window_title", "")
            game_type = self.game_optimizer.detect_game(process_name, window_title)
            
            # Update shared context
            self.shared_context["current_game"] = game_type
            self.feature_states["game_optimization"]["current_game"] = game_type
            
            return {"game_type": game_type.value, "detected": True}
        
        elif action == "apply_optimizations":
            game_type = params.get("game_type")
            if isinstance(game_type, str):
                game_type = GameType(game_type)
            
            optimizations = self.game_optimizer.apply_optimizations(game_type)
            
            return {
                "optimizations_applied": len(optimizations),
                "optimizations": optimizations,
                "game_type": game_type.value
            }
        
        elif action == "get_comprehensive_optimizations":
            game_type = params.get("game_type")
            if isinstance(game_type, str):
                game_type = GameType(game_type)
            
            result = self.game_optimizer.apply_comprehensive_optimizations(game_type)
            
            return result
        
        elif action == "get_optimization_summary":
            return self.game_optimizer.get_optimization_summary()
        
        else:
            raise ValueError(f"Unknown game optimization action: {action}")
    
    async def _handle_performance_monitoring(self, request: APIRequest) -> Dict[str, Any]:
        """Handle performance monitoring requests"""
        if not self.performance_monitor:
            raise RuntimeError("Performance monitor not available")
        
        action = request.action
        params = request.parameters
        
        if action == "start_monitoring":
            success = self.performance_monitor.start_monitoring()
            self.feature_states["performance_monitoring"]["monitoring"] = success

            return {"monitoring_started": success}

        elif action == "stop_monitoring":
            self.performance_monitor.stop_monitoring()
            self.feature_states["performance_monitoring"]["monitoring"] = False

            return {"monitoring_stopped": True}
        
        elif action == "get_current_performance":
            current = self.performance_monitor.get_current_performance()
            if current:
                metrics = {}
                for metric_type, metric in current.metrics.items():
                    metrics[metric_type.value] = {
                        "value": metric.value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp
                    }
                
                # Update shared context
                self.shared_context["performance_metrics"] = metrics
                
                return {"current_performance": metrics}
            else:
                return {"current_performance": None}
        
        elif action == "get_analytics":
            analytics = self.performance_monitor.get_performance_analytics()
            return {"analytics": analytics}
        
        elif action == "get_optimization_suggestions":
            suggestions = self.performance_monitor.get_optimization_suggestions()
            return {"suggestions": suggestions}
        
        elif action == "get_bottlenecks":
            bottlenecks = self.performance_monitor.get_active_bottlenecks()
            bottleneck_data = []
            for bottleneck in bottlenecks:
                bottleneck_data.append({
                    "type": bottleneck.bottleneck_type.value,
                    "severity": bottleneck.severity,
                    "description": bottleneck.description,
                    "suggestions": bottleneck.suggestions
                })
            
            return {"active_bottlenecks": bottleneck_data}
        
        else:
            raise ValueError(f"Unknown performance monitoring action: {action}")
    
    async def _handle_multi_agent_coordination(self, request: APIRequest) -> Dict[str, Any]:
        """Handle multi-agent coordination requests"""
        if not self.multi_agent_coordinator:
            raise RuntimeError("Multi-agent coordinator not available")
        
        action = request.action
        params = request.parameters
        
        if action == "start_coordination":
            success = self.multi_agent_coordinator.start_coordination()
            self.feature_states["multi_agent_coordination"]["active"] = success

            return {"coordination_started": success}

        elif action == "stop_coordination":
            success = self.multi_agent_coordinator.stop_coordination()
            self.feature_states["multi_agent_coordination"]["active"] = False

            return {"coordination_stopped": success}
        
        elif action == "register_agent":
            agent_id = params.get("agent_id")
            agent_type = params.get("agent_type", "default")
            capabilities = params.get("capabilities", [])
            
            # Create dummy callback for API
            def dummy_callback(message):
                pass
            
            success = self.multi_agent_coordinator.register_agent(
                agent_id, agent_type, capabilities, dummy_callback
            )
            
            if success:
                current_agents = self.feature_states["multi_agent_coordination"]["agents"]
                self.feature_states["multi_agent_coordination"]["agents"] = current_agents + 1
            
            return {"agent_registered": success, "agent_id": agent_id}
        
        elif action == "create_team":
            team_id = params.get("team_id")
            agent_ids = params.get("agent_ids", [])
            strategy_type = params.get("strategy_type")
            
            if isinstance(strategy_type, str):
                strategy_type = StrategyType(strategy_type)
            
            success = self.multi_agent_coordinator.create_team(team_id, agent_ids, strategy_type)
            
            return {"team_created": success, "team_id": team_id}
        
        elif action == "get_coordination_stats":
            stats = self.multi_agent_coordinator.get_coordination_stats()
            
            # Update shared context
            self.shared_context["coordination_stats"] = stats
            
            return {"coordination_stats": stats}
        
        elif action == "get_agent_list":
            agents = self.multi_agent_coordinator.get_agent_list()
            return {"agents": agents}
        
        else:
            raise ValueError(f"Unknown multi-agent coordination action: {action}")
    
    async def _handle_team_behaviors(self, request: APIRequest) -> Dict[str, Any]:
        """Handle team behaviors requests"""
        if not self.team_behaviors:
            raise RuntimeError("Team behaviors not available")
        
        action = request.action
        params = request.parameters
        
        if action == "get_available_behaviors":
            behaviors = self.team_behaviors.get_available_behaviors()
            return {"available_behaviors": [b.value for b in behaviors]}
        
        elif action == "execute_behavior":
            behavior_type = params.get("behavior_type")
            context = params.get("context", {})
            
            if isinstance(behavior_type, str):
                behavior_type = TeamBehaviorType(behavior_type)
            
            result = self.team_behaviors.execute_behavior(behavior_type, context)
            
            return {"behavior_execution": result}
        
        elif action == "create_team_behavior":
            team_id = params.get("team_id")
            agent_ids = params.get("agent_ids", [])
            behavior_type = params.get("behavior_type")
            
            if isinstance(behavior_type, str):
                behavior_type = TeamBehaviorType(behavior_type)
            
            behavior_id = self.team_behaviors.create_team_behavior(team_id, agent_ids, behavior_type)
            
            return {"behavior_created": bool(behavior_id), "behavior_id": behavior_id}
        
        elif action == "get_team_metrics":
            metrics = self.team_behaviors.get_team_metrics()
            return {"team_metrics": metrics}
        
        else:
            raise ValueError(f"Unknown team behaviors action: {action}")
    
    async def _handle_ai_assistance(self, request: APIRequest) -> Dict[str, Any]:
        """Handle AI assistance requests"""
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("Ollama not available")
        
        action = request.action
        params = request.parameters
        
        if action == "get_gaming_advice":
            context = params.get("context", {})
            query = params.get("query", "")
            
            advice = await self._get_ollama_gaming_advice(query, context)
            
            return {"ai_advice": advice}
        
        elif action == "analyze_performance":
            performance_data = params.get("performance_data", {})
            
            analysis = await self._get_ollama_performance_analysis(performance_data)
            
            return {"ai_analysis": analysis}
        
        elif action == "suggest_optimizations":
            game_context = params.get("game_context", {})
            
            suggestions = await self._get_ollama_optimization_suggestions(game_context)
            
            return {"ai_suggestions": suggestions}
        
        else:
            raise ValueError(f"Unknown AI assistance action: {action}")
    
    async def _get_ai_insights(self, request: APIRequest, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI insights for request/response"""
        if not OLLAMA_AVAILABLE:
            return None
        
        try:
            # Create context for AI
            context = {
                "feature": request.feature.value,
                "action": request.action,
                "parameters": request.parameters,
                "response": response_data,
                "shared_context": self.shared_context
            }
            
            # Get AI insights
            insights = await self._query_ollama_insights(context)
            
            return {"insights": insights, "generated_at": time.time()}
            
        except Exception as e:
            self.logger.warning(f"⚠️ AI insights generation failed: {e}")
            return None

    async def _query_ollama_insights(self, context: Dict[str, Any]) -> str:
        """Query Ollama for AI insights"""
        try:
            # Safely serialize context data
            parameters_str = self._safe_json_serialize(context['parameters'])
            response_str = self._safe_json_serialize(context['response'])

            prompt = f"""
            You are an expert Gaming AI assistant. Analyze the following Gaming AI operation and provide insights:

            Feature: {context['feature']}
            Action: {context['action']}
            Parameters: {parameters_str}
            Response: {response_str}

            Provide brief, actionable insights about:
            1. Performance optimization opportunities
            2. Potential improvements
            3. Gaming strategy recommendations

            Keep response under 200 words and focus on practical advice.
            """

            response = await self._call_ollama(prompt)
            return response

        except Exception as e:
            self.logger.error(f"❌ Ollama insights query failed: {e}")
            return "AI insights temporarily unavailable"

    async def _get_ollama_gaming_advice(self, query: str, context: Dict[str, Any]) -> str:
        """Get gaming advice from Ollama"""
        try:
            prompt = f"""
            You are a professional gaming coach and AI expert. Answer this gaming question:

            Question: {query}

            Gaming Context:
            {self._safe_json_serialize(context)}

            Provide specific, actionable gaming advice. Focus on:
            - Tactical improvements
            - Performance optimization
            - Strategic recommendations

            Keep response concise and practical.
            """

            response = await self._call_ollama(prompt)
            return response

        except Exception as e:
            self.logger.error(f"❌ Ollama gaming advice failed: {e}")
            return "Gaming advice temporarily unavailable"

    async def _get_ollama_performance_analysis(self, performance_data: Dict[str, Any]) -> str:
        """Get performance analysis from Ollama"""
        try:
            prompt = f"""
            You are a gaming performance analyst. Analyze this performance data:

            Performance Data:
            {self._safe_json_serialize(performance_data)}

            Provide analysis covering:
            1. Performance bottlenecks
            2. Optimization priorities
            3. Hardware recommendations
            4. Settings adjustments

            Be specific and actionable in your recommendations.
            """

            response = await self._call_ollama(prompt)
            return response

        except Exception as e:
            self.logger.error(f"❌ Ollama performance analysis failed: {e}")
            return "Performance analysis temporarily unavailable"

    async def _get_ollama_optimization_suggestions(self, game_context: Dict[str, Any]) -> str:
        """Get optimization suggestions from Ollama"""
        try:
            prompt = f"""
            You are a gaming optimization expert. Based on this game context, suggest optimizations:

            Game Context:
            {self._safe_json_serialize(game_context)}

            Provide optimization suggestions for:
            1. Graphics settings
            2. Input optimization
            3. Network settings
            4. System performance
            5. Game-specific tweaks

            Prioritize suggestions by impact and provide specific values where possible.
            """

            response = await self._call_ollama(prompt)
            return response

        except Exception as e:
            self.logger.error(f"❌ Ollama optimization suggestions failed: {e}")
            return "Optimization suggestions temporarily unavailable"

    async def _call_ollama(self, prompt: str, model: str = "llama3.2:3b") -> str:
        """Call Ollama API"""
        try:
            if not OLLAMA_AVAILABLE:
                return "Ollama not available"

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from AI")
            else:
                return f"Ollama API error: {response.status_code}"

        except Exception as e:
            self.logger.error(f"❌ Ollama API call failed: {e}")
            return "AI service temporarily unavailable"

    def _safe_json_serialize(self, obj: Any) -> str:
        """Safely serialize object to JSON string"""
        try:
            return json.dumps(obj, indent=2, default=self._json_serializer)
        except Exception as e:
            self.logger.warning(f"⚠️ JSON serialization failed: {e}")
            return str(obj)

    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for complex objects"""
        try:
            # Handle dataclass objects
            if hasattr(obj, '__dataclass_fields__'):
                return {field: getattr(obj, field) for field in obj.__dataclass_fields__}

            # Handle objects with __dict__
            if hasattr(obj, '__dict__'):
                return obj.__dict__

            # Handle enum objects
            if hasattr(obj, 'value'):
                return obj.value

            # Handle other iterables
            if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
                return list(obj)

            # Fallback to string representation
            return str(obj)

        except Exception:
            return str(obj)

    def _update_response_time_metric(self, execution_time: float):
        """Update average response time metric"""
        current_avg = self.api_metrics["average_response_time"]
        total_requests = self.api_metrics["successful_requests"]

        if total_requests > 0:
            self.api_metrics["average_response_time"] = (
                (current_avg * (total_requests - 1) + execution_time) / total_requests
            )

    def _update_shared_context(self, request: APIRequest, response_data: Dict[str, Any]):
        """Update shared context with request/response data"""
        try:
            # Update feature-specific context
            feature_key = f"{request.feature.value}_last_response"
            self.shared_context[feature_key] = {
                "action": request.action,
                "response": response_data,
                "timestamp": time.time()
            }

            # Update cross-feature context based on feature type
            if request.feature == APIFeature.GAME_OPTIMIZATION:
                if "game_type" in response_data:
                    self.shared_context["current_game_type"] = response_data["game_type"]

            elif request.feature == APIFeature.PERFORMANCE_MONITORING:
                if "current_performance" in response_data:
                    self.shared_context["latest_performance"] = response_data["current_performance"]

            elif request.feature == APIFeature.MULTI_AGENT_COORDINATION:
                if "coordination_stats" in response_data:
                    self.shared_context["coordination_status"] = response_data["coordination_stats"]

        except Exception as e:
            self.logger.warning(f"⚠️ Shared context update failed: {e}")

    def get_feature_compatibility(self, feature_a: APIFeature, feature_b: APIFeature) -> Optional[FeatureCompatibility]:
        """Get compatibility information between two features"""
        key1 = f"{feature_a.value}_{feature_b.value}"
        key2 = f"{feature_b.value}_{feature_a.value}"

        return self.compatibility_matrix.get(key1) or self.compatibility_matrix.get(key2)

    def get_api_status(self) -> Dict[str, Any]:
        """Get unified API status"""
        return {
            "api_version": "1.0.0",
            "features_available": GAMING_AI_MODULES_AVAILABLE,
            "ollama_available": OLLAMA_AVAILABLE,
            "active_features": [
                feature for feature, state in self.feature_states.items()
                if state.get("active", False)
            ],
            "feature_states": self.feature_states,
            "shared_context_keys": list(self.shared_context.keys()),
            "compatibility_matrix_size": len(self.compatibility_matrix),
            "metrics": self.api_metrics,
            "ollama_host": self.ollama_host
        }

    def get_integration_recommendations(self) -> List[Dict[str, Any]]:
        """Get feature integration recommendations"""
        recommendations = []

        # Check for beneficial integrations
        if (self.feature_states["game_optimization"]["active"] and
            not self.feature_states["performance_monitoring"]["monitoring"]):
            recommendations.append({
                "type": "integration_opportunity",
                "features": ["game_optimization", "performance_monitoring"],
                "benefit": "Real-time optimization based on performance feedback",
                "action": "Start performance monitoring to enhance game optimizations"
            })

        if (self.feature_states["multi_agent_coordination"]["active"] and
            self.feature_states["team_behaviors"]["teams"] == 0):
            recommendations.append({
                "type": "integration_opportunity",
                "features": ["multi_agent_coordination", "team_behaviors"],
                "benefit": "Enhanced team coordination with behavior patterns",
                "action": "Create team behaviors for coordinated agents"
            })

        # Check for optimization opportunities
        if self.api_metrics["ai_assisted_requests"] == 0:
            recommendations.append({
                "type": "enhancement_opportunity",
                "features": ["ai_assistance"],
                "benefit": "AI-powered insights and recommendations",
                "action": "Enable AI assistance for intelligent gaming optimization"
            })

        return recommendations

# Convenience functions for easy API usage
def create_request(feature: str, action: str, parameters: Dict[str, Any] = None,
                  ai_assistance: bool = False) -> APIRequest:
    """Create API request"""
    import uuid

    return APIRequest(
        request_id=str(uuid.uuid4()),
        feature=APIFeature(feature),
        action=action,
        parameters=parameters or {},
        ai_assistance=ai_assistance
    )

async def quick_optimize_game(api: UnifiedGamingAI, game_type: str, ai_assistance: bool = True) -> APIResponse:
    """Quick game optimization with optional AI assistance"""
    request = create_request(
        feature="game_optimization",
        action="get_comprehensive_optimizations",
        parameters={"game_type": game_type},
        ai_assistance=ai_assistance
    )

    return await api.process_request(request)

async def quick_performance_check(api: UnifiedGamingAI, ai_assistance: bool = True) -> APIResponse:
    """Quick performance check with optional AI assistance"""
    request = create_request(
        feature="performance_monitoring",
        action="get_current_performance",
        ai_assistance=ai_assistance
    )

    return await api.process_request(request)

# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def test_unified_api():
        """Test unified Gaming AI API"""
        print("🔗 UNIFIED GAMING AI API TEST")
        print("=" * 60)

        # Initialize API
        api = UnifiedGamingAI()

        # Test API status
        status = api.get_api_status()
        print(f"📊 API Status:")
        print(f"  - Features available: {status['features_available']}")
        print(f"  - Ollama available: {status['ollama_available']}")
        print(f"  - Active features: {len(status['active_features'])}")

        # Test game optimization
        print(f"\n🎮 Testing Game Optimization...")
        game_request = create_request(
            feature="game_optimization",
            action="get_optimization_summary"
        )

        game_response = await api.process_request(game_request)
        print(f"  - Success: {game_response.success}")
        print(f"  - Execution time: {game_response.execution_time:.3f}s")

        # Test performance monitoring
        print(f"\n📊 Testing Performance Monitoring...")
        perf_request = create_request(
            feature="performance_monitoring",
            action="start_monitoring"
        )

        perf_response = await api.process_request(perf_request)
        print(f"  - Success: {perf_response.success}")
        print(f"  - Monitoring started: {perf_response.data.get('monitoring_started', False)}")

        # Wait a bit for data collection
        await asyncio.sleep(1.0)

        # Get current performance
        current_perf_request = create_request(
            feature="performance_monitoring",
            action="get_current_performance",
            ai_assistance=True  # Test AI assistance
        )

        current_perf_response = await api.process_request(current_perf_request)
        print(f"  - Performance data: {'Available' if current_perf_response.data.get('current_performance') else 'Not available'}")
        print(f"  - AI insights: {'Available' if current_perf_response.ai_insights else 'Not available'}")

        # Test multi-agent coordination
        print(f"\n🤝 Testing Multi-Agent Coordination...")
        coord_request = create_request(
            feature="multi_agent_coordination",
            action="start_coordination"
        )

        coord_response = await api.process_request(coord_request)
        print(f"  - Success: {coord_response.success}")
        print(f"  - Coordination started: {coord_response.data.get('coordination_started', False)}")

        # Test team behaviors
        print(f"\n🧠 Testing Team Behaviors...")
        behavior_request = create_request(
            feature="team_behaviors",
            action="get_available_behaviors"
        )

        behavior_response = await api.process_request(behavior_request)
        print(f"  - Success: {behavior_response.success}")
        behaviors = behavior_response.data.get('available_behaviors', [])
        print(f"  - Available behaviors: {len(behaviors)}")

        # Test AI assistance (if available)
        if status['ollama_available']:
            print(f"\n🤖 Testing AI Assistance...")
            ai_request = create_request(
                feature="ai_assistance",
                action="get_gaming_advice",
                parameters={
                    "query": "How can I improve my FPS in competitive gaming?",
                    "context": {"game": "VALORANT", "current_fps": 60}
                }
            )

            ai_response = await api.process_request(ai_request)
            print(f"  - Success: {ai_response.success}")
            if ai_response.success:
                advice = ai_response.data.get('ai_advice', '')
                print(f"  - AI advice length: {len(advice)} characters")

        # Get integration recommendations
        print(f"\n💡 Integration Recommendations:")
        recommendations = api.get_integration_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['type']}: {rec['benefit']}")

        # Final metrics
        final_status = api.get_api_status()
        metrics = final_status['metrics']
        print(f"\n📊 Final Metrics:")
        print(f"  - Requests processed: {metrics['requests_processed']}")
        print(f"  - Success rate: {metrics['successful_requests']}/{metrics['requests_processed']}")
        print(f"  - Average response time: {metrics['average_response_time']:.3f}s")
        print(f"  - AI assisted requests: {metrics['ai_assisted_requests']}")

        # Stop monitoring
        stop_request = create_request(
            feature="performance_monitoring",
            action="stop_monitoring"
        )
        await api.process_request(stop_request)

        print(f"\n✅ Unified Gaming AI API test completed!")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run test
    asyncio.run(test_unified_api())
