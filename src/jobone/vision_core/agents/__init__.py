#!/usr/bin/env python3
"""
Orion Vision Core - Agents Package
Specialized agent implementations for various tasks
"""

__version__ = "1.0.0"
__author__ = "Orion Development Team"

# Core agent exports
try:
    from .communication_agent import CommunicationAgent, OrionMessage, MessageType, MessagePriority
    __all__ = ["CommunicationAgent", "OrionMessage", "MessageType", "MessagePriority"]
except ImportError as e:
    print(f"Warning: Could not import communication_agent: {e}")
    __all__ = []

# Optional agent imports
try:
    from .llm_router import LLMRouter
    __all__.append("LLMRouter")
except ImportError:
    pass

try:
    from .memory import MemoryAgent
    __all__.append("MemoryAgent")
except ImportError:
    pass

try:
    from .voice_agent import VoiceAgent
    __all__.append("VoiceAgent")
except ImportError:
    pass

try:
    from .speech_agent import SpeechAgent
    __all__.append("SpeechAgent")
except ImportError:
    pass

try:
    from .screen_agent import ScreenAgent
    __all__.append("ScreenAgent")
except ImportError:
    pass

try:
    from .mouse_control import MouseControlAgent
    __all__.append("MouseControlAgent")
except ImportError:
    pass

try:
    from .orion_brain import OrionBrain
    __all__.append("OrionBrain")
except ImportError:
    pass

def get_available_agents():
    """Get list of available agent classes"""
    return __all__

def get_agent_info():
    """Get information about the agents package"""
    return {
        'package': 'orion_vision_core.agents',
        'version': __version__,
        'author': __author__,
        'available_agents': get_available_agents(),
        'description': 'Specialized agent implementations for Orion Vision Core'
    }
