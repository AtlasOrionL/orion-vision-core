#!/usr/bin/env python3
"""
🧠 Game State Analyzer - Gaming AI

Real-time game state understanding and analysis system.

Sprint 3 - Task 3.1: Game State Analysis Implementation
- Real-time game state detection (60 FPS)
- Multi-game support (5+ game types)
- Context extraction accuracy >85%
- State change detection <50ms

Author: Nexus - Quantum AI Architect
Sprint: 3.1 - AI Intelligence & Decision Making
"""

import time
import cv2
import numpy as np
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import warnings

# Import vision system from Sprint 1
try:
    import sys
    sys.path.append('../')
    from vision_core.advanced_ocr import AdvancedOCR
    from vision_core.screen_capture import ScreenCapture
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    warnings.warn("🎮 Vision system not available", ImportWarning)

class GameType(Enum):
    """Supported game types"""
    FPS = "fps"  # First Person Shooter
    MOBA = "moba"  # Multiplayer Online Battle Arena
    RTS = "rts"  # Real Time Strategy
    RPG = "rpg"  # Role Playing Game
    BATTLE_ROYALE = "battle_royale"
    UNKNOWN = "unknown"

class GameState(Enum):
    """Game state enumeration"""
    MENU = "menu"
    LOADING = "loading"
    IN_GAME = "in_game"
    PAUSED = "paused"
    INVENTORY = "inventory"
    SETTINGS = "settings"
    DEAD = "dead"
    VICTORY = "victory"
    DEFEAT = "defeat"
    UNKNOWN = "unknown"

@dataclass
class GameContext:
    """Game context information"""
    game_type: GameType
    current_state: GameState
    confidence: float
    timestamp: float
    screen_region: Optional[Tuple[int, int, int, int]] = None
    extracted_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StateTransition:
    """Game state transition"""
    from_state: GameState
    to_state: GameState
    timestamp: float
    confidence: float
    trigger_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalysisMetrics:
    """Game state analysis metrics"""
    frames_analyzed: int = 0
    state_changes_detected: int = 0
    average_analysis_time: float = 0.0
    accuracy_rate: float = 0.0
    fps: float = 0.0

