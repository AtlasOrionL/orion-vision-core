#!/usr/bin/env python3
"""
Zero Trust Architecture Demo
Sprint 6.1 - Epic 1: Zero Trust Architecture Foundation
Orion Vision Core - Zero Trust Implementation Demo

This demo showcases the Zero Trust Architecture implementation including:
- Network micro-segmentation
- Identity verification and MFA
- Device trust scoring
- Risk-based access control
- Continuous monitoring

Author: Orion Development Team
Version: 1.0.0
Date: 30 Mayıs 2025
"""

import asyncio
import json
import logging
import time
import uuid
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ZeroTrustDemo")

class TrustLevel(Enum):
    TRUSTED = "trusted"
    CONDITIONAL = "conditional"
    UNTRUSTED = "untrusted"
    BLOCKED = "blocked"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Device:
    device_id: str
    device_type: str
    os_version: str
    fingerprint: str
    compliance_score: float
    last_seen: datetime
    trust_level: TrustLevel
    
@dataclass
class User:
    user_id: str
    username: str
    roles: List[str]
    mfa_enabled: bool
    last_login: datetime
    risk_score: float
    
@dataclass
class AccessRequest:
    request_id: str
    user: User
    device: Device
    resource: str
    action: str
    timestamp: datetime
    context: Dict[str, Any]

class DeviceFingerprinter:
    """Device fingerprinting and trust scoring"""
    
    def __init__(self):
        self.known_devices = {}
        self.trust_scores = {}
        
    def generate_fingerprint(self, device_info: Dict[str, Any]) -> str:
        """Generate device fingerprint"""
        fingerprint_data = {
            'hardware': device_info.get('hardware', {}),
            'software': device_info.get('software', {}),
            'network': device_info.get('network', {})
        }
        
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()
    
    def calculate_trust_score(self, device: Device) -> float:
        """Calculate device trust score"""
        score = 0.0
        
        # Compliance score (40% weight)
        score += device.compliance_score * 0.4
        
        # Device age factor (20% weight)
        days_since_seen = (datetime.now() - device.last_seen).days
        age_factor = max(0, 1 - (days_since_seen / 30))  # Decay over 30 days
        score += age_factor * 0.2
        
        # Device type factor (20% weight)
        type_scores = {
            'laptop': 0.8,
            'desktop': 0.9,
            'mobile': 0.6,
            'tablet': 0.5,
            'iot': 0.3
        }
        score += type_scores.get(device.device_type, 0.5) * 0.2
        
        # Historical behavior (20% weight)
        historical_score = self.trust_scores.get(device.device_id, 0.5)
        score += historical_score * 0.2
        
        return min(1.0, max(0.0, score))
    
    def determine_trust_level(self, trust_score: float) -> TrustLevel:
        """Determine trust level based on score"""
        if trust_score >= 0.8:
            return TrustLevel.TRUSTED
        elif trust_score >= 0.6:
            return TrustLevel.CONDITIONAL
        elif trust_score >= 0.4:
            return TrustLevel.UNTRUSTED
        else:
            return TrustLevel.BLOCKED

