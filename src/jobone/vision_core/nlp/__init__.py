#!/usr/bin/env python3
"""
🗣️ Orion Vision Core - Enhanced NLP Module
Sprint 9.1 - Enhanced AI Capabilities and Cloud Integration
Multi-language support and personality customization

This module provides comprehensive NLP capabilities:
- Multi-language processing and translation
- AI personality customization and adaptation
- Advanced text analysis and understanding
- Real-time language detection and switching
- Cultural context awareness and localization
- Sentiment analysis and emotion recognition

Author: Orion Development Team
Version: 9.1.0
Date: 31 Mayıs 2025
"""

# Import NLP components
from .natural_language_processor import (
    NaturalLanguageProcessor, get_natural_language_processor, IntentType, EntityType,
    LanguageModel, Entity, Intent, NLPResult
)

# Import Enhanced NLP components (Sprint 9.1)
try:
    from .language_manager import LanguageManager, LanguageConfig, SupportedLanguage
    from .personality_engine import PersonalityEngine, PersonalityProfile, PersonalityTrait
    from .translation_service import TranslationService, TranslationResult, TranslationProvider
    from .text_analyzer import TextAnalyzer, AnalysisResult, TextMetrics
    from .sentiment_analyzer import SentimentAnalyzer, SentimentResult, EmotionType
except ImportError:
    # Fallback for development - will be created
    LanguageManager = None
    PersonalityEngine = None
    TranslationService = None
    TextAnalyzer = None
    SentimentAnalyzer = None
    LanguageConfig = None
    SupportedLanguage = None
    PersonalityProfile = None
    PersonalityTrait = None
    TranslationResult = None
    TranslationProvider = None
    AnalysisResult = None
    TextMetrics = None
    SentimentResult = None
    EmotionType = None

# Version information
__version__ = "9.1.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'NaturalLanguageProcessor',
    'Entity',
    'Intent',
    'NLPResult',

    # Enums
    'IntentType',
    'EntityType',
    'LanguageModel',

    # Functions
    'get_natural_language_processor',

    # Utilities
    'initialize_nlp_system',
    'get_nlp_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_nlp_system() -> bool:
    """
    Initialize the complete NLP system.

    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize Natural Language Processor
        nlp_processor = get_natural_language_processor()

        logger.info("🧠 NLP system initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Error initializing NLP system: {e}")
        return False

def get_nlp_info() -> dict:
    """
    Get NLP module information.

    Returns:
        Dictionary containing NLP module information
    """
    return {
        'module': 'orion_vision_core.nlp',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'NaturalLanguageProcessor': 'Advanced NLP and intent recognition system'
        },
        'features': [
            'Intent recognition and classification',
            'Entity extraction and normalization',
            'Sentiment analysis',
            'Language detection',
            'Conversational context management',
            'Multi-language support',
            'Pattern-based recognition',
            'Machine learning integration',
            'Brain AI integration',
            'LLM integration'
        ],
        'intent_types': [
            'Task execution',
            'Workflow creation',
            'System query',
            'File operation',
            'Automation setup',
            'Information request',
            'Conversation',
            'Command execution',
            'Help request'
        ],
        'entity_types': [
            'Task name',
            'File path',
            'Command',
            'Parameter',
            'Time',
            'Number',
            'Person',
            'Location',
            'System component'
        ],
        'language_models': [
            'Simple rules',
            'Pattern matching',
            'Machine learning',
            'Transformer',
            'Hybrid'
        ],
        'supported_languages': [
            'English (en)',
            'Turkish (tr)'
        ],
        'nlp_capabilities': [
            'Text normalization',
            'Intent classification',
            'Entity extraction',
            'Sentiment analysis',
            'Language detection',
            'Context management',
            'Conversation tracking',
            'Pattern learning'
        ]
    }

# Module initialization
logger.info(f"📦 Orion Vision Core NLP Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
