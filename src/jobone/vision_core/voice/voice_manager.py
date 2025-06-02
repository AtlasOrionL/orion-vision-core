#!/usr/bin/env python3
"""
Voice Manager - Voice Command Recognition and Speech Synthesis
Sprint 8.5 - Voice Commands and Natural Language Interface
Orion Vision Core - Autonomous AI Operating System

This module provides voice command recognition, speech synthesis, and
audio processing capabilities for the Orion Vision Core autonomous AI
operating system.

Author: Orion Development Team
Version: 8.5.0
Date: 30 Mayıs 2025
"""

import logging
import asyncio
import json
import threading
import queue
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VoiceManager")

class VoiceCommand(Enum):
    """Voice command enumeration"""
    WAKE_UP = "wake_up"
    SLEEP = "sleep"
    EXECUTE_TASK = "execute_task"
    CREATE_WORKFLOW = "create_workflow"
    SYSTEM_STATUS = "system_status"
    FILE_OPERATION = "file_operation"
    TERMINAL_COMMAND = "terminal_command"
    HELP = "help"
    STOP = "stop"
    REPEAT = "repeat"

class VoiceState(Enum):
    """Voice system state enumeration"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"

class AudioFormat(Enum):
    """Audio format enumeration"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"

@dataclass
class VoiceCommandResult:
    """Voice command processing result"""
    command_id: str
    original_text: str
    recognized_command: VoiceCommand
    confidence: float
    parameters: Dict[str, Any]
    timestamp: datetime
    processing_time: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class SpeechSynthesisRequest:
    """Speech synthesis request"""
    request_id: str
    text: str
    voice_id: str
    speed: float
    pitch: float
    volume: float
    language: str
    emotion: str
    priority: int

