"""
😊 Orion Vision Core - Sentiment Analyzer
Sentiment analysis and emotion recognition

This module provides sentiment analysis capabilities:
- Sentiment polarity detection (positive, negative, neutral)
- Emotion recognition and classification
- Intensity scoring and confidence assessment
- Multi-language sentiment analysis
- Context-aware sentiment evaluation

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re

from .language_manager import SupportedLanguage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentPolarity(Enum):
    """Sentiment polarity classifications"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    SLIGHTLY_POSITIVE = "slightly_positive"
    NEUTRAL = "neutral"
    SLIGHTLY_NEGATIVE = "slightly_negative"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class EmotionType(Enum):
    """Primary emotion types"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    LOVE = "love"
    EXCITEMENT = "excitement"
    FRUSTRATION = "frustration"
    CONFUSION = "confusion"

@dataclass
class EmotionScore:
    """Individual emotion score"""
    emotion: EmotionType
    intensity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0

@dataclass
class SentimentResult:
    """Complete sentiment analysis result"""
    original_text: str
    language: SupportedLanguage
    polarity: SentimentPolarity
    polarity_score: float  # -1.0 to 1.0 (negative to positive)
    intensity: float  # 0.0 to 1.0 (weak to strong)
    confidence: float  # 0.0 to 1.0
    primary_emotion: Optional[EmotionType] = None
    emotion_scores: List[EmotionScore] = field(default_factory=list)
    key_sentiment_words: List[str] = field(default_factory=list)
    context_factors: List[str] = field(default_factory=list)
    analysis_time: float = 0.0

class SentimentAnalyzer:
    """
    Sentiment analysis and emotion recognition system.
    
    Provides comprehensive sentiment analysis with:
    - Multi-language sentiment detection
    - Emotion classification and scoring
    - Context-aware analysis
    - Intensity and confidence assessment
    - Sentiment trend tracking
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        
        # Sentiment lexicons for different languages
        self.sentiment_lexicons = self._initialize_sentiment_lexicons()
        
        # Emotion keywords
        self.emotion_keywords = self._initialize_emotion_keywords()
        
        # Intensity modifiers
        self.intensity_modifiers = self._initialize_intensity_modifiers()
        
        # Negation words
        self.negation_words = self._initialize_negation_words()
        
        # Performance metrics
        self.metrics = {
            'analyses_performed': 0,
            'average_analysis_time': 0.0,
            'average_confidence': 0.0,
            'polarity_distribution': {polarity.value: 0 for polarity in SentimentPolarity},
            'emotion_distribution': {emotion.value: 0 for emotion in EmotionType},
            'language_distribution': {}
        }
        
        logger.info("😊 Sentiment Analyzer initialized")
    
    def _initialize_sentiment_lexicons(self) -> Dict[SupportedLanguage, Dict[str, float]]:
        """Initialize sentiment lexicons for different languages"""
        
        lexicons = {}
        
        # English sentiment lexicon
        english_lexicon = {
            # Very positive words
            'excellent': 0.9, 'amazing': 0.9, 'outstanding': 0.9, 'fantastic': 0.9,
            'wonderful': 0.8, 'great': 0.8, 'awesome': 0.8, 'brilliant': 0.8,
            'perfect': 0.9, 'superb': 0.8, 'magnificent': 0.8, 'marvelous': 0.8,
            
            # Positive words
            'good': 0.6, 'nice': 0.5, 'happy': 0.7, 'pleased': 0.6, 'satisfied': 0.6,
            'love': 0.8, 'like': 0.5, 'enjoy': 0.6, 'appreciate': 0.6, 'glad': 0.6,
            'positive': 0.6, 'success': 0.7, 'win': 0.7, 'achieve': 0.6, 'improve': 0.5,
            
            # Negative words
            'bad': -0.6, 'terrible': -0.8, 'awful': -0.8, 'horrible': -0.8,
            'hate': -0.8, 'dislike': -0.5, 'sad': -0.6, 'angry': -0.7, 'upset': -0.6,
            'disappointed': -0.6, 'frustrated': -0.6, 'annoyed': -0.5, 'worried': -0.5,
            
            # Very negative words
            'disgusting': -0.9, 'outrageous': -0.8, 'devastating': -0.9, 'catastrophic': -0.9,
            'furious': -0.8, 'enraged': -0.8, 'livid': -0.8, 'despise': -0.9,
            'fail': -0.7, 'failure': -0.7, 'disaster': -0.8, 'crisis': -0.7
        }
        lexicons[SupportedLanguage.ENGLISH] = english_lexicon
        
        # Turkish sentiment lexicon
        turkish_lexicon = {
            # Positive words
            'mükemmel': 0.9, 'harika': 0.8, 'güzel': 0.6, 'iyi': 0.6, 'başarılı': 0.7,
            'mutlu': 0.7, 'sevmek': 0.7, 'beğenmek': 0.5, 'memnun': 0.6, 'keyifli': 0.6,
            'olumlu': 0.6, 'başarı': 0.7, 'kazanmak': 0.7, 'gelişmek': 0.5,
            
            # Negative words
            'kötü': -0.6, 'berbat': -0.8, 'korkunç': -0.8, 'nefret': -0.8,
            'üzgün': -0.6, 'kızgın': -0.7, 'sinirli': -0.6, 'hayal kırıklığı': -0.6,
            'endişeli': -0.5, 'başarısız': -0.7, 'felaket': -0.8, 'kriz': -0.7
        }
        lexicons[SupportedLanguage.TURKISH] = turkish_lexicon
        
        # Spanish sentiment lexicon
        spanish_lexicon = {
            # Positive words
            'excelente': 0.9, 'increíble': 0.8, 'bueno': 0.6, 'feliz': 0.7, 'amor': 0.8,
            'gustar': 0.5, 'contento': 0.6, 'positivo': 0.6, 'éxito': 0.7, 'ganar': 0.7,
            
            # Negative words
            'malo': -0.6, 'terrible': -0.8, 'odiar': -0.8, 'triste': -0.6, 'enojado': -0.7,
            'molesto': -0.6, 'preocupado': -0.5, 'fracaso': -0.7, 'desastre': -0.8
        }
        lexicons[SupportedLanguage.SPANISH] = spanish_lexicon
        
        return lexicons
    
    def _initialize_emotion_keywords(self) -> Dict[EmotionType, List[str]]:
        """Initialize emotion-specific keywords"""
        
        return {
            EmotionType.JOY: ['happy', 'joy', 'cheerful', 'delighted', 'elated', 'ecstatic', 'blissful'],
            EmotionType.SADNESS: ['sad', 'depressed', 'melancholy', 'sorrowful', 'grief', 'mourning'],
            EmotionType.ANGER: ['angry', 'furious', 'rage', 'mad', 'irritated', 'annoyed', 'livid'],
            EmotionType.FEAR: ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous'],
            EmotionType.SURPRISE: ['surprised', 'amazed', 'astonished', 'shocked', 'stunned'],
            EmotionType.DISGUST: ['disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated'],
            EmotionType.TRUST: ['trust', 'confident', 'secure', 'reliable', 'dependable'],
            EmotionType.ANTICIPATION: ['excited', 'eager', 'anticipating', 'looking forward'],
            EmotionType.LOVE: ['love', 'adore', 'cherish', 'treasure', 'devoted'],
            EmotionType.EXCITEMENT: ['excited', 'thrilled', 'exhilarated', 'energetic'],
            EmotionType.FRUSTRATION: ['frustrated', 'exasperated', 'irritated', 'aggravated'],
            EmotionType.CONFUSION: ['confused', 'puzzled', 'bewildered', 'perplexed']
        }
    
    def _initialize_intensity_modifiers(self) -> Dict[str, float]:
        """Initialize words that modify sentiment intensity"""
        
        return {
            # Amplifiers
            'very': 1.5, 'extremely': 2.0, 'incredibly': 1.8, 'absolutely': 1.7,
            'completely': 1.6, 'totally': 1.5, 'really': 1.3, 'quite': 1.2,
            'rather': 1.1, 'pretty': 1.1, 'so': 1.4, 'too': 1.3,
            
            # Diminishers
            'slightly': 0.7, 'somewhat': 0.8, 'a bit': 0.7, 'a little': 0.7,
            'kind of': 0.8, 'sort of': 0.8, 'barely': 0.5, 'hardly': 0.5
        }
    
    def _initialize_negation_words(self) -> List[str]:
        """Initialize negation words that flip sentiment"""
        
        return [
            'not', 'no', 'never', 'nothing', 'nobody', 'nowhere', 'neither',
            'nor', 'none', 'without', 'lack', 'lacking', 'absent', 'missing',
            "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "couldn't",
            "shouldn't", "mustn't", "needn't", "isn't", "aren't", "wasn't", "weren't"
        ]
    
    async def analyze_sentiment(self, text: str, language: Optional[SupportedLanguage] = None,
                              context: Optional[Dict[str, Any]] = None) -> SentimentResult:
        """
        Analyze sentiment and emotions in text.
        
        Args:
            text: Text to analyze
            language: Language of the text (auto-detect if None)
            context: Optional context information
            
        Returns:
            SentimentResult with comprehensive sentiment analysis
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Auto-detect language if not provided
            if language is None:
                language = await self._detect_language(text)
            
            # Calculate sentiment polarity
            polarity_score, key_words = await self._calculate_polarity(text, language)
            
            # Determine polarity classification
            polarity = self._classify_polarity(polarity_score)
            
            # Calculate intensity
            intensity = abs(polarity_score)
            
            # Analyze emotions
            emotion_scores = await self._analyze_emotions(text)
            primary_emotion = self._get_primary_emotion(emotion_scores)
            
            # Calculate confidence
            confidence = self._calculate_confidence(polarity_score, emotion_scores, len(key_words))
            
            # Identify context factors
            context_factors = self._identify_context_factors(text, context)
            
            analysis_time = asyncio.get_event_loop().time() - start_time
            
            # Create result
            result = SentimentResult(
                original_text=text,
                language=language,
                polarity=polarity,
                polarity_score=polarity_score,
                intensity=intensity,
                confidence=confidence,
                primary_emotion=primary_emotion,
                emotion_scores=emotion_scores,
                key_sentiment_words=key_words,
                context_factors=context_factors,
                analysis_time=analysis_time
            )
            
            # Update metrics
            self._update_metrics(result)
            
            logger.info(f"😊 Sentiment analyzed: {polarity.value} ({polarity_score:.2f}), emotion: {primary_emotion.value if primary_emotion else 'none'}")
            return result
            
        except Exception as e:
            analysis_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"❌ Sentiment analysis failed: {e}")
            
            # Return neutral result on failure
            return SentimentResult(
                original_text=text,
                language=language or SupportedLanguage.ENGLISH,
                polarity=SentimentPolarity.NEUTRAL,
                polarity_score=0.0,
                intensity=0.0,
                confidence=0.0,
                analysis_time=analysis_time
            )
    
    async def _detect_language(self, text: str) -> SupportedLanguage:
        """Simple language detection for sentiment analysis"""
        
        # Basic keyword-based detection
        text_lower = text.lower()
        
        # Check for Turkish words
        turkish_words = ['ve', 'bir', 'bu', 'çok', 'iyi', 'kötü', 'güzel']
        if any(word in text_lower for word in turkish_words):
            return SupportedLanguage.TURKISH
        
        # Check for Spanish words
        spanish_words = ['el', 'la', 'es', 'muy', 'bueno', 'malo', 'que']
        if any(word in text_lower for word in spanish_words):
            return SupportedLanguage.SPANISH
        
        # Default to English
        return SupportedLanguage.ENGLISH
    
    async def _calculate_polarity(self, text: str, language: SupportedLanguage) -> Tuple[float, List[str]]:
        """Calculate sentiment polarity score"""
        
        # Get sentiment lexicon for language
        lexicon = self.sentiment_lexicons.get(language, self.sentiment_lexicons[SupportedLanguage.ENGLISH])
        
        words = text.lower().split()
        sentiment_score = 0.0
        sentiment_words = []
        
        for i, word in enumerate(words):
            # Clean word
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            if clean_word in lexicon:
                word_score = lexicon[clean_word]
                
                # Check for negation in previous 3 words
                negated = False
                for j in range(max(0, i-3), i):
                    if words[j] in self.negation_words:
                        negated = True
                        break
                
                # Apply negation
                if negated:
                    word_score *= -0.8  # Flip and slightly reduce intensity
                
                # Check for intensity modifiers
                modifier = 1.0
                for j in range(max(0, i-2), i):
                    if words[j] in self.intensity_modifiers:
                        modifier = self.intensity_modifiers[words[j]]
                        break
                
                # Apply modifier
                final_score = word_score * modifier
                sentiment_score += final_score
                sentiment_words.append(clean_word)
        
        # Normalize score
        if sentiment_words:
            sentiment_score = sentiment_score / len(sentiment_words)
        
        # Clamp to [-1, 1] range
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        return sentiment_score, sentiment_words
    
    def _classify_polarity(self, score: float) -> SentimentPolarity:
        """Classify polarity based on score"""
        
        if score >= 0.7:
            return SentimentPolarity.VERY_POSITIVE
        elif score >= 0.3:
            return SentimentPolarity.POSITIVE
        elif score >= 0.1:
            return SentimentPolarity.SLIGHTLY_POSITIVE
        elif score <= -0.7:
            return SentimentPolarity.VERY_NEGATIVE
        elif score <= -0.3:
            return SentimentPolarity.NEGATIVE
        elif score <= -0.1:
            return SentimentPolarity.SLIGHTLY_NEGATIVE
        else:
            return SentimentPolarity.NEUTRAL
    
    async def _analyze_emotions(self, text: str) -> List[EmotionScore]:
        """Analyze emotions in text"""
        
        text_lower = text.lower()
        emotion_scores = []
        
        for emotion, keywords in self.emotion_keywords.items():
            # Count emotion keyword matches
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            
            if matches > 0:
                # Calculate intensity based on matches and text length
                intensity = min(matches / len(text.split()) * 10, 1.0)
                confidence = min(matches / len(keywords), 1.0)
                
                emotion_scores.append(EmotionScore(
                    emotion=emotion,
                    intensity=intensity,
                    confidence=confidence
                ))
        
        # Sort by intensity
        emotion_scores.sort(key=lambda x: x.intensity, reverse=True)
        
        return emotion_scores[:5]  # Return top 5 emotions
    
    def _get_primary_emotion(self, emotion_scores: List[EmotionScore]) -> Optional[EmotionType]:
        """Get the primary emotion from scores"""
        
        if emotion_scores and emotion_scores[0].intensity > 0.1:
            return emotion_scores[0].emotion
        
        return None
    
    def _calculate_confidence(self, polarity_score: float, emotion_scores: List[EmotionScore],
                            sentiment_word_count: int) -> float:
        """Calculate confidence in sentiment analysis"""
        
        confidence_factors = []
        
        # Polarity strength factor
        polarity_confidence = abs(polarity_score)
        confidence_factors.append(polarity_confidence)
        
        # Sentiment word count factor
        word_confidence = min(sentiment_word_count / 5.0, 1.0)
        confidence_factors.append(word_confidence)
        
        # Emotion detection factor
        if emotion_scores:
            emotion_confidence = emotion_scores[0].confidence
            confidence_factors.append(emotion_confidence)
        else:
            confidence_factors.append(0.3)  # Lower confidence without emotions
        
        # Average all factors
        return sum(confidence_factors) / len(confidence_factors)
    
    def _identify_context_factors(self, text: str, context: Optional[Dict[str, Any]]) -> List[str]:
        """Identify context factors that might affect sentiment"""
        
        factors = []
        
        # Text length factor
        word_count = len(text.split())
        if word_count < 5:
            factors.append("short_text")
        elif word_count > 100:
            factors.append("long_text")
        
        # Punctuation factors
        if '!' in text:
            factors.append("exclamation")
        if '?' in text:
            factors.append("question")
        if text.count('!') > 2:
            factors.append("high_excitement")
        
        # Capitalization factor
        if text.isupper():
            factors.append("all_caps")
        elif sum(1 for c in text if c.isupper()) / max(len(text), 1) > 0.3:
            factors.append("high_caps")
        
        # Context-specific factors
        if context:
            if context.get('formal', False):
                factors.append("formal_context")
            if context.get('urgent', False):
                factors.append("urgent_context")
            if context.get('customer_service', False):
                factors.append("customer_service")
        
        return factors
    
    def _update_metrics(self, result: SentimentResult):
        """Update analyzer metrics"""
        
        self.metrics['analyses_performed'] += 1
        
        # Update average analysis time
        total_analyses = self.metrics['analyses_performed']
        current_avg_time = self.metrics['average_analysis_time']
        self.metrics['average_analysis_time'] = (
            (current_avg_time * (total_analyses - 1) + result.analysis_time) / total_analyses
        )
        
        # Update average confidence
        current_avg_confidence = self.metrics['average_confidence']
        self.metrics['average_confidence'] = (
            (current_avg_confidence * (total_analyses - 1) + result.confidence) / total_analyses
        )
        
        # Update polarity distribution
        self.metrics['polarity_distribution'][result.polarity.value] += 1
        
        # Update emotion distribution
        if result.primary_emotion:
            self.metrics['emotion_distribution'][result.primary_emotion.value] += 1
        
        # Update language distribution
        lang_code = result.language.code
        if lang_code not in self.metrics['language_distribution']:
            self.metrics['language_distribution'][lang_code] = 0
        self.metrics['language_distribution'][lang_code] += 1
    
    def get_sentiment_trends(self, results: List[SentimentResult]) -> Dict[str, Any]:
        """Analyze sentiment trends from multiple results"""
        
        if not results:
            return {}
        
        # Calculate average polarity
        avg_polarity = sum(r.polarity_score for r in results) / len(results)
        
        # Calculate polarity distribution
        polarity_counts = {}
        for result in results:
            polarity = result.polarity.value
            polarity_counts[polarity] = polarity_counts.get(polarity, 0) + 1
        
        # Calculate emotion distribution
        emotion_counts = {}
        for result in results:
            if result.primary_emotion:
                emotion = result.primary_emotion.value
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Calculate trend direction
        if len(results) >= 2:
            recent_avg = sum(r.polarity_score for r in results[-5:]) / min(len(results), 5)
            earlier_avg = sum(r.polarity_score for r in results[:-5]) / max(len(results) - 5, 1)
            trend_direction = "improving" if recent_avg > earlier_avg else "declining"
        else:
            trend_direction = "stable"
        
        return {
            'average_polarity': avg_polarity,
            'polarity_distribution': polarity_counts,
            'emotion_distribution': emotion_counts,
            'trend_direction': trend_direction,
            'total_analyses': len(results),
            'average_confidence': sum(r.confidence for r in results) / len(results)
        }
    
    def get_analyzer_metrics(self) -> Dict[str, Any]:
        """Get sentiment analyzer performance metrics"""
        return {
            **self.metrics,
            'supported_languages': len(self.sentiment_lexicons),
            'emotion_types': len(self.emotion_keywords),
            'intensity_modifiers': len(self.intensity_modifiers),
            'negation_words': len(self.negation_words)
        }
