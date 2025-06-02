"""
📊 Orion Vision Core - Text Analyzer
Advanced text analysis and understanding

This module provides text analysis capabilities:
- Text quality assessment and metrics
- Readability analysis and scoring
- Language complexity evaluation
- Text structure analysis
- Content categorization and classification

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import string

from .language_manager import SupportedLanguage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextComplexity(Enum):
    """Text complexity levels"""
    VERY_SIMPLE = "very_simple"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

class TextCategory(Enum):
    """Text content categories"""
    TECHNICAL = "technical"
    CASUAL = "casual"
    FORMAL = "formal"
    CREATIVE = "creative"
    EDUCATIONAL = "educational"
    BUSINESS = "business"
    PERSONAL = "personal"
    NEWS = "news"

@dataclass
class TextMetrics:
    """Comprehensive text metrics"""
    # Basic metrics
    character_count: int = 0
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    
    # Advanced metrics
    average_word_length: float = 0.0
    average_sentence_length: float = 0.0
    vocabulary_richness: float = 0.0  # Unique words / Total words
    
    # Readability scores
    flesch_reading_ease: float = 0.0
    flesch_kincaid_grade: float = 0.0
    automated_readability_index: float = 0.0
    
    # Language features
    punctuation_density: float = 0.0
    capitalization_ratio: float = 0.0
    numeric_content_ratio: float = 0.0
    
    # Quality indicators
    spelling_errors: int = 0
    grammar_issues: int = 0
    style_suggestions: int = 0

@dataclass
class AnalysisResult:
    """Complete text analysis result"""
    original_text: str
    language: SupportedLanguage
    metrics: TextMetrics
    complexity: TextComplexity
    category: TextCategory
    quality_score: float  # 0.0 to 1.0
    readability_score: float  # 0.0 to 1.0
    key_phrases: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    analysis_time: float = 0.0

class TextAnalyzer:
    """
    Advanced text analysis and understanding system.
    
    Provides comprehensive text analysis with:
    - Text quality assessment
    - Readability analysis
    - Language complexity evaluation
    - Content categorization
    - Style and grammar checking
    """
    
    def __init__(self):
        """Initialize the text analyzer."""
        
        # Common words for different languages (for vocabulary analysis)
        self.common_words = {
            SupportedLanguage.ENGLISH: {
                'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with',
                'for', 'as', 'was', 'on', 'are', 'you', 'be', 'at', 'have', 'this'
            },
            SupportedLanguage.TURKISH: {
                've', 'bir', 'bu', 'da', 'de', 'ile', 'için', 'var', 'olan', 'gibi',
                'daha', 'çok', 'en', 'o', 'bu', 'şu', 'her', 'hiç', 'bazı', 'tüm'
            },
            SupportedLanguage.SPANISH: {
                'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se',
                'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para'
            }
        }
        
        # Technical keywords for categorization
        self.technical_keywords = {
            'programming', 'algorithm', 'database', 'software', 'hardware', 'network',
            'system', 'code', 'function', 'variable', 'class', 'method', 'api',
            'framework', 'library', 'server', 'client', 'protocol', 'security'
        }
        
        # Business keywords
        self.business_keywords = {
            'revenue', 'profit', 'market', 'customer', 'sales', 'strategy',
            'management', 'business', 'company', 'organization', 'team',
            'project', 'budget', 'investment', 'growth', 'performance'
        }
        
        # Performance metrics
        self.metrics = {
            'analyses_performed': 0,
            'average_analysis_time': 0.0,
            'average_quality_score': 0.0,
            'complexity_distribution': {complexity.value: 0 for complexity in TextComplexity},
            'category_distribution': {category.value: 0 for category in TextCategory}
        }
        
        logger.info("📊 Text Analyzer initialized")
    
    async def analyze_text(self, text: str, language: Optional[SupportedLanguage] = None) -> AnalysisResult:
        """
        Perform comprehensive text analysis.
        
        Args:
            text: Text to analyze
            language: Language of the text (auto-detect if None)
            
        Returns:
            AnalysisResult with comprehensive analysis
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Auto-detect language if not provided
            if language is None:
                language = await self._detect_language(text)
            
            # Calculate basic metrics
            metrics = await self._calculate_metrics(text, language)
            
            # Determine complexity
            complexity = self._determine_complexity(metrics)
            
            # Categorize content
            category = self._categorize_content(text)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(metrics, text)
            
            # Calculate readability score
            readability_score = self._calculate_readability_score(metrics)
            
            # Extract key phrases
            key_phrases = await self._extract_key_phrases(text, language)
            
            # Identify topics
            topics = await self._identify_topics(text)
            
            # Generate suggestions
            suggestions = await self._generate_suggestions(text, metrics, quality_score)
            
            analysis_time = asyncio.get_event_loop().time() - start_time
            
            # Create result
            result = AnalysisResult(
                original_text=text,
                language=language,
                metrics=metrics,
                complexity=complexity,
                category=category,
                quality_score=quality_score,
                readability_score=readability_score,
                key_phrases=key_phrases,
                topics=topics,
                suggestions=suggestions,
                analysis_time=analysis_time
            )
            
            # Update metrics
            self._update_metrics(result)
            
            logger.info(f"📊 Text analyzed: {len(text)} chars, quality: {quality_score:.2f}, complexity: {complexity.value}")
            return result
            
        except Exception as e:
            analysis_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"❌ Text analysis failed: {e}")
            
            # Return minimal result on failure
            return AnalysisResult(
                original_text=text,
                language=language or SupportedLanguage.ENGLISH,
                metrics=TextMetrics(),
                complexity=TextComplexity.MODERATE,
                category=TextCategory.CASUAL,
                quality_score=0.0,
                readability_score=0.0,
                analysis_time=analysis_time
            )
    
    async def _detect_language(self, text: str) -> SupportedLanguage:
        """Simple language detection"""
        
        # Basic keyword-based detection
        text_lower = text.lower()
        words = set(text_lower.split())
        
        # Check for language-specific common words
        for language, common_words in self.common_words.items():
            overlap = len(words.intersection(common_words))
            if overlap >= 2:  # If at least 2 common words found
                return language
        
        # Default to English
        return SupportedLanguage.ENGLISH
    
    async def _calculate_metrics(self, text: str, language: SupportedLanguage) -> TextMetrics:
        """Calculate comprehensive text metrics"""
        
        # Basic counts
        character_count = len(text)
        words = text.split()
        word_count = len(words)
        
        # Sentence count (simple approximation)
        sentence_endings = re.findall(r'[.!?]+', text)
        sentence_count = max(len(sentence_endings), 1)
        
        # Paragraph count
        paragraphs = text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # Average word length
        if word_count > 0:
            total_word_chars = sum(len(word.strip(string.punctuation)) for word in words)
            average_word_length = total_word_chars / word_count
        else:
            average_word_length = 0.0
        
        # Average sentence length
        average_sentence_length = word_count / sentence_count if sentence_count > 0 else 0.0
        
        # Vocabulary richness (unique words / total words)
        unique_words = set(word.lower().strip(string.punctuation) for word in words)
        vocabulary_richness = len(unique_words) / word_count if word_count > 0 else 0.0
        
        # Readability scores
        flesch_reading_ease = self._calculate_flesch_reading_ease(
            word_count, sentence_count, self._count_syllables(text)
        )
        flesch_kincaid_grade = self._calculate_flesch_kincaid_grade(
            word_count, sentence_count, self._count_syllables(text)
        )
        automated_readability_index = self._calculate_ari(
            character_count, word_count, sentence_count
        )
        
        # Language features
        punctuation_chars = sum(1 for char in text if char in string.punctuation)
        punctuation_density = punctuation_chars / character_count if character_count > 0 else 0.0
        
        capital_chars = sum(1 for char in text if char.isupper())
        capitalization_ratio = capital_chars / character_count if character_count > 0 else 0.0
        
        numeric_chars = sum(1 for char in text if char.isdigit())
        numeric_content_ratio = numeric_chars / character_count if character_count > 0 else 0.0
        
        # Quality indicators (simplified)
        spelling_errors = await self._count_spelling_errors(text, language)
        grammar_issues = await self._count_grammar_issues(text)
        style_suggestions = await self._count_style_suggestions(text)
        
        return TextMetrics(
            character_count=character_count,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            average_word_length=average_word_length,
            average_sentence_length=average_sentence_length,
            vocabulary_richness=vocabulary_richness,
            flesch_reading_ease=flesch_reading_ease,
            flesch_kincaid_grade=flesch_kincaid_grade,
            automated_readability_index=automated_readability_index,
            punctuation_density=punctuation_density,
            capitalization_ratio=capitalization_ratio,
            numeric_content_ratio=numeric_content_ratio,
            spelling_errors=spelling_errors,
            grammar_issues=grammar_issues,
            style_suggestions=style_suggestions
        )
    
    def _count_syllables(self, text: str) -> int:
        """Estimate syllable count (simplified)"""
        
        # Simple syllable counting heuristic
        words = text.split()
        total_syllables = 0
        
        for word in words:
            word_clean = word.lower().strip(string.punctuation)
            if not word_clean:
                continue
            
            # Count vowel groups
            vowels = 'aeiouy'
            syllable_count = 0
            prev_was_vowel = False
            
            for char in word_clean:
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = is_vowel
            
            # Adjust for silent 'e'
            if word_clean.endswith('e') and syllable_count > 1:
                syllable_count -= 1
            
            # Minimum of 1 syllable per word
            total_syllables += max(syllable_count, 1)
        
        return total_syllables
    
    def _calculate_flesch_reading_ease(self, words: int, sentences: int, syllables: int) -> float:
        """Calculate Flesch Reading Ease score"""
        
        if sentences == 0 or words == 0:
            return 0.0
        
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0.0, min(100.0, score))
    
    def _calculate_flesch_kincaid_grade(self, words: int, sentences: int, syllables: int) -> float:
        """Calculate Flesch-Kincaid Grade Level"""
        
        if sentences == 0 or words == 0:
            return 0.0
        
        grade = (0.39 * (words / sentences)) + (11.8 * (syllables / words)) - 15.59
        return max(0.0, grade)
    
    def _calculate_ari(self, characters: int, words: int, sentences: int) -> float:
        """Calculate Automated Readability Index"""
        
        if words == 0 or sentences == 0:
            return 0.0
        
        ari = (4.71 * (characters / words)) + (0.5 * (words / sentences)) - 21.43
        return max(0.0, ari)
    
    def _determine_complexity(self, metrics: TextMetrics) -> TextComplexity:
        """Determine text complexity based on metrics"""
        
        # Combine multiple factors for complexity assessment
        complexity_score = 0
        
        # Average sentence length factor
        if metrics.average_sentence_length > 25:
            complexity_score += 2
        elif metrics.average_sentence_length > 15:
            complexity_score += 1
        
        # Average word length factor
        if metrics.average_word_length > 6:
            complexity_score += 2
        elif metrics.average_word_length > 4.5:
            complexity_score += 1
        
        # Vocabulary richness factor
        if metrics.vocabulary_richness > 0.8:
            complexity_score += 2
        elif metrics.vocabulary_richness > 0.6:
            complexity_score += 1
        
        # Flesch-Kincaid grade factor
        if metrics.flesch_kincaid_grade > 16:
            complexity_score += 2
        elif metrics.flesch_kincaid_grade > 12:
            complexity_score += 1
        
        # Map score to complexity level
        if complexity_score >= 7:
            return TextComplexity.VERY_COMPLEX
        elif complexity_score >= 5:
            return TextComplexity.COMPLEX
        elif complexity_score >= 3:
            return TextComplexity.MODERATE
        elif complexity_score >= 1:
            return TextComplexity.SIMPLE
        else:
            return TextComplexity.VERY_SIMPLE
    
    def _categorize_content(self, text: str) -> TextCategory:
        """Categorize text content"""
        
        text_lower = text.lower()
        words = set(text_lower.split())
        
        # Check for technical content
        technical_matches = len(words.intersection(self.technical_keywords))
        if technical_matches >= 3:
            return TextCategory.TECHNICAL
        
        # Check for business content
        business_matches = len(words.intersection(self.business_keywords))
        if business_matches >= 3:
            return TextCategory.BUSINESS
        
        # Check for formal indicators
        formal_indicators = {'therefore', 'furthermore', 'consequently', 'moreover', 'nevertheless'}
        if words.intersection(formal_indicators):
            return TextCategory.FORMAL
        
        # Check for casual indicators
        casual_indicators = {'hey', 'yeah', 'cool', 'awesome', 'lol', 'btw'}
        if words.intersection(casual_indicators):
            return TextCategory.CASUAL
        
        # Default categorization
        return TextCategory.PERSONAL
    
    def _calculate_quality_score(self, metrics: TextMetrics, text: str) -> float:
        """Calculate overall text quality score"""
        
        quality_factors = []
        
        # Spelling and grammar factor
        error_ratio = (metrics.spelling_errors + metrics.grammar_issues) / max(metrics.word_count, 1)
        spelling_grammar_score = max(0.0, 1.0 - error_ratio * 2)
        quality_factors.append(spelling_grammar_score)
        
        # Readability factor
        readability_score = metrics.flesch_reading_ease / 100.0
        quality_factors.append(readability_score)
        
        # Vocabulary richness factor
        vocab_score = min(metrics.vocabulary_richness * 1.5, 1.0)
        quality_factors.append(vocab_score)
        
        # Structure factor (based on sentence and paragraph variation)
        if metrics.sentence_count > 1 and metrics.paragraph_count > 0:
            structure_score = 0.8
        else:
            structure_score = 0.4
        quality_factors.append(structure_score)
        
        # Average all factors
        return sum(quality_factors) / len(quality_factors)
    
    def _calculate_readability_score(self, metrics: TextMetrics) -> float:
        """Calculate readability score (0.0 to 1.0)"""
        
        # Normalize Flesch Reading Ease to 0-1 scale
        flesch_normalized = metrics.flesch_reading_ease / 100.0
        
        # Consider sentence length (shorter is more readable)
        sentence_factor = max(0.0, 1.0 - (metrics.average_sentence_length - 15) / 20)
        
        # Consider word length (shorter is more readable)
        word_factor = max(0.0, 1.0 - (metrics.average_word_length - 4) / 4)
        
        # Combine factors
        readability = (flesch_normalized + sentence_factor + word_factor) / 3
        return max(0.0, min(1.0, readability))
    
    async def _extract_key_phrases(self, text: str, language: SupportedLanguage) -> List[str]:
        """Extract key phrases from text"""
        
        # Simple key phrase extraction (in real implementation, use NLP libraries)
        words = text.split()
        
        # Find phrases with 2-3 words that appear to be important
        key_phrases = []
        
        for i in range(len(words) - 1):
            # Two-word phrases
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 6 and phrase.lower() not in self.common_words.get(language, set()):
                key_phrases.append(phrase.strip(string.punctuation))
        
        # Remove duplicates and limit to top 5
        unique_phrases = list(dict.fromkeys(key_phrases))
        return unique_phrases[:5]
    
    async def _identify_topics(self, text: str) -> List[str]:
        """Identify main topics in text"""
        
        # Simple topic identification based on keywords
        topics = []
        text_lower = text.lower()
        
        # Technology topics
        if any(keyword in text_lower for keyword in self.technical_keywords):
            topics.append("Technology")
        
        # Business topics
        if any(keyword in text_lower for keyword in self.business_keywords):
            topics.append("Business")
        
        # Education topics
        education_keywords = {'learn', 'study', 'education', 'school', 'university', 'course'}
        if any(keyword in text_lower for keyword in education_keywords):
            topics.append("Education")
        
        # Health topics
        health_keywords = {'health', 'medical', 'doctor', 'treatment', 'medicine', 'wellness'}
        if any(keyword in text_lower for keyword in health_keywords):
            topics.append("Health")
        
        return topics[:3]  # Limit to top 3 topics
    
    async def _generate_suggestions(self, text: str, metrics: TextMetrics, quality_score: float) -> List[str]:
        """Generate improvement suggestions"""
        
        suggestions = []
        
        # Readability suggestions
        if metrics.average_sentence_length > 25:
            suggestions.append("Consider breaking long sentences into shorter ones for better readability")
        
        if metrics.average_word_length > 6:
            suggestions.append("Try using simpler words to improve accessibility")
        
        # Structure suggestions
        if metrics.paragraph_count == 1 and metrics.sentence_count > 5:
            suggestions.append("Consider breaking the text into multiple paragraphs")
        
        # Quality suggestions
        if metrics.spelling_errors > 0:
            suggestions.append(f"Check for {metrics.spelling_errors} potential spelling errors")
        
        if metrics.grammar_issues > 0:
            suggestions.append(f"Review {metrics.grammar_issues} potential grammar issues")
        
        # Vocabulary suggestions
        if metrics.vocabulary_richness < 0.3:
            suggestions.append("Consider using more varied vocabulary to enhance the text")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    async def _count_spelling_errors(self, text: str, language: SupportedLanguage) -> int:
        """Count potential spelling errors (simplified)"""
        
        # Simple heuristic: words with unusual character patterns
        words = text.split()
        error_count = 0
        
        for word in words:
            word_clean = word.lower().strip(string.punctuation)
            if len(word_clean) < 2:
                continue
            
            # Check for repeated characters (potential typos)
            if re.search(r'(.)\1{2,}', word_clean):
                error_count += 1
            
            # Check for unusual character combinations
            if re.search(r'[qxz]{2,}', word_clean):
                error_count += 1
        
        return error_count
    
    async def _count_grammar_issues(self, text: str) -> int:
        """Count potential grammar issues (simplified)"""
        
        # Simple grammar checks
        issues = 0
        
        # Check for double spaces
        if '  ' in text:
            issues += text.count('  ')
        
        # Check for missing spaces after punctuation
        if re.search(r'[.!?][a-zA-Z]', text):
            issues += len(re.findall(r'[.!?][a-zA-Z]', text))
        
        # Check for repeated punctuation
        if re.search(r'[.!?]{3,}', text):
            issues += len(re.findall(r'[.!?]{3,}', text))
        
        return issues
    
    async def _count_style_suggestions(self, text: str) -> int:
        """Count potential style improvements (simplified)"""
        
        suggestions = 0
        
        # Check for passive voice indicators
        passive_indicators = ['was', 'were', 'been', 'being']
        for indicator in passive_indicators:
            suggestions += text.lower().count(indicator)
        
        # Check for weak words
        weak_words = ['very', 'really', 'quite', 'rather']
        for word in weak_words:
            suggestions += text.lower().count(word)
        
        return min(suggestions, 10)  # Cap at 10
    
    def _update_metrics(self, result: AnalysisResult):
        """Update analyzer metrics"""
        
        self.metrics['analyses_performed'] += 1
        
        # Update average analysis time
        total_analyses = self.metrics['analyses_performed']
        current_avg_time = self.metrics['average_analysis_time']
        self.metrics['average_analysis_time'] = (
            (current_avg_time * (total_analyses - 1) + result.analysis_time) / total_analyses
        )
        
        # Update average quality score
        current_avg_quality = self.metrics['average_quality_score']
        self.metrics['average_quality_score'] = (
            (current_avg_quality * (total_analyses - 1) + result.quality_score) / total_analyses
        )
        
        # Update complexity distribution
        self.metrics['complexity_distribution'][result.complexity.value] += 1
        
        # Update category distribution
        self.metrics['category_distribution'][result.category.value] += 1
    
    def get_analyzer_metrics(self) -> Dict[str, Any]:
        """Get text analyzer performance metrics"""
        return {
            **self.metrics,
            'supported_languages': len(self.common_words),
            'technical_keywords': len(self.technical_keywords),
            'business_keywords': len(self.business_keywords)
        }
