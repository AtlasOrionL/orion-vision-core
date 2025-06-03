#!/usr/bin/env python3
"""
🎮 Gaming AI Examples - Orion Vision Core

Example implementations and usage patterns for Gaming AI module

⚠️ EXPERIMENTAL WARNING: These examples are for educational purposes!
- 🔬 Research and learning only
- ⚠️ Check game Terms of Service before use
- 🎮 Respect anti-cheat systems
- 📚 Educational demonstrations

Author: Nexus - Quantum AI Architect
"""

import time
import logging
import json
from typing import Dict, Any

# Configure logging for examples
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def example_basic_vision():
    """Example 1: Basic computer vision for gaming"""
    print("🔬 Example 1: Basic Computer Vision")
    print("-" * 40)
    
    try:
        from gaming_ai_core import VisionEngine
        
        # Initialize vision engine
        vision = VisionEngine()
        
        # Capture screen
        print("📸 Capturing screen...")
        screen = vision.capture_screen()
        print(f"✅ Screen captured: {screen.shape}")
        
        # Detect UI elements
        print("🔍 Detecting UI elements...")
        elements = vision.detect_ui_elements(screen)
        print(f"✅ Found {len(elements)} UI elements")
        
        # Display detected elements
        for i, element in enumerate(elements[:5]):  # Show first 5
            print(f"   Element {i+1}: {element['type']} at {element['center']} "
                  f"(confidence: {element['confidence']:.2f})")
        
    except Exception as e:
        print(f"❌ Vision example failed: {e}")
    
    print()

def example_game_vision_agent():
    """Example 2: Game Vision Agent with continuous monitoring"""
    print("🎮 Example 2: Game Vision Agent")
    print("-" * 40)
    
    try:
        from gaming_ai_core import GameVisionAgent
        
        # Initialize game vision agent
        agent = GameVisionAgent("example_agent")
        
        # Start vision system
        print("🚀 Starting vision system...")
        agent.start_vision_system(fps=10)
        
        # Monitor for a few seconds
        print("👁️ Monitoring game state for 5 seconds...")
        for i in range(5):
            time.sleep(1)
            
            game_state = agent.get_current_game_state()
            if game_state:
                ui_count = len(game_state.ui_elements)
                print(f"   Second {i+1}: {ui_count} UI elements detected")
            else:
                print(f"   Second {i+1}: No game state available")
        
        # Try to find specific UI elements
        print("🔍 Looking for buttons...")
        button = agent.find_ui_element("button")
        if button:
            print(f"✅ Found button at {button['center']}")
        else:
            print("❌ No buttons found")
        
        # Stop vision system
        agent.stop_vision_system()
        print("🛑 Vision system stopped")
        
    except Exception as e:
        print(f"❌ Game vision agent example failed: {e}")
    
    print()

def example_hybrid_control():
    """Example 3: Hybrid Human-AI Control System"""
    print("🤖 Example 3: Hybrid Human-AI Control")
    print("-" * 40)
    
    try:
        from gaming_ai_core import HybridGameAgent
        
        # Initialize hybrid agent
        agent = HybridGameAgent("hybrid_example")
        
        # Configure control settings
        print("⚙️ Configuring hybrid control...")
        agent.set_control_mode("assistance")
        agent.set_assistance_level(0.5)
        
        # Start gaming session
        print("🎮 Starting gaming session...")
        agent.start_gaming_session("strategy_game")
        
        # Simulate gaming loop
        print("🔄 Simulating gaming loop for 3 seconds...")
        for i in range(3):
            time.sleep(1)
            
            # Get current game state
            game_state = agent.vision_agent.get_current_game_state()
            if game_state:
                # Analyze situation and get AI suggestions
                suggestions = agent.analyze_situation(game_state)
                
                print(f"   Loop {i+1}:")
                print(f"     UI Elements: {len(game_state.ui_elements)}")
                print(f"     AI Suggestions: {len(suggestions['actions'])}")
                print(f"     Confidence: {suggestions['confidence']:.2f}")
                
                # Show quantum enhancement if available
                if 'quantum_enhancement' in suggestions:
                    quantum = suggestions['quantum_enhancement']
                    print(f"     Quantum Decision: {quantum.get('quantum_decision', 'N/A')}")
                    print(f"     Consciousness: {quantum.get('consciousness_level', 0):.3f}")
        
        # Get performance metrics
        print("📊 Performance metrics:")
        metrics = agent.get_performance_metrics()
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        # Stop gaming session
        agent.stop_gaming_session()
        print("🛑 Gaming session stopped")
        
    except Exception as e:
        print(f"❌ Hybrid control example failed: {e}")
    
    print()