class IdentityVerifier:
    """Identity verification and MFA"""
    
    def __init__(self):
        self.user_sessions = {}
        self.mfa_challenges = {}
        
    def verify_identity(self, username: str, password: str) -> Optional[User]:
        """Verify user identity"""
        # Simulate user database lookup
        users_db = {
            'admin': {
                'user_id': 'user_001',
                'username': 'admin',
                'password_hash': 'admin_hash',
                'roles': ['admin', 'agent-operator'],
                'mfa_enabled': True
            },
            'operator': {
                'user_id': 'user_002',
                'username': 'operator',
                'password_hash': 'operator_hash',
                'roles': ['agent-operator'],
                'mfa_enabled': True
            },
            'viewer': {
                'user_id': 'user_003',
                'username': 'viewer',
                'password_hash': 'viewer_hash',
                'roles': ['agent-viewer'],
                'mfa_enabled': False
            }
        }
        
        user_data = users_db.get(username)
        if user_data and self._verify_password(password, user_data['password_hash']):
            return User(
                user_id=user_data['user_id'],
                username=user_data['username'],
                roles=user_data['roles'],
                mfa_enabled=user_data['mfa_enabled'],
                last_login=datetime.now(),
                risk_score=0.1  # Low risk for successful auth
            )
        return None
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password (simplified)"""
        return f"{password}_hash" == password_hash
    
    def initiate_mfa(self, user: User) -> str:
        """Initiate MFA challenge"""
        if not user.mfa_enabled:
            return "mfa_not_required"
        
        challenge_id = str(uuid.uuid4())
        self.mfa_challenges[challenge_id] = {
            'user_id': user.user_id,
            'challenge_type': 'totp',
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(minutes=5)
        }
        
        logger.info(f"MFA challenge initiated for user {user.username}: {challenge_id}")
        return challenge_id
    
    def verify_mfa(self, challenge_id: str, response: str) -> bool:
        """Verify MFA response"""
        challenge = self.mfa_challenges.get(challenge_id)
        if not challenge:
            return False
        
        if datetime.now() > challenge['expires_at']:
            del self.mfa_challenges[challenge_id]
            return False
        
        # Simulate TOTP verification (accept 123456 as valid)
        is_valid = response == "123456"
        
        if is_valid:
            del self.mfa_challenges[challenge_id]
            logger.info(f"MFA verification successful for challenge {challenge_id}")
        
        return is_valid

class RiskEngine:
    """Risk assessment and scoring"""
    
    def __init__(self):
        self.risk_factors = {}
        
    def calculate_risk_score(self, access_request: AccessRequest) -> float:
        """Calculate risk score for access request"""
        risk_score = 0.0
        
        # User risk factors (30% weight)
        user_risk = self._calculate_user_risk(access_request.user)
        risk_score += user_risk * 0.3
        
        # Device risk factors (25% weight)
        device_risk = self._calculate_device_risk(access_request.device)
        risk_score += device_risk * 0.25
        
        # Context risk factors (25% weight)
        context_risk = self._calculate_context_risk(access_request.context)
        risk_score += context_risk * 0.25
        
        # Resource risk factors (20% weight)
        resource_risk = self._calculate_resource_risk(access_request.resource, access_request.action)
        risk_score += resource_risk * 0.2
        
        return min(1.0, max(0.0, risk_score))
    
    def _calculate_user_risk(self, user: User) -> float:
        """Calculate user-specific risk"""
        risk = user.risk_score
        
        # Time since last login
        if user.last_login:
            hours_since_login = (datetime.now() - user.last_login).total_seconds() / 3600
            if hours_since_login > 24:
                risk += 0.2
        
        # Role-based risk
        if 'admin' in user.roles:
            risk += 0.1  # Admins are higher risk
        
        return risk
    
    def _calculate_device_risk(self, device: Device) -> float:
        """Calculate device-specific risk"""
        risk = 1.0 - device.compliance_score
        
        # Trust level adjustment
        trust_adjustments = {
            TrustLevel.TRUSTED: -0.3,
            TrustLevel.CONDITIONAL: 0.0,
            TrustLevel.UNTRUSTED: 0.3,
            TrustLevel.BLOCKED: 0.8
        }
        risk += trust_adjustments.get(device.trust_level, 0.0)
        
        return max(0.0, min(1.0, risk))
    
    def _calculate_context_risk(self, context: Dict[str, Any]) -> float:
        """Calculate context-specific risk"""
        risk = 0.0
        
        # Time-based risk
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Outside business hours
            risk += 0.3
        
        # Location-based risk
        location = context.get('location', 'unknown')
        if location not in ['office', 'home']:
            risk += 0.4
        
        # Network-based risk
        network = context.get('network', 'unknown')
        if network in ['public_wifi', 'mobile']:
            risk += 0.2
        
        return risk
    
    def _calculate_resource_risk(self, resource: str, action: str) -> float:
        """Calculate resource and action specific risk"""
        risk = 0.0
        
        # Resource sensitivity
        sensitive_resources = {
            '/api/admin': 0.8,
            '/api/agents/delete': 0.7,
            '/api/config': 0.6,
            '/api/agents': 0.3,
            '/dashboard': 0.1
        }
        risk += sensitive_resources.get(resource, 0.2)
        
        # Action risk
        risky_actions = {
            'DELETE': 0.8,
            'PUT': 0.6,
            'PATCH': 0.5,
            'POST': 0.3,
            'GET': 0.1
        }
        risk += risky_actions.get(action.upper(), 0.2)
        
        return min(1.0, risk)
    
    def determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score"""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

