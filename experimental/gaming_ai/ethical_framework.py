#!/usr/bin/env python3
"""
⚖️ Ethical Framework - Gaming AI

Comprehensive ethical compliance system for fair play and transparency.

Sprint 2 - Task 2.4: Ethical Framework Implementation
- Fair play guidelines enforcement
- Transparency mechanisms
- User consent systems
- Ethical decision engine

Author: Nexus - Quantum AI Architect
Sprint: 2.4 - Control & Action System
"""

import time
import json
import hashlib
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import warnings

class EthicalLevel(Enum):
    """Ethical compliance level"""
    STRICT = "strict"
    STANDARD = "standard"
    PERMISSIVE = "permissive"

class ConsentType(Enum):
    """User consent type"""
    EXPLICIT = "explicit"
    IMPLIED = "implied"
    ONGOING = "ongoing"
    REVOKED = "revoked"

class TransparencyLevel(Enum):
    """Transparency level"""
    FULL = "full"
    PARTIAL = "partial"
    MINIMAL = "minimal"

@dataclass
class EthicalRule:
    """Ethical rule definition"""
    rule_id: str
    category: str  # 'fair_play', 'transparency', 'consent', 'privacy'
    description: str
    enforcement_level: str  # 'mandatory', 'recommended', 'optional'
    violation_action: str  # 'block', 'warn', 'log'
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserConsent:
    """User consent record"""
    consent_id: str
    user_id: str
    consent_type: ConsentType
    granted_at: datetime
    expires_at: Optional[datetime]
    scope: List[str]  # What the consent covers
    revoked: bool = False
    revoked_at: Optional[datetime] = None

@dataclass
class EthicalDecision:
    """Ethical decision record"""
    decision_id: str
    timestamp: datetime
    context: Dict[str, Any]
    rules_applied: List[str]
    decision: str  # 'allow', 'deny', 'modify'
    reasoning: str
    confidence: float

@dataclass
class TransparencyLog:
    """Transparency log entry"""
    log_id: str
    timestamp: datetime
    action_type: str
    ai_involvement: float  # 0.0 to 1.0
    human_oversight: bool
    explanation: str
    user_notified: bool = False