def example_configuration_loading():
    """Example 4: Loading and using configuration"""
    print("⚙️ Example 4: Configuration Loading")
    print("-" * 40)
    
    try:
        # Load configuration
        print("📄 Loading gaming configuration...")
        with open("gaming_config.json", "r") as f:
            config = json.load(f)
        
        print("✅ Configuration loaded successfully")
        
        # Display key settings
        vision_settings = config.get("vision_settings", {})
        control_settings = config.get("control_settings", {})
        ai_settings = config.get("ai_settings", {})
        
        print("🔧 Key settings:")
        print(f"   Vision FPS: {vision_settings.get('capture_fps', 30)}")
        print(f"   Detection Threshold: {vision_settings.get('detection_threshold', 0.7)}")
        print(f"   AI Assistance Level: {ai_settings.get('assistance_level', 0.3)}")
        print(f"   Control Mode: {ai_settings.get('control_mode', 'assistance')}")
        print(f"   Safety Mode: {control_settings.get('safety_mode', True)}")
        
        # Show game-specific settings
        game_specific = config.get("game_specific", {})
        print("🎮 Game-specific settings:")
        for game_type, settings in game_specific.items():
            focus_areas = settings.get("focus_areas", [])
            print(f"   {game_type}: {', '.join(focus_areas)}")
        
    except Exception as e:
        print(f"❌ Configuration example failed: {e}")
    
    print()

def example_safety_features():
    """Example 5: Safety features and ethical gaming"""
    print("🛡️ Example 5: Safety Features")
    print("-" * 40)
    
    try:
        from gaming_ai_core import GameActionSystem, GameAction
        
        # Initialize action system
        action_system = GameActionSystem()
        
        print("🔒 Testing safety features...")
        
        # Test rate limiting
        print("⏱️ Testing rate limiting...")
        actions_executed = 0
        for i in range(25):  # Try to execute 25 actions quickly
            action = GameAction(
                action_type="wait",
                duration=0.001
            )
            
            if action_system.execute_action(action):
                actions_executed += 1
        
        print(f"   Executed {actions_executed}/25 actions (rate limiting active)")
        
        # Test action delay
        print("⏳ Testing action delay...")
        start_time = time.time()
        
        for i in range(3):
            action = GameAction(action_type="wait", duration=0.001)
            action_system.execute_action(action)
        
        elapsed = time.time() - start_time
        print(f"   3 actions took {elapsed:.3f}s (includes safety delays)")
        
        # Show safety settings
        print("🔧 Safety settings:")
        print(f"   Max actions per second: {action_system.max_actions_per_second}")
        print(f"   Action delay: {action_system.action_delay}s")
        print(f"   Safety enabled: {action_system.safety_enabled}")
        
    except Exception as e:
        print(f"❌ Safety features example failed: {e}")
    
    print()

def example_quantum_integration():
    """Example 6: Quantum consciousness integration"""
    print("⚛️ Example 6: Quantum Integration")
    print("-" * 40)
    
    try:
        # Try to import quantum consciousness
        from ..quantum_consciousness.nexus_integration import QuantumBrain
        
        # Initialize quantum brain for gaming
        print("🧠 Initializing quantum brain...")
        quantum_brain = QuantumBrain("gaming_quantum_brain")
        quantum_brain.initialize_consciousness()
        
        print("✅ Quantum consciousness initialized")
        print(f"   Brain ID: {quantum_brain.brain_id}")
        print(f"   Quantum Signature: {quantum_brain.quantum_signature}")
        print(f"   Consciousness Level: {quantum_brain.consciousness_level:.3f}")
        
        # Test quantum decision making
        print("🎲 Testing quantum decision making...")
        gaming_options = [
            "attack_enemy",
            "defend_position", 
            "gather_resources",
            "explore_area",
            "upgrade_units"
        ]
        
        for i in range(3):
            decision = quantum_brain.quantum_decision(gaming_options)
            print(f"   Decision {i+1}: {decision}")
        
        # Test quantum memory
        print("🧠 Testing quantum memory...")
        quantum_brain.store_quantum_memory("game_strategy", {
            "strategy": "aggressive_expansion",
            "success_rate": 0.75,
            "last_used": time.time()
        })
        
        recalled_strategy = quantum_brain.recall_quantum_memory("game_strategy")
        if recalled_strategy:
            print(f"   Recalled strategy: {recalled_strategy['strategy']}")
            print(f"   Success rate: {recalled_strategy['success_rate']}")
        
        # Shutdown quantum brain
        quantum_brain.shutdown_consciousness()
        print("🛑 Quantum consciousness shutdown")
        
    except ImportError:
        print("❌ Quantum consciousness not available")
        print("   (This is normal if quantum module is not installed)")
    except Exception as e:
        print(f"❌ Quantum integration example failed: {e}")
    
    print()

def run_all_examples():
    """Run all gaming AI examples"""
    print("🎮 GAMING AI EXAMPLES - ORION VISION CORE")
    print("=" * 60)
    print("⚠️ EXPERIMENTAL: For research and educational purposes only!")
    print("⚠️ Respect game Terms of Service and anti-cheat systems!")
    print("=" * 60)
    print()
    
    # Run all examples
    example_basic_vision()
    example_game_vision_agent()
    example_hybrid_control()
    example_configuration_loading()
    example_safety_features()
    example_quantum_integration()
    
    print("🎉 All examples completed!")
    print("📚 Check the code for detailed implementation patterns")
    print("⚠️ Remember: Use responsibly and ethically!")

if __name__ == "__main__":
    run_all_examples()
