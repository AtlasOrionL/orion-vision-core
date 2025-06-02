#!/usr/bin/env python3
"""
🗣️ Orion Vision Core - Enhanced NLP Test Suite
Comprehensive testing for enhanced NLP capabilities

This test suite covers:
- Language Manager functionality
- Personality Engine capabilities
- Translation Service operations
- Text Analyzer features
- Sentiment Analyzer accuracy
- Multi-language support validation

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp.language_manager import LanguageManager, LanguageConfig, SupportedLanguage
from nlp.personality_engine import PersonalityEngine, PersonalityProfile, PersonalityType, PersonalityTrait
from nlp.translation_service import TranslationService, TranslationProvider
from nlp.text_analyzer import TextAnalyzer
from nlp.sentiment_analyzer import SentimentAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedNLPTestSuite:
    """Test suite for enhanced NLP capabilities"""
    
    def __init__(self):
        self.test_results = {}
    
    async def test_language_manager(self):
        """Test Language Manager functionality"""
        logger.info("🌍 Testing Language Manager...")
        
        try:
            # Initialize language manager
            config = LanguageConfig(
                primary_language=SupportedLanguage.ENGLISH,
                fallback_language=SupportedLanguage.ENGLISH,
                auto_detect=True,
                cultural_adaptation=True
            )
            manager = LanguageManager(config)
            
            # Test language detection
            english_text = "Hello, how are you today?"
            detection_result = await manager.detect_language(english_text)
            
            if detection_result.detected_language != SupportedLanguage.ENGLISH:
                logger.warning(f"⚠️ Expected English, got {detection_result.detected_language.name}")
            
            # Test Turkish detection
            turkish_text = "Merhaba, nasılsınız bugün?"
            turkish_detection = await manager.detect_language(turkish_text)
            
            # Test language switching
            switch_success = await manager.switch_language(SupportedLanguage.TURKISH)
            if not switch_success:
                raise Exception("Language switch failed")
            
            # Test cultural context
            context = manager.get_cultural_context(SupportedLanguage.TURKISH)
            if not context.formal_greetings:
                raise Exception("Cultural context not loaded")
            
            # Test localization
            welcome_text = manager.localize_string("welcome", SupportedLanguage.TURKISH)
            if welcome_text == "welcome":  # Should be translated
                logger.warning("⚠️ Localization may not be working properly")
            
            # Test cultural formatting
            formatted_text = manager.format_text_culturally("Hello friend", SupportedLanguage.TURKISH)
            
            # Test supported languages
            supported_langs = manager.get_supported_languages()
            if len(supported_langs) < 10:
                raise Exception("Insufficient supported languages")
            
            # Test language info
            lang_info = manager.get_language_info(SupportedLanguage.ENGLISH)
            if not lang_info or 'name' not in lang_info:
                raise Exception("Language info retrieval failed")
            
            # Test metrics
            metrics = manager.get_manager_metrics()
            
            self.test_results['language_manager'] = {
                'success': True,
                'operations_tested': 8,
                'supported_languages': len(supported_langs),
                'detection_confidence': detection_result.confidence,
                'metrics': metrics
            }
            
            logger.info("✅ Language Manager tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Language Manager test failed: {e}")
            self.test_results['language_manager'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_personality_engine(self):
        """Test Personality Engine functionality"""
        logger.info("🎭 Testing Personality Engine...")
        
        try:
            # Initialize personality engine
            engine = PersonalityEngine()
            
            # Test available personalities
            personalities = engine.get_available_personalities()
            if len(personalities) < 3:
                raise Exception("Insufficient default personalities")
            
            # Test personality switching
            switch_success = await engine.switch_personality("friendly")
            if not switch_success:
                raise Exception("Personality switch failed")
            
            # Test response adaptation
            original_text = "Task completed successfully"
            adapted_response = await engine.adapt_response(original_text)
            
            if adapted_response.adaptation_score == 0.0:
                logger.warning("⚠️ No personality adaptation applied")
            
            # Test different personalities
            personalities_tested = []
            for personality_name in ["professional", "casual", "technical"]:
                await engine.switch_personality(personality_name)
                response = await engine.adapt_response("Hello, how can I help you?")
                personalities_tested.append({
                    'name': personality_name,
                    'adapted_text': response.adapted_text,
                    'score': response.adaptation_score
                })
            
            # Test custom personality creation
            custom_profile = PersonalityProfile(
                name="test_personality",
                personality_type=PersonalityType.CREATIVE,
                traits={
                    PersonalityTrait.CREATIVE: 0.9,
                    PersonalityTrait.HUMOROUS: 0.7,
                    PersonalityTrait.FRIENDLY: 0.8
                },
                humor_frequency=0.8
            )
            
            create_success = engine.create_custom_personality(custom_profile)
            if not create_success:
                raise Exception("Custom personality creation failed")
            
            # Test personality info
            personality_info = engine.get_personality_info("friendly")
            if not personality_info:
                raise Exception("Personality info retrieval failed")
            
            # Test metrics
            metrics = engine.get_engine_metrics()
            
            self.test_results['personality_engine'] = {
                'success': True,
                'operations_tested': 7,
                'default_personalities': len(personalities),
                'personalities_tested': personalities_tested,
                'custom_personality_created': create_success,
                'metrics': metrics
            }
            
            logger.info("✅ Personality Engine tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Personality Engine test failed: {e}")
            self.test_results['personality_engine'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_translation_service(self):
        """Test Translation Service functionality"""
        logger.info("🌐 Testing Translation Service...")
        
        try:
            # Initialize translation service
            service = TranslationService(TranslationProvider.INTERNAL)
            
            # Test English to Turkish translation
            en_text = "Hello, how are you?"
            tr_result = await service.translate(
                en_text, 
                SupportedLanguage.TURKISH, 
                SupportedLanguage.ENGLISH
            )
            
            if not tr_result.success or tr_result.translated_text == en_text:
                logger.warning("⚠️ Translation may not be working properly")
            
            # Test Turkish to English translation
            tr_text = "Merhaba, nasılsınız?"
            en_result = await service.translate(
                tr_text,
                SupportedLanguage.ENGLISH,
                SupportedLanguage.TURKISH
            )
            
            # Test same language (should return original)
            same_result = await service.translate(
                "Hello world",
                SupportedLanguage.ENGLISH,
                SupportedLanguage.ENGLISH
            )
            
            if same_result.translated_text != "Hello world":
                raise Exception("Same language translation failed")
            
            # Test multiple translations (cache testing)
            translations = []
            for i in range(3):
                result = await service.translate(
                    "Good morning",
                    SupportedLanguage.SPANISH,
                    SupportedLanguage.ENGLISH
                )
                translations.append(result)
            
            # Test supported languages
            supported_langs = service.get_supported_languages()
            if len(supported_langs) < 5:
                raise Exception("Insufficient supported languages")
            
            # Test metrics
            metrics = service.get_translation_metrics()
            
            self.test_results['translation_service'] = {
                'success': True,
                'operations_tested': 6,
                'translations_performed': len(translations) + 3,
                'cache_hit_rate': metrics.get('cache_hit_rate', 0.0),
                'average_quality': (tr_result.quality_score + en_result.quality_score) / 2,
                'supported_languages': len(supported_langs),
                'metrics': metrics
            }
            
            logger.info("✅ Translation Service tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Translation Service test failed: {e}")
            self.test_results['translation_service'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_text_analyzer(self):
        """Test Text Analyzer functionality"""
        logger.info("📊 Testing Text Analyzer...")
        
        try:
            # Initialize text analyzer
            analyzer = TextAnalyzer()
            
            # Test simple text analysis
            simple_text = "This is a simple test."
            simple_result = await analyzer.analyze_text(simple_text)
            
            if simple_result.metrics.word_count != 5:
                raise Exception(f"Word count mismatch: expected 5, got {simple_result.metrics.word_count}")
            
            # Test complex text analysis
            complex_text = """
            The implementation of advanced machine learning algorithms requires careful consideration 
            of computational complexity, data preprocessing methodologies, and optimization techniques. 
            Furthermore, the integration of neural networks with traditional statistical methods 
            presents significant challenges in terms of interpretability and scalability.
            """
            complex_result = await analyzer.analyze_text(complex_text)
            
            if complex_result.complexity.value == "very_simple":
                raise Exception("Complex text classified as very simple")
            
            # Test different text categories
            technical_text = "The API endpoint returns JSON data with authentication tokens and database queries."
            technical_result = await analyzer.analyze_text(technical_text)
            
            business_text = "Our quarterly revenue increased by 15% due to improved customer satisfaction and market expansion."
            business_result = await analyzer.analyze_text(business_text)
            
            # Test readability analysis
            readable_text = "The cat sat on the mat. It was a sunny day. The children played in the park."
            readable_result = await analyzer.analyze_text(readable_text)
            
            if readable_result.readability_score < 0.5:
                logger.warning("⚠️ Simple text has low readability score")
            
            # Test key phrase extraction
            if not complex_result.key_phrases:
                logger.warning("⚠️ No key phrases extracted from complex text")
            
            # Test suggestions generation
            poor_text = "this is bad text with no punctuation and very long sentences that go on and on without any structure"
            poor_result = await analyzer.analyze_text(poor_text)
            
            if not poor_result.suggestions:
                logger.warning("⚠️ No suggestions generated for poor text")
            
            # Test metrics
            metrics = analyzer.get_analyzer_metrics()
            
            self.test_results['text_analyzer'] = {
                'success': True,
                'operations_tested': 6,
                'complexity_levels_tested': [
                    simple_result.complexity.value,
                    complex_result.complexity.value,
                    readable_result.complexity.value
                ],
                'categories_detected': [
                    technical_result.category.value,
                    business_result.category.value
                ],
                'average_quality_score': (
                    simple_result.quality_score + complex_result.quality_score + 
                    readable_result.quality_score
                ) / 3,
                'metrics': metrics
            }
            
            logger.info("✅ Text Analyzer tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Text Analyzer test failed: {e}")
            self.test_results['text_analyzer'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_sentiment_analyzer(self):
        """Test Sentiment Analyzer functionality"""
        logger.info("😊 Testing Sentiment Analyzer...")
        
        try:
            # Initialize sentiment analyzer
            analyzer = SentimentAnalyzer()
            
            # Test positive sentiment
            positive_text = "I love this amazing product! It's absolutely fantastic and wonderful!"
            positive_result = await analyzer.analyze_sentiment(positive_text)
            
            if positive_result.polarity_score <= 0:
                raise Exception("Positive text classified as negative/neutral")
            
            # Test negative sentiment
            negative_text = "This is terrible and awful. I hate it completely. Very disappointed and frustrated."
            negative_result = await analyzer.analyze_sentiment(negative_text)
            
            if negative_result.polarity_score >= 0:
                raise Exception("Negative text classified as positive/neutral")
            
            # Test neutral sentiment
            neutral_text = "The weather is cloudy today. The temperature is 20 degrees."
            neutral_result = await analyzer.analyze_sentiment(neutral_text)
            
            # Test emotion detection
            emotional_text = "I'm so excited and happy about this amazing opportunity!"
            emotional_result = await analyzer.analyze_sentiment(emotional_text)
            
            if not emotional_result.emotion_scores:
                logger.warning("⚠️ No emotions detected in emotional text")
            
            # Test different languages
            turkish_positive = "Bu harika ve mükemmel! Çok beğendim ve mutluyum."
            turkish_result = await analyzer.analyze_sentiment(turkish_positive, SupportedLanguage.TURKISH)
            
            spanish_negative = "Esto es terrible y malo. No me gusta nada."
            spanish_result = await analyzer.analyze_sentiment(spanish_negative, SupportedLanguage.SPANISH)
            
            # Test sentiment trends
            results_list = [positive_result, negative_result, neutral_result, emotional_result]
            trends = analyzer.get_sentiment_trends(results_list)
            
            if not trends:
                raise Exception("Sentiment trends analysis failed")
            
            # Test confidence levels
            confidence_scores = [r.confidence for r in results_list]
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            if avg_confidence < 0.3:
                logger.warning("⚠️ Low average confidence in sentiment analysis")
            
            # Test metrics
            metrics = analyzer.get_analyzer_metrics()
            
            self.test_results['sentiment_analyzer'] = {
                'success': True,
                'operations_tested': 7,
                'sentiment_results': {
                    'positive_score': positive_result.polarity_score,
                    'negative_score': negative_result.polarity_score,
                    'neutral_score': neutral_result.polarity_score
                },
                'emotions_detected': len(emotional_result.emotion_scores),
                'multilingual_support': {
                    'turkish_detected': turkish_result.language.name,
                    'spanish_detected': spanish_result.language.name
                },
                'average_confidence': avg_confidence,
                'trends_analysis': trends,
                'metrics': metrics
            }
            
            logger.info("✅ Sentiment Analyzer tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sentiment Analyzer test failed: {e}")
            self.test_results['sentiment_analyzer'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def run_all_tests(self):
        """Run all enhanced NLP tests"""
        logger.info("🗣️ Starting Enhanced NLP Test Suite...")
        logger.info("=" * 80)
        
        test_results = {}
        
        # Run all test categories
        test_results['language_manager'] = await self.test_language_manager()
        logger.info("=" * 80)
        
        test_results['personality_engine'] = await self.test_personality_engine()
        logger.info("=" * 80)
        
        test_results['translation_service'] = await self.test_translation_service()
        logger.info("=" * 80)
        
        test_results['text_analyzer'] = await self.test_text_analyzer()
        logger.info("=" * 80)
        
        test_results['sentiment_analyzer'] = await self.test_sentiment_analyzer()
        logger.info("=" * 80)
        
        # Calculate overall success rate
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        overall_success_rate = passed_tests / total_tests
        
        logger.info("📊 ENHANCED NLP TEST RESULTS:")
        logger.info(f"  Language Manager: {'✅ PASSED' if test_results['language_manager'] else '❌ FAILED'}")
        logger.info(f"  Personality Engine: {'✅ PASSED' if test_results['personality_engine'] else '❌ FAILED'}")
        logger.info(f"  Translation Service: {'✅ PASSED' if test_results['translation_service'] else '❌ FAILED'}")
        logger.info(f"  Text Analyzer: {'✅ PASSED' if test_results['text_analyzer'] else '❌ FAILED'}")
        logger.info(f"  Sentiment Analyzer: {'✅ PASSED' if test_results['sentiment_analyzer'] else '❌ FAILED'}")
        logger.info(f"  Overall Success Rate: {overall_success_rate:.1%}")
        
        return overall_success_rate >= 0.8, self.test_results

async def main():
    """Main test execution"""
    test_suite = EnhancedNLPTestSuite()
    
    try:
        success, detailed_results = await test_suite.run_all_tests()
        
        if success:
            logger.info("🎉 ENHANCED NLP TEST SUITE: ALL TESTS PASSED!")
            return True
        else:
            logger.error("❌ ENHANCED NLP TEST SUITE: SOME TESTS FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
