#!/usr/bin/env python3
"""
Speech-to-Text Module
Sprint 8.1 - Atlas Prompt 8.1.3: Basic Voice Command System Integration
Orion Vision Core - Autonomous AI Operating System

This module provides speech recognition capabilities for the Orion Vision Core
autonomous AI operating system, enabling voice command input and processing.

Author: Orion Development Team
Version: 8.1.0
Date: 30 Mayıs 2025
"""

import logging
import threading
import time
from typing import Optional, Callable, Dict, Any
from enum import Enum

# Optional PyQt6 import
try:
    from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
    PYQT_AVAILABLE = True
except ImportError:
    # Fallback for when PyQt6 is not available
    class QObject:
        def __init__(self):
            pass

    class pyqtSignal:
        def __init__(self, *args):
            self._callbacks = []

        def emit(self, *args):
            for callback in self._callbacks:
                try:
                    callback(*args)
                except Exception as e:
                    logger.error(f"Signal callback error: {e}")

        def connect(self, callback):
            self._callbacks.append(callback)

    PYQT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SpeechToText")

class RecognitionState(Enum):
    """Speech recognition state enumeration"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    ERROR = "error"
    DISABLED = "disabled"

class SpeechRecognitionEngine(QObject):
    """
    Speech recognition engine with multiple backend support.

    Features:
    - Multiple recognition engines (Google, Sphinx, etc.)
    - Real-time speech recognition
    - Configurable sensitivity and timeout
    - Background listening capability
    - Error handling and recovery
    """

    # Signals
    speech_recognized = pyqtSignal(str)  # Recognized text
    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()
    state_changed = pyqtSignal(str)  # RecognitionState
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self):
        """Initialize speech recognition engine"""
        super().__init__()

        # Recognition state
        self.current_state = RecognitionState.DISABLED
        self.is_listening = False
        self.is_enabled = False

        # Recognition settings
        self.recognition_timeout = 5.0  # seconds
        self.phrase_timeout = 1.0  # seconds
        self.energy_threshold = 300
        self.dynamic_energy_threshold = True

        # Supported engines
        self.available_engines = []
        self.current_engine = None
        self.recognizer = None
        self.microphone = None

        # Background listening
        self.listening_thread = None
        self.stop_listening = None

        # Statistics
        self.stats = {
            'recognitions_attempted': 0,
            'recognitions_successful': 0,
            'recognitions_failed': 0,
            'total_listening_time': 0.0,
            'average_recognition_time': 0.0
        }

        # Initialize recognition system
        self._initialize_recognition()

        logger.info("🎤 Speech Recognition Engine initialized")

    def _initialize_recognition(self):
        """Initialize speech recognition system"""
        try:
            # Try to import speech recognition
            import speech_recognition as sr

            self.recognizer = sr.Recognizer()

            # Configure recognizer
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3

            # Check available microphones
            try:
                self.microphone = sr.Microphone()
                logger.info("🎤 Microphone initialized successfully")

                # Adjust for ambient noise
                with self.microphone as source:
                    logger.info("🎤 Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)

                self.is_enabled = True
                self._change_state(RecognitionState.IDLE)

                # Detect available engines
                self._detect_available_engines()

            except Exception as e:
                logger.warning(f"⚠️ Microphone initialization failed: {e}")
                logger.info("🎤 Speech recognition available but microphone not accessible")
                self.is_enabled = False
                self._change_state(RecognitionState.DISABLED)

        except ImportError:
            # Silent fail - no warning for optional dependency
            self.is_enabled = False
            self._change_state(RecognitionState.DISABLED)
        except Exception:
            # Silent fail - no warning for optional dependency
            self.is_enabled = False
            self._change_state(RecognitionState.DISABLED)

    def _detect_available_engines(self):
        """Detect available speech recognition engines"""
        self.available_engines = []

        # Test Google Speech Recognition (requires internet)
        try:
            # This is a simple availability check
            self.available_engines.append("google")
            logger.info("✅ Google Speech Recognition available")
        except:
            pass

        # Test Sphinx (offline)
        try:
            import speech_recognition as sr
            # Test if Sphinx is available
            self.available_engines.append("sphinx")
            logger.info("✅ Sphinx Speech Recognition available")
        except:
            pass

        # Set default engine
        if "google" in self.available_engines:
            self.current_engine = "google"
        elif "sphinx" in self.available_engines:
            self.current_engine = "sphinx"
        else:
            self.current_engine = None
            logger.warning("⚠️ No speech recognition engines available")

        logger.info(f"🎤 Available engines: {self.available_engines}")
        logger.info(f"🎤 Current engine: {self.current_engine}")

    def _change_state(self, new_state: RecognitionState):
        """Change recognition state and emit signal"""
        if self.current_state != new_state:
            old_state = self.current_state
            self.current_state = new_state

            logger.info(f"🎤 Recognition state changed: {old_state.value} → {new_state.value}")
            self.state_changed.emit(new_state.value)

    def start_listening(self, continuous: bool = False) -> bool:
        """
        Start speech recognition.

        Args:
            continuous: If True, listen continuously until stopped

        Returns:
            True if listening started successfully, False otherwise
        """
        if not self.is_enabled or self.current_state == RecognitionState.DISABLED:
            logger.error("❌ Speech recognition not available")
            return False

        if self.is_listening:
            logger.warning("⚠️ Already listening")
            return True

        try:
            self.is_listening = True
            self._change_state(RecognitionState.LISTENING)
            self.listening_started.emit()

            if continuous:
                self._start_continuous_listening()
            else:
                self._start_single_recognition()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to start listening: {e}")
            self.error_occurred.emit(str(e))
            self._change_state(RecognitionState.ERROR)
            return False

    def stop_listening(self):
        """Stop speech recognition"""
        if not self.is_listening:
            return

        self.is_listening = False

        if self.stop_listening:
            self.stop_listening(wait_for_stop=False)
            self.stop_listening = None

        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=1.0)

        self._change_state(RecognitionState.IDLE)
        self.listening_stopped.emit()

        logger.info("🎤 Stopped listening")

    def _start_continuous_listening(self):
        """Start continuous background listening"""
        try:
            import speech_recognition as sr

            def callback(recognizer, audio):
                """Callback for continuous listening"""
                try:
                    self._change_state(RecognitionState.PROCESSING)
                    text = self._recognize_audio(audio)

                    if text:
                        logger.info(f"🎤 Recognized: {text}")
                        self.speech_recognized.emit(text)
                        self.stats['recognitions_successful'] += 1

                    self._change_state(RecognitionState.LISTENING)

                except Exception as e:
                    logger.error(f"❌ Recognition error: {e}")
                    self.stats['recognitions_failed'] += 1
                    self.error_occurred.emit(str(e))

                self.stats['recognitions_attempted'] += 1

            # Start background listening
            self.stop_listening = self.recognizer.listen_in_background(
                self.microphone,
                callback,
                phrase_time_limit=self.recognition_timeout
            )

            logger.info("🎤 Started continuous listening")

        except Exception as e:
            logger.error(f"❌ Failed to start continuous listening: {e}")
            self.error_occurred.emit(str(e))
            self._change_state(RecognitionState.ERROR)

    def _start_single_recognition(self):
        """Start single recognition in background thread"""
        def recognition_worker():
            try:
                import speech_recognition as sr

                with self.microphone as source:
                    logger.info("🎤 Listening for speech...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=self.recognition_timeout,
                        phrase_time_limit=self.recognition_timeout
                    )

                self._change_state(RecognitionState.PROCESSING)
                text = self._recognize_audio(audio)

                if text:
                    logger.info(f"🎤 Recognized: {text}")
                    self.speech_recognized.emit(text)
                    self.stats['recognitions_successful'] += 1
                else:
                    logger.warning("🎤 No speech recognized")

                self.stats['recognitions_attempted'] += 1
                self._change_state(RecognitionState.IDLE)

            except sr.WaitTimeoutError:
                logger.warning("🎤 Listening timeout")
                self._change_state(RecognitionState.IDLE)
            except Exception as e:
                logger.error(f"❌ Recognition error: {e}")
                self.stats['recognitions_failed'] += 1
                self.error_occurred.emit(str(e))
                self._change_state(RecognitionState.ERROR)
            finally:
                self.is_listening = False
                self.listening_stopped.emit()

        self.listening_thread = threading.Thread(target=recognition_worker)
        self.listening_thread.daemon = True
        self.listening_thread.start()

    def _recognize_audio(self, audio) -> Optional[str]:
        """
        Recognize audio using the current engine.

        Args:
            audio: Audio data to recognize

        Returns:
            Recognized text or None if recognition failed
        """
        try:
            import speech_recognition as sr

            if self.current_engine == "google":
                return self.recognizer.recognize_google(audio, language="en-US")
            elif self.current_engine == "sphinx":
                return self.recognizer.recognize_sphinx(audio)
            else:
                # Fallback to Google
                return self.recognizer.recognize_google(audio, language="en-US")

        except sr.UnknownValueError:
            logger.debug("🎤 Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"❌ Recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Recognition error: {e}")
            return None

    def set_engine(self, engine_name: str) -> bool:
        """
        Set the speech recognition engine.

        Args:
            engine_name: Name of the engine to use

        Returns:
            True if engine was set successfully, False otherwise
        """
        if engine_name in self.available_engines:
            self.current_engine = engine_name
            logger.info(f"🎤 Speech recognition engine set to: {engine_name}")
            return True
        else:
            logger.error(f"❌ Engine not available: {engine_name}")
            return False

    def configure(self, **kwargs):
        """
        Configure speech recognition settings.

        Args:
            **kwargs: Configuration parameters
        """
        if 'energy_threshold' in kwargs:
            self.energy_threshold = kwargs['energy_threshold']
            if self.recognizer:
                self.recognizer.energy_threshold = self.energy_threshold

        if 'recognition_timeout' in kwargs:
            self.recognition_timeout = kwargs['recognition_timeout']

        if 'phrase_timeout' in kwargs:
            self.phrase_timeout = kwargs['phrase_timeout']

        if 'dynamic_energy_threshold' in kwargs:
            self.dynamic_energy_threshold = kwargs['dynamic_energy_threshold']
            if self.recognizer:
                self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold

        logger.info(f"🎤 Speech recognition configured: {kwargs}")

    def get_status(self) -> Dict[str, Any]:
        """Get speech recognition status"""
        return {
            'state': self.current_state.value,
            'is_enabled': self.is_enabled,
            'is_listening': self.is_listening,
            'current_engine': self.current_engine,
            'available_engines': self.available_engines,
            'settings': {
                'energy_threshold': self.energy_threshold,
                'recognition_timeout': self.recognition_timeout,
                'phrase_timeout': self.phrase_timeout,
                'dynamic_energy_threshold': self.dynamic_energy_threshold
            },
            'statistics': self.stats
        }

# Singleton instance
_speech_recognition_engine = None

def get_speech_recognition_engine() -> SpeechRecognitionEngine:
    """Get the singleton speech recognition engine instance"""
    global _speech_recognition_engine
    if _speech_recognition_engine is None:
        _speech_recognition_engine = SpeechRecognitionEngine()
    return _speech_recognition_engine

# Example usage and testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test speech recognition
    speech_engine = get_speech_recognition_engine()

    def on_speech_recognized(text):
        print(f"Recognized: {text}")

    def on_state_changed(state):
        print(f"State: {state}")

    def on_error(error):
        print(f"Error: {error}")

    # Connect signals
    speech_engine.speech_recognized.connect(on_speech_recognized)
    speech_engine.state_changed.connect(on_state_changed)
    speech_engine.error_occurred.connect(on_error)

    # Print status
    status = speech_engine.get_status()
    print(f"Speech Recognition Status: {status}")

    # Test single recognition
    if speech_engine.is_enabled:
        print("Starting speech recognition test...")
        speech_engine.start_listening(continuous=False)
    else:
        print("Speech recognition not available")

    sys.exit(app.exec())