class EthicalFramework:
    """
    Comprehensive Ethical Framework for Gaming AI
    
    Features:
    - Fair play guidelines enforcement
    - Transparency mechanisms and logging
    - User consent management
    - Ethical decision engine
    - Privacy protection
    - Audit trail maintenance
    """
    
    def __init__(self, ethical_level: EthicalLevel = EthicalLevel.STANDARD):
        self.ethical_level = ethical_level
        self.logger = logging.getLogger("EthicalFramework")
        
        # Ethical configuration
        self.ethical_rules = []
        self.user_consents = {}
        self.decision_history = []
        self.transparency_log = []
        
        # Threading and locks
        self.ethics_lock = threading.RLock()
        
        # Monitoring and metrics
        self.ethics_metrics = {
            'decisions_made': 0,
            'rules_violated': 0,
            'consent_requests': 0,
            'transparency_events': 0
        }
        
        # Initialize ethical rules
        self._initialize_ethical_rules()
        
        # Initialize transparency system
        self.transparency_level = TransparencyLevel.FULL
        self.transparency_enabled = True
        
        # User notification system
        self.notification_callbacks = []
        
        self.logger.info(f"⚖️ Ethical Framework initialized (level: {ethical_level.value})")
    
    def _initialize_ethical_rules(self):
        """Initialize default ethical rules"""
        self.ethical_rules = [
            # Fair Play Rules
            EthicalRule(
                "no_unfair_advantage",
                "fair_play",
                "AI assistance must not provide unfair advantages over human players",
                "mandatory",
                "block",
                {"max_assistance_level": 0.7, "skill_enhancement_only": True}
            ),
            
            EthicalRule(
                "respect_game_design",
                "fair_play",
                "AI must respect intended game mechanics and design",
                "mandatory",
                "block",
                {"no_exploit_abuse": True, "respect_difficulty": True}
            ),
            
            EthicalRule(
                "competitive_integrity",
                "fair_play",
                "Maintain competitive integrity in multiplayer environments",
                "mandatory",
                "block",
                {"no_ranked_automation": True, "human_oversight_required": True}
            ),
            
            # Transparency Rules
            EthicalRule(
                "ai_disclosure",
                "transparency",
                "AI assistance must be disclosed to other players when required",
                "mandatory",
                "warn",
                {"disclosure_required": True, "clear_indication": True}
            ),
            
            EthicalRule(
                "decision_explanation",
                "transparency",
                "AI decisions must be explainable to the user",
                "recommended",
                "log",
                {"explanation_detail": "high", "reasoning_visible": True}
            ),
            
            # Consent Rules
            EthicalRule(
                "explicit_consent",
                "consent",
                "Explicit user consent required for AI assistance",
                "mandatory",
                "block",
                {"consent_type": "explicit", "renewable": True}
            ),
            
            EthicalRule(
                "consent_granularity",
                "consent",
                "Users must be able to consent to specific AI features",
                "recommended",
                "warn",
                {"granular_control": True, "feature_specific": True}
            ),
            
            # Privacy Rules
            EthicalRule(
                "data_minimization",
                "privacy",
                "Collect and process only necessary data",
                "mandatory",
                "block",
                {"minimal_data": True, "purpose_limitation": True}
            ),
            
            EthicalRule(
                "user_control",
                "privacy",
                "Users must have control over their data",
                "mandatory",
                "warn",
                {"data_access": True, "deletion_rights": True}
            )
        ]
    
    def evaluate_ethical_compliance(self, action_context: Dict[str, Any]) -> Tuple[bool, List[str], str]:
        """Evaluate action against ethical rules"""
        with self.ethics_lock:
            violations = []
            warnings = []
            decision = "allow"
            
            try:
                for rule in self.ethical_rules:
                    compliance_result = self._check_rule_compliance(action_context, rule)
                    
                    if not compliance_result[0]:  # Rule violated
                        violation_msg = f"Rule '{rule.rule_id}' violated: {compliance_result[1]}"
                        
                        if rule.enforcement_level == "mandatory":
                            if rule.violation_action == "block":
                                violations.append(violation_msg)
                                decision = "deny"
                            elif rule.violation_action == "warn":
                                warnings.append(violation_msg)
                        elif rule.enforcement_level == "recommended":
                            warnings.append(f"Recommended: {violation_msg}")
                
                # Create ethical decision record
                decision_record = EthicalDecision(
                    decision_id=self._generate_decision_id(),
                    timestamp=datetime.now(),
                    context=action_context.copy(),
                    rules_applied=[rule.rule_id for rule in self.ethical_rules],
                    decision=decision,
                    reasoning=f"Violations: {len(violations)}, Warnings: {len(warnings)}",
                    confidence=1.0 - (len(violations) * 0.3 + len(warnings) * 0.1)
                )
                
                self.decision_history.append(decision_record)
                self.ethics_metrics['decisions_made'] += 1
                
                if violations:
                    self.ethics_metrics['rules_violated'] += len(violations)
                
                # Log transparency event
                if self.transparency_enabled:
                    self._log_transparency_event(action_context, decision_record)
                
                is_compliant = len(violations) == 0
                all_messages = violations + warnings
                
                return is_compliant, all_messages, decision
                
            except Exception as e:
                self.logger.error(f"❌ Ethical evaluation failed: {e}")
                return False, [f"Ethical evaluation error: {e}"], "deny"
    
    def _check_rule_compliance(self, context: Dict[str, Any], rule: EthicalRule) -> Tuple[bool, str]:
        """Check compliance with specific ethical rule"""
        try:
            if rule.category == "fair_play":
                return self._check_fair_play_compliance(context, rule)
            elif rule.category == "transparency":
                return self._check_transparency_compliance(context, rule)
            elif rule.category == "consent":
                return self._check_consent_compliance(context, rule)
            elif rule.category == "privacy":
                return self._check_privacy_compliance(context, rule)
            else:
                return True, "Unknown rule category"
        
        except Exception as e:
            return False, f"Rule check failed: {e}"
    
    def _check_fair_play_compliance(self, context: Dict[str, Any], rule: EthicalRule) -> Tuple[bool, str]:
        """Check fair play compliance"""
        if rule.rule_id == "no_unfair_advantage":
            assistance_level = context.get("ai_assistance_level", 0.0)
            max_allowed = rule.parameters.get("max_assistance_level", 0.7)
            
            if assistance_level > max_allowed:
                return False, f"AI assistance level {assistance_level} exceeds maximum {max_allowed}"
        
        elif rule.rule_id == "respect_game_design":
            if context.get("exploiting_bugs", False):
                return False, "Action exploits game bugs or unintended mechanics"
        
        elif rule.rule_id == "competitive_integrity":
            if context.get("competitive_mode", False) and context.get("full_automation", False):
                return False, "Full automation not allowed in competitive modes"
        
        return True, "Fair play compliance verified"
    
    def _check_transparency_compliance(self, context: Dict[str, Any], rule: EthicalRule) -> Tuple[bool, str]:
        """Check transparency compliance"""
        if rule.rule_id == "ai_disclosure":
            if context.get("multiplayer", False) and not context.get("ai_disclosed", False):
                return False, "AI assistance not disclosed in multiplayer environment"
        
        elif rule.rule_id == "decision_explanation":
            if not context.get("explanation_available", True):
                return False, "AI decision explanation not available"
        
        return True, "Transparency compliance verified"
    
    def _check_consent_compliance(self, context: Dict[str, Any], rule: EthicalRule) -> Tuple[bool, str]:
        """Check consent compliance"""
        user_id = context.get("user_id")
        if not user_id:
            return False, "No user ID provided for consent check"
        
        if rule.rule_id == "explicit_consent":
            consent = self._get_valid_consent(user_id, ["ai_assistance"])
            if not consent:
                return False, "No valid explicit consent for AI assistance"
        
        elif rule.rule_id == "consent_granularity":
            feature = context.get("feature_type")
            if feature:
                consent = self._get_valid_consent(user_id, [feature])
                if not consent:
                    return False, f"No consent for specific feature: {feature}"
        
        return True, "Consent compliance verified"
    
    def _check_privacy_compliance(self, context: Dict[str, Any], rule: EthicalRule) -> Tuple[bool, str]:
        """Check privacy compliance"""
        if rule.rule_id == "data_minimization":
            data_collected = context.get("data_collected", [])
            necessary_data = context.get("necessary_data", [])
            
            unnecessary_data = set(data_collected) - set(necessary_data)
            if unnecessary_data:
                return False, f"Collecting unnecessary data: {unnecessary_data}"
        
        elif rule.rule_id == "user_control":
            if not context.get("user_data_control", True):
                return False, "User lacks control over their data"
        
        return True, "Privacy compliance verified"
    
    def request_user_consent(self, user_id: str, scope: List[str], 
                           consent_type: ConsentType = ConsentType.EXPLICIT,
                           duration_days: Optional[int] = None) -> str:
        """Request user consent for specific scope"""
        with self.ethics_lock:
            consent_id = self._generate_consent_id()
            expires_at = None
            
            if duration_days:
                expires_at = datetime.now() + timedelta(days=duration_days)
            
            # In a real implementation, this would trigger UI for user consent
            # For now, we'll simulate consent being granted
            consent = UserConsent(
                consent_id=consent_id,
                user_id=user_id,
                consent_type=consent_type,
                granted_at=datetime.now(),
                expires_at=expires_at,
                scope=scope
            )
            
            self.user_consents[consent_id] = consent
            self.ethics_metrics['consent_requests'] += 1
            
            # Notify user (would be actual UI in real implementation)
            self._notify_user_consent_request(user_id, scope, consent_id)
            
            self.logger.info(f"📝 Consent requested: {consent_id} for user {user_id}")
            return consent_id
    
    def grant_consent(self, consent_id: str) -> bool:
        """Grant user consent (simulated user action)"""
        with self.ethics_lock:
            if consent_id in self.user_consents:
                consent = self.user_consents[consent_id]
                consent.granted_at = datetime.now()
                self.logger.info(f"✅ Consent granted: {consent_id}")
                return True
            return False
    
    def revoke_consent(self, consent_id: str) -> bool:
        """Revoke user consent"""
        with self.ethics_lock:
            if consent_id in self.user_consents:
                consent = self.user_consents[consent_id]
                consent.revoked = True
                consent.revoked_at = datetime.now()
                self.logger.info(f"❌ Consent revoked: {consent_id}")
                return True
            return False
    
    def _get_valid_consent(self, user_id: str, required_scope: List[str]) -> Optional[UserConsent]:
        """Get valid consent for user and scope"""
        for consent in self.user_consents.values():
            if (consent.user_id == user_id and 
                not consent.revoked and
                all(item in consent.scope for item in required_scope)):
                
                # Check expiration
                if consent.expires_at and datetime.now() > consent.expires_at:
                    continue
                
                return consent
        
        return None
    
    def _log_transparency_event(self, context: Dict[str, Any], decision: EthicalDecision):
        """Log transparency event"""
        log_entry = TransparencyLog(
            log_id=self._generate_log_id(),
            timestamp=datetime.now(),
            action_type=context.get("action_type", "unknown"),
            ai_involvement=context.get("ai_assistance_level", 0.0),
            human_oversight=context.get("human_oversight", False),
            explanation=decision.reasoning
        )
        
        self.transparency_log.append(log_entry)
        self.ethics_metrics['transparency_events'] += 1
        
        # Notify user if required
        if self.transparency_level == TransparencyLevel.FULL:
            self._notify_user_transparency(context.get("user_id"), log_entry)
    
    def _notify_user_consent_request(self, user_id: str, scope: List[str], consent_id: str):
        """Notify user of consent request"""
        notification = {
            "type": "consent_request",
            "user_id": user_id,
            "scope": scope,
            "consent_id": consent_id,
            "message": f"AI assistance requires consent for: {', '.join(scope)}"
        }
        
        self._send_notification(notification)
    
    def _notify_user_transparency(self, user_id: str, log_entry: TransparencyLog):
        """Notify user of transparency event"""
        if not user_id:
            return
        
        notification = {
            "type": "transparency",
            "user_id": user_id,
            "ai_involvement": log_entry.ai_involvement,
            "explanation": log_entry.explanation,
            "message": f"AI assistance level: {log_entry.ai_involvement:.1%}"
        }
        
        self._send_notification(notification)
    
    def _send_notification(self, notification: Dict[str, Any]):
        """Send notification to user"""
        for callback in self.notification_callbacks:
            try:
                callback(notification)
            except Exception as e:
                self.logger.error(f"❌ Notification callback failed: {e}")
    
    def add_notification_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add notification callback"""
        self.notification_callbacks.append(callback)
    
    def generate_ethics_report(self) -> Dict[str, Any]:
        """Generate comprehensive ethics report"""
        with self.ethics_lock:
            return {
                "ethical_level": self.ethical_level.value,
                "transparency_level": self.transparency_level.value,
                "metrics": self.ethics_metrics.copy(),
                "rules_count": len(self.ethical_rules),
                "active_consents": len([c for c in self.user_consents.values() if not c.revoked]),
                "decisions_made": len(self.decision_history),
                "transparency_events": len(self.transparency_log),
                "compliance_rate": self._calculate_compliance_rate(),
                "recent_violations": self._get_recent_violations()
            }
    
    def _calculate_compliance_rate(self) -> float:
        """Calculate overall compliance rate"""
        if not self.decision_history:
            return 100.0
        
        compliant_decisions = len([d for d in self.decision_history if d.decision == "allow"])
        return (compliant_decisions / len(self.decision_history)) * 100
    
    def _get_recent_violations(self) -> List[Dict[str, Any]]:
        """Get recent rule violations"""
        recent_violations = []
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for decision in self.decision_history:
            if decision.timestamp > cutoff_time and decision.decision == "deny":
                recent_violations.append({
                    "timestamp": decision.timestamp.isoformat(),
                    "reasoning": decision.reasoning,
                    "confidence": decision.confidence
                })
        
        return recent_violations[-10:]  # Last 10 violations
    
    def _generate_decision_id(self) -> str:
        """Generate unique decision ID"""
        timestamp = str(time.time())
        return hashlib.md5(f"decision_{timestamp}".encode()).hexdigest()[:12]
    
    def _generate_consent_id(self) -> str:
        """Generate unique consent ID"""
        timestamp = str(time.time())
        return hashlib.md5(f"consent_{timestamp}".encode()).hexdigest()[:12]
    
    def _generate_log_id(self) -> str:
        """Generate unique log ID"""
        timestamp = str(time.time())
        return hashlib.md5(f"log_{timestamp}".encode()).hexdigest()[:12]

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("⚖️ Ethical Framework - Sprint 2 Test")
    print("=" * 60)
    
    # Create ethical framework
    ethics = EthicalFramework(EthicalLevel.STANDARD)
    
    # Test ethical evaluation
    print("\n🔍 Testing ethical evaluation...")
    
    test_context = {
        "user_id": "test_user_123",
        "action_type": "mouse_click",
        "ai_assistance_level": 0.5,
        "multiplayer": True,
        "ai_disclosed": True,
        "human_oversight": True,
        "competitive_mode": False
    }
    
    is_compliant, messages, decision = ethics.evaluate_ethical_compliance(test_context)
    print(f"Ethical compliance: {is_compliant}")
    print(f"Decision: {decision}")
    for msg in messages:
        print(f"  - {msg}")
    
    # Test consent system
    print("\n📝 Testing consent system...")
    consent_id = ethics.request_user_consent("test_user_123", ["ai_assistance", "data_collection"])
    print(f"Consent requested: {consent_id}")
    
    # Grant consent
    granted = ethics.grant_consent(consent_id)
    print(f"Consent granted: {granted}")
    
    # Test with consent
    test_context["feature_type"] = "ai_assistance"
    is_compliant, messages, decision = ethics.evaluate_ethical_compliance(test_context)
    print(f"With consent - Compliant: {is_compliant}, Decision: {decision}")
    
    # Generate ethics report
    print("\n📊 Ethics Report:")
    report = ethics.generate_ethics_report()
    for key, value in report.items():
        if isinstance(value, (int, float, str)):
            print(f"   {key}: {value}")
    
    print("\n🎉 Sprint 2 - Task 2.4 test completed!")
    print("🎯 Target: Full ethical compliance")
    print(f"📈 Current: {report['compliance_rate']:.1f}% compliance rate")