class PolicyEngine:
    """Zero Trust policy enforcement"""
    
    def __init__(self):
        self.policies = self._load_policies()
        
    def _load_policies(self) -> List[Dict[str, Any]]:
        """Load zero trust policies"""
        return [
            {
                'name': 'admin_access',
                'condition': 'user.roles contains "admin"',
                'requirements': ['mfa_required', 'trusted_device'],
                'actions': ['allow'],
                'priority': 100
            },
            {
                'name': 'high_risk_block',
                'condition': 'risk_level == "critical"',
                'requirements': [],
                'actions': ['deny', 'alert'],
                'priority': 10
            },
            {
                'name': 'untrusted_device',
                'condition': 'device.trust_level == "untrusted"',
                'requirements': ['additional_verification'],
                'actions': ['conditional_allow'],
                'priority': 50
            },
            {
                'name': 'default_allow',
                'condition': 'risk_level in ["low", "medium"]',
                'requirements': ['basic_auth'],
                'actions': ['allow'],
                'priority': 1000
            }
        ]
    
    def evaluate_access(self, access_request: AccessRequest, risk_level: RiskLevel, 
                       trust_level: TrustLevel) -> Dict[str, Any]:
        """Evaluate access request against policies"""
        
        # Sort policies by priority
        sorted_policies = sorted(self.policies, key=lambda p: p['priority'])
        
        for policy in sorted_policies:
            if self._evaluate_condition(policy['condition'], access_request, risk_level, trust_level):
                return {
                    'policy_name': policy['name'],
                    'decision': policy['actions'][0],
                    'requirements': policy['requirements'],
                    'actions': policy['actions']
                }
        
        # Default deny
        return {
            'policy_name': 'default_deny',
            'decision': 'deny',
            'requirements': [],
            'actions': ['deny', 'log']
        }
    
    def _evaluate_condition(self, condition: str, access_request: AccessRequest, 
                          risk_level: RiskLevel, trust_level: TrustLevel) -> bool:
        """Evaluate policy condition (simplified)"""
        
        # Simple condition evaluation
        if 'admin' in condition and 'admin' in access_request.user.roles:
            return True
        elif 'critical' in condition and risk_level == RiskLevel.CRITICAL:
            return True
        elif 'untrusted' in condition and trust_level == TrustLevel.UNTRUSTED:
            return True
        elif 'low' in condition and risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
            return True
        
        return False

