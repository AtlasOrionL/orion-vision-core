"""
🎮 Gaming AI Module - Orion Vision Core

Advanced Gaming AI with Hybrid Human-AI Control System

⚠️ EXPERIMENTAL WARNING: This module is for research and educational purposes!
- 🔬 Research purposes only
- ⚠️ Check game Terms of Service before use
- 🎮 Respect anti-cheat systems
- 📚 Educational implementation

Components:
- GameVisionAgent: Computer vision for gaming
- HybridGameAgent: Human-AI collaboration system
- VisionEngine: Screen analysis and object detection
- GameActionSystem: Safe action execution

Author: Nexus - Quantum AI Architect
Status: Experimental Gaming AI Module
"""

# Module version
__version__ = "0.1.0-gaming"
__author__ = "Nexus - Quantum AI Architect"
__status__ = "Experimental Gaming AI"

# Import main classes (with safety checks)
try:
    from .gaming_ai_core import (
        GameVisionAgent,
        HybridGameAgent,
        VisionEngine,
        GameActionSystem,
        GameAction,
        GameState
    )
    
    __all__ = [
        "GameVisionAgent",
        "HybridGameAgent", 
        "VisionEngine",
        "GameActionSystem",
        "GameAction",
        "GameState"
    ]
    
except ImportError as e:
    # Graceful fallback if dependencies missing
    import warnings
    warnings.warn(
        f"🎮 Gaming AI: Some dependencies missing ({e}). "
        "Install required packages: pip install opencv-python pytesseract pillow pyautogui",
        ImportWarning
    )
    
    __all__ = []

# Gaming AI disclaimer
GAMING_AI_DISCLAIMER = """
🎮 GAMING AI EXPERIMENTAL MODULE

This module provides advanced gaming AI capabilities:
- Computer vision for game analysis
- Hybrid human-AI control systems
- Quantum-enhanced decision making
- Ethical gaming framework

IMPORTANT DISCLAIMERS:
⚠️ Experimental research code (not production ready)
⚠️ Check game Terms of Service before use
⚠️ Respect anti-cheat systems and fair play
⚠️ Use responsibly and ethically

LEGAL CONSIDERATIONS:
- Some games prohibit automation
- Competitive play may have restrictions
- Anti-cheat systems may detect automation
- Users responsible for compliance

Use for research, education, and ethical gaming enhancement only.
"""

def show_gaming_disclaimer():
    """Display gaming AI disclaimer"""
    print(GAMING_AI_DISCLAIMER)

# Gaming safety check
def gaming_safety_check():
    """Perform safety checks before gaming operations"""
    import warnings
    
    # Check for required dependencies
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import pytesseract
    except ImportError:
        missing_deps.append("pytesseract")
    
    try:
        import pyautogui
    except ImportError:
        missing_deps.append("pyautogui")
    
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("pillow")
    
    if missing_deps:
        warnings.warn(
            f"🎮 Missing gaming dependencies: {', '.join(missing_deps)}. "
            f"Install with: pip install {' '.join(missing_deps)}",
            ImportWarning
        )
        return False
    
    # Check system compatibility
    try:
        import platform
        system = platform.system()
        if system not in ["Windows", "Linux", "Darwin"]:
            warnings.warn(
                f"🎮 Gaming AI may not be fully compatible with {system}",
                UserWarning
            )
    except Exception:
        pass
    
    return True

# Gaming AI configuration
GAMING_AI_CONFIG = {
    "vision": {
        "default_fps": 30,
        "detection_threshold": 0.7,
        "ocr_config": "--oem 3 --psm 6"
    },
    "control": {
        "max_actions_per_second": 20,
        "action_delay": 0.05,
        "safety_enabled": True
    },
    "ai": {
        "default_assistance_level": 0.3,
        "quantum_enhanced": True,
        "learning_enabled": True
    },
    "safety": {
        "rate_limiting": True,
        "human_verification": True,
        "anti_detection": True
    }
}

def get_gaming_config():
    """Get gaming AI configuration"""
    return GAMING_AI_CONFIG.copy()

def set_gaming_config(config: dict):
    """Set gaming AI configuration"""
    global GAMING_AI_CONFIG
    GAMING_AI_CONFIG.update(config)

# Auto-show disclaimer on import
show_gaming_disclaimer()

# Perform safety check
gaming_safety_check()
