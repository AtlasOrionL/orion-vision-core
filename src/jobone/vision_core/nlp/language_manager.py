"""
🗣️ Orion Vision Core - Language Manager
Multi-language processing and management

This module provides comprehensive language management:
- Multi-language support and detection
- Language switching and configuration
- Cultural context awareness
- Localization and internationalization
- Language-specific processing rules

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupportedLanguage(Enum):
    """Supported languages with ISO codes"""
    ENGLISH = ("en", "English", "🇺🇸")
    TURKISH = ("tr", "Türkçe", "🇹🇷")
    SPANISH = ("es", "Español", "🇪🇸")
    FRENCH = ("fr", "Français", "🇫🇷")
    GERMAN = ("de", "Deutsch", "🇩🇪")
    ITALIAN = ("it", "Italiano", "🇮🇹")
    PORTUGUESE = ("pt", "Português", "🇵🇹")
    RUSSIAN = ("ru", "Русский", "🇷🇺")
    CHINESE = ("zh", "中文", "🇨🇳")
    JAPANESE = ("ja", "日本語", "🇯🇵")
    KOREAN = ("ko", "한국어", "🇰🇷")
    ARABIC = ("ar", "العربية", "🇸🇦")
    HINDI = ("hi", "हिन्दी", "🇮🇳")
    DUTCH = ("nl", "Nederlands", "🇳🇱")
    SWEDISH = ("sv", "Svenska", "🇸🇪")
    NORWEGIAN = ("no", "Norsk", "🇳🇴")
    DANISH = ("da", "Dansk", "🇩🇰")
    FINNISH = ("fi", "Suomi", "🇫🇮")
    POLISH = ("pl", "Polski", "🇵🇱")
    CZECH = ("cs", "Čeština", "🇨🇿")
    
    def __init__(self, code: str, name: str, flag: str):
        self.code = code
        self.name = name
        self.flag = flag

@dataclass
class LanguageConfig:
    """Configuration for language processing"""
    primary_language: SupportedLanguage = SupportedLanguage.ENGLISH
    fallback_language: SupportedLanguage = SupportedLanguage.ENGLISH
    auto_detect: bool = True
    auto_translate: bool = False
    cultural_adaptation: bool = True
    formal_tone: bool = False
    regional_variant: Optional[str] = None
    custom_phrases: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class LanguageDetectionResult:
    """Result of language detection"""
    detected_language: SupportedLanguage
    confidence: float
    alternative_languages: List[Tuple[SupportedLanguage, float]] = field(default_factory=list)
    text_sample: str = ""

@dataclass
class CulturalContext:
    """Cultural context information for a language"""
    language: SupportedLanguage
    formal_greetings: List[str] = field(default_factory=list)
    informal_greetings: List[str] = field(default_factory=list)
    polite_expressions: List[str] = field(default_factory=list)
    cultural_notes: List[str] = field(default_factory=list)
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M"
    number_format: str = "1,234.56"

class LanguageManager:
    """
    Multi-language processing and management system.
    
    Provides comprehensive language support with:
    - Language detection and switching
    - Cultural context awareness
    - Localization support
    - Multi-language text processing
    - Regional adaptation
    """
    
    def __init__(self, config: Optional[LanguageConfig] = None):
        """
        Initialize the language manager.
        
        Args:
            config: Language configuration (optional)
        """
        self.config = config or LanguageConfig()
        self.current_language = self.config.primary_language
        self.cultural_contexts: Dict[SupportedLanguage, CulturalContext] = {}
        self.language_patterns: Dict[SupportedLanguage, Dict[str, List[str]]] = {}
        self.localization_data: Dict[SupportedLanguage, Dict[str, str]] = {}
        
        # Performance metrics
        self.metrics = {
            'detections_performed': 0,
            'language_switches': 0,
            'translations_requested': 0,
            'cultural_adaptations': 0,
            'average_detection_time': 0.0
        }
        
        # Initialize language data
        self._initialize_language_data()
        
        logger.info(f"🌍 Language Manager initialized with primary language: {self.current_language.name}")
    
    def _initialize_language_data(self):
        """Initialize language-specific data and patterns"""
        
        # Initialize cultural contexts
        self._initialize_cultural_contexts()
        
        # Initialize language patterns
        self._initialize_language_patterns()
        
        # Initialize localization data
        self._initialize_localization_data()
        
        logger.info(f"📚 Initialized data for {len(self.cultural_contexts)} languages")
    
    def _initialize_cultural_contexts(self):
        """Initialize cultural context data for supported languages"""
        
        # English cultural context
        self.cultural_contexts[SupportedLanguage.ENGLISH] = CulturalContext(
            language=SupportedLanguage.ENGLISH,
            formal_greetings=["Good morning", "Good afternoon", "Good evening", "Hello"],
            informal_greetings=["Hi", "Hey", "What's up", "Howdy"],
            polite_expressions=["Please", "Thank you", "You're welcome", "Excuse me"],
            cultural_notes=["Direct communication style", "Individualistic culture", "Time-conscious"],
            date_format="%m/%d/%Y",
            time_format="%I:%M %p",
            number_format="1,234.56"
        )
        
        # Turkish cultural context
        self.cultural_contexts[SupportedLanguage.TURKISH] = CulturalContext(
            language=SupportedLanguage.TURKISH,
            formal_greetings=["Günaydın", "İyi günler", "İyi akşamlar", "Merhaba"],
            informal_greetings=["Selam", "Naber", "Nasılsın"],
            polite_expressions=["Lütfen", "Teşekkür ederim", "Rica ederim", "Affedersiniz"],
            cultural_notes=["Respectful communication", "Family-oriented culture", "Hospitality important"],
            date_format="%d.%m.%Y",
            time_format="%H:%M",
            number_format="1.234,56"
        )
        
        # Spanish cultural context
        self.cultural_contexts[SupportedLanguage.SPANISH] = CulturalContext(
            language=SupportedLanguage.SPANISH,
            formal_greetings=["Buenos días", "Buenas tardes", "Buenas noches", "Hola"],
            informal_greetings=["¡Hola!", "¿Qué tal?", "¿Cómo estás?"],
            polite_expressions=["Por favor", "Gracias", "De nada", "Disculpe"],
            cultural_notes=["Warm communication style", "Family-centered", "Personal relationships important"],
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format="1.234,56"
        )
        
        # Add more languages as needed
        for lang in SupportedLanguage:
            if lang not in self.cultural_contexts:
                # Default cultural context for other languages
                self.cultural_contexts[lang] = CulturalContext(
                    language=lang,
                    formal_greetings=["Hello", "Good day"],
                    informal_greetings=["Hi", "Hey"],
                    polite_expressions=["Please", "Thank you"],
                    cultural_notes=["Standard communication style"]
                )
    
    def _initialize_language_patterns(self):
        """Initialize language detection patterns"""
        
        # Common words and patterns for language detection
        self.language_patterns = {
            SupportedLanguage.ENGLISH: {
                'common_words': ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'],
                'patterns': ['ing$', 'tion$', 'ly$', '^un', '^re']
            },
            SupportedLanguage.TURKISH: {
                'common_words': ['ve', 'bir', 'bu', 'da', 'de', 'ile', 'için', 'var', 'olan', 'gibi'],
                'patterns': ['lar$', 'ler$', 'ın$', 'un$', 'ım$', 'um$']
            },
            SupportedLanguage.SPANISH: {
                'common_words': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se'],
                'patterns': ['ción$', 'dad$', 'mente$', '^des', 'ando$', 'iendo$']
            },
            SupportedLanguage.FRENCH: {
                'common_words': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
                'patterns': ['tion$', 'ment$', 'eur$', '^dé', 'ant$', 'ent$']
            },
            SupportedLanguage.GERMAN: {
                'common_words': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
                'patterns': ['ung$', 'keit$', 'lich$', 'isch$', 'ern$']
            }
        }
    
    def _initialize_localization_data(self):
        """Initialize localization strings"""
        
        self.localization_data = {
            SupportedLanguage.ENGLISH: {
                'welcome': 'Welcome',
                'goodbye': 'Goodbye',
                'please_wait': 'Please wait',
                'error': 'Error',
                'success': 'Success',
                'loading': 'Loading...',
                'save': 'Save',
                'cancel': 'Cancel',
                'yes': 'Yes',
                'no': 'No'
            },
            SupportedLanguage.TURKISH: {
                'welcome': 'Hoş geldiniz',
                'goodbye': 'Güle güle',
                'please_wait': 'Lütfen bekleyin',
                'error': 'Hata',
                'success': 'Başarılı',
                'loading': 'Yükleniyor...',
                'save': 'Kaydet',
                'cancel': 'İptal',
                'yes': 'Evet',
                'no': 'Hayır'
            },
            SupportedLanguage.SPANISH: {
                'welcome': 'Bienvenido',
                'goodbye': 'Adiós',
                'please_wait': 'Por favor espere',
                'error': 'Error',
                'success': 'Éxito',
                'loading': 'Cargando...',
                'save': 'Guardar',
                'cancel': 'Cancelar',
                'yes': 'Sí',
                'no': 'No'
            }
        }
    
    async def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Detect the language of given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            LanguageDetectionResult with detection details
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Simple pattern-based detection (in real implementation, use ML models)
            scores = {}
            text_lower = text.lower()
            words = text_lower.split()
            
            for language, patterns in self.language_patterns.items():
                score = 0
                
                # Check common words
                for word in words:
                    if word in patterns.get('common_words', []):
                        score += 2
                
                # Check patterns
                import re
                for pattern in patterns.get('patterns', []):
                    matches = len(re.findall(pattern, text_lower))
                    score += matches
                
                scores[language] = score / max(len(words), 1)
            
            # Find best match
            if scores:
                best_language = max(scores, key=scores.get)
                confidence = min(scores[best_language], 1.0)
                
                # Create alternatives list
                alternatives = [
                    (lang, score) for lang, score in scores.items() 
                    if lang != best_language and score > 0
                ]
                alternatives.sort(key=lambda x: x[1], reverse=True)
                alternatives = alternatives[:3]  # Top 3 alternatives
            else:
                best_language = self.config.fallback_language
                confidence = 0.1
                alternatives = []
            
            detection_time = asyncio.get_event_loop().time() - start_time
            
            # Update metrics
            self.metrics['detections_performed'] += 1
            total_detections = self.metrics['detections_performed']
            current_avg = self.metrics['average_detection_time']
            self.metrics['average_detection_time'] = (
                (current_avg * (total_detections - 1) + detection_time) / total_detections
            )
            
            result = LanguageDetectionResult(
                detected_language=best_language,
                confidence=confidence,
                alternative_languages=alternatives,
                text_sample=text[:100] + "..." if len(text) > 100 else text
            )
            
            logger.info(f"🔍 Detected language: {best_language.name} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Language detection failed: {e}")
            return LanguageDetectionResult(
                detected_language=self.config.fallback_language,
                confidence=0.0,
                text_sample=text[:100] + "..." if len(text) > 100 else text
            )
    
    async def switch_language(self, language: SupportedLanguage) -> bool:
        """
        Switch to a different language.
        
        Args:
            language: Target language
            
        Returns:
            True if switch successful, False otherwise
        """
        try:
            old_language = self.current_language
            self.current_language = language
            self.metrics['language_switches'] += 1
            
            logger.info(f"🔄 Language switched: {old_language.name} → {language.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Language switch failed: {e}")
            return False
    
    def get_cultural_context(self, language: Optional[SupportedLanguage] = None) -> CulturalContext:
        """
        Get cultural context for a language.
        
        Args:
            language: Target language (current if None)
            
        Returns:
            CulturalContext for the language
        """
        target_language = language or self.current_language
        return self.cultural_contexts.get(target_language, self.cultural_contexts[SupportedLanguage.ENGLISH])
    
    def localize_string(self, key: str, language: Optional[SupportedLanguage] = None) -> str:
        """
        Get localized string for a key.
        
        Args:
            key: Localization key
            language: Target language (current if None)
            
        Returns:
            Localized string
        """
        target_language = language or self.current_language
        
        # Try target language first
        if target_language in self.localization_data:
            if key in self.localization_data[target_language]:
                return self.localization_data[target_language][key]
        
        # Fallback to English
        if SupportedLanguage.ENGLISH in self.localization_data:
            if key in self.localization_data[SupportedLanguage.ENGLISH]:
                return self.localization_data[SupportedLanguage.ENGLISH][key]
        
        # Return key if not found
        return key
    
    def format_text_culturally(self, text: str, language: Optional[SupportedLanguage] = None) -> str:
        """
        Format text according to cultural conventions.
        
        Args:
            text: Text to format
            language: Target language (current if None)
            
        Returns:
            Culturally formatted text
        """
        target_language = language or self.current_language
        context = self.get_cultural_context(target_language)
        
        # Apply cultural formatting
        formatted_text = text
        
        # Add cultural adaptations based on language
        if self.config.cultural_adaptation:
            self.metrics['cultural_adaptations'] += 1
            
            # Example adaptations (extend as needed)
            if target_language == SupportedLanguage.JAPANESE:
                # Add respectful language markers
                formatted_text = formatted_text.replace("you", "あなた")
            elif target_language == SupportedLanguage.GERMAN:
                # Formal addressing
                if self.config.formal_tone:
                    formatted_text = formatted_text.replace("you", "Sie")
        
        return formatted_text
    
    def get_supported_languages(self) -> List[SupportedLanguage]:
        """Get list of all supported languages"""
        return list(SupportedLanguage)
    
    def get_language_info(self, language: SupportedLanguage) -> Dict[str, Any]:
        """
        Get comprehensive information about a language.
        
        Args:
            language: Target language
            
        Returns:
            Dictionary with language information
        """
        context = self.get_cultural_context(language)
        
        return {
            'code': language.code,
            'name': language.name,
            'flag': language.flag,
            'cultural_context': {
                'formal_greetings': context.formal_greetings,
                'informal_greetings': context.informal_greetings,
                'polite_expressions': context.polite_expressions,
                'cultural_notes': context.cultural_notes,
                'date_format': context.date_format,
                'time_format': context.time_format,
                'number_format': context.number_format
            },
            'has_localization': language in self.localization_data,
            'has_patterns': language in self.language_patterns
        }
    
    def get_manager_metrics(self) -> Dict[str, Any]:
        """Get language manager performance metrics"""
        return {
            **self.metrics,
            'current_language': {
                'code': self.current_language.code,
                'name': self.current_language.name,
                'flag': self.current_language.flag
            },
            'supported_languages_count': len(SupportedLanguage),
            'cultural_contexts_loaded': len(self.cultural_contexts),
            'localization_languages': len(self.localization_data)
        }
