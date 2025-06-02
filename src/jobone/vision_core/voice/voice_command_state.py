#!/usr/bin/env python3
"""
Voice Command State Machine
Sprint 8.1 - Atlas Prompt 8.1.3: Basic Voice Command System Integration
Orion Vision Core - Autonomous AI Operating System

This module provides a state machine for voice command processing and AI control
transition mechanisms in the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.1.0
Date: 30 Mayıs 2025
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from .speech_to_text import get_speech_recognition_engine
from .text_to_speech import get_tts_engine
from ..core_ai_manager import get_core_ai_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VoiceCommandState")

class VoiceState(Enum):
    """Voice command system state enumeration"""
    INACTIVE = "inactive"
    LISTENING = "listening"
    PROCESSING = "processing"
    AI_RESPONDING = "ai_responding"
    AI_CONTROL = "ai_control"
    ERROR = "error"
    DISABLED = "disabled"

class ControlMode(Enum):
    """AI control mode enumeration"""
    USER_CONTROL = "user_control"
    AI_CONTROL = "ai_control"
    SHARED_CONTROL = "shared_control"

@dataclass
class VoiceCommand:
    """Voice command data structure"""
    command_id: str
    command_text: str
    command_type: str
    confidence: float
    timestamp: datetime
    processed: bool = False
    response: Optional[str] = None

class VoiceCommandStateMachine(QObject):
    """
    Voice command state machine with AI control transition.
    
    Features:
    - Voice command recognition and processing
    - State machine for voice interaction flow
    - AI control transition mechanism
    - Wake word detection
    - Command validation and execution
    - Error handling and recovery
    """
    
    # Signals
    state_changed = pyqtSignal(str)  # VoiceState
    command_recognized = pyqtSignal(dict)  # VoiceCommand as dict
    command_processed = pyqtSignal(dict)  # VoiceCommand as dict
    control_mode_changed = pyqtSignal(str)  # ControlMode
    wake_word_detected = pyqtSignal(str)  # Wake word
    ai_response_ready = pyqtSignal(str)  # AI response text
    error_occurred = pyqtSignal(str)  # Error message
    
    def __init__(self):
        """Initialize voice command state machine"""
        super().__init__()
        
        # State machine
        self.current_state = VoiceState.DISABLED
        self.previous_state = VoiceState.DISABLED
        self.state_start_time = datetime.now()
        
        # Control mode
        self.control_mode = ControlMode.USER_CONTROL
        self.ai_control_timeout = 30.0  # seconds
        self.ai_control_timer = QTimer()
        self.ai_control_timer.timeout.connect(self._ai_control_timeout)
        
        # Voice components
        self.speech_engine = get_speech_recognition_engine()
        self.tts_engine = get_tts_engine()
        self.ai_manager = get_core_ai_manager()
        
        # Wake words
        self.wake_words = ["orion", "hey orion", "ok orion", "computer"]
        self.wake_word_detected_recently = False
        self.wake_word_timeout = 5.0  # seconds
        self.wake_word_timer = QTimer()
        self.wake_word_timer.timeout.connect(self._wake_word_timeout)
        
        # Command processing
        self.command_history: List[VoiceCommand] = []
        self.command_counter = 0
        self.max_command_history = 100
        
        # Voice command patterns
        self.command_patterns = {
            'greeting': ['hello', 'hi', 'hey'],
            'question': ['what', 'how', 'when', 'where', 'why', 'who'],
            'request': ['please', 'can you', 'could you', 'would you'],
            'control': ['take control', 'ai control', 'autonomous mode'],
            'release': ['release control', 'user control', 'manual mode'],
            'status': ['status', 'how are you', 'what are you doing'],
            'stop': ['stop', 'cancel', 'abort', 'quit']
        }
        
        # Statistics
        self.stats = {
            'commands_processed': 0,
            'wake_words_detected': 0,
            'ai_control_sessions': 0,
            'total_listening_time': 0.0,
            'average_response_time': 0.0,
            'error_count': 0
        }
        
        # Connect component signals
        self._connect_signals()
        
        # Initialize state machine
        self._initialize_state_machine()
        
        logger.info("🎙️ Voice Command State Machine initialized")
    
    def _connect_signals(self):
        """Connect signals from voice components"""
        # Speech recognition signals
        self.speech_engine.speech_recognized.connect(self._on_speech_recognized)
        self.speech_engine.state_changed.connect(self._on_speech_state_changed)
        self.speech_engine.error_occurred.connect(self._on_speech_error)
        
        # TTS signals
        self.tts_engine.speech_finished.connect(self._on_tts_finished)
        self.tts_engine.error_occurred.connect(self._on_tts_error)
        
        # AI manager signals
        self.ai_manager.state_changed.connect(self._on_ai_state_changed)
    
    def _initialize_state_machine(self):
        """Initialize the voice command state machine"""
        if self.speech_engine.is_enabled and self.tts_engine.is_enabled:
            self._change_state(VoiceState.INACTIVE)
        else:
            self._change_state(VoiceState.DISABLED)
            logger.warning("⚠️ Voice command system disabled - components not available")
    
    def _change_state(self, new_state: VoiceState):
        """Change state machine state"""
        if self.current_state != new_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_start_time = datetime.now()
            
            logger.info(f"🎙️ Voice state changed: {self.previous_state.value} → {new_state.value}")
            self.state_changed.emit(new_state.value)
            
            # Handle state-specific actions
            self._handle_state_entry(new_state)
    
    def _handle_state_entry(self, state: VoiceState):
        """Handle actions when entering a new state"""
        if state == VoiceState.LISTENING:
            self._start_listening()
        elif state == VoiceState.AI_CONTROL:
            self._enter_ai_control_mode()
        elif state == VoiceState.INACTIVE:
            self._stop_listening()
    
    def start_voice_system(self) -> bool:
        """
        Start the voice command system.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.current_state == VoiceState.DISABLED:
            logger.error("❌ Voice system disabled")
            return False
        
        try:
            self._change_state(VoiceState.LISTENING)
            logger.info("🎙️ Voice command system started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start voice system: {e}")
            self.error_occurred.emit(str(e))
            return False
    
    def stop_voice_system(self):
        """Stop the voice command system"""
        try:
            self._stop_listening()
            self._change_state(VoiceState.INACTIVE)
            logger.info("🎙️ Voice command system stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop voice system: {e}")
    
    def _start_listening(self):
        """Start continuous speech recognition"""
        if self.speech_engine.is_enabled:
            self.speech_engine.start_listening(continuous=True)
    
    def _stop_listening(self):
        """Stop speech recognition"""
        if self.speech_engine.is_listening:
            self.speech_engine.stop_listening()
    
    def _on_speech_recognized(self, text: str):
        """Handle recognized speech"""
        try:
            logger.info(f"🎙️ Speech recognized: {text}")
            
            # Check for wake word
            if self._check_wake_word(text):
                return
            
            # Process as command if wake word was detected recently
            if self.wake_word_detected_recently or self.control_mode == ControlMode.AI_CONTROL:
                self._process_voice_command(text)
            
        except Exception as e:
            logger.error(f"❌ Error processing recognized speech: {e}")
            self.error_occurred.emit(str(e))
    
    def _check_wake_word(self, text: str) -> bool:
        """
        Check if text contains a wake word.
        
        Args:
            text: Recognized text to check
            
        Returns:
            True if wake word detected, False otherwise
        """
        text_lower = text.lower()
        
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                logger.info(f"🎙️ Wake word detected: {wake_word}")
                self.wake_word_detected.emit(wake_word)
                
                self.wake_word_detected_recently = True
                self.wake_word_timer.start(int(self.wake_word_timeout * 1000))
                
                self.stats['wake_words_detected'] += 1
                
                # Respond to wake word
                self.tts_engine.speak("Yes, I'm listening.", interrupt=True)
                
                return True
        
        return False
    
    def _wake_word_timeout(self):
        """Handle wake word timeout"""
        self.wake_word_detected_recently = False
        self.wake_word_timer.stop()
        logger.debug("🎙️ Wake word timeout")
    
    def _process_voice_command(self, text: str):
        """Process a voice command"""
        try:
            self._change_state(VoiceState.PROCESSING)
            
            # Create command object
            command = VoiceCommand(
                command_id=self._generate_command_id(),
                command_text=text,
                command_type=self._classify_command(text),
                confidence=1.0,  # Placeholder - would come from speech recognition
                timestamp=datetime.now()
            )
            
            # Add to history
            self.command_history.append(command)
            if len(self.command_history) > self.max_command_history:
                self.command_history.pop(0)
            
            self.command_recognized.emit(self._command_to_dict(command))
            
            # Process command based on type
            if command.command_type == 'control':
                self._handle_control_command(command)
            elif command.command_type == 'release':
                self._handle_release_command(command)
            elif command.command_type == 'stop':
                self._handle_stop_command(command)
            else:
                self._handle_general_command(command)
            
            self.stats['commands_processed'] += 1
            
        except Exception as e:
            logger.error(f"❌ Error processing voice command: {e}")
            self.error_occurred.emit(str(e))
            self._change_state(VoiceState.ERROR)
    
    def _classify_command(self, text: str) -> str:
        """Classify command type based on text"""
        text_lower = text.lower()
        
        for command_type, patterns in self.command_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return command_type
        
        return 'general'
    
    def _handle_control_command(self, command: VoiceCommand):
        """Handle AI control request"""
        logger.info("🎙️ AI control requested")
        self._change_control_mode(ControlMode.AI_CONTROL)
        
        response = "Taking control. I am now in autonomous mode."
        command.response = response
        command.processed = True
        
        self.tts_engine.speak(response)
        self.command_processed.emit(self._command_to_dict(command))
        
        self._change_state(VoiceState.AI_CONTROL)
    
    def _handle_release_command(self, command: VoiceCommand):
        """Handle control release request"""
        logger.info("🎙️ Control release requested")
        self._change_control_mode(ControlMode.USER_CONTROL)
        
        response = "Releasing control. You are now in manual mode."
        command.response = response
        command.processed = True
        
        self.tts_engine.speak(response)
        self.command_processed.emit(self._command_to_dict(command))
        
        self._change_state(VoiceState.LISTENING)
    
    def _handle_stop_command(self, command: VoiceCommand):
        """Handle stop command"""
        logger.info("🎙️ Stop command received")
        
        response = "Stopping voice command system."
        command.response = response
        command.processed = True
        
        self.tts_engine.speak(response)
        self.command_processed.emit(self._command_to_dict(command))
        
        self.stop_voice_system()
    
    def _handle_general_command(self, command: VoiceCommand):
        """Handle general command through AI manager"""
        try:
            self._change_state(VoiceState.AI_RESPONDING)
            
            # Process through AI manager
            ai_response = self.ai_manager.process_user_input(command.command_text)
            
            command.response = ai_response
            command.processed = True
            
            # Speak AI response
            self.tts_engine.speak(ai_response)
            self.ai_response_ready.emit(ai_response)
            self.command_processed.emit(self._command_to_dict(command))
            
        except Exception as e:
            logger.error(f"❌ Error handling general command: {e}")
            self.error_occurred.emit(str(e))
    
    def _change_control_mode(self, new_mode: ControlMode):
        """Change AI control mode"""
        if self.control_mode != new_mode:
            old_mode = self.control_mode
            self.control_mode = new_mode
            
            logger.info(f"🎙️ Control mode changed: {old_mode.value} → {new_mode.value}")
            self.control_mode_changed.emit(new_mode.value)
            
            if new_mode == ControlMode.AI_CONTROL:
                self.stats['ai_control_sessions'] += 1
                self.ai_control_timer.start(int(self.ai_control_timeout * 1000))
            else:
                self.ai_control_timer.stop()
    
    def _enter_ai_control_mode(self):
        """Enter AI control mode"""
        logger.info("🎙️ Entering AI control mode")
        # Here we would implement actual AI control mechanisms
        # For now, this is a placeholder for future Sprint 8.3 implementation
    
    def _ai_control_timeout(self):
        """Handle AI control timeout"""
        logger.info("🎙️ AI control timeout - returning to user control")
        self._change_control_mode(ControlMode.USER_CONTROL)
        self._change_state(VoiceState.LISTENING)
        
        self.tts_engine.speak("AI control timeout. Returning to manual mode.")
    
    def _generate_command_id(self) -> str:
        """Generate unique command ID"""
        self.command_counter += 1
        return f"cmd_{self.command_counter:06d}"
    
    def _command_to_dict(self, command: VoiceCommand) -> Dict[str, Any]:
        """Convert VoiceCommand to dictionary"""
        return {
            'command_id': command.command_id,
            'command_text': command.command_text,
            'command_type': command.command_type,
            'confidence': command.confidence,
            'timestamp': command.timestamp.isoformat(),
            'processed': command.processed,
            'response': command.response
        }
    
    def _on_speech_state_changed(self, state: str):
        """Handle speech recognition state changes"""
        logger.debug(f"🎙️ Speech recognition state: {state}")
    
    def _on_speech_error(self, error: str):
        """Handle speech recognition errors"""
        logger.error(f"🎙️ Speech recognition error: {error}")
        self.error_occurred.emit(f"Speech recognition error: {error}")
        self.stats['error_count'] += 1
    
    def _on_tts_finished(self, text: str):
        """Handle TTS completion"""
        if self.current_state == VoiceState.AI_RESPONDING:
            self._change_state(VoiceState.LISTENING)
    
    def _on_tts_error(self, error: str):
        """Handle TTS errors"""
        logger.error(f"🎙️ TTS error: {error}")
        self.error_occurred.emit(f"TTS error: {error}")
        self.stats['error_count'] += 1
    
    def _on_ai_state_changed(self, state: str):
        """Handle AI manager state changes"""
        logger.debug(f"🎙️ AI manager state: {state}")
    
    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get command history"""
        return [self._command_to_dict(cmd) for cmd in self.command_history]
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice command system status"""
        return {
            'current_state': self.current_state.value,
            'control_mode': self.control_mode.value,
            'wake_word_active': self.wake_word_detected_recently,
            'speech_engine_enabled': self.speech_engine.is_enabled,
            'tts_engine_enabled': self.tts_engine.is_enabled,
            'ai_manager_connected': self.ai_manager is not None,
            'wake_words': self.wake_words,
            'command_history_count': len(self.command_history),
            'statistics': self.stats
        }