class GameStateAnalyzer:
    """
    Real-time Game State Analysis System
    
    Features:
    - Real-time game state detection (60 FPS target)
    - Multi-game support with adaptive recognition
    - Context extraction and understanding
    - State change detection and tracking
    - Performance optimization for real-time analysis
    """
    
    def __init__(self, target_fps: float = 60.0):
        self.target_fps = target_fps
        self.logger = logging.getLogger("GameStateAnalyzer")
        
        # Analysis configuration
        self.current_game_type = GameType.UNKNOWN
        self.current_context = None
        self.state_history = []
        self.metrics = AnalysisMetrics()
        
        # Threading and real-time processing
        self.analysis_active = False
        self.analysis_thread = None
        self.analysis_lock = threading.RLock()
        
        # Vision system integration
        self.screen_capture = None
        self.ocr_engine = None
        self._initialize_vision_systems()
        
        # Game-specific analyzers
        self.game_analyzers = {}
        self._initialize_game_analyzers()
        
        # State detection patterns
        self.state_patterns = {}
        self._initialize_state_patterns()
        
        # Performance tracking
        self.frame_times = []
        self.last_analysis_time = 0.0
        
        self.logger.info(f"🧠 Game State Analyzer initialized (target: {target_fps} FPS)")
    
    def _initialize_vision_systems(self):
        """Initialize vision system components"""
        if VISION_AVAILABLE:
            try:
                self.screen_capture = ScreenCapture()
                self.ocr_engine = AdvancedOCR()
                self.logger.info("✅ Vision systems initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Vision system initialization failed: {e}")
        else:
            self.logger.warning("⚠️ Vision systems not available")
    
    def _initialize_game_analyzers(self):
        """Initialize game-specific analyzers"""
        self.game_analyzers = {
            GameType.FPS: self._analyze_fps_game,
            GameType.MOBA: self._analyze_moba_game,
            GameType.RTS: self._analyze_rts_game,
            GameType.RPG: self._analyze_rpg_game,
            GameType.BATTLE_ROYALE: self._analyze_battle_royale_game
        }
    
    def _initialize_state_patterns(self):
        """Initialize state detection patterns"""
        self.state_patterns = {
            GameState.MENU: {
                "text_patterns": ["play", "start", "menu", "options", "quit"],
                "ui_elements": ["buttons", "menu_items"],
                "color_patterns": [(50, 50, 50), (200, 200, 200)],  # Common menu colors
                "confidence_threshold": 0.7
            },
            
            GameState.LOADING: {
                "text_patterns": ["loading", "please wait", "connecting"],
                "ui_elements": ["progress_bar", "spinner"],
                "color_patterns": [(0, 0, 0), (100, 100, 100)],  # Dark loading screens
                "confidence_threshold": 0.8
            },
            
            GameState.IN_GAME: {
                "text_patterns": ["health", "ammo", "score", "time"],
                "ui_elements": ["hud", "minimap", "crosshair"],
                "color_patterns": [(255, 0, 0), (0, 255, 0), (0, 0, 255)],  # HUD colors
                "confidence_threshold": 0.6
            },
            
            GameState.PAUSED: {
                "text_patterns": ["paused", "resume", "settings"],
                "ui_elements": ["pause_menu", "overlay"],
                "color_patterns": [(128, 128, 128)],  # Grayed out
                "confidence_threshold": 0.8
            },
            
            GameState.DEAD: {
                "text_patterns": ["you died", "respawn", "game over"],
                "ui_elements": ["death_screen", "respawn_timer"],
                "color_patterns": [(255, 0, 0), (0, 0, 0)],  # Red/black death screens
                "confidence_threshold": 0.9
            },
            
            GameState.VICTORY: {
                "text_patterns": ["victory", "you win", "success", "completed"],
                "ui_elements": ["victory_screen", "celebration"],
                "color_patterns": [(255, 215, 0), (0, 255, 0)],  # Gold/green victory
                "confidence_threshold": 0.9
            },
            
            GameState.DEFEAT: {
                "text_patterns": ["defeat", "you lose", "failed", "game over"],
                "ui_elements": ["defeat_screen"],
                "color_patterns": [(255, 0, 0), (128, 0, 0)],  # Red defeat
                "confidence_threshold": 0.9
            }
        }
    
    def detect_game_type(self, frame: np.ndarray) -> Tuple[GameType, float]:
        """Detect the type of game being played"""
        try:
            # Extract features for game type detection
            features = self._extract_game_features(frame)
            
            # Game type detection logic
            confidence_scores = {}
            
            # FPS detection
            fps_score = self._calculate_fps_score(features)
            confidence_scores[GameType.FPS] = fps_score
            
            # MOBA detection
            moba_score = self._calculate_moba_score(features)
            confidence_scores[GameType.MOBA] = moba_score
            
            # RTS detection
            rts_score = self._calculate_rts_score(features)
            confidence_scores[GameType.RTS] = rts_score
            
            # RPG detection
            rpg_score = self._calculate_rpg_score(features)
            confidence_scores[GameType.RPG] = rpg_score
            
            # Battle Royale detection
            br_score = self._calculate_battle_royale_score(features)
            confidence_scores[GameType.BATTLE_ROYALE] = br_score
            
            # Select highest confidence game type
            best_game_type = max(confidence_scores, key=confidence_scores.get)
            best_confidence = confidence_scores[best_game_type]
            
            # Require minimum confidence
            if best_confidence < 0.5:
                return GameType.UNKNOWN, best_confidence
            
            return best_game_type, best_confidence
            
        except Exception as e:
            self.logger.error(f"❌ Game type detection failed: {e}")
            return GameType.UNKNOWN, 0.0
    
    def _extract_game_features(self, frame: np.ndarray) -> Dict[str, Any]:
        """Extract features for game analysis"""
        features = {
            "frame_shape": frame.shape,
            "color_histogram": cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]),
            "edge_density": 0.0,
            "text_regions": [],
            "ui_elements": []
        }
        
        try:
            # Edge detection for UI analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            features["edge_density"] = np.sum(edges > 0) / edges.size
            
            # Text detection using OCR
            if self.ocr_engine:
                text_results = self.ocr_engine.extract_text(frame)
                features["text_regions"] = text_results.get("regions", [])
            
            # UI element detection (simplified)
            features["ui_elements"] = self._detect_ui_elements(frame)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Feature extraction error: {e}")
        
        return features
    
    def _detect_ui_elements(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements in frame"""
        ui_elements = []
        
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect rectangular UI elements
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter by area
                area = cv2.contourArea(contour)
                if 100 < area < 10000:  # Reasonable UI element size
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    # Classify UI element type
                    element_type = "unknown"
                    if 0.8 < aspect_ratio < 1.2:
                        element_type = "button"
                    elif aspect_ratio > 3:
                        element_type = "bar"
                    elif aspect_ratio < 0.5:
                        element_type = "vertical_bar"
                    
                    ui_elements.append({
                        "type": element_type,
                        "bbox": (x, y, w, h),
                        "area": area,
                        "aspect_ratio": aspect_ratio
                    })
            
        except Exception as e:
            self.logger.warning(f"⚠️ UI element detection error: {e}")
        
        return ui_elements[:20]  # Limit to top 20 elements
    
    def _calculate_fps_score(self, features: Dict[str, Any]) -> float:
        """Calculate FPS game confidence score"""
        score = 0.0
        
        # Check for FPS-specific features
        text_regions = features.get("text_regions", [])
        ui_elements = features.get("ui_elements", [])
        
        # Look for FPS indicators
        fps_keywords = ["health", "ammo", "weapon", "crosshair", "kill", "death"]
        for region in text_regions:
            text = region.get("text", "").lower()
            for keyword in fps_keywords:
                if keyword in text:
                    score += 0.2
        
        # Check UI layout (HUD elements)
        if len(ui_elements) > 5:  # FPS games typically have many HUD elements
            score += 0.3
        
        # Edge density (FPS games often have sharp edges)
        edge_density = features.get("edge_density", 0.0)
        if edge_density > 0.1:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_moba_score(self, features: Dict[str, Any]) -> float:
        """Calculate MOBA game confidence score"""
        score = 0.0
        
        text_regions = features.get("text_regions", [])
        ui_elements = features.get("ui_elements", [])
        
        # MOBA-specific keywords
        moba_keywords = ["level", "gold", "mana", "ability", "minion", "tower"]
        for region in text_regions:
            text = region.get("text", "").lower()
            for keyword in moba_keywords:
                if keyword in text:
                    score += 0.2
        
        # MOBA games typically have complex UI
        if len(ui_elements) > 10:
            score += 0.4
        
        return min(1.0, score)
    
    def _calculate_rts_score(self, features: Dict[str, Any]) -> float:
        """Calculate RTS game confidence score"""
        score = 0.0
        
        text_regions = features.get("text_regions", [])
        ui_elements = features.get("ui_elements", [])
        
        # RTS-specific keywords
        rts_keywords = ["resources", "units", "build", "command", "army"]
        for region in text_regions:
            text = region.get("text", "").lower()
            for keyword in rts_keywords:
                if keyword in text:
                    score += 0.25
        
        # RTS games have many UI panels
        if len(ui_elements) > 8:
            score += 0.3
        
        return min(1.0, score)
    
    def _calculate_rpg_score(self, features: Dict[str, Any]) -> float:
        """Calculate RPG game confidence score"""
        score = 0.0
        
        text_regions = features.get("text_regions", [])
        
        # RPG-specific keywords
        rpg_keywords = ["experience", "level", "quest", "inventory", "stats", "magic"]
        for region in text_regions:
            text = region.get("text", "").lower()
            for keyword in rpg_keywords:
                if keyword in text:
                    score += 0.2
        
        return min(1.0, score)
    
    def _calculate_battle_royale_score(self, features: Dict[str, Any]) -> float:
        """Calculate Battle Royale game confidence score"""
        score = 0.0
        
        text_regions = features.get("text_regions", [])
        
        # Battle Royale keywords
        br_keywords = ["zone", "circle", "players", "alive", "storm", "drop"]
        for region in text_regions:
            text = region.get("text", "").lower()
            for keyword in br_keywords:
                if keyword in text:
                    score += 0.25
        
        return min(1.0, score)
    
    def analyze_game_state(self, frame: np.ndarray) -> GameContext:
        """Analyze current game state from frame"""
        start_time = time.time()
        
        try:
            # Detect game type if unknown
            if self.current_game_type == GameType.UNKNOWN:
                game_type, confidence = self.detect_game_type(frame)
                if confidence > 0.7:
                    self.current_game_type = game_type
                    self.logger.info(f"🎮 Game type detected: {game_type.value} ({confidence:.2f})")
            
            # Analyze current state
            current_state, state_confidence = self._detect_current_state(frame)
            
            # Extract context data
            context_data = self._extract_context_data(frame, current_state)
            
            # Create game context
            context = GameContext(
                game_type=self.current_game_type,
                current_state=current_state,
                confidence=state_confidence,
                timestamp=time.time(),
                extracted_data=context_data
            )
            
            # Track state changes
            self._track_state_change(context)
            
            # Update metrics
            analysis_time = time.time() - start_time
            self._update_metrics(analysis_time)
            
            self.current_context = context
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Game state analysis failed: {e}")
            return GameContext(
                game_type=GameType.UNKNOWN,
                current_state=GameState.UNKNOWN,
                confidence=0.0,
                timestamp=time.time()
            )
    
    def _detect_current_state(self, frame: np.ndarray) -> Tuple[GameState, float]:
        """Detect current game state"""
        state_scores = {}
        
        # Extract features for state detection
        features = self._extract_game_features(frame)
        
        # Check each state pattern
        for state, pattern in self.state_patterns.items():
            score = self._calculate_state_score(features, pattern)
            state_scores[state] = score
        
        # Select best state
        best_state = max(state_scores, key=state_scores.get)
        best_confidence = state_scores[best_state]
        
        # Apply confidence threshold
        threshold = self.state_patterns[best_state]["confidence_threshold"]
        if best_confidence < threshold:
            return GameState.UNKNOWN, best_confidence
        
        return best_state, best_confidence
    
    def _calculate_state_score(self, features: Dict[str, Any], pattern: Dict[str, Any]) -> float:
        """Calculate state confidence score"""
        score = 0.0
        
        # Text pattern matching
        text_patterns = pattern.get("text_patterns", [])
        text_regions = features.get("text_regions", [])
        
        for region in text_regions:
            text = region.get("text", "").lower()
            for pattern_text in text_patterns:
                if pattern_text in text:
                    score += 0.3
        
        # UI element matching
        ui_patterns = pattern.get("ui_elements", [])
        ui_elements = features.get("ui_elements", [])
        
        for ui_element in ui_elements:
            element_type = ui_element.get("type", "")
            if element_type in ui_patterns:
                score += 0.2
        
        # Color pattern matching (simplified)
        color_patterns = pattern.get("color_patterns", [])
        if color_patterns:
            score += 0.1  # Basic color presence
        
        return min(1.0, score)
    
    def _extract_context_data(self, frame: np.ndarray, state: GameState) -> Dict[str, Any]:
        """Extract context-specific data"""
        context_data = {}
        
        try:
            # Use game-specific analyzer if available
            if self.current_game_type in self.game_analyzers:
                analyzer = self.game_analyzers[self.current_game_type]
                context_data = analyzer(frame, state)
            
            # Add general context data
            context_data.update({
                "frame_timestamp": time.time(),
                "frame_shape": frame.shape,
                "analysis_version": "3.1.0"
            })
            
        except Exception as e:
            self.logger.warning(f"⚠️ Context extraction error: {e}")
        
        return context_data
    
    def _analyze_fps_game(self, frame: np.ndarray, state: GameState) -> Dict[str, Any]:
        """Analyze FPS game specific context"""
        context = {}
        
        # Extract FPS-specific information
        if self.ocr_engine:
            text_results = self.ocr_engine.extract_text(frame)
            
            # Look for health, ammo, etc.
            for region in text_results.get("regions", []):
                text = region.get("text", "").lower()
                
                if "health" in text or "hp" in text:
                    context["health_detected"] = True
                if "ammo" in text:
                    context["ammo_detected"] = True
                if any(word in text for word in ["kill", "death", "k/d"]):
                    context["score_detected"] = True
        
        return context
    
    def _analyze_moba_game(self, frame: np.ndarray, state: GameState) -> Dict[str, Any]:
        """Analyze MOBA game specific context"""
        return {"game_type": "moba", "minimap_detected": False}
    
    def _analyze_rts_game(self, frame: np.ndarray, state: GameState) -> Dict[str, Any]:
        """Analyze RTS game specific context"""
        return {"game_type": "rts", "resource_panel_detected": False}
    
    def _analyze_rpg_game(self, frame: np.ndarray, state: GameState) -> Dict[str, Any]:
        """Analyze RPG game specific context"""
        return {"game_type": "rpg", "character_stats_detected": False}
    
    def _analyze_battle_royale_game(self, frame: np.ndarray, state: GameState) -> Dict[str, Any]:
        """Analyze Battle Royale game specific context"""
        return {"game_type": "battle_royale", "player_count_detected": False}
    
    def _track_state_change(self, context: GameContext):
        """Track game state changes"""
        if self.current_context and self.current_context.current_state != context.current_state:
            transition = StateTransition(
                from_state=self.current_context.current_state,
                to_state=context.current_state,
                timestamp=context.timestamp,
                confidence=context.confidence
            )
            
            self.state_history.append(transition)
            self.metrics.state_changes_detected += 1
            
            self.logger.info(f"🔄 State change: {transition.from_state.value} → {transition.to_state.value}")
    
    def _update_metrics(self, analysis_time: float):
        """Update analysis metrics"""
        self.metrics.frames_analyzed += 1
        
        # Update average analysis time
        self.metrics.average_analysis_time = (
            (self.metrics.average_analysis_time * (self.metrics.frames_analyzed - 1) + analysis_time) /
            self.metrics.frames_analyzed
        )
        
        # Calculate FPS
        current_time = time.time()
        if self.last_analysis_time > 0:
            frame_interval = current_time - self.last_analysis_time
            if frame_interval > 0:
                current_fps = 1.0 / frame_interval
                self.metrics.fps = (self.metrics.fps * 0.9 + current_fps * 0.1)  # Smoothed FPS
        
        self.last_analysis_time = current_time
        
        # Track frame times for performance analysis
        self.frame_times.append(analysis_time)
        if len(self.frame_times) > 100:
            self.frame_times.pop(0)
    
    def start_real_time_analysis(self):
        """Start real-time game state analysis"""
        if self.analysis_active:
            return
        
        self.analysis_active = True
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        self.logger.info("🔄 Real-time analysis started")
    
    def stop_real_time_analysis(self):
        """Stop real-time analysis"""
        self.analysis_active = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=1.0)
        self.logger.info("🛑 Real-time analysis stopped")
    
    def _analysis_loop(self):
        """Real-time analysis loop"""
        target_interval = 1.0 / self.target_fps
        
        while self.analysis_active:
            try:
                loop_start = time.time()
                
                # Capture frame
                if self.screen_capture:
                    frame = self.screen_capture.capture_screen()
                    if frame is not None:
                        # Analyze game state
                        context = self.analyze_game_state(frame)
                
                # Maintain target FPS
                loop_time = time.time() - loop_start
                sleep_time = max(0, target_interval - loop_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"❌ Analysis loop error: {e}")
                time.sleep(0.1)
    
    def get_analysis_metrics(self) -> Dict[str, Any]:
        """Get current analysis metrics"""
        return {
            "frames_analyzed": self.metrics.frames_analyzed,
            "state_changes_detected": self.metrics.state_changes_detected,
            "average_analysis_time": self.metrics.average_analysis_time,
            "current_fps": self.metrics.fps,
            "target_fps": self.target_fps,
            "current_game_type": self.current_game_type.value,
            "current_state": self.current_context.current_state.value if self.current_context else "unknown",
            "analysis_active": self.analysis_active
        }

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🧠 Game State Analyzer - Sprint 3 Test")
    print("=" * 60)
    
    # Create game state analyzer
    analyzer = GameStateAnalyzer(target_fps=60.0)
    
    # Test with dummy frame
    print("\n🎮 Testing game state analysis...")
    dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Add some test content to frame
    cv2.putText(dummy_frame, "HEALTH: 100", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(dummy_frame, "AMMO: 30/90", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Analyze game state
    context = analyzer.analyze_game_state(dummy_frame)
    
    print(f"Game Type: {context.game_type.value}")
    print(f"Game State: {context.current_state.value}")
    print(f"Confidence: {context.confidence:.3f}")
    print(f"Extracted Data: {context.extracted_data}")
    
    # Get metrics
    metrics = analyzer.get_analysis_metrics()
    print(f"\n📊 Analysis Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n🎉 Sprint 3 - Task 3.1 test completed!")
    print("🎯 Target: Real-time analysis, multi-game support, >85% accuracy")
    print(f"📈 Current: {metrics['current_fps']:.1f} FPS, {context.confidence:.1%} confidence")