class VoiceManager(QObject):
    """
    Voice command recognition and speech synthesis manager.

    Features:
    - Voice command recognition
    - Speech-to-text conversion
    - Text-to-speech synthesis
    - Natural language processing
    - Voice-driven automation
    - Audio feedback and responses
    """

    # Signals
    voice_command_recognized = pyqtSignal(dict)  # VoiceCommandResult as dict
    speech_synthesis_completed = pyqtSignal(str, bool)  # request_id, success
    voice_state_changed = pyqtSignal(str)  # new_state
    audio_level_changed = pyqtSignal(float)  # audio_level
    wake_word_detected = pyqtSignal(str)  # wake_word

    def __init__(self):
        """Initialize Voice Manager"""
        super().__init__()

        # Voice configuration
        self.voice_enabled = True
        self.wake_words = ["orion", "atlas", "computer", "assistant"]
        self.current_state = VoiceState.IDLE
        self.listening_timeout = 5.0  # seconds
        self.confidence_threshold = 0.7

        # Audio configuration
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.audio_format = AudioFormat.WAV

        # Voice recognition
        self.recognition_enabled = True
        self.continuous_listening = False
        self.noise_threshold = 0.1
        self.silence_timeout = 2.0

        # Speech synthesis
        self.synthesis_enabled = True
        self.default_voice = "en-US-Standard-A"
        self.default_speed = 1.0
        self.default_pitch = 0.0
        self.default_volume = 0.8
        self.default_language = "en-US"

        # Command patterns
        self.command_patterns = {
            VoiceCommand.WAKE_UP: [
                r"wake up", r"hello orion", r"hey atlas", r"start listening"
            ],
            VoiceCommand.SLEEP: [
                r"go to sleep", r"stop listening", r"goodbye", r"sleep mode"
            ],
            VoiceCommand.EXECUTE_TASK: [
                r"execute task", r"run task", r"start task", r"perform task"
            ],
            VoiceCommand.CREATE_WORKFLOW: [
                r"create workflow", r"new workflow", r"build workflow", r"make workflow"
            ],
            VoiceCommand.SYSTEM_STATUS: [
                r"system status", r"how are you", r"status report", r"health check"
            ],
            VoiceCommand.FILE_OPERATION: [
                r"create file", r"open file", r"delete file", r"copy file", r"move file"
            ],
            VoiceCommand.TERMINAL_COMMAND: [
                r"run command", r"execute command", r"terminal", r"command line"
            ],
            VoiceCommand.HELP: [
                r"help", r"what can you do", r"commands", r"assistance"
            ],
            VoiceCommand.STOP: [
                r"stop", r"cancel", r"abort", r"halt"
            ],
            VoiceCommand.REPEAT: [
                r"repeat", r"say again", r"what did you say", r"pardon"
            ]
        }

        # State management
        self.command_history: List[VoiceCommandResult] = []
        self.synthesis_queue: queue.Queue = queue.Queue()
        self.audio_buffer: List[bytes] = []
        self.last_command_text = ""
        self.command_counter = 0
        self.synthesis_counter = 0

        # Statistics
        self.voice_stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'average_confidence': 0.0,
            'average_processing_time': 0.0,
            'wake_word_detections': 0,
            'synthesis_requests': 0,
            'successful_synthesis': 0
        }

        # Audio processing
        self.audio_thread = None
        self.audio_running = False
        self.current_audio_level = 0.0

        # Monitoring
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self._monitor_voice_system)
        self.monitoring_timer.start(1000)  # Monitor every second

        logger.info("🎤 Voice Manager initialized")

    async def process_natural_language_command(self, text: str) -> Optional[VoiceCommandResult]:
        """Process natural language command using NLP"""
        try:
            # Import here to avoid circular imports
            from ..nlp.natural_language_processor import get_natural_language_processor

            nlp_processor = get_natural_language_processor()
            nlp_result = await nlp_processor.process_text(text)

            if not nlp_result.success:
                logger.warning(f"⚠️ NLP processing failed: {nlp_result.error_message}")
                return None

            # Convert NLP intent to voice command
            command_mapping = {
                'task_execution': VoiceCommand.EXECUTE_TASK,
                'workflow_creation': VoiceCommand.CREATE_WORKFLOW,
                'system_query': VoiceCommand.SYSTEM_STATUS,
                'file_operation': VoiceCommand.FILE_OPERATION,
                'command_execution': VoiceCommand.TERMINAL_COMMAND,
                'help_request': VoiceCommand.HELP,
                'conversation': VoiceCommand.WAKE_UP
            }

            voice_command = command_mapping.get(
                nlp_result.intent.intent_type.value,
                VoiceCommand.HELP
            )

            # Extract parameters from entities
            parameters = {}
            for entity in nlp_result.entities:
                if entity.entity_type.value == 'task_name':
                    parameters['task_identifier'] = entity.value
                elif entity.entity_type.value == 'file_path':
                    parameters['filename'] = entity.value
                elif entity.entity_type.value == 'command':
                    parameters['command'] = entity.value

            # Create voice command result
            command_id = self._generate_command_id()
            result = VoiceCommandResult(
                command_id=command_id,
                original_text=text,
                recognized_command=voice_command,
                confidence=nlp_result.confidence,
                parameters=parameters,
                timestamp=datetime.now(),
                processing_time=nlp_result.processing_time,
                success=True
            )

            # Store in history
            self.command_history.append(result)
            self._update_voice_stats(result)

            # Emit signal
            self.voice_command_recognized.emit(self._command_result_to_dict(result))

            logger.info(f"🎤 NLP command processed: {voice_command.value} "
                       f"(confidence: {nlp_result.confidence:.3f})")

            return result

        except Exception as e:
            logger.error(f"❌ Error processing natural language command: {e}")
            return None

    def start_listening(self) -> bool:
        """Start voice recognition"""
        try:
            if not self.voice_enabled or not self.recognition_enabled:
                logger.warning("⚠️ Voice recognition is disabled")
                return False

            if self.current_state == VoiceState.LISTENING:
                logger.info("🎤 Already listening")
                return True

            # Start audio processing thread
            if not self.audio_running:
                self.audio_running = True
                self.audio_thread = threading.Thread(target=self._audio_processing_loop)
                self.audio_thread.daemon = True
                self.audio_thread.start()

            # Change state
            self._set_voice_state(VoiceState.LISTENING)

            logger.info("🎤 Started voice recognition")
            return True

        except Exception as e:
            logger.error(f"❌ Error starting voice recognition: {e}")
            self._set_voice_state(VoiceState.ERROR)
            return False

    def stop_listening(self) -> bool:
        """Stop voice recognition"""
        try:
            if self.current_state == VoiceState.IDLE:
                logger.info("🎤 Already stopped")
                return True

            # Stop audio processing
            self.audio_running = False
            if self.audio_thread and self.audio_thread.is_alive():
                self.audio_thread.join(timeout=2.0)

            # Change state
            self._set_voice_state(VoiceState.IDLE)

            logger.info("🎤 Stopped voice recognition")
            return True

        except Exception as e:
            logger.error(f"❌ Error stopping voice recognition: {e}")
            return False

    async def process_voice_command(self, audio_data: bytes) -> Optional[VoiceCommandResult]:
        """Process voice command from audio data"""
        try:
            command_id = self._generate_command_id()
            start_time = datetime.now()

            # Change state
            self._set_voice_state(VoiceState.PROCESSING)

            # Convert speech to text (simulated)
            recognized_text = await self._speech_to_text(audio_data)

            if not recognized_text:
                logger.warning("⚠️ No speech recognized")
                self._set_voice_state(VoiceState.LISTENING)
                return None

            # Check for wake words
            if self._contains_wake_word(recognized_text):
                self.wake_word_detected.emit(recognized_text)
                self.voice_stats['wake_word_detections'] += 1

            # Parse command
            command, confidence, parameters = self._parse_voice_command(recognized_text)

            # Check confidence threshold
            if confidence < self.confidence_threshold:
                logger.warning(f"⚠️ Low confidence: {confidence:.3f}")
                await self.speak(f"I'm not sure what you said. Could you repeat that?")
                self._set_voice_state(VoiceState.LISTENING)
                return None

            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            # Create result
            result = VoiceCommandResult(
                command_id=command_id,
                original_text=recognized_text,
                recognized_command=command,
                confidence=confidence,
                parameters=parameters,
                timestamp=start_time,
                processing_time=processing_time,
                success=True
            )

            # Store in history
            self.command_history.append(result)
            if len(self.command_history) > 1000:  # Keep last 1000 commands
                self.command_history.pop(0)

            # Update statistics
            self._update_voice_stats(result)

            # Emit signal
            self.voice_command_recognized.emit(self._command_result_to_dict(result))

            # Store last command for repeat functionality
            self.last_command_text = recognized_text

            # Return to listening state
            self._set_voice_state(VoiceState.LISTENING)

            logger.info(f"🎤 Voice command processed: {command.value} "
                       f"(confidence: {confidence:.3f}, time: {processing_time:.3f}s)")

            return result

        except Exception as e:
            logger.error(f"❌ Error processing voice command: {e}")
            self._set_voice_state(VoiceState.ERROR)
            return VoiceCommandResult(
                command_id=self._generate_command_id(),
                original_text="",
                recognized_command=VoiceCommand.HELP,
                confidence=0.0,
                parameters={},
                timestamp=datetime.now(),
                processing_time=0.0,
                success=False,
                error_message=str(e)
            )

    async def speak(self, text: str, voice_id: str = None, speed: float = None,
                   pitch: float = None, volume: float = None, language: str = None,
                   emotion: str = "neutral", priority: int = 5) -> str:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            voice_id: Voice ID to use
            speed: Speech speed (0.5-2.0)
            pitch: Speech pitch (-20.0 to 20.0)
            volume: Speech volume (0.0-1.0)
            language: Language code
            emotion: Emotion for speech
            priority: Priority (1-10, higher is more important)

        Returns:
            Request ID
        """
        try:
            if not self.synthesis_enabled:
                logger.warning("⚠️ Speech synthesis is disabled")
                return None

            request_id = self._generate_synthesis_id()

            # Use defaults if not specified
            voice_id = voice_id or self.default_voice
            speed = speed or self.default_speed
            pitch = pitch or self.default_pitch
            volume = volume or self.default_volume
            language = language or self.default_language

            # Create synthesis request
            request = SpeechSynthesisRequest(
                request_id=request_id,
                text=text,
                voice_id=voice_id,
                speed=speed,
                pitch=pitch,
                volume=volume,
                language=language,
                emotion=emotion,
                priority=priority
            )

            # Add to synthesis queue
            self.synthesis_queue.put(request)

            # Process synthesis
            success = await self._process_speech_synthesis(request)

            # Update statistics
            self.voice_stats['synthesis_requests'] += 1
            if success:
                self.voice_stats['successful_synthesis'] += 1

            # Emit signal
            self.speech_synthesis_completed.emit(request_id, success)

            logger.info(f"🔊 Speech synthesis: {text[:50]}... "
                       f"(voice: {voice_id}, success: {success})")

            return request_id

        except Exception as e:
            logger.error(f"❌ Error in speech synthesis: {e}")
            return None

    async def _speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """Convert speech to text (simulated implementation)"""
        try:
            # Simulate speech recognition processing
            await asyncio.sleep(0.1)

            # In a real implementation, this would use a speech recognition service
            # For simulation, we'll return some sample commands
            sample_commands = [
                "orion system status",
                "create new workflow",
                "execute task number one",
                "open file manager",
                "run terminal command ls",
                "what can you do",
                "help me with automation",
                "stop current task"
            ]

            # Simulate recognition based on audio data length
            if len(audio_data) > 1000:
                import random
                return random.choice(sample_commands)

            return None

        except Exception as e:
            logger.error(f"❌ Error in speech to text: {e}")
            return None

    def _parse_voice_command(self, text: str) -> tuple[VoiceCommand, float, Dict[str, Any]]:
        """Parse voice command from text"""
        try:
            text_lower = text.lower().strip()
            best_command = VoiceCommand.HELP
            best_confidence = 0.0
            parameters = {}

            # Check each command pattern
            for command, patterns in self.command_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        # Calculate confidence based on pattern match
                        confidence = len(pattern) / len(text_lower)
                        confidence = min(1.0, confidence * 1.5)  # Boost confidence

                        if confidence > best_confidence:
                            best_command = command
                            best_confidence = confidence

            # Extract parameters based on command
            if best_command == VoiceCommand.EXECUTE_TASK:
                # Extract task name or number
                words = text_lower.split()
                for i, word in enumerate(words):
                    if word in ["task", "number"] and i + 1 < len(words):
                        parameters['task_identifier'] = words[i + 1]
                        break

            elif best_command == VoiceCommand.FILE_OPERATION:
                # Extract file operation and filename
                if "create" in text_lower:
                    parameters['operation'] = 'create'
                elif "open" in text_lower:
                    parameters['operation'] = 'open'
                elif "delete" in text_lower:
                    parameters['operation'] = 'delete'
                elif "copy" in text_lower:
                    parameters['operation'] = 'copy'
                elif "move" in text_lower:
                    parameters['operation'] = 'move'

                # Extract filename (simplified)
                words = text_lower.split()
                for word in words:
                    if "." in word and len(word) > 3:
                        parameters['filename'] = word
                        break

            elif best_command == VoiceCommand.TERMINAL_COMMAND:
                # Extract command after "run" or "execute"
                words = text_lower.split()
                for i, word in enumerate(words):
                    if word in ["run", "execute", "command"] and i + 1 < len(words):
                        parameters['command'] = " ".join(words[i + 1:])
                        break

            # Ensure minimum confidence
            if best_confidence < 0.3:
                best_confidence = 0.3

            return best_command, best_confidence, parameters

        except Exception as e:
            logger.error(f"❌ Error parsing voice command: {e}")
            return VoiceCommand.HELP, 0.5, {}

    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains wake word"""
        text_lower = text.lower()
        return any(wake_word in text_lower for wake_word in self.wake_words)

    async def _process_speech_synthesis(self, request: SpeechSynthesisRequest) -> bool:
        """Process speech synthesis request"""
        try:
            # Change state
            self._set_voice_state(VoiceState.SPEAKING)

            # Simulate speech synthesis processing
            synthesis_time = len(request.text) * 0.05  # 50ms per character
            await asyncio.sleep(min(synthesis_time, 3.0))  # Max 3 seconds

            # In a real implementation, this would:
            # 1. Use TTS service (Google TTS, Azure Speech, etc.)
            # 2. Generate audio file
            # 3. Play audio through speakers

            logger.info(f"🔊 Speaking: {request.text}")

            # Return to previous state
            self._set_voice_state(VoiceState.LISTENING if self.audio_running else VoiceState.IDLE)

            return True

        except Exception as e:
            logger.error(f"❌ Error in speech synthesis: {e}")
            self._set_voice_state(VoiceState.ERROR)
            return False

    def _audio_processing_loop(self):
        """Audio processing loop (runs in separate thread)"""
        try:
            logger.info("🎤 Audio processing loop started")

            while self.audio_running:
                try:
                    # Simulate audio capture
                    # In a real implementation, this would:
                    # 1. Capture audio from microphone
                    # 2. Detect voice activity
                    # 3. Buffer audio data
                    # 4. Trigger voice command processing

                    # Simulate audio level
                    import random
                    self.current_audio_level = random.uniform(0.0, 1.0)
                    self.audio_level_changed.emit(self.current_audio_level)

                    # Sleep to simulate real-time processing
                    threading.Event().wait(0.1)

                except Exception as e:
                    logger.error(f"❌ Error in audio processing: {e}")
                    break

            logger.info("🎤 Audio processing loop stopped")

        except Exception as e:
            logger.error(f"❌ Fatal error in audio processing loop: {e}")

    def _set_voice_state(self, new_state: VoiceState):
        """Set voice system state"""
        if self.current_state != new_state:
            self.current_state = new_state
            self.voice_state_changed.emit(new_state.value)
            logger.debug(f"🎤 Voice state changed to: {new_state.value}")

    def _update_voice_stats(self, result: VoiceCommandResult):
        """Update voice statistics"""
        self.voice_stats['total_commands'] += 1

        if result.success:
            self.voice_stats['successful_commands'] += 1
        else:
            self.voice_stats['failed_commands'] += 1

        # Update averages
        total = self.voice_stats['total_commands']

        # Average confidence
        current_avg_conf = self.voice_stats['average_confidence']
        new_avg_conf = ((current_avg_conf * (total - 1)) + result.confidence) / total
        self.voice_stats['average_confidence'] = new_avg_conf

        # Average processing time
        current_avg_time = self.voice_stats['average_processing_time']
        new_avg_time = ((current_avg_time * (total - 1)) + result.processing_time) / total
        self.voice_stats['average_processing_time'] = new_avg_time

    def _monitor_voice_system(self):
        """Monitor voice system health"""
        try:
            # Check if audio thread is alive
            if self.audio_running and (not self.audio_thread or not self.audio_thread.is_alive()):
                logger.warning("⚠️ Audio thread died, restarting...")
                self.start_listening()

            # Check synthesis queue size
            if self.synthesis_queue.qsize() > 10:
                logger.warning(f"⚠️ Synthesis queue is large: {self.synthesis_queue.qsize()}")

        except Exception as e:
            logger.error(f"❌ Error monitoring voice system: {e}")

    def _generate_command_id(self) -> str:
        """Generate unique command ID"""
        self.command_counter += 1
        return f"voice_cmd_{self.command_counter:06d}"

    def _generate_synthesis_id(self) -> str:
        """Generate unique synthesis request ID"""
        self.synthesis_counter += 1
        return f"speech_syn_{self.synthesis_counter:06d}"

    def _command_result_to_dict(self, result: VoiceCommandResult) -> Dict[str, Any]:
        """Convert VoiceCommandResult to dictionary"""
        return {
            'command_id': result.command_id,
            'original_text': result.original_text,
            'recognized_command': result.recognized_command.value,
            'confidence': result.confidence,
            'parameters': result.parameters,
            'timestamp': result.timestamp.isoformat(),
            'processing_time': result.processing_time,
            'success': result.success,
            'error_message': result.error_message
        }

    def get_voice_stats(self) -> Dict[str, Any]:
        """Get voice statistics"""
        return self.voice_stats.copy()

    def get_command_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get voice command history"""
        history = self.command_history[-limit:] if limit > 0 else self.command_history
        return [self._command_result_to_dict(result) for result in history]

    def get_voice_state(self) -> str:
        """Get current voice state"""
        return self.current_state.value

    def set_wake_words(self, wake_words: List[str]):
        """Set wake words"""
        self.wake_words = [word.lower() for word in wake_words]
        logger.info(f"🎤 Wake words updated: {self.wake_words}")

    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"🎤 Confidence threshold set to: {self.confidence_threshold}")

    def enable_continuous_listening(self, enabled: bool):
        """Enable/disable continuous listening"""
        self.continuous_listening = enabled
        logger.info(f"🎤 Continuous listening: {'enabled' if enabled else 'disabled'}")

# Singleton instance
_voice_manager = None

def get_voice_manager() -> VoiceManager:
    """Get the singleton Voice Manager instance"""
    global _voice_manager
    if _voice_manager is None:
        _voice_manager = VoiceManager()
    return _voice_manager