# Singleton instance
_voice_command_state = None

def get_voice_command_state() -> VoiceCommandStateMachine:
    """Get the singleton voice command state machine instance"""
    global _voice_command_state
    if _voice_command_state is None:
        _voice_command_state = VoiceCommandStateMachine()
    return _voice_command_state

# Example usage and testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test voice command state machine
    voice_state = get_voice_command_state()
    
    def on_state_changed(state):
        print(f"Voice State: {state}")
    
    def on_command_recognized(command_data):
        print(f"Command Recognized: {command_data}")
    
    def on_control_mode_changed(mode):
        print(f"Control Mode: {mode}")
    
    def on_wake_word_detected(wake_word):
        print(f"Wake Word: {wake_word}")
    
    # Connect signals
    voice_state.state_changed.connect(on_state_changed)
    voice_state.command_recognized.connect(on_command_recognized)
    voice_state.control_mode_changed.connect(on_control_mode_changed)
    voice_state.wake_word_detected.connect(on_wake_word_detected)
    
    # Print status
    status = voice_state.get_status()
    print(f"Voice Command Status: {status}")
    
    # Start voice system
    if voice_state.current_state != VoiceState.DISABLED:
        print("Starting voice command system...")
        voice_state.start_voice_system()
    else:
        print("Voice command system disabled")
    
    sys.exit(app.exec())
