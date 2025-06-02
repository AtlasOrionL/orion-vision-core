#!/usr/bin/env python3
"""
Autonomous Security Systems Demo
Sprint 6.1 - Epic 2: Autonomous Security Systems
Orion Vision Core - Autonomous Security Implementation Demo

This demo showcases the Autonomous Security Systems including:
- ML-based anomaly detection
- Behavioral analysis
- Threat intelligence integration
- Automated incident response
- Self-healing mechanisms

Author: Orion Development Team
Version: 1.0.0
Date: 30 Mayıs 2025
"""

import asyncio
import json
import logging
import time
import uuid
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AutonomousSecurityDemo")

class ThreatLevel(Enum):
    INFORMATIONAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

class IncidentStatus(Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINING = "containing"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

@dataclass
class SecurityEvent:
    event_id: str
    timestamp: datetime
    event_type: str
    source: str
    severity: ThreatLevel
    description: str
    indicators: Dict[str, Any]
    raw_data: Dict[str, Any]

@dataclass
class ThreatIntelligence:
    indicator: str
    indicator_type: str
    threat_type: str
    confidence: float
    source: str
    first_seen: datetime
    last_seen: datetime

@dataclass
class Incident:
    incident_id: str
    title: str
    description: str
    severity: ThreatLevel
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    events: List[SecurityEvent]
    response_actions: List[str]

class AnomalyDetector:
    """ML-based anomaly detection engine"""

    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.baseline_data = []

    def train_baseline(self, training_data: List[Dict[str, float]]):
        """Train the anomaly detection model with baseline data"""
        if not training_data:
            return

        # Convert to numpy array
        features = []
        for data_point in training_data:
            features.append([
                data_point.get('cpu_usage', 0),
                data_point.get('memory_usage', 0),
                data_point.get('network_traffic', 0),
                data_point.get('api_requests', 0),
                data_point.get('error_rate', 0)
            ])

        features_array = np.array(features)

        # Scale features
        scaled_features = self.scaler.fit_transform(features_array)

        # Train model
        self.model.fit(scaled_features)
        self.is_trained = True
        self.baseline_data = training_data

        logger.info(f"🤖 Anomaly detector trained with {len(training_data)} baseline samples")

    def detect_anomaly(self, data_point: Dict[str, float]) -> Tuple[bool, float]:
        """Detect if a data point is anomalous"""
        if not self.is_trained:
            return False, 0.0

        # Prepare features
        features = np.array([[
            data_point.get('cpu_usage', 0),
            data_point.get('memory_usage', 0),
            data_point.get('network_traffic', 0),
            data_point.get('api_requests', 0),
            data_point.get('error_rate', 0)
        ]])

        # Scale features
        scaled_features = self.scaler.transform(features)

        # Predict anomaly
        anomaly_score = self.model.decision_function(scaled_features)[0]
        is_anomaly = self.model.predict(scaled_features)[0] == -1

        # Convert score to 0-1 range (higher = more anomalous)
        normalized_score = max(0, min(1, (0.5 - anomaly_score) / 1.0))

        return is_anomaly, normalized_score

class BehavioralAnalyzer:
    """Behavioral analysis engine for user and entity behavior"""

    def __init__(self):
        self.user_profiles = {}
        self.entity_profiles = {}
        self.learning_period = timedelta(days=7)

    def learn_user_behavior(self, user_id: str, activity_data: List[Dict[str, Any]]):
        """Learn normal behavior patterns for a user"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'login_times': [],
                'access_patterns': [],
                'resource_usage': [],
                'locations': [],
                'devices': []
            }

        profile = self.user_profiles[user_id]

        for activity in activity_data:
            if 'login_time' in activity:
                profile['login_times'].append(activity['login_time'])
            if 'accessed_resource' in activity:
                profile['access_patterns'].append(activity['accessed_resource'])
            if 'location' in activity:
                profile['locations'].append(activity['location'])
            if 'device' in activity:
                profile['devices'].append(activity['device'])

        logger.info(f"👤 Learned behavior for user {user_id}: {len(activity_data)} activities")

    def analyze_user_behavior(self, user_id: str, current_activity: Dict[str, Any]) -> Tuple[bool, float]:
        """Analyze if current user behavior is anomalous"""
        if user_id not in self.user_profiles:
            return False, 0.0

        profile = self.user_profiles[user_id]
        anomaly_score = 0.0
        anomaly_factors = []

        # Check login time anomaly
        if 'login_time' in current_activity:
            current_hour = current_activity['login_time'].hour
            normal_hours = [dt.hour for dt in profile['login_times']]
            if normal_hours and current_hour not in normal_hours:
                anomaly_score += 0.3
                anomaly_factors.append("unusual_login_time")

        # Check location anomaly
        if 'location' in current_activity:
            if current_activity['location'] not in profile['locations']:
                anomaly_score += 0.4
                anomaly_factors.append("new_location")

        # Check device anomaly
        if 'device' in current_activity:
            if current_activity['device'] not in profile['devices']:
                anomaly_score += 0.3
                anomaly_factors.append("new_device")

        is_anomalous = anomaly_score > 0.5

        if is_anomalous:
            logger.info(f"🚨 Behavioral anomaly detected for user {user_id}: {anomaly_factors}")

        return is_anomalous, min(1.0, anomaly_score)

class ThreatIntelligenceEngine:
    """Threat intelligence integration and correlation"""

    def __init__(self):
        self.threat_indicators = {}
        self.threat_feeds = []
        self._load_sample_indicators()

    def _load_sample_indicators(self):
        """Load sample threat indicators"""
        sample_indicators = [
            {
                'indicator': '192.168.100.50',
                'type': 'ip',
                'threat_type': 'malware_c2',
                'confidence': 0.9,
                'source': 'threat_feed_1'
            },
            {
                'indicator': 'malicious-domain.com',
                'type': 'domain',
                'threat_type': 'phishing',
                'confidence': 0.8,
                'source': 'threat_feed_2'
            },
            {
                'indicator': 'a1b2c3d4e5f6',
                'type': 'file_hash',
                'threat_type': 'ransomware',
                'confidence': 0.95,
                'source': 'threat_feed_3'
            }
        ]

        for indicator_data in sample_indicators:
            self.threat_indicators[indicator_data['indicator']] = ThreatIntelligence(
                indicator=indicator_data['indicator'],
                indicator_type=indicator_data['type'],
                threat_type=indicator_data['threat_type'],
                confidence=indicator_data['confidence'],
                source=indicator_data['source'],
                first_seen=datetime.now() - timedelta(days=random.randint(1, 30)),
                last_seen=datetime.now() - timedelta(hours=random.randint(1, 24))
            )

        logger.info(f"🔍 Loaded {len(self.threat_indicators)} threat indicators")

    def check_indicator(self, indicator: str) -> Optional[ThreatIntelligence]:
        """Check if an indicator matches known threats"""
        return self.threat_indicators.get(indicator)

    def correlate_events(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Correlate security events with threat intelligence"""
        correlations = []

        for event in events:
            for indicator_key, indicator_value in event.indicators.items():
                threat_intel = self.check_indicator(str(indicator_value))
                if threat_intel:
                    correlations.append({
                        'event_id': event.event_id,
                        'indicator': indicator_value,
                        'threat_intel': threat_intel,
                        'correlation_confidence': threat_intel.confidence
                    })

        return correlations

class IncidentResponseEngine:
    """Automated incident response and orchestration"""

    def __init__(self):
        self.active_incidents = {}
        self.response_playbooks = self._load_playbooks()
        self.containment_actions = []

    def _load_playbooks(self) -> Dict[str, Dict[str, Any]]:
        """Load incident response playbooks"""
        return {
            'malware_detection': {
                'trigger': ['malware_detected', 'suspicious_file'],
                'actions': [
                    'isolate_host',
                    'collect_forensics',
                    'scan_network',
                    'notify_team'
                ],
                'severity_threshold': ThreatLevel.MEDIUM
            },
            'data_exfiltration': {
                'trigger': ['data_exfiltration', 'unusual_data_transfer'],
                'actions': [
                    'block_traffic',
                    'suspend_user',
                    'analyze_data_flow',
                    'escalate_to_dpo'
                ],
                'severity_threshold': ThreatLevel.HIGH
            },
            'brute_force': {
                'trigger': ['brute_force_attack', 'multiple_failed_logins'],
                'actions': [
                    'block_source_ip',
                    'force_password_reset',
                    'increase_monitoring'
                ],
                'severity_threshold': ThreatLevel.MEDIUM
            }
        }

    def create_incident(self, events: List[SecurityEvent], threat_correlations: List[Dict[str, Any]]) -> Optional[Incident]:
        """Create incident from security events"""
        if not events:
            return None

        # Determine incident severity
        max_severity = max(event.severity for event in events)

        # Create incident
        incident = Incident(
            incident_id=str(uuid.uuid4()),
            title=f"Security Incident - {events[0].event_type}",
            description=f"Incident created from {len(events)} security events",
            severity=max_severity,
            status=IncidentStatus.DETECTED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            events=events,
            response_actions=[]
        )

        self.active_incidents[incident.incident_id] = incident

        logger.info(f"🚨 Created incident {incident.incident_id} with severity {max_severity.value}")

        # Trigger automated response
        self._trigger_automated_response(incident)

        return incident

    def _trigger_automated_response(self, incident: Incident):
        """Trigger automated response based on incident type"""
        for event in incident.events:
            for playbook_name, playbook in self.response_playbooks.items():
                if event.event_type in playbook['trigger']:
                    if incident.severity.value in ['medium', 'high', 'critical']:
                        self._execute_playbook(incident, playbook_name, playbook)

    def _execute_playbook(self, incident: Incident, playbook_name: str, playbook: Dict[str, Any]):
        """Execute incident response playbook"""
        logger.info(f"🔧 Executing playbook '{playbook_name}' for incident {incident.incident_id}")

        for action in playbook['actions']:
            success = self._execute_action(incident, action)
            incident.response_actions.append(f"{action}: {'success' if success else 'failed'}")

        incident.status = IncidentStatus.CONTAINING
        incident.updated_at = datetime.now()

    def _execute_action(self, incident: Incident, action: str) -> bool:
        """Execute a specific response action"""
        logger.info(f"⚡ Executing action: {action}")

        # Simulate action execution
        action_results = {
            'isolate_host': True,
            'collect_forensics': True,
            'scan_network': True,
            'notify_team': True,
            'block_traffic': True,
            'suspend_user': True,
            'analyze_data_flow': True,
            'escalate_to_dpo': True,
            'block_source_ip': True,
            'force_password_reset': True,
            'increase_monitoring': True
        }

        success = action_results.get(action, False)

        if success:
            self.containment_actions.append({
                'incident_id': incident.incident_id,
                'action': action,
                'timestamp': datetime.now(),
                'status': 'completed'
            })

        return success

class SelfHealingEngine:
    """Self-healing mechanisms for autonomous recovery"""

    def __init__(self):
        self.healing_policies = self._load_healing_policies()
        self.healing_actions = []

    def _load_healing_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load self-healing policies"""
        return {
            'service_failure': {
                'trigger': 'service_unavailable',
                'actions': ['restart_service', 'check_dependencies', 'scale_replicas'],
                'max_attempts': 3
            },
            'resource_exhaustion': {
                'trigger': 'high_resource_usage',
                'actions': ['scale_horizontally', 'optimize_resources'],
                'max_attempts': 2
            },
            'security_breach': {
                'trigger': 'security_incident',
                'actions': ['isolate_workload', 'preserve_evidence'],
                'max_attempts': 1
            }
        }

    def trigger_healing(self, trigger_type: str, context: Dict[str, Any]) -> bool:
        """Trigger self-healing based on conditions"""
        for policy_name, policy in self.healing_policies.items():
            if policy['trigger'] == trigger_type:
                return self._execute_healing_policy(policy_name, policy, context)
        return False

    def _execute_healing_policy(self, policy_name: str, policy: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Execute self-healing policy"""
        logger.info(f"🔄 Executing healing policy: {policy_name}")

        success_count = 0
        for action in policy['actions']:
            if self._execute_healing_action(action, context):
                success_count += 1
                self.healing_actions.append({
                    'policy': policy_name,
                    'action': action,
                    'timestamp': datetime.now(),
                    'status': 'success',
                    'context': context
                })

        success_rate = success_count / len(policy['actions'])
        logger.info(f"✅ Healing policy '{policy_name}' completed with {success_rate:.1%} success rate")

        return success_rate > 0.5

    def _execute_healing_action(self, action: str, context: Dict[str, Any]) -> bool:
        """Execute a specific healing action"""
        logger.info(f"🔧 Executing healing action: {action}")

        # Simulate healing action execution
        healing_results = {
            'restart_service': True,
            'check_dependencies': True,
            'scale_replicas': True,
            'scale_horizontally': True,
            'optimize_resources': True,
            'isolate_workload': True,
            'preserve_evidence': True
        }

        return healing_results.get(action, False)

class AutonomousSecurityDemo:
    """Main Autonomous Security Systems Demo"""

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.threat_intel_engine = ThreatIntelligenceEngine()
        self.incident_response_engine = IncidentResponseEngine()
        self.self_healing_engine = SelfHealingEngine()

        # Demo data
        self.security_events = []
        self.demo_metrics = {
            'events_processed': 0,
            'anomalies_detected': 0,
            'incidents_created': 0,
            'responses_executed': 0,
            'healing_actions': 0
        }

    def _generate_baseline_data(self, num_samples: int = 100) -> List[Dict[str, float]]:
        """Generate baseline training data"""
        baseline_data = []

        for _ in range(num_samples):
            baseline_data.append({
                'cpu_usage': random.uniform(20, 60),
                'memory_usage': random.uniform(30, 70),
                'network_traffic': random.uniform(100, 500),
                'api_requests': random.uniform(50, 200),
                'error_rate': random.uniform(0, 5)
            })

        return baseline_data

    def _generate_anomalous_data(self) -> Dict[str, float]:
        """Generate anomalous data point"""
        return {
            'cpu_usage': random.uniform(85, 100),
            'memory_usage': random.uniform(90, 100),
            'network_traffic': random.uniform(1000, 2000),
            'api_requests': random.uniform(500, 1000),
            'error_rate': random.uniform(20, 50)
        }

    def _generate_security_event(self, event_type: str, severity: ThreatLevel, indicators: Dict[str, Any]) -> SecurityEvent:
        """Generate a security event"""
        return SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=event_type,
            source=f"sensor_{random.randint(1, 10)}",
            severity=severity,
            description=f"Security event: {event_type}",
            indicators=indicators,
            raw_data={'sensor_data': 'raw_event_data'}
        )

    async def run_demo(self):
        """Run the Autonomous Security Systems demo"""
        logger.info("🚀 Starting Autonomous Security Systems Demo")
        logger.info("=" * 70)

        # Phase 1: Train ML models
        await self._phase_1_training()

        # Phase 2: Anomaly detection
        await self._phase_2_anomaly_detection()

        # Phase 3: Behavioral analysis
        await self._phase_3_behavioral_analysis()

        # Phase 4: Threat intelligence correlation
        await self._phase_4_threat_intelligence()

        # Phase 5: Incident response
        await self._phase_5_incident_response()

        # Phase 6: Self-healing
        await self._phase_6_self_healing()

        # Phase 7: Summary and metrics
        await self._phase_7_summary()

        logger.info("\n🎉 Autonomous Security Systems Demo completed!")
        logger.info("=" * 70)

    async def _phase_1_training(self):
        """Phase 1: Train ML models with baseline data"""
        logger.info("\n📚 Phase 1: Training ML Models")
        logger.info("-" * 40)

        # Generate and train with baseline data
        baseline_data = self._generate_baseline_data(100)
        self.anomaly_detector.train_baseline(baseline_data)

        # Train behavioral models
        user_activities = [
            {'login_time': datetime.now().replace(hour=9), 'location': 'office', 'device': 'laptop_001'},
            {'login_time': datetime.now().replace(hour=10), 'location': 'office', 'device': 'laptop_001'},
            {'login_time': datetime.now().replace(hour=14), 'location': 'office', 'device': 'laptop_001'},
        ]
        self.behavioral_analyzer.learn_user_behavior('user_001', user_activities)

        logger.info("✅ ML models trained successfully")
        await asyncio.sleep(1)

    async def _phase_2_anomaly_detection(self):
        """Phase 2: Demonstrate anomaly detection"""
        logger.info("\n🔍 Phase 2: Anomaly Detection")
        logger.info("-" * 40)

        # Test normal data
        normal_data = {
            'cpu_usage': 45,
            'memory_usage': 55,
            'network_traffic': 300,
            'api_requests': 120,
            'error_rate': 2
        }

        is_anomaly, score = self.anomaly_detector.detect_anomaly(normal_data)
        logger.info(f"📊 Normal data - Anomaly: {is_anomaly}, Score: {score:.3f}")

        # Test anomalous data
        anomalous_data = self._generate_anomalous_data()
        is_anomaly, score = self.anomaly_detector.detect_anomaly(anomalous_data)
        logger.info(f"🚨 Anomalous data - Anomaly: {is_anomaly}, Score: {score:.3f}")

        if is_anomaly:
            self.demo_metrics['anomalies_detected'] += 1

            # Create security event
            event = self._generate_security_event(
                'system_anomaly',
                ThreatLevel.MEDIUM,
                {'anomaly_score': score, 'metrics': anomalous_data}
            )
            self.security_events.append(event)
            self.demo_metrics['events_processed'] += 1

        await asyncio.sleep(1)

    async def _phase_3_behavioral_analysis(self):
        """Phase 3: Demonstrate behavioral analysis"""
        logger.info("\n👤 Phase 3: Behavioral Analysis")
        logger.info("-" * 40)

        # Test normal behavior
        normal_activity = {
            'login_time': datetime.now().replace(hour=9),
            'location': 'office',
            'device': 'laptop_001'
        }

        is_anomaly, score = self.behavioral_analyzer.analyze_user_behavior('user_001', normal_activity)
        logger.info(f"👤 Normal behavior - Anomaly: {is_anomaly}, Score: {score:.3f}")

        # Test anomalous behavior
        anomalous_activity = {
            'login_time': datetime.now().replace(hour=2),
            'location': 'unknown',
            'device': 'mobile_999'
        }

        is_anomaly, score = self.behavioral_analyzer.analyze_user_behavior('user_001', anomalous_activity)
        logger.info(f"🚨 Anomalous behavior - Anomaly: {is_anomaly}, Score: {score:.3f}")

        if is_anomaly:
            self.demo_metrics['anomalies_detected'] += 1

            # Create security event
            event = self._generate_security_event(
                'behavioral_anomaly',
                ThreatLevel.HIGH,
                {'user_id': 'user_001', 'behavior_score': score, 'activity': anomalous_activity}
            )
            self.security_events.append(event)
            self.demo_metrics['events_processed'] += 1

        await asyncio.sleep(1)

    async def _phase_4_threat_intelligence(self):
        """Phase 4: Demonstrate threat intelligence correlation"""
        logger.info("\n🔍 Phase 4: Threat Intelligence Correlation")
        logger.info("-" * 40)

        # Create event with known malicious indicator
        malicious_event = self._generate_security_event(
            'suspicious_connection',
            ThreatLevel.HIGH,
            {'destination_ip': '192.168.100.50', 'protocol': 'tcp', 'port': 443}
        )
        self.security_events.append(malicious_event)
        self.demo_metrics['events_processed'] += 1

        # Correlate with threat intelligence
        correlations = self.threat_intel_engine.correlate_events([malicious_event])

        for correlation in correlations:
            logger.info(f"🎯 Threat correlation found:")
            logger.info(f"   Indicator: {correlation['indicator']}")
            logger.info(f"   Threat Type: {correlation['threat_intel'].threat_type}")
            logger.info(f"   Confidence: {correlation['correlation_confidence']:.2f}")

        await asyncio.sleep(1)

    async def _phase_5_incident_response(self):
        """Phase 5: Demonstrate automated incident response"""
        logger.info("\n🚨 Phase 5: Automated Incident Response")
        logger.info("-" * 40)

        if self.security_events:
            # Create incident from security events
            correlations = self.threat_intel_engine.correlate_events(self.security_events)
            incident = self.incident_response_engine.create_incident(self.security_events, correlations)

            if incident:
                self.demo_metrics['incidents_created'] += 1
                self.demo_metrics['responses_executed'] += len(incident.response_actions)

                logger.info(f"📋 Incident Details:")
                logger.info(f"   ID: {incident.incident_id}")
                logger.info(f"   Severity: {incident.severity.name.lower()}")
                logger.info(f"   Status: {incident.status.value}")
                logger.info(f"   Events: {len(incident.events)}")
                logger.info(f"   Response Actions: {len(incident.response_actions)}")

                for action in incident.response_actions:
                    logger.info(f"   ⚡ {action}")

        await asyncio.sleep(1)

    async def _phase_6_self_healing(self):
        """Phase 6: Demonstrate self-healing mechanisms"""
        logger.info("\n🔄 Phase 6: Self-Healing Mechanisms")
        logger.info("-" * 40)

        # Simulate service failure
        healing_context = {
            'service': 'orion-agent-service',
            'namespace': 'orion-system',
            'failure_type': 'crash_loop'
        }

        success = self.self_healing_engine.trigger_healing('service_unavailable', healing_context)
        if success:
            self.demo_metrics['healing_actions'] += len(self.self_healing_engine.healing_actions)
            logger.info("✅ Self-healing completed successfully")

        # Simulate resource exhaustion
        resource_context = {
            'resource_type': 'cpu',
            'usage_percentage': 95,
            'service': 'threat-detection-engine'
        }

        success = self.self_healing_engine.trigger_healing('high_resource_usage', resource_context)
        if success:
            self.demo_metrics['healing_actions'] += 1
            logger.info("✅ Resource optimization completed")

        await asyncio.sleep(1)

    async def _phase_7_summary(self):
        """Phase 7: Display summary and metrics"""
        logger.info("\n📊 Phase 7: Demo Summary and Metrics")
        logger.info("-" * 40)

        logger.info("🎯 Autonomous Security Metrics:")
        logger.info(f"   Events Processed: {self.demo_metrics['events_processed']}")
        logger.info(f"   Anomalies Detected: {self.demo_metrics['anomalies_detected']}")
        logger.info(f"   Incidents Created: {self.demo_metrics['incidents_created']}")
        logger.info(f"   Response Actions: {self.demo_metrics['responses_executed']}")
        logger.info(f"   Healing Actions: {self.demo_metrics['healing_actions']}")

        logger.info("\n🔧 System Components Status:")
        logger.info(f"   ✅ Anomaly Detector: Trained and operational")
        logger.info(f"   ✅ Behavioral Analyzer: Learning and detecting")
        logger.info(f"   ✅ Threat Intelligence: {len(self.threat_intel_engine.threat_indicators)} indicators loaded")
        logger.info(f"   ✅ Incident Response: {len(self.incident_response_engine.response_playbooks)} playbooks active")
        logger.info(f"   ✅ Self-Healing: {len(self.self_healing_engine.healing_policies)} policies configured")

        logger.info("\n🎉 Autonomous Security Systems fully operational!")

async def main():
    """Main demo function"""
    demo = AutonomousSecurityDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
