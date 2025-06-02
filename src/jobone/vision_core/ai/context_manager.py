"""
🧠 Orion Vision Core - Advanced Context Manager
Context awareness and conversation memory management

This module provides advanced context management:
- Long-term conversation memory
- Context-aware decision making
- Semantic context understanding
- Dynamic context adaptation
- Multi-session context persistence

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import logging
import json
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Types of context information"""
    CONVERSATION = "conversation"
    TASK = "task"
    USER_PREFERENCE = "user_preference"
    SYSTEM_STATE = "system_state"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    TEMPORAL = "temporal"
    EMOTIONAL = "emotional"

class ContextScope(Enum):
    """Scope of context information"""
    SESSION = "session"
    USER = "user"
    GLOBAL = "global"
    TEMPORARY = "temporary"

@dataclass
class ContextItem:
    """Individual context item"""
    context_id: str
    context_type: ContextType
    scope: ContextScope
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    expires_at: Optional[datetime] = None

@dataclass
class ContextQuery:
    """Query for retrieving relevant context"""
    query_text: str
    context_types: List[ContextType] = field(default_factory=list)
    scopes: List[ContextScope] = field(default_factory=list)
    max_results: int = 10
    min_relevance: float = 0.3
    time_window: Optional[timedelta] = None

@dataclass
class ContextSummary:
    """Summary of context for a specific query or session"""
    summary_id: str
    query: str
    relevant_contexts: List[ContextItem]
    summary_text: str
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.now)

class ContextManager:
    """
    Advanced context manager for Orion Vision Core.

    Manages conversation memory and context awareness:
    - Stores and retrieves conversation history
    - Maintains user preferences and system state
    - Provides context-aware recommendations
    - Manages temporal and emotional context
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the context manager"""
        self.storage_path = storage_path or "src/jobone/vision_core/data/context"
        self.contexts: Dict[str, ContextItem] = {}
        self.context_summaries: List[ContextSummary] = []
        self.session_id = self._generate_session_id()

        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)

        # Load existing contexts
        self._load_contexts()

        logger.info("🧠 Context Manager initialized with session: %s", self.session_id)

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]

    def add_context(self, content: str, context_type: ContextType,
                   scope: ContextScope = ContextScope.SESSION,
                   metadata: Optional[Dict[str, Any]] = None,
                   expires_in: Optional[timedelta] = None) -> str:
        """Add new context item"""

        context_id = self._generate_context_id(content, context_type)

        expires_at = None
        if expires_in:
            expires_at = datetime.now() + expires_in

        context_item = ContextItem(
            context_id=context_id,
            context_type=context_type,
            scope=scope,
            content=content,
            metadata=metadata or {},
            expires_at=expires_at
        )

        self.contexts[context_id] = context_item

        logger.info("📝 Added context: %s (%s)", context_type.value, scope.value)

        # Auto-save for persistent scopes
        if scope in [ContextScope.USER, ContextScope.GLOBAL]:
            self._save_context(context_item)

        return context_id

    def _generate_context_id(self, content: str, context_type: ContextType) -> str:
        """Generate unique context ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = int(datetime.now().timestamp())
        return f"{context_type.value}_{timestamp}_{content_hash}"

    def get_relevant_context(self, query: ContextQuery) -> List[ContextItem]:
        """Retrieve relevant context items based on query"""

        relevant_contexts = []

        for context in self.contexts.values():
            # Check if context has expired
            if context.expires_at and datetime.now() > context.expires_at:
                continue

            # Filter by context type
            if query.context_types and context.context_type not in query.context_types:
                continue

            # Filter by scope
            if query.scopes and context.scope not in query.scopes:
                continue

            # Filter by time window
            if query.time_window:
                cutoff_time = datetime.now() - query.time_window
                if context.created_at < cutoff_time:
                    continue

            # Calculate relevance score
            relevance = self._calculate_relevance(query.query_text, context)

            if relevance >= query.min_relevance:
                context.relevance_score = relevance
                context.last_accessed = datetime.now()
                context.access_count += 1
                relevant_contexts.append(context)

        # Sort by relevance score
        relevant_contexts.sort(key=lambda c: c.relevance_score, reverse=True)

        # Limit results
        return relevant_contexts[:query.max_results]

    def _calculate_relevance(self, query: str, context: ContextItem) -> float:
        """Calculate relevance score between query and context"""

        query_lower = query.lower()
        content_lower = context.content.lower()

        # Simple keyword matching (in real implementation, use semantic similarity)
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())

        if not query_words:
            return 0.0

        # Jaccard similarity
        intersection = query_words.intersection(content_words)
        union = query_words.union(content_words)

        jaccard_score = len(intersection) / len(union) if union else 0.0

        # Boost score based on context type relevance
        type_boost = {
            ContextType.CONVERSATION: 1.2,
            ContextType.TASK: 1.1,
            ContextType.USER_PREFERENCE: 1.0,
            ContextType.DOMAIN_KNOWLEDGE: 1.3,
            ContextType.SYSTEM_STATE: 0.8
        }.get(context.context_type, 1.0)

        # Boost score based on recency
        age_hours = (datetime.now() - context.created_at).total_seconds() / 3600
        recency_boost = max(0.5, 1.0 - (age_hours / 168))  # Decay over a week

        # Boost score based on access frequency
        frequency_boost = min(1.5, 1.0 + (context.access_count * 0.1))

        final_score = jaccard_score * type_boost * recency_boost * frequency_boost
        return min(final_score, 1.0)

    async def generate_context_summary(self, query: str, max_contexts: int = 5) -> ContextSummary:
        """Generate a summary of relevant context for a query"""

        context_query = ContextQuery(
            query_text=query,
            max_results=max_contexts,
            min_relevance=0.2
        )

        relevant_contexts = self.get_relevant_context(context_query)

        if not relevant_contexts:
            return ContextSummary(
                summary_id=f"summary_{int(datetime.now().timestamp())}",
                query=query,
                relevant_contexts=[],
                summary_text="No relevant context found.",
                confidence_score=0.0
            )

        # Create summary text
        context_texts = []
        for context in relevant_contexts:
            context_texts.append(f"[{context.context_type.value}] {context.content[:200]}...")

        summary_text = f"""
