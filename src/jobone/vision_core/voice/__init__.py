#!/usr/bin/env python3
"""
Orion Vision Core Voice Module
Sprint 8.5 - Voice Commands and Natural Language Interface
Orion Vision Core - Autonomous AI Operating System

This module provides advanced voice command recognition, speech synthesis, and
conversational AI capabilities for the Orion Vision Core autonomous AI
operating system.

Author: Orion Development Team
Version: 8.5.0
Date: 30 Mayıs 2025
"""

# Legacy imports (Sprint 8.1)
from .speech_to_text import SpeechRecognitionEngine, get_speech_recognition_engine, RecognitionState
from .text_to_speech import TextToSpeechEngine, get_tts_engine, SpeechState, Voice
from .voice_command_state import VoiceCommandStateMachine, get_voice_command_state, VoiceState, ControlMode, VoiceCommand

# New imports (Sprint 8.5)
from .voice_manager import (
    VoiceManager, get_voice_manager, VoiceCommand as VoiceCmd, VoiceState as VState, AudioFormat,
    VoiceCommandResult, SpeechSynthesisRequest
)
from .conversational_ai import (
    ConversationalAI, get_conversational_ai, ConversationMode, ResponseType,
    PersonalityTrait, ConversationContext, ConversationResponse
)

# Version information
__version__ = "8.5.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'SpeechRecognitionEngine',
    'TextToSpeechEngine',
    'VoiceCommandStateMachine',
    'Voice',
    'VoiceCommand',

    # Enums
    'RecognitionState',
    'SpeechState',
    'VoiceState',
    'ControlMode',

    # Functions
    'get_speech_recognition_engine',
    'get_tts_engine',
    'get_voice_command_state',

    # Utilities
    'initialize_voice_system',
    'test_voice_system',
    'get_voice_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_voice_system() -> bool:
    """
    Initialize the complete voice command system.

    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize speech recognition
        speech_engine = get_speech_recognition_engine()
        speech_available = speech_engine.is_enabled

        # Initialize text-to-speech
        tts_engine = get_tts_engine()
        tts_available = tts_engine.is_enabled

        # Initialize voice command state machine
        voice_state = get_voice_command_state()
        state_machine_available = voice_state.current_state != VoiceState.DISABLED

        if speech_available and tts_available and state_machine_available:
            logger.info("🎙️ Voice system initialized successfully")
            return True
        else:
            logger.warning(f"⚠️ Voice system partially available - Speech: {speech_available}, TTS: {tts_available}, State: {state_machine_available}")
            return False

    except Exception as e:
        logger.error(f"❌ Error initializing voice system: {e}")
        return False

def test_voice_system() -> dict:
    """
    Test voice system components and return status.

    Returns:
        Dictionary containing test results
    """
    results = {
        'speech_recognition': False,
        'text_to_speech': False,
        'voice_state_machine': False,
        'overall_status': False,
        'errors': []
    }

    try:
        # Test speech recognition
        speech_engine = get_speech_recognition_engine()
        results['speech_recognition'] = speech_engine.is_enabled
        if not speech_engine.is_enabled:
            results['errors'].append("Speech recognition not available")

        # Test text-to-speech
        tts_engine = get_tts_engine()
        results['text_to_speech'] = tts_engine.is_enabled
        if not tts_engine.is_enabled:
            results['errors'].append("Text-to-speech not available")

        # Test voice state machine
        voice_state = get_voice_command_state()
        results['voice_state_machine'] = voice_state.current_state != VoiceState.DISABLED
        if voice_state.current_state == VoiceState.DISABLED:
            results['errors'].append("Voice state machine disabled")

        # Overall status
        results['overall_status'] = all([
            results['speech_recognition'],
            results['text_to_speech'],
            results['voice_state_machine']
        ])

        logger.info(f"🧪 Voice system test completed: {results['overall_status']}")

    except Exception as e:
        logger.error(f"❌ Error testing voice system: {e}")
        results['errors'].append(str(e))

    return results

def get_voice_info() -> dict:
    """
    Get voice module information.

    Returns:
        Dictionary containing voice module information
    """
    return {
        'module': 'orion_vision_core.voice',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'SpeechRecognitionEngine': 'Speech-to-text processing with multiple engines',
            'TextToSpeechEngine': 'Text-to-speech synthesis with voice selection',
            'VoiceCommandStateMachine': 'Voice command processing and AI control transition'
        },
        'features': [
            'Real-time speech recognition',
            'Multiple TTS voices',
            'Wake word detection',
            'Voice command classification',
            'AI control transition',
            'State machine management',
            'Error handling and recovery',
            'Background processing',
            'Queue management'
        ],
        'dependencies': [
            'SpeechRecognition',
            'pyttsx3',
            'pyaudio',
            'PyQt6',
            'Python 3.8+'
        ],
        'wake_words': ['orion', 'hey orion', 'ok orion', 'computer'],
        'supported_commands': [
            'greeting', 'question', 'request', 'control',
            'release', 'status', 'stop'
        ]
    }

def start_voice_system() -> bool:
    """
    Start the voice command system.

    Returns:
        True if started successfully, False otherwise
    """
    try:
        voice_state = get_voice_command_state()
        return voice_state.start_voice_system()
    except Exception as e:
        logger.error(f"❌ Error starting voice system: {e}")
        return False

def stop_voice_system():
    """Stop the voice command system"""
    try:
        voice_state = get_voice_command_state()
        voice_state.stop_voice_system()
    except Exception as e:
        logger.error(f"❌ Error stopping voice system: {e}")

def get_voice_status() -> dict:
    """
    Get comprehensive voice system status.

    Returns:
        Dictionary containing status of all voice components
    """
    try:
        speech_engine = get_speech_recognition_engine()
        tts_engine = get_tts_engine()
        voice_state = get_voice_command_state()

        return {
            'speech_recognition': speech_engine.get_status(),
            'text_to_speech': tts_engine.get_status(),
            'voice_command_state': voice_state.get_status(),
            'system_initialized': initialize_voice_system()
        }
    except Exception as e:
        logger.error(f"❌ Error getting voice status: {e}")
        return {'error': str(e)}

# Module initialization
logger.info(f"📦 Orion Vision Core Voice Module v{__version__} loaded")

# Check dependencies (silent mode - no warnings)
SPEECH_RECOGNITION_AVAILABLE = False
PYTTSX3_AVAILABLE = False
PYAUDIO_AVAILABLE = False

try:
    import speech_recognition
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    pass  # Silent fail - no warning

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    pass  # Silent fail - no warning

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    pass  # Silent fail - no warning

class VoiceSystem:
    """
    Unified Voice System Class

    This class provides a unified interface for all voice-related functionality
    including speech recognition, text-to-speech, and voice command processing.
    """

    def __init__(self):
        """Initialize the Voice System"""
        self.initialized = False
        self.speech_engine = None
        self.tts_engine = None
        self.voice_state = None
        self.logger = logger

    def initialize(self) -> bool:
        """
        Initialize all voice components

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize speech recognition
            self.speech_engine = get_speech_recognition_engine()

            # Initialize text-to-speech
            self.tts_engine = get_tts_engine()

            # Initialize voice command state
            self.voice_state = get_voice_command_state()

            # Check if all components are available
            self.initialized = (
                self.speech_engine.is_enabled and
                self.tts_engine.is_enabled and
                self.voice_state.current_state != VoiceState.DISABLED
            )

            if self.initialized:
                self.logger.info("🎙️ Voice System initialized successfully")
            else:
                self.logger.warning("⚠️ Voice System partially initialized")

            return self.initialized

        except Exception as e:
            self.logger.error(f"❌ Voice System initialization failed: {e}")
            self.initialized = False
            return False

    def start(self) -> bool:
        """Start the voice system"""
        if not self.initialized:
            if not self.initialize():
                return False

        return start_voice_system()

    def stop(self):
        """Stop the voice system"""
        stop_voice_system()

    def get_status(self) -> dict:
        """Get voice system status"""
        return get_voice_status()

    def is_available(self) -> bool:
        """Check if voice system is available"""
        return SPEECH_RECOGNITION_AVAILABLE and PYTTSX3_AVAILABLE

    def get_info(self) -> dict:
        """Get voice system information"""
        return get_voice_info()

    def health_check(self) -> bool:
        """Health check for component coordinator"""
        try:
            if not self.initialized:
                return False

            # Check if all components are still working
            status = self.get_status()
            return not status.get('error', False)

        except Exception:
            return False


# Export version for external access
VERSION = __version__
