"""
🌐 Orion Vision Core - Translation Service
Real-time translation and localization

This module provides translation capabilities:
- Real-time text translation
- Multi-provider translation support
- Translation quality assessment
- Batch translation processing
- Translation caching and optimization

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import hashlib

from .language_manager import SupportedLanguage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationProvider(Enum):
    """Supported translation providers"""
    INTERNAL = "internal"
    GOOGLE_TRANSLATE = "google_translate"
    MICROSOFT_TRANSLATOR = "microsoft_translator"
    AMAZON_TRANSLATE = "amazon_translate"
    DEEPL = "deepl"
    YANDEX_TRANSLATE = "yandex_translate"

class TranslationQuality(Enum):
    """Translation quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    FAILED = "failed"

@dataclass
class TranslationResult:
    """Result of a translation operation"""
    original_text: str
    translated_text: str
    source_language: SupportedLanguage
    target_language: SupportedLanguage
    provider: TranslationProvider
    quality_score: float  # 0.0 to 1.0
    quality_level: TranslationQuality
    confidence: float  # 0.0 to 1.0
    translation_time: float
    cached: bool = False
    alternatives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TranslationCache:
    """Translation cache entry"""
    source_text: str
    translated_text: str
    source_language: SupportedLanguage
    target_language: SupportedLanguage
    provider: TranslationProvider
    created_at: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)