class ZeroTrustDemo:
    """Main Zero Trust Architecture Demo"""
    
    def __init__(self):
        self.device_fingerprinter = DeviceFingerprinter()
        self.identity_verifier = IdentityVerifier()
        self.risk_engine = RiskEngine()
        self.policy_engine = PolicyEngine()
        
        # Demo data
        self.demo_devices = self._create_demo_devices()
        self.demo_users = self._create_demo_users()
        
    def _create_demo_devices(self) -> List[Device]:
        """Create demo devices"""
        devices = []
        
        # Trusted laptop
        devices.append(Device(
            device_id="dev_001",
            device_type="laptop",
            os_version="Windows 11",
            fingerprint="abc123def456",
            compliance_score=0.95,
            last_seen=datetime.now() - timedelta(hours=1),
            trust_level=TrustLevel.TRUSTED
        ))
        
        # Conditional mobile
        devices.append(Device(
            device_id="dev_002",
            device_type="mobile",
            os_version="iOS 17",
            fingerprint="xyz789uvw012",
            compliance_score=0.75,
            last_seen=datetime.now() - timedelta(hours=6),
            trust_level=TrustLevel.CONDITIONAL
        ))
        
        # Untrusted device
        devices.append(Device(
            device_id="dev_003",
            device_type="laptop",
            os_version="Windows 10",
            fingerprint="old456device789",
            compliance_score=0.45,
            last_seen=datetime.now() - timedelta(days=7),
            trust_level=TrustLevel.UNTRUSTED
        ))
        
        return devices
    
    def _create_demo_users(self) -> List[User]:
        """Create demo users"""
        return [
            User(
                user_id="user_001",
                username="admin",
                roles=["admin", "agent-operator"],
                mfa_enabled=True,
                last_login=datetime.now() - timedelta(hours=2),
                risk_score=0.1
            ),
            User(
                user_id="user_002",
                username="operator",
                roles=["agent-operator"],
                mfa_enabled=True,
                last_login=datetime.now() - timedelta(hours=8),
                risk_score=0.2
            ),
            User(
                user_id="user_003",
                username="viewer",
                roles=["agent-viewer"],
                mfa_enabled=False,
                last_login=datetime.now() - timedelta(days=1),
                risk_score=0.3
            )
        ]
    
    async def run_demo(self):
        """Run the Zero Trust demo"""
        logger.info("🚀 Starting Zero Trust Architecture Demo")
        logger.info("=" * 60)
        
        # Demo scenarios
        scenarios = [
            {
                'name': 'Admin Access from Trusted Device',
                'user': self.demo_users[0],
                'device': self.demo_devices[0],
                'resource': '/api/admin',
                'action': 'GET',
                'context': {'location': 'office', 'network': 'corporate'}
            },
            {
                'name': 'Operator Access from Mobile Device',
                'user': self.demo_users[1],
                'device': self.demo_devices[1],
                'resource': '/api/agents',
                'action': 'POST',
                'context': {'location': 'home', 'network': 'wifi'}
            },
            {
                'name': 'Viewer Access from Untrusted Device',
                'user': self.demo_users[2],
                'device': self.demo_devices[2],
                'resource': '/dashboard',
                'action': 'GET',
                'context': {'location': 'public', 'network': 'public_wifi'}
            },
            {
                'name': 'High-Risk Admin Operation',
                'user': self.demo_users[0],
                'device': self.demo_devices[2],
                'resource': '/api/agents/delete',
                'action': 'DELETE',
                'context': {'location': 'unknown', 'network': 'mobile'}
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            logger.info(f"\n📋 Scenario {i}: {scenario['name']}")
            logger.info("-" * 50)
            
            await self._run_scenario(scenario)
            
            if i < len(scenarios):
                logger.info("\n⏳ Waiting 2 seconds before next scenario...")
                await asyncio.sleep(2)
        
        logger.info("\n🎉 Zero Trust Architecture Demo completed!")
        logger.info("=" * 60)
    
    async def _run_scenario(self, scenario: Dict[str, Any]):
        """Run a single demo scenario"""
        
        # Create access request
        access_request = AccessRequest(
            request_id=str(uuid.uuid4()),
            user=scenario['user'],
            device=scenario['device'],
            resource=scenario['resource'],
            action=scenario['action'],
            timestamp=datetime.now(),
            context=scenario['context']
        )
        
        logger.info(f"👤 User: {access_request.user.username} (roles: {access_request.user.roles})")
        logger.info(f"📱 Device: {access_request.device.device_type} (trust: {access_request.device.trust_level.value})")
        logger.info(f"🎯 Resource: {access_request.resource} ({access_request.action})")
        logger.info(f"🌍 Context: {access_request.context}")
        
        # Step 1: Device Trust Assessment
        trust_score = self.device_fingerprinter.calculate_trust_score(access_request.device)
        trust_level = self.device_fingerprinter.determine_trust_level(trust_score)
        logger.info(f"🔒 Device Trust Score: {trust_score:.2f} ({trust_level.value})")
        
        # Step 2: Risk Assessment
        risk_score = self.risk_engine.calculate_risk_score(access_request)
        risk_level = self.risk_engine.determine_risk_level(risk_score)
        logger.info(f"⚠️  Risk Score: {risk_score:.2f} ({risk_level.value})")
        
        # Step 3: Policy Evaluation
        policy_decision = self.policy_engine.evaluate_access(access_request, risk_level, trust_level)
        logger.info(f"📜 Policy: {policy_decision['policy_name']}")
        logger.info(f"✅ Decision: {policy_decision['decision'].upper()}")
        
        if policy_decision['requirements']:
            logger.info(f"📋 Requirements: {', '.join(policy_decision['requirements'])}")
        
        # Step 4: MFA if required
        if 'mfa_required' in policy_decision.get('requirements', []):
            logger.info("🔐 MFA Required - Initiating challenge...")
            challenge_id = self.identity_verifier.initiate_mfa(access_request.user)
            
            if challenge_id != "mfa_not_required":
                # Simulate MFA response
                mfa_success = self.identity_verifier.verify_mfa(challenge_id, "123456")
                logger.info(f"🔐 MFA Result: {'SUCCESS' if mfa_success else 'FAILED'}")
                
                if not mfa_success:
                    logger.info("❌ Access DENIED - MFA verification failed")
                    return
        
        # Step 5: Final decision
        if policy_decision['decision'] == 'allow':
            logger.info("✅ Access GRANTED")
        elif policy_decision['decision'] == 'conditional_allow':
            logger.info("⚠️  Access GRANTED with conditions")
        else:
            logger.info("❌ Access DENIED")
        
        # Step 6: Logging and monitoring
        self._log_access_attempt(access_request, policy_decision, risk_score, trust_score)
    
    def _log_access_attempt(self, access_request: AccessRequest, policy_decision: Dict[str, Any],
                           risk_score: float, trust_score: float):
        """Log access attempt for monitoring"""
        log_entry = {
            'timestamp': access_request.timestamp.isoformat(),
            'request_id': access_request.request_id,
            'user_id': access_request.user.user_id,
            'device_id': access_request.device.device_id,
            'resource': access_request.resource,
            'action': access_request.action,
            'risk_score': risk_score,
            'trust_score': trust_score,
            'policy': policy_decision['policy_name'],
            'decision': policy_decision['decision'],
            'context': access_request.context
        }
        
        logger.info(f"📊 Audit Log: {json.dumps(log_entry, indent=2)}")

async def main():
    """Main demo function"""
    demo = ZeroTrustDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
