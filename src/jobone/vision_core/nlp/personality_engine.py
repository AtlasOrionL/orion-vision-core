"""
🎭 Orion Vision Core - Personality Engine
AI personality customization and adaptation

This module provides AI personality management:
- Dynamic personality adaptation
- Personality trait configuration
- Communication style adjustment
- Emotional response modeling
- Context-aware personality switching

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalityTrait(Enum):
    """Core personality traits"""
    # Communication Style
    FORMAL = "formal"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    
    # Emotional Characteristics
    EMPATHETIC = "empathetic"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    LOGICAL = "logical"
    
    # Interaction Style
    ASSERTIVE = "assertive"
    SUPPORTIVE = "supportive"
    ENCOURAGING = "encouraging"
    DIRECT = "direct"
    
    # Specialized Traits
    HUMOROUS = "humorous"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"
    PATIENT = "patient"

class PersonalityType(Enum):
    """Predefined personality types"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    FORMAL = "formal"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    EMPATHETIC = "empathetic"
    ASSERTIVE = "assertive"
    HUMOROUS = "humorous"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"
    SUPPORTIVE = "supportive"

@dataclass
class PersonalityProfile:
    """Complete personality profile configuration"""
    name: str
    personality_type: PersonalityType
    traits: Dict[PersonalityTrait, float] = field(default_factory=dict)  # 0.0 to 1.0
    communication_style: str = "balanced"
    emotional_responsiveness: float = 0.5  # 0.0 to 1.0
    formality_level: float = 0.5  # 0.0 to 1.0
    humor_frequency: float = 0.3  # 0.0 to 1.0
    technical_depth: float = 0.5  # 0.0 to 1.0
    patience_level: float = 0.7  # 0.0 to 1.0
    encouragement_level: float = 0.6  # 0.0 to 1.0
    custom_phrases: List[str] = field(default_factory=list)
    response_templates: Dict[str, List[str]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class PersonalityContext:
    """Context for personality adaptation"""
    user_mood: Optional[str] = None
    conversation_topic: Optional[str] = None
    interaction_history: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    time_of_day: Optional[str] = None
    urgency_level: float = 0.5  # 0.0 to 1.0

@dataclass
class PersonalityResponse:
    """Response generated with personality adaptation"""
    original_text: str
    adapted_text: str
    personality_applied: PersonalityProfile
    adaptation_score: float
    traits_used: List[PersonalityTrait]
    context_factors: List[str]

class PersonalityEngine:
    """
    AI personality customization and adaptation engine.
    
    Provides dynamic personality management with:
    - Personality trait configuration
    - Context-aware adaptation
    - Communication style adjustment
    - Emotional response modeling
    - Multi-personality support
    """
    
    def __init__(self):
        """Initialize the personality engine."""
        self.personalities: Dict[str, PersonalityProfile] = {}
        self.current_personality: Optional[PersonalityProfile] = None
        self.context: PersonalityContext = PersonalityContext()
        
        # Performance metrics
        self.metrics = {
            'adaptations_performed': 0,
            'personality_switches': 0,
            'context_updates': 0,
            'responses_generated': 0,
            'average_adaptation_score': 0.0
        }
        
        # Initialize default personalities
        self._initialize_default_personalities()
        
        # Set default personality
        self.current_personality = self.personalities.get("professional")
        
        logger.info("🎭 Personality Engine initialized with default personalities")
    
    def _initialize_default_personalities(self):
        """Initialize predefined personality profiles"""
        
        # Professional personality
        professional = PersonalityProfile(
            name="professional",
            personality_type=PersonalityType.PROFESSIONAL,
            traits={
                PersonalityTrait.FORMAL: 0.8,
                PersonalityTrait.PROFESSIONAL: 0.9,
                PersonalityTrait.ANALYTICAL: 0.7,
                PersonalityTrait.DIRECT: 0.6,
                PersonalityTrait.LOGICAL: 0.8
            },
            communication_style="formal",
            formality_level=0.8,
            humor_frequency=0.1,
            technical_depth=0.7,
            response_templates={
                'greeting': ["Good morning", "Good afternoon", "Hello"],
                'acknowledgment': ["Understood", "Noted", "I see"],
                'completion': ["Task completed successfully", "Operation finished", "Done"]
            }
        )
        
        # Friendly personality
        friendly = PersonalityProfile(
            name="friendly",
            personality_type=PersonalityType.FRIENDLY,
            traits={
                PersonalityTrait.FRIENDLY: 0.9,
                PersonalityTrait.EMPATHETIC: 0.8,
                PersonalityTrait.SUPPORTIVE: 0.8,
                PersonalityTrait.ENCOURAGING: 0.7,
                PersonalityTrait.PATIENT: 0.8
            },
            communication_style="warm",
            formality_level=0.3,
            humor_frequency=0.5,
            emotional_responsiveness=0.8,
            encouragement_level=0.8,
            response_templates={
                'greeting': ["Hi there!", "Hello friend!", "Hey! How are you?"],
                'acknowledgment': ["Got it!", "Sure thing!", "Absolutely!"],
                'completion': ["All done! 😊", "There you go!", "Perfect!"]
            }
        )
        
        # Casual personality
        casual = PersonalityProfile(
            name="casual",
            personality_type=PersonalityType.CASUAL,
            traits={
                PersonalityTrait.CASUAL: 0.9,
                PersonalityTrait.FRIENDLY: 0.7,
                PersonalityTrait.HUMOROUS: 0.6,
                PersonalityTrait.DIRECT: 0.5
            },
            communication_style="relaxed",
            formality_level=0.2,
            humor_frequency=0.6,
            response_templates={
                'greeting': ["Hey!", "What's up?", "Yo!"],
                'acknowledgment': ["Cool", "Alright", "Yep"],
                'completion': ["Done!", "All set!", "There ya go!"]
            }
        )
        
        # Technical personality
        technical = PersonalityProfile(
            name="technical",
            personality_type=PersonalityType.TECHNICAL,
            traits={
                PersonalityTrait.TECHNICAL: 0.9,
                PersonalityTrait.ANALYTICAL: 0.8,
                PersonalityTrait.LOGICAL: 0.9,
                PersonalityTrait.DIRECT: 0.7,
                PersonalityTrait.EDUCATIONAL: 0.8
            },
            communication_style="precise",
            formality_level=0.6,
            technical_depth=0.9,
            response_templates={
                'greeting': ["System ready", "Interface active", "Ready for input"],
                'acknowledgment': ["Processing", "Executing", "Confirmed"],
                'completion': ["Operation completed", "Process finished", "Execution successful"]
            }
        )
        
        # Creative personality
        creative = PersonalityProfile(
            name="creative",
            personality_type=PersonalityType.CREATIVE,
            traits={
                PersonalityTrait.CREATIVE: 0.9,
                PersonalityTrait.HUMOROUS: 0.7,
                PersonalityTrait.ENCOURAGING: 0.8,
                PersonalityTrait.FRIENDLY: 0.7
            },
            communication_style="expressive",
            formality_level=0.3,
            humor_frequency=0.7,
            emotional_responsiveness=0.8,
            response_templates={
                'greeting': ["Hello, creative soul!", "Ready to create magic?", "Let's make something amazing!"],
                'acknowledgment': ["Love it!", "Brilliant idea!", "That's inspiring!"],
                'completion': ["Masterpiece created! ✨", "Beautiful work!", "Creative magic complete!"]
            }
        )
        
        # Store personalities
        self.personalities = {
            "professional": professional,
            "friendly": friendly,
            "casual": casual,
            "technical": technical,
            "creative": creative
        }
    
    async def adapt_response(self, text: str, context: Optional[PersonalityContext] = None) -> PersonalityResponse:
        """
        Adapt text response based on current personality and context.
        
        Args:
            text: Original text to adapt
            context: Optional context for adaptation
            
        Returns:
            PersonalityResponse with adapted text
        """
        if not self.current_personality:
            return PersonalityResponse(
                original_text=text,
                adapted_text=text,
                personality_applied=None,
                adaptation_score=0.0,
                traits_used=[],
                context_factors=[]
            )
        
        try:
            # Update context if provided
            if context:
                self.context = context
                self.metrics['context_updates'] += 1
            
            # Apply personality adaptation
            adapted_text = await self._apply_personality_traits(text)
            
            # Calculate adaptation score
            adaptation_score = self._calculate_adaptation_score(text, adapted_text)
            
            # Determine traits used
            traits_used = self._get_active_traits()
            
            # Identify context factors
            context_factors = self._identify_context_factors()
            
            # Update metrics
            self.metrics['adaptations_performed'] += 1
            self.metrics['responses_generated'] += 1
            
            # Update average adaptation score
            total_adaptations = self.metrics['adaptations_performed']
            current_avg = self.metrics['average_adaptation_score']
            self.metrics['average_adaptation_score'] = (
                (current_avg * (total_adaptations - 1) + adaptation_score) / total_adaptations
            )
            
            response = PersonalityResponse(
                original_text=text,
                adapted_text=adapted_text,
                personality_applied=self.current_personality,
                adaptation_score=adaptation_score,
                traits_used=traits_used,
                context_factors=context_factors
            )
            
            logger.info(f"🎭 Response adapted with {self.current_personality.name} personality (score: {adaptation_score:.2f})")
            return response
            
        except Exception as e:
            logger.error(f"❌ Personality adaptation failed: {e}")
            return PersonalityResponse(
                original_text=text,
                adapted_text=text,
                personality_applied=self.current_personality,
                adaptation_score=0.0,
                traits_used=[],
                context_factors=[]
            )
    
    async def _apply_personality_traits(self, text: str) -> str:
        """Apply personality traits to text"""
        adapted_text = text
        personality = self.current_personality
        
        # Apply formality level
        if personality.formality_level > 0.7:
            adapted_text = self._make_formal(adapted_text)
        elif personality.formality_level < 0.3:
            adapted_text = self._make_casual(adapted_text)
        
        # Apply humor if appropriate
        if personality.humor_frequency > 0.5 and random.random() < personality.humor_frequency:
            adapted_text = self._add_humor(adapted_text)
        
        # Apply empathy
        if PersonalityTrait.EMPATHETIC in personality.traits:
            empathy_level = personality.traits[PersonalityTrait.EMPATHETIC]
            if empathy_level > 0.6:
                adapted_text = self._add_empathy(adapted_text)
        
        # Apply encouragement
        if personality.encouragement_level > 0.6:
            adapted_text = self._add_encouragement(adapted_text)
        
        # Apply technical depth
        if personality.technical_depth > 0.7:
            adapted_text = self._add_technical_detail(adapted_text)
        
        return adapted_text
    
    def _make_formal(self, text: str) -> str:
        """Make text more formal"""
        # Simple formal transformations
        replacements = {
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not",
            "isn't": "is not",
            "aren't": "are not",
            "hi": "hello",
            "hey": "hello",
            "yeah": "yes",
            "ok": "very well"
        }
        
        formal_text = text
        for informal, formal in replacements.items():
            formal_text = formal_text.replace(informal, formal)
        
        return formal_text
    
    def _make_casual(self, text: str) -> str:
        """Make text more casual"""
        # Simple casual transformations
        replacements = {
            "cannot": "can't",
            "will not": "won't",
            "do not": "don't",
            "is not": "isn't",
            "are not": "aren't",
            "hello": "hi",
            "very well": "ok"
        }
        
        casual_text = text
        for formal, casual in replacements.items():
            casual_text = casual_text.replace(formal, casual)
        
        return casual_text
    
    def _add_humor(self, text: str) -> str:
        """Add humor to text"""
        humor_additions = [
            " 😄", " 😊", " 🎉", " ✨",
            " (with a smile)", " (cheerfully)"
        ]
        
        if random.random() < 0.3:  # 30% chance to add humor
            return text + random.choice(humor_additions)
        
        return text
    
    def _add_empathy(self, text: str) -> str:
        """Add empathetic elements to text"""
        empathy_prefixes = [
            "I understand that ",
            "I can see that ",
            "I appreciate that "
        ]
        
        if text.startswith(("I", "You", "This")):
            return random.choice(empathy_prefixes) + text.lower()
        
        return text
    
    def _add_encouragement(self, text: str) -> str:
        """Add encouraging elements to text"""
        encouragement_additions = [
            " You're doing great!",
            " Keep up the good work!",
            " You've got this!",
            " Excellent progress!"
        ]
        
        if random.random() < 0.2:  # 20% chance to add encouragement
            return text + random.choice(encouragement_additions)
        
        return text
    
    def _add_technical_detail(self, text: str) -> str:
        """Add technical detail to text"""
        # This would be more sophisticated in a real implementation
        if "completed" in text.lower():
            return text + " (Process executed successfully with exit code 0)"
        elif "error" in text.lower():
            return text + " (Error code: 500 - Internal processing error)"
        
        return text
    
    def _calculate_adaptation_score(self, original: str, adapted: str) -> float:
        """Calculate how much the text was adapted"""
        if original == adapted:
            return 0.0
        
        # Simple scoring based on text differences
        char_diff = abs(len(adapted) - len(original))
        word_diff = abs(len(adapted.split()) - len(original.split()))
        
        # Normalize score between 0 and 1
        score = min((char_diff + word_diff * 5) / max(len(original), 1), 1.0)
        return score
    
    def _get_active_traits(self) -> List[PersonalityTrait]:
        """Get currently active personality traits"""
        if not self.current_personality:
            return []
        
        active_traits = []
        for trait, strength in self.current_personality.traits.items():
            if strength > 0.5:  # Consider trait active if strength > 0.5
                active_traits.append(trait)
        
        return active_traits
    
    def _identify_context_factors(self) -> List[str]:
        """Identify context factors affecting adaptation"""
        factors = []
        
        if self.context.user_mood:
            factors.append(f"user_mood:{self.context.user_mood}")
        
        if self.context.conversation_topic:
            factors.append(f"topic:{self.context.conversation_topic}")
        
        if self.context.urgency_level > 0.7:
            factors.append("high_urgency")
        
        if self.context.time_of_day:
            factors.append(f"time:{self.context.time_of_day}")
        
        return factors
    
    async def switch_personality(self, personality_name: str) -> bool:
        """
        Switch to a different personality.
        
        Args:
            personality_name: Name of the personality to switch to
            
        Returns:
            True if switch successful, False otherwise
        """
        if personality_name not in self.personalities:
            logger.error(f"❌ Personality '{personality_name}' not found")
            return False
        
        try:
            old_personality = self.current_personality.name if self.current_personality else "none"
            self.current_personality = self.personalities[personality_name]
            self.metrics['personality_switches'] += 1
            
            logger.info(f"🔄 Personality switched: {old_personality} → {personality_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Personality switch failed: {e}")
            return False
    
    def create_custom_personality(self, profile: PersonalityProfile) -> bool:
        """
        Create a custom personality profile.
        
        Args:
            profile: PersonalityProfile to add
            
        Returns:
            True if creation successful, False otherwise
        """
        try:
            self.personalities[profile.name] = profile
            logger.info(f"✨ Created custom personality: {profile.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create personality: {e}")
            return False
    
    def get_available_personalities(self) -> List[str]:
        """Get list of available personality names"""
        return list(self.personalities.keys())
    
    def get_personality_info(self, personality_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a personality.
        
        Args:
            personality_name: Name of the personality
            
        Returns:
            Dictionary with personality information
        """
        if personality_name not in self.personalities:
            return None
        
        personality = self.personalities[personality_name]
        
        return {
            'name': personality.name,
            'type': personality.personality_type.value,
            'traits': {trait.value: strength for trait, strength in personality.traits.items()},
            'communication_style': personality.communication_style,
            'formality_level': personality.formality_level,
            'humor_frequency': personality.humor_frequency,
            'technical_depth': personality.technical_depth,
            'patience_level': personality.patience_level,
            'encouragement_level': personality.encouragement_level,
            'custom_phrases_count': len(personality.custom_phrases),
            'response_templates_count': len(personality.response_templates),
            'created_at': personality.created_at.isoformat()
        }
    
    def get_engine_metrics(self) -> Dict[str, Any]:
        """Get personality engine performance metrics"""
        return {
            **self.metrics,
            'current_personality': self.current_personality.name if self.current_personality else None,
            'available_personalities': len(self.personalities),
            'active_traits': len(self._get_active_traits()),
            'context_factors': len(self._identify_context_factors())
        }