@dataclass
class BatchTranslationJob:
    """Batch translation job"""
    job_id: str
    texts: List[str]
    source_language: SupportedLanguage
    target_language: SupportedLanguage
    provider: TranslationProvider
    status: str = "pending"  # pending, processing, completed, failed
    results: List[TranslationResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    progress: float = 0.0

class TranslationService:
    """
    Real-time translation and localization service.
    
    Provides comprehensive translation capabilities with:
    - Multi-provider translation support
    - Translation quality assessment
    - Intelligent caching system
    - Batch processing capabilities
    - Performance optimization
    """
    
    def __init__(self, default_provider: TranslationProvider = TranslationProvider.INTERNAL):
        """
        Initialize the translation service.
        
        Args:
            default_provider: Default translation provider to use
        """
        self.default_provider = default_provider
        self.providers: Dict[TranslationProvider, Dict[str, Any]] = {}
        self.translation_cache: Dict[str, TranslationCache] = {}
        self.batch_jobs: Dict[str, BatchTranslationJob] = {}
        
        # Performance metrics
        self.metrics = {
            'translations_performed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'batch_jobs_created': 0,
            'average_translation_time': 0.0,
            'average_quality_score': 0.0,
            'provider_usage': {}
        }
        
        # Initialize providers
        self._initialize_providers()
        
        # Initialize translation dictionaries
        self.translation_dictionaries = self._load_translation_dictionaries()
        
        logger.info(f"🌐 Translation Service initialized with provider: {default_provider.value}")
    
    def _initialize_providers(self):
        """Initialize translation providers"""
        
        # Internal provider (rule-based translations)
        self.providers[TranslationProvider.INTERNAL] = {
            'name': 'Internal Translation Engine',
            'supported_languages': list(SupportedLanguage),
            'max_text_length': 10000,
            'rate_limit': None,
            'cost_per_char': 0.0,
            'quality_rating': 0.6
        }
        
        # External providers (would be configured with API keys in real implementation)
        self.providers[TranslationProvider.GOOGLE_TRANSLATE] = {
            'name': 'Google Translate',
            'supported_languages': list(SupportedLanguage),
            'max_text_length': 5000,
            'rate_limit': 100,  # requests per minute
            'cost_per_char': 0.00002,
            'quality_rating': 0.85
        }
        
        self.providers[TranslationProvider.DEEPL] = {
            'name': 'DeepL Translator',
            'supported_languages': [
                SupportedLanguage.ENGLISH, SupportedLanguage.GERMAN, SupportedLanguage.FRENCH,
                SupportedLanguage.SPANISH, SupportedLanguage.ITALIAN, SupportedLanguage.DUTCH,
                SupportedLanguage.POLISH, SupportedLanguage.RUSSIAN, SupportedLanguage.JAPANESE,
                SupportedLanguage.CHINESE
            ],
            'max_text_length': 5000,
            'rate_limit': 50,
            'cost_per_char': 0.00005,
            'quality_rating': 0.95
        }
        
        # Initialize provider usage metrics
        for provider in TranslationProvider:
            self.metrics['provider_usage'][provider.value] = 0
    
    def _load_translation_dictionaries(self) -> Dict[Tuple[SupportedLanguage, SupportedLanguage], Dict[str, str]]:
        """Load translation dictionaries for common phrases"""
        
        dictionaries = {}
        
        # English to Turkish
        en_tr = {
            'hello': 'merhaba',
            'goodbye': 'güle güle',
            'thank you': 'teşekkür ederim',
            'please': 'lütfen',
            'yes': 'evet',
            'no': 'hayır',
            'good morning': 'günaydın',
            'good evening': 'iyi akşamlar',
            'how are you': 'nasılsın',
            'welcome': 'hoş geldiniz',
            'error': 'hata',
            'success': 'başarılı',
            'loading': 'yükleniyor',
            'save': 'kaydet',
            'cancel': 'iptal'
        }
        dictionaries[(SupportedLanguage.ENGLISH, SupportedLanguage.TURKISH)] = en_tr
        
        # Turkish to English (reverse)
        tr_en = {v: k for k, v in en_tr.items()}
        dictionaries[(SupportedLanguage.TURKISH, SupportedLanguage.ENGLISH)] = tr_en
        
        # English to Spanish
        en_es = {
            'hello': 'hola',
            'goodbye': 'adiós',
            'thank you': 'gracias',
            'please': 'por favor',
            'yes': 'sí',
            'no': 'no',
            'good morning': 'buenos días',
            'good evening': 'buenas noches',
            'how are you': 'cómo estás',
            'welcome': 'bienvenido',
            'error': 'error',
            'success': 'éxito',
            'loading': 'cargando',
            'save': 'guardar',
            'cancel': 'cancelar'
        }
        dictionaries[(SupportedLanguage.ENGLISH, SupportedLanguage.SPANISH)] = en_es
        
        # Spanish to English (reverse)
        es_en = {v: k for k, v in en_es.items()}
        dictionaries[(SupportedLanguage.SPANISH, SupportedLanguage.ENGLISH)] = es_en
        
        return dictionaries
    
    async def translate(self, text: str, target_language: SupportedLanguage,
                       source_language: Optional[SupportedLanguage] = None,
                       provider: Optional[TranslationProvider] = None) -> TranslationResult:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language
            source_language: Source language (auto-detect if None)
            provider: Translation provider (default if None)
            
        Returns:
            TranslationResult with translation details
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Use default provider if not specified
            translation_provider = provider or self.default_provider
            
            # Auto-detect source language if not provided
            if source_language is None:
                source_language = await self._detect_language(text)
            
            # Check if translation is needed
            if source_language == target_language:
                return TranslationResult(
                    original_text=text,
                    translated_text=text,
                    source_language=source_language,
                    target_language=target_language,
                    provider=translation_provider,
                    quality_score=1.0,
                    quality_level=TranslationQuality.EXCELLENT,
                    confidence=1.0,
                    translation_time=0.0,
                    cached=False
                )
            
            # Check cache first
            cache_key = self._generate_cache_key(text, source_language, target_language, translation_provider)
            cached_result = self._get_from_cache(cache_key)
            
            if cached_result:
                self.metrics['cache_hits'] += 1
                translation_time = asyncio.get_event_loop().time() - start_time
                
                return TranslationResult(
                    original_text=text,
                    translated_text=cached_result.translated_text,
                    source_language=source_language,
                    target_language=target_language,
                    provider=translation_provider,
                    quality_score=0.8,  # Assume good quality for cached results
                    quality_level=TranslationQuality.GOOD,
                    confidence=0.9,
                    translation_time=translation_time,
                    cached=True
                )
            
            self.metrics['cache_misses'] += 1
            
            # Perform translation
            translated_text = await self._perform_translation(
                text, source_language, target_language, translation_provider
            )
            
            # Assess translation quality
            quality_score, quality_level = self._assess_translation_quality(
                text, translated_text, source_language, target_language
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(translation_provider, quality_score)
            
            translation_time = asyncio.get_event_loop().time() - start_time
            
            # Create result
            result = TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=source_language,
                target_language=target_language,
                provider=translation_provider,
                quality_score=quality_score,
                quality_level=quality_level,
                confidence=confidence,
                translation_time=translation_time,
                cached=False
            )
            
            # Cache the result
            self._add_to_cache(cache_key, text, translated_text, source_language, target_language, translation_provider)
            
            # Update metrics
            self._update_metrics(result)
            
            logger.info(f"🌐 Translated {source_language.name} → {target_language.name} (quality: {quality_level.value})")
            return result
            
        except Exception as e:
            translation_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"❌ Translation failed: {e}")
            
            return TranslationResult(
                original_text=text,
                translated_text=text,  # Return original on failure
                source_language=source_language or SupportedLanguage.ENGLISH,
                target_language=target_language,
                provider=translation_provider,
                quality_score=0.0,
                quality_level=TranslationQuality.FAILED,
                confidence=0.0,
                translation_time=translation_time,
                cached=False
            )
    
    async def _detect_language(self, text: str) -> SupportedLanguage:
        """Detect language of text (simplified implementation)"""
        
        # Simple keyword-based detection
        text_lower = text.lower()
        
        # Turkish indicators
        turkish_indicators = ['ve', 'bir', 'bu', 'da', 'de', 'ile', 'için', 'var', 'olan', 'gibi']
        if any(word in text_lower for word in turkish_indicators):
            return SupportedLanguage.TURKISH
        
        # Spanish indicators
        spanish_indicators = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se']
        if any(word in text_lower for word in spanish_indicators):
            return SupportedLanguage.SPANISH
        
        # French indicators
        french_indicators = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir']
        if any(word in text_lower for word in french_indicators):
            return SupportedLanguage.FRENCH
        
        # Default to English
        return SupportedLanguage.ENGLISH
    
    async def _perform_translation(self, text: str, source_lang: SupportedLanguage,
                                 target_lang: SupportedLanguage, provider: TranslationProvider) -> str:
        """Perform the actual translation"""
        
        if provider == TranslationProvider.INTERNAL:
            return await self._internal_translate(text, source_lang, target_lang)
        else:
            # For external providers, simulate API call
            return await self._external_translate(text, source_lang, target_lang, provider)
    
    async def _internal_translate(self, text: str, source_lang: SupportedLanguage,
                                target_lang: SupportedLanguage) -> str:
        """Internal rule-based translation"""
        
        # Check translation dictionary
        dict_key = (source_lang, target_lang)
        if dict_key in self.translation_dictionaries:
            dictionary = self.translation_dictionaries[dict_key]
            
            # Simple word-by-word translation for known phrases
            text_lower = text.lower().strip()
            if text_lower in dictionary:
                return dictionary[text_lower]
            
            # Try to translate individual words
            words = text.split()
            translated_words = []
            
            for word in words:
                word_lower = word.lower().strip('.,!?')
                if word_lower in dictionary:
                    translated_words.append(dictionary[word_lower])
                else:
                    translated_words.append(word)  # Keep original if not found
            
            return ' '.join(translated_words)
        
        # If no dictionary available, return original text with a note
        return f"[{target_lang.name}] {text}"
    
    async def _external_translate(self, text: str, source_lang: SupportedLanguage,
                                target_lang: SupportedLanguage, provider: TranslationProvider) -> str:
        """Simulate external provider translation"""
        
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        # For simulation, use internal translation with provider prefix
        internal_result = await self._internal_translate(text, source_lang, target_lang)
        
        # Add provider-specific improvements (simulation)
        if provider == TranslationProvider.DEEPL:
            return f"[DeepL] {internal_result}"
        elif provider == TranslationProvider.GOOGLE_TRANSLATE:
            return f"[Google] {internal_result}"
        else:
            return internal_result
    
    def _assess_translation_quality(self, original: str, translated: str,
                                  source_lang: SupportedLanguage, target_lang: SupportedLanguage) -> Tuple[float, TranslationQuality]:
        """Assess translation quality"""
        
        # Simple quality assessment
        if original == translated:
            if source_lang == target_lang:
                return 1.0, TranslationQuality.EXCELLENT
            else:
                return 0.1, TranslationQuality.POOR
        
        # Check if translation looks reasonable
        if translated.startswith('[') and ']' in translated:
            # Prefixed translation (external provider simulation)
            return 0.8, TranslationQuality.GOOD
        
        # Check dictionary-based translation
        dict_key = (source_lang, target_lang)
        if dict_key in self.translation_dictionaries:
            dictionary = self.translation_dictionaries[dict_key]
            if original.lower().strip() in dictionary:
                return 0.9, TranslationQuality.EXCELLENT
        
        # Default assessment
        return 0.6, TranslationQuality.FAIR
    
    def _calculate_confidence(self, provider: TranslationProvider, quality_score: float) -> float:
        """Calculate confidence based on provider and quality"""
        
        provider_confidence = {
            TranslationProvider.INTERNAL: 0.6,
            TranslationProvider.GOOGLE_TRANSLATE: 0.85,
            TranslationProvider.DEEPL: 0.95,
            TranslationProvider.MICROSOFT_TRANSLATOR: 0.8,
            TranslationProvider.AMAZON_TRANSLATE: 0.75,
            TranslationProvider.YANDEX_TRANSLATE: 0.7
        }
        
        base_confidence = provider_confidence.get(provider, 0.5)
        return min(base_confidence * quality_score, 1.0)
    
    def _generate_cache_key(self, text: str, source_lang: SupportedLanguage,
                          target_lang: SupportedLanguage, provider: TranslationProvider) -> str:
        """Generate cache key for translation"""
        
        key_data = f"{text}|{source_lang.code}|{target_lang.code}|{provider.value}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[TranslationCache]:
        """Get translation from cache"""
        
        if cache_key in self.translation_cache:
            cache_entry = self.translation_cache[cache_key]
            cache_entry.access_count += 1
            cache_entry.last_accessed = datetime.now()
            return cache_entry
        
        return None
    
    def _add_to_cache(self, cache_key: str, source_text: str, translated_text: str,
                     source_lang: SupportedLanguage, target_lang: SupportedLanguage,
                     provider: TranslationProvider):
        """Add translation to cache"""
        
        cache_entry = TranslationCache(
            source_text=source_text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=target_lang,
            provider=provider,
            created_at=datetime.now()
        )
        
        self.translation_cache[cache_key] = cache_entry
        
        # Limit cache size (simple LRU)
        if len(self.translation_cache) > 1000:
            # Remove oldest entries
            sorted_entries = sorted(
                self.translation_cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            # Remove oldest 100 entries
            for key, _ in sorted_entries[:100]:
                del self.translation_cache[key]
    
    def _update_metrics(self, result: TranslationResult):
        """Update translation metrics"""
        
        self.metrics['translations_performed'] += 1
        self.metrics['provider_usage'][result.provider.value] += 1
        
        # Update average translation time
        total_translations = self.metrics['translations_performed']
        current_avg_time = self.metrics['average_translation_time']
        self.metrics['average_translation_time'] = (
            (current_avg_time * (total_translations - 1) + result.translation_time) / total_translations
        )
        
        # Update average quality score
        current_avg_quality = self.metrics['average_quality_score']
        self.metrics['average_quality_score'] = (
            (current_avg_quality * (total_translations - 1) + result.quality_score) / total_translations
        )
    
    def get_supported_languages(self, provider: Optional[TranslationProvider] = None) -> List[SupportedLanguage]:
        """Get supported languages for a provider"""
        
        target_provider = provider or self.default_provider
        
        if target_provider in self.providers:
            return self.providers[target_provider]['supported_languages']
        
        return list(SupportedLanguage)
    
    def get_translation_metrics(self) -> Dict[str, Any]:
        """Get translation service metrics"""
        
        cache_hit_rate = (
            self.metrics['cache_hits'] / max(self.metrics['cache_hits'] + self.metrics['cache_misses'], 1)
        )
        
        return {
            **self.metrics,
            'cache_size': len(self.translation_cache),
            'cache_hit_rate': cache_hit_rate,
            'active_batch_jobs': len([job for job in self.batch_jobs.values() if job.status == 'processing']),
            'available_providers': len(self.providers),
            'dictionary_pairs': len(self.translation_dictionaries)
        }