Relevant context for: {query}

Found {len(relevant_contexts)} relevant context items:

{chr(10).join(context_texts)}

Key insights:
- Most relevant context type: {relevant_contexts[0].context_type.value}
- Time range: {relevant_contexts[-1].created_at.strftime('%Y-%m-%d')} to {relevant_contexts[0].created_at.strftime('%Y-%m-%d')}
- Average relevance: {sum(c.relevance_score for c in relevant_contexts) / len(relevant_contexts):.2f}
"""

        confidence_score = (
            sum(c.relevance_score for c in relevant_contexts) / len(relevant_contexts)
        )

        summary = ContextSummary(
            summary_id=f"summary_{int(datetime.now().timestamp())}",
            query=query,
            relevant_contexts=relevant_contexts,
            summary_text=summary_text,
            confidence_score=confidence_score
        )

        self.context_summaries.append(summary)
        return summary

    def add_conversation_turn(
        self, user_input: str, ai_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a conversation turn to context"""

        # Add user input
        user_context_id = self.add_context(
            content=f"User: {user_input}",
            context_type=ContextType.CONVERSATION,
            scope=ContextScope.SESSION,
            metadata={**(metadata or {}), 'role': 'user'}
        )

        # Add AI response
        ai_context_id = self.add_context(
            content=f"AI: {ai_response}",
            context_type=ContextType.CONVERSATION,
            scope=ContextScope.SESSION,
            metadata={**(metadata or {}), 'role': 'ai', 'user_context_id': user_context_id}
        )

        return user_context_id, ai_context_id

    def add_user_preference(self, preference_key: str, preference_value: Any):
        """Add or update user preference"""

        content = f"{preference_key}: {preference_value}"

        self.add_context(
            content=content,
            context_type=ContextType.USER_PREFERENCE,
            scope=ContextScope.USER,
            metadata={'key': preference_key, 'value': preference_value}
        )

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get all user preferences"""

        preferences = {}

        for context in self.contexts.values():
            if (context.context_type == ContextType.USER_PREFERENCE and
                context.scope == ContextScope.USER):

                key = context.metadata.get('key')
                value = context.metadata.get('value')

                if key:
                    preferences[key] = value

        return preferences

    def cleanup_expired_contexts(self):
        """Remove expired context items"""

        now = datetime.now()
        expired_ids = []

        for context_id, context in self.contexts.items():
            if context.expires_at and now > context.expires_at:
                expired_ids.append(context_id)

        for context_id in expired_ids:
            del self.contexts[context_id]

        if expired_ids:
            logger.info("🧹 Cleaned up %d expired contexts", len(expired_ids))

    def _save_context(self, context: ContextItem):
        """Save context to persistent storage"""

        try:
            filename = f"{context.scope.value}_{context.context_type.value}.json"
            filepath = os.path.join(self.storage_path, filename)

            # Load existing contexts
            existing_contexts = []
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_contexts = json.load(f)

            # Add new context
            context_dict = {
                'context_id': context.context_id,
                'context_type': context.context_type.value,
                'scope': context.scope.value,
                'content': context.content,
                'metadata': context.metadata,
                'relevance_score': context.relevance_score,
                'created_at': context.created_at.isoformat(),
                'last_accessed': context.last_accessed.isoformat(),
                'access_count': context.access_count,
                'expires_at': context.expires_at.isoformat() if context.expires_at else None
            }

            existing_contexts.append(context_dict)

            # Save back to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_contexts, f, indent=2)

        except (OSError, IOError, json.JSONDecodeError) as e:
            logger.error("❌ Failed to save context: %s", e)

    def _load_contexts(self):
        """Load contexts from persistent storage"""

        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_path, filename)

                    with open(filepath, 'r', encoding='utf-8') as f:
                        contexts_data = json.load(f)

                    for context_data in contexts_data:
                        context = ContextItem(
                            context_id=context_data['context_id'],
                            context_type=ContextType(context_data['context_type']),
                            scope=ContextScope(context_data['scope']),
                            content=context_data['content'],
                            metadata=context_data['metadata'],
                            relevance_score=context_data['relevance_score'],
                            created_at=datetime.fromisoformat(context_data['created_at']),
                            last_accessed=datetime.fromisoformat(context_data['last_accessed']),
                            access_count=context_data['access_count'],
                            expires_at=(
                                datetime.fromisoformat(context_data['expires_at'])
                                if context_data['expires_at'] else None
                            )
                        )

                        self.contexts[context.context_id] = context

            logger.info("📁 Loaded %d contexts from storage", len(self.contexts))

        except (OSError, IOError, json.JSONDecodeError) as e:
            logger.error("❌ Failed to load contexts: %s", e)

    def get_context_statistics(self) -> Dict[str, Any]:
        """Get context manager statistics"""

        total_contexts = len(self.contexts)

        if total_contexts == 0:
            return {
                'total_contexts': 0,
                'contexts_by_type': {},
                'contexts_by_scope': {},
                'average_relevance': 0.0,
                'session_id': self.session_id
            }

        # Count by type
        type_counts = {}
        for context in self.contexts.values():
            type_name = context.context_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        # Count by scope
        scope_counts = {}
        for context in self.contexts.values():
            scope_name = context.scope.value
            scope_counts[scope_name] = scope_counts.get(scope_name, 0) + 1

        # Average relevance
        avg_relevance = sum(c.relevance_score for c in self.contexts.values()) / total_contexts

        return {
            'total_contexts': total_contexts,
            'contexts_by_type': type_counts,
            'contexts_by_scope': scope_counts,
            'average_relevance': avg_relevance,
            'session_id': self.session_id,
            'total_summaries': len(self.context_summaries)
        }
