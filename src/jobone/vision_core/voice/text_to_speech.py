#!/usr/bin/env python3
"""
Text-to-Speech Module
Sprint 8.1 - Atlas Prompt 8.1.3: Basic Voice Command System Integration
Orion Vision Core - Autonomous AI Operating System

This module provides text-to-speech synthesis capabilities for the Orion Vision Core
autonomous AI operating system, enabling voice responses and audio feedback.

Author: Orion Development Team
Version: 8.1.0
Date: 30 Mayıs 2025
"""

import logging
import threading
import time
from typing import Optional, Callable, Dict, Any, List
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TextToSpeech")

class SpeechState(Enum):
    """Text-to-speech state enumeration"""
    IDLE = "idle"
    SPEAKING = "speaking"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"

class Voice:
    """Voice configuration data structure"""
    def __init__(self, voice_id: str, name: str, language: str, gender: str, rate: int = 200):
        self.voice_id = voice_id
        self.name = name
        self.language = language
        self.gender = gender
        self.rate = rate

class TextToSpeechEngine(QObject):
    """
    Text-to-speech engine with multiple backend support.

    Features:
    - Multiple TTS engines (pyttsx3, system TTS)
    - Voice selection and configuration
    - Speech rate and volume control
    - Queue management for multiple texts
    - Background speech synthesis
    - Error handling and recovery
    """

    # Signals
    speech_started = pyqtSignal(str)  # Text being spoken
    speech_finished = pyqtSignal(str)  # Text that was spoken
    speech_paused = pyqtSignal()
    speech_resumed = pyqtSignal()
    state_changed = pyqtSignal(str)  # SpeechState
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self):
        """Initialize text-to-speech engine"""
        super().__init__()

        # Speech state
        self.current_state = SpeechState.DISABLED
        self.is_speaking = False
        self.is_enabled = False

        # TTS engine
        self.tts_engine = None
        self.available_voices: List[Voice] = []
        self.current_voice: Optional[Voice] = None

        # Speech settings
        self.speech_rate = 200  # words per minute
        self.speech_volume = 0.8  # 0.0 to 1.0
        self.speech_pitch = 0  # -50 to 50

        # Speech queue
        self.speech_queue: List[str] = []
        self.current_text = ""
        self.queue_lock = threading.Lock()

        # Background processing
        self.speech_thread = None
        self.stop_speech_flag = False

        # Statistics
        self.stats = {
            'texts_spoken': 0,
            'total_characters': 0,
            'total_speaking_time': 0.0,
            'average_speech_rate': 0.0,
            'queue_max_size': 0
        }

        # Initialize TTS system
        self._initialize_tts()

        logger.info("🔊 Text-to-Speech Engine initialized")

    def _initialize_tts(self):
        """Initialize text-to-speech system"""
        try:
            # Try to import pyttsx3
            global pyttsx3
            import pyttsx3

            self.tts_engine = pyttsx3.init()

            if self.tts_engine:
                # Configure engine
                self.tts_engine.setProperty('rate', self.speech_rate)
                self.tts_engine.setProperty('volume', self.speech_volume)

                # Load available voices
                self._load_available_voices()

                # Set default voice
                if self.available_voices:
                    self.current_voice = self.available_voices[0]
                    self.tts_engine.setProperty('voice', self.current_voice.voice_id)

                self.is_enabled = True
                self._change_state(SpeechState.IDLE)

                logger.info("🔊 TTS engine initialized successfully")

            else:
                logger.error("❌ Failed to initialize TTS engine")
                self._change_state(SpeechState.DISABLED)

        except ImportError:
            # Silent fail - no warning for optional dependency
            self._change_state(SpeechState.DISABLED)
        except Exception:
            # Silent fail - no warning for optional dependency
            self._change_state(SpeechState.DISABLED)

    def _load_available_voices(self):
        """Load available system voices"""
        try:
            if not self.tts_engine:
                return

            voices = self.tts_engine.getProperty('voices')
            self.available_voices = []

            for voice in voices:
                # Parse voice information
                voice_id = voice.id
                name = getattr(voice, 'name', 'Unknown')
                languages = getattr(voice, 'languages', [])
                language = languages[0] if languages else 'en'

                # Determine gender from name (simple heuristic)
                gender = 'female' if any(word in name.lower() for word in ['female', 'woman', 'zira', 'hazel']) else 'male'

                voice_obj = Voice(voice_id, name, language, gender, self.speech_rate)
                self.available_voices.append(voice_obj)

            logger.info(f"🔊 Loaded {len(self.available_voices)} voices")

            # Log available voices
            for voice in self.available_voices:
                logger.debug(f"🔊 Voice: {voice.name} ({voice.language}, {voice.gender})")

        except Exception as e:
            logger.error(f"❌ Failed to load voices: {e}")

    def _change_state(self, new_state: SpeechState):
        """Change speech state and emit signal"""
        if self.current_state != new_state:
            old_state = self.current_state
            self.current_state = new_state

            logger.info(f"🔊 Speech state changed: {old_state.value} → {new_state.value}")
            self.state_changed.emit(new_state.value)

    def speak(self, text: str, interrupt: bool = False) -> bool:
        """
        Speak the given text.

        Args:
            text: Text to speak
            interrupt: If True, interrupt current speech

        Returns:
            True if text was queued/started successfully, False otherwise
        """
        if not self.is_enabled or self.current_state == SpeechState.DISABLED:
            logger.error("❌ Text-to-speech not available")
            return False

        if not text.strip():
            logger.warning("⚠️ Empty text provided")
            return False

        try:
            with self.queue_lock:
                if interrupt:
                    self.stop_speech()
                    self.speech_queue.clear()

                self.speech_queue.append(text)
                self.stats['queue_max_size'] = max(self.stats['queue_max_size'], len(self.speech_queue))

            # Start speech processing if not already running
            if not self.is_speaking:
                self._start_speech_processing()

            logger.info(f"🔊 Text queued for speech: {text[:50]}...")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to queue text for speech: {e}")
            self.error_occurred.emit(str(e))
            return False

    def stop_speech(self):
        """Stop current speech"""
        if not self.is_speaking:
            return

        try:
            self.stop_speech_flag = True

            if self.tts_engine:
                self.tts_engine.stop()

            self.is_speaking = False
            self._change_state(SpeechState.IDLE)

            logger.info("🔊 Speech stopped")

        except Exception as e:
            logger.error(f"❌ Failed to stop speech: {e}")

    def pause_speech(self):
        """Pause current speech"""
        if not self.is_speaking or self.current_state != SpeechState.SPEAKING:
            return

        try:
            # Note: pyttsx3 doesn't support pause/resume, so we implement it differently
            self._change_state(SpeechState.PAUSED)
            self.speech_paused.emit()

            logger.info("🔊 Speech paused")

        except Exception as e:
            logger.error(f"❌ Failed to pause speech: {e}")

    def resume_speech(self):
        """Resume paused speech"""
        if self.current_state != SpeechState.PAUSED:
            return

        try:
            self._change_state(SpeechState.SPEAKING)
            self.speech_resumed.emit()

            logger.info("🔊 Speech resumed")

        except Exception as e:
            logger.error(f"❌ Failed to resume speech: {e}")

    def _start_speech_processing(self):
        """Start background speech processing"""
        if self.speech_thread and self.speech_thread.is_alive():
            return

        def speech_worker():
            """Background speech processing worker"""
            self.is_speaking = True
            self.stop_speech_flag = False

            try:
                while True:
                    # Get next text from queue
                    with self.queue_lock:
                        if not self.speech_queue or self.stop_speech_flag:
                            break
                        text = self.speech_queue.pop(0)

                    # Speak the text
                    self._speak_text(text)

                    if self.stop_speech_flag:
                        break

            except Exception as e:
                logger.error(f"❌ Speech processing error: {e}")
                self.error_occurred.emit(str(e))
            finally:
                self.is_speaking = False
                self._change_state(SpeechState.IDLE)

        self.speech_thread = threading.Thread(target=speech_worker)
        self.speech_thread.daemon = True
        self.speech_thread.start()

    def _speak_text(self, text: str):
        """Speak a single text"""
        try:
            if not self.tts_engine or self.stop_speech_flag:
                return

            self.current_text = text
            self._change_state(SpeechState.SPEAKING)
            self.speech_started.emit(text)

            start_time = time.time()

            # Use pyttsx3 to speak
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

            end_time = time.time()
            speaking_time = end_time - start_time

            # Update statistics
            self.stats['texts_spoken'] += 1
            self.stats['total_characters'] += len(text)
            self.stats['total_speaking_time'] += speaking_time

            if self.stats['texts_spoken'] > 0:
                self.stats['average_speech_rate'] = self.stats['total_characters'] / self.stats['total_speaking_time'] * 60  # chars per minute

            self.speech_finished.emit(text)
            logger.info(f"🔊 Finished speaking: {text[:50]}...")

        except Exception as e:
            logger.error(f"❌ Failed to speak text: {e}")
            self.error_occurred.emit(str(e))

    def set_voice(self, voice_name: str) -> bool:
        """
        Set the current voice.

        Args:
            voice_name: Name of the voice to use

        Returns:
            True if voice was set successfully, False otherwise
        """
        try:
            for voice in self.available_voices:
                if voice.name == voice_name:
                    self.current_voice = voice
                    if self.tts_engine:
                        self.tts_engine.setProperty('voice', voice.voice_id)
                    logger.info(f"🔊 Voice set to: {voice_name}")
                    return True

            logger.error(f"❌ Voice not found: {voice_name}")
            return False

        except Exception as e:
            logger.error(f"❌ Failed to set voice: {e}")
            return False

    def configure(self, **kwargs):
        """
        Configure text-to-speech settings.

        Args:
            **kwargs: Configuration parameters
        """
        try:
            if 'rate' in kwargs:
                self.speech_rate = kwargs['rate']
                if self.tts_engine:
                    self.tts_engine.setProperty('rate', self.speech_rate)

            if 'volume' in kwargs:
                self.speech_volume = max(0.0, min(1.0, kwargs['volume']))
                if self.tts_engine:
                    self.tts_engine.setProperty('volume', self.speech_volume)

            if 'pitch' in kwargs:
                self.speech_pitch = max(-50, min(50, kwargs['pitch']))
                # Note: pyttsx3 doesn't support pitch control directly

            logger.info(f"🔊 TTS configured: {kwargs}")

        except Exception as e:
            logger.error(f"❌ Failed to configure TTS: {e}")

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices"""
        return [
            {
                'id': voice.voice_id,
                'name': voice.name,
                'language': voice.language,
                'gender': voice.gender,
                'rate': voice.rate
            }
            for voice in self.available_voices
        ]

    def clear_queue(self):
        """Clear the speech queue"""
        with self.queue_lock:
            self.speech_queue.clear()
        logger.info("🔊 Speech queue cleared")

    def get_status(self) -> Dict[str, Any]:
        """Get text-to-speech status"""
        return {
            'state': self.current_state.value,
            'is_enabled': self.is_enabled,
            'is_speaking': self.is_speaking,
            'current_voice': self.current_voice.name if self.current_voice else None,
            'queue_size': len(self.speech_queue),
            'current_text': self.current_text,
            'settings': {
                'speech_rate': self.speech_rate,
                'speech_volume': self.speech_volume,
                'speech_pitch': self.speech_pitch
            },
            'statistics': self.stats,
            'available_voices_count': len(self.available_voices)
        }

# Singleton instance
_tts_engine = None

def get_tts_engine() -> TextToSpeechEngine:
    """Get the singleton text-to-speech engine instance"""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TextToSpeechEngine()
    return _tts_engine

# Example usage and testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test text-to-speech
    tts_engine = get_tts_engine()

    def on_speech_started(text):
        print(f"Started speaking: {text}")

    def on_speech_finished(text):
        print(f"Finished speaking: {text}")

    def on_state_changed(state):
        print(f"TTS State: {state}")

    def on_error(error):
        print(f"TTS Error: {error}")

    # Connect signals
    tts_engine.speech_started.connect(on_speech_started)
    tts_engine.speech_finished.connect(on_speech_finished)
    tts_engine.state_changed.connect(on_state_changed)
    tts_engine.error_occurred.connect(on_error)

    # Print status
    status = tts_engine.get_status()
    print(f"TTS Status: {status}")

    # Print available voices
    voices = tts_engine.get_available_voices()
    print(f"Available voices: {len(voices)}")
    for voice in voices[:3]:  # Show first 3 voices
        print(f"  - {voice['name']} ({voice['language']}, {voice['gender']})")

    # Test speech
    if tts_engine.is_enabled:
        print("Testing text-to-speech...")
        tts_engine.speak("Hello! I am Orion, your autonomous AI assistant.")
        tts_engine.speak("Text-to-speech system is working correctly.")
    else:
        print("Text-to-speech not available")

    sys.exit(app.exec())
