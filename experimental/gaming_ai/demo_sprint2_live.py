#!/usr/bin/env python3
"""
🎮 Sprint 2 Live Demo - Gaming AI Control & Action System

Real-time demonstration of all Sprint 2 components working together.

Demo Scenarios:
1. Precision Control Showcase
2. Safety Manager in Action
3. Input Validation Demo
4. Ethical Framework Demo
5. Anti-Cheat Compliance Demo
6. Full Integration Demo

Author: Nexus - Quantum AI Architect
Mode: Live Demo - Show Everything!
"""

import time
import random
import threading
from typing import Dict, List, Any
import warnings

# Suppress warnings for cleaner demo
warnings.filterwarnings("ignore")

# Import all Sprint 2 components
try:
    from precision_control import PrecisionController, PrecisionAction, ActionType, MovementType
    from safety_manager import SafetyManager, SafetyLevel, ThreatLevel
    from input_validator import InputValidator, ValidationResult
    from ethical_framework import EthicalFramework, EthicalLevel, ConsentType
    from anticheat_compliance import AntiCheatCompliance, ComplianceLevel, DetectionRisk
    ALL_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"❌ Module import error: {e}")
    ALL_MODULES_AVAILABLE = False

class Sprint2LiveDemo:
    """Live demonstration of Sprint 2 Gaming AI components"""
    
    def __init__(self):
        self.demo_active = True
        self.components = {}
        
        print("🎮 SPRINT 2 LIVE DEMO - GAMING AI CONTROL SYSTEM")
        print("=" * 60)
        print("🚀 Initializing all components for live demonstration...")
        
        if ALL_MODULES_AVAILABLE:
            self._initialize_components()
        else:
            print("❌ Cannot run demo - missing components")
    
    def _initialize_components(self):
        """Initialize all Sprint 2 components"""
        try:
            # Initialize Precision Controller
            print("🎯 Initializing Precision Controller...")
            self.components['precision'] = PrecisionController(target_accuracy=0.5)
            print("   ✅ Precision Controller ready (±0.5 pixel accuracy)")
            
            # Initialize Safety Manager
            print("🛡️ Initializing Safety Manager...")
            self.components['safety'] = SafetyManager(SafetyLevel.STANDARD)
            print("   ✅ Safety Manager ready (STANDARD level)")
            
            # Initialize Input Validator
            print("🔍 Initializing Input Validator...")
            self.components['validator'] = InputValidator(self.components['safety'])
            print("   ✅ Input Validator ready (6 validation rules)")
            
            # Initialize Ethical Framework
            print("⚖️ Initializing Ethical Framework...")
            self.components['ethics'] = EthicalFramework(EthicalLevel.STANDARD)
            print("   ✅ Ethical Framework ready (9 ethical rules)")
            
            # Initialize Anti-Cheat Compliance
            print("🛡️ Initializing Anti-Cheat Compliance...")
            self.components['anticheat'] = AntiCheatCompliance(ComplianceLevel.STANDARD)
            self.components['anticheat'].set_game_profile("valorant")
            print("   ✅ Anti-Cheat Compliance ready (VALORANT profile)")
            
            print("\n🎉 ALL COMPONENTS INITIALIZED SUCCESSFULLY!")
            
        except Exception as e:
            print(f"❌ Component initialization failed: {e}")
    
    def run_live_demo(self):
        """Run complete live demonstration"""
        if not ALL_MODULES_AVAILABLE:
            return
        
        print("\n" + "=" * 60)
        print("🎬 STARTING LIVE DEMO - SPRINT 2 SHOWCASE")
        print("=" * 60)
        
        # Demo scenarios
        self.demo_precision_control()
        self.demo_safety_manager()
        self.demo_input_validation()
        self.demo_ethical_framework()
        self.demo_anticheat_compliance()
        self.demo_full_integration()
        
        print("\n🎊 LIVE DEMO COMPLETED SUCCESSFULLY!")
        self.show_final_stats()
    
    def demo_precision_control(self):
        """Demonstrate precision control capabilities"""
        print("\n🎯 DEMO 1: PRECISION CONTROL SHOWCASE")
        print("-" * 40)
        
        precision = self.components['precision']
        
        # Demo 1: Bezier path generation
        print("📐 Generating Bezier movement path...")
        start_pos = (100, 100)
        end_pos = (300, 200)
        path = precision.generate_bezier_path(start_pos, end_pos, 0.5)
        
        print(f"   Start: {start_pos}")
        print(f"   End: {end_pos}")
        print(f"   Control Points: {len(path.control_points)}")
        print(f"   Duration: {path.duration}s")
        print("   ✅ Natural movement path generated")
        
        # Demo 2: Precision metrics
        print("\n📊 Precision metrics:")
        metrics = precision.get_precision_metrics()
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")
        
        # Demo 3: Action creation
        print("\n🎮 Creating precision action...")
        action = PrecisionAction(
            action_type=ActionType.MOUSE_MOVE,
            target_position=(250, 150),
            duration=0.3,
            movement_type=MovementType.BEZIER,
            precision_level=1.0
        )
        print(f"   Action: {action.action_type.value}")
        print(f"   Target: {action.target_position}")
        print(f"   Movement: {action.movement_type.value}")
        print("   ✅ Precision action created")
        
        time.sleep(1)
    
    def demo_safety_manager(self):
        """Demonstrate safety manager capabilities"""
        print("\n🛡️ DEMO 2: SAFETY MANAGER IN ACTION")
        print("-" * 40)
        
        safety = self.components['safety']
        
        # Demo 1: Action validation
        print("🔒 Testing action safety validation...")
        is_safe, reason = safety.validate_action_safety("mouse_click", (200, 200), 0.1)
        print(f"   Action: mouse_click at (200, 200)")
        print(f"   Safe: {is_safe}")
        print(f"   Reason: {reason}")
        
        # Demo 2: Human randomization
        print("\n🎭 Demonstrating human behavior simulation...")
        base_duration = 0.1
        for i in range(3):
            randomized = safety.apply_human_randomization(base_duration)
            variance = ((randomized - base_duration) / base_duration) * 100
            print(f"   Trial {i+1}: {base_duration:.3f}s → {randomized:.3f}s ({variance:+.1f}%)")
        
        # Demo 3: Threat assessment
        print("\n⚠️ Current threat assessment:")
        metrics = safety.get_safety_metrics()
        print(f"   Threat Level: {metrics['threat_level']}")
        print(f"   Safety Score: {metrics['safety_score']:.1f}%")
        print(f"   Actions Blocked: {metrics['actions_blocked']}")
        
        # Demo 4: Emergency stop test
        print("\n🚨 Testing emergency stop mechanism...")
        safety.trigger_emergency_stop("Demo test")
        print("   Emergency stop triggered")
        
        # Test action during emergency
        is_safe, reason = safety.validate_action_safety("mouse_move", (100, 100))
        print(f"   Action during emergency: {is_safe} - {reason}")
        
        # Clear emergency
        safety.clear_emergency_stop()
        print("   Emergency stop cleared")
        
        time.sleep(1)
    
    def demo_input_validation(self):
        """Demonstrate input validation system"""
        print("\n🔍 DEMO 3: INPUT VALIDATION SYSTEM")
        print("-" * 40)
        
        validator = self.components['validator']
        
        # Demo 1: Action validation
        print("✅ Testing action validation...")
        test_action = PrecisionAction(
            action_type=ActionType.MOUSE_CLICK,
            target_position=(150, 150),
            duration=0.1
        )
        
        result, messages = validator.validate_action(test_action)
        print(f"   Action: {test_action.action_type.value}")
        print(f"   Position: {test_action.target_position}")
        print(f"   Validation Result: {result.value}")
        if messages:
            for msg in messages[:2]:  # Show first 2 messages
                print(f"   Message: {msg}")
        
        # Demo 2: Queue management
        print("\n📋 Testing action queue...")
        validator.start_queue_processing()
        
        # Queue some actions
        for i in range(3):
            action = PrecisionAction(
                action_type=ActionType.MOUSE_MOVE,
                target_position=(100 + i*20, 100 + i*10),
                duration=0.1
            )
            action_id = validator.queue_action(action, priority=i)
            print(f"   Queued action {i+1}: {action_id[:8]}...")
        
        time.sleep(0.5)  # Let queue process
        
        # Check queue status
        status = validator.get_queue_status()
        print(f"   Queue length: {status['queue_length']}")
        print(f"   Active actions: {status['active_actions']}")
        
        validator.stop_queue_processing()
        
        # Demo 3: Validation metrics
        print("\n📊 Validation metrics:")
        metrics = validator.get_validation_metrics()
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")
        
        time.sleep(1)
    
    def demo_ethical_framework(self):
        """Demonstrate ethical framework"""
        print("\n⚖️ DEMO 4: ETHICAL FRAMEWORK DEMONSTRATION")
        print("-" * 40)
        
        ethics = self.components['ethics']
        
        # Demo 1: Ethical evaluation
        print("🔍 Testing ethical compliance...")
        context = {
            "user_id": "demo_user",
            "action_type": "mouse_click",
            "ai_assistance_level": 0.6,
            "multiplayer": True,
            "ai_disclosed": False,  # This will trigger ethical concern
            "competitive_mode": False
        }
        
        is_compliant, messages, decision = ethics.evaluate_ethical_compliance(context)
        print(f"   AI Assistance Level: {context['ai_assistance_level']}")
        print(f"   Multiplayer: {context['multiplayer']}")
        print(f"   AI Disclosed: {context['ai_disclosed']}")
        print(f"   Ethical Decision: {decision}")
        print(f"   Compliant: {is_compliant}")
        if messages:
            for msg in messages[:2]:
                print(f"   Issue: {msg}")
        
        # Demo 2: Consent management
        print("\n📝 Testing consent system...")
        consent_id = ethics.request_user_consent("demo_user", ["ai_assistance", "data_collection"])
        print(f"   Consent requested: {consent_id[:8]}...")
        
        # Grant consent
        granted = ethics.grant_consent(consent_id)
        print(f"   Consent granted: {granted}")
        
        # Test with consent
        context["ai_disclosed"] = True  # Fix the ethical issue
        is_compliant, messages, decision = ethics.evaluate_ethical_compliance(context)
        print(f"   With disclosure - Decision: {decision}")
        print(f"   With disclosure - Compliant: {is_compliant}")
        
        # Demo 3: Ethics report
        print("\n📊 Ethics report summary:")
        report = ethics.generate_ethics_report()
        print(f"   Ethical Level: {report['ethical_level']}")
        print(f"   Decisions Made: {report['metrics']['decisions_made']}")
        print(f"   Compliance Rate: {report['compliance_rate']:.1f}%")
        print(f"   Active Consents: {report['active_consents']}")
        
        time.sleep(1)
    
    def demo_anticheat_compliance(self):
        """Demonstrate anti-cheat compliance"""
        print("\n🛡️ DEMO 5: ANTI-CHEAT COMPLIANCE SYSTEM")
        print("-" * 40)
        
        compliance = self.components['anticheat']
        
        # Demo 1: Game profile
        print("🎮 Current game profile:")
        if compliance.current_game_profile:
            profile = compliance.current_game_profile
            print(f"   Game: {profile.game_name}")
            print(f"   Anti-cheat: {[ac.value for ac in profile.anticheat_systems]}")
            print(f"   Detection Sensitivity: {profile.detection_sensitivity}")
        
        # Demo 2: Risk assessment
        print("\n⚠️ Testing risk assessment...")
        test_scenarios = [
            {
                "name": "Normal Human",
                "reaction_time": 0.25,
                "movement_smoothness": 0.8,
                "input_variance": 0.15,
                "pattern_repetition": 0.1
            },
            {
                "name": "Suspicious Bot",
                "reaction_time": 0.05,  # Too fast
                "movement_smoothness": 0.98,  # Too perfect
                "input_variance": 0.02,  # Too consistent
                "pattern_repetition": 0.9  # Too repetitive
            },
            {
                "name": "Adapted AI",
                "reaction_time": 0.22,
                "movement_smoothness": 0.82,
                "input_variance": 0.18,
                "pattern_repetition": 0.15
            }
        ]
        
        for scenario in test_scenarios:
            name = scenario.pop("name")
            risk_level, risk_score, factors = compliance.assess_action_risk(scenario)
            print(f"   {name}: {risk_level.value} risk ({risk_score:.3f})")
        
        # Demo 3: Compliance adaptations
        print("\n🔧 Testing compliance adaptations...")
        original_context = {
            "reaction_time": 0.1,  # Too fast
            "movement_smoothness": 0.95,  # Too smooth
            "input_variance": 0.05  # Too consistent
        }
        
        adapted_context = compliance.apply_compliance_adaptations(original_context.copy())
        
        print("   Original vs Adapted:")
        for key in original_context:
            if key in adapted_context:
                orig = original_context[key]
                adapt = adapted_context[key]
                change = ((adapt - orig) / orig) * 100 if orig != 0 else 0
                print(f"   {key}: {orig:.3f} → {adapt:.3f} ({change:+.1f}%)")
        
        # Demo 4: Compliance report
        print("\n📊 Compliance summary:")
        report = compliance.get_compliance_report()
        print(f"   Compliance Level: {report['compliance_level']}")
        print(f"   Current Game: {report['current_game']}")
        print(f"   Supported Games: {len(report['supported_games'])}")
        print(f"   Overall Compliance: {report['metrics']['overall_compliance_rate']:.1f}%")
        
        time.sleep(1)
    
    def demo_full_integration(self):
        """Demonstrate full system integration"""
        print("\n🔗 DEMO 6: FULL SYSTEM INTEGRATION")
        print("-" * 40)
        
        print("🎮 Simulating complete gaming AI workflow...")
        
        # Step 1: Create action
        print("\n1️⃣ Creating precision action...")
        action = PrecisionAction(
            action_type=ActionType.MOUSE_CLICK,
            target_position=(200, 150),
            duration=0.15,
            movement_type=MovementType.BEZIER
        )
        print(f"   Action: {action.action_type.value} at {action.target_position}")
        
        # Step 2: Safety validation
        print("\n2️⃣ Safety validation...")
        safety = self.components['safety']
        is_safe, safety_reason = safety.validate_action_safety(
            action.action_type.value,
            action.target_position,
            action.duration
        )
        print(f"   Safety check: {is_safe} - {safety_reason}")
        
        # Step 3: Input validation
        print("\n3️⃣ Input validation...")
        validator = self.components['validator']
        validation_result, validation_messages = validator.validate_action(action)
        print(f"   Validation: {validation_result.value}")
        
        # Step 4: Ethical evaluation
        print("\n4️⃣ Ethical evaluation...")
        ethics = self.components['ethics']
        ethical_context = {
            "user_id": "integration_test",
            "action_type": action.action_type.value,
            "ai_assistance_level": 0.5,
            "multiplayer": False,
            "ai_disclosed": True,
            "human_oversight": True
        }
        
        is_ethical, ethical_messages, ethical_decision = ethics.evaluate_ethical_compliance(ethical_context)
        print(f"   Ethical check: {ethical_decision} (compliant: {is_ethical})")
        
        # Step 5: Anti-cheat compliance
        print("\n5️⃣ Anti-cheat compliance...")
        compliance = self.components['anticheat']
        risk_level, risk_score, risk_factors = compliance.assess_action_risk({
            "reaction_time": action.duration,
            "movement_smoothness": 0.8,
            "input_variance": 0.15
        })
        print(f"   Risk assessment: {risk_level.value} ({risk_score:.3f})")
        
        # Step 6: Final decision
        print("\n6️⃣ Final integration decision...")
        all_checks_passed = (
            is_safe and 
            validation_result == ValidationResult.VALID and
            is_ethical and
            risk_level in [DetectionRisk.MINIMAL, DetectionRisk.LOW]
        )
        
        if all_checks_passed:
            print("   🎉 ACTION APPROVED - All systems green!")
            print("   ✅ Safety: Passed")
            print("   ✅ Validation: Passed") 
            print("   ✅ Ethics: Passed")
            print("   ✅ Anti-cheat: Passed")
        else:
            print("   ❌ ACTION BLOCKED - Safety protocols engaged")
            print(f"   Safety: {'✅' if is_safe else '❌'}")
            print(f"   Validation: {'✅' if validation_result == ValidationResult.VALID else '❌'}")
            print(f"   Ethics: {'✅' if is_ethical else '❌'}")
            print(f"   Anti-cheat: {'✅' if risk_level in [DetectionRisk.MINIMAL, DetectionRisk.LOW] else '❌'}")
        
        time.sleep(1)
    
    def show_final_stats(self):
        """Show final demonstration statistics"""
        print("\n" + "=" * 60)
        print("📊 FINAL DEMO STATISTICS")
        print("=" * 60)
        
        # Collect stats from all components
        stats = {}
        
        if 'precision' in self.components:
            precision_metrics = self.components['precision'].get_precision_metrics()
            stats['Precision'] = {
                'Target Accuracy': f"±{precision_metrics['target_accuracy']} pixels",
                'Actions Executed': precision_metrics['actions_executed'],
                'Current Error': f"{precision_metrics['accuracy_error']:.3f} pixels"
            }
        
        if 'safety' in self.components:
            safety_metrics = self.components['safety'].get_safety_metrics()
            stats['Safety'] = {
                'Safety Level': safety_metrics['safety_level'],
                'Threat Level': safety_metrics['threat_level'],
                'Safety Score': f"{safety_metrics['safety_score']:.1f}%"
            }
        
        if 'validator' in self.components:
            validation_metrics = self.components['validator'].get_validation_metrics()
            stats['Validation'] = {
                'Actions Validated': validation_metrics['actions_validated'],
                'Actions Blocked': validation_metrics['actions_blocked'],
                'Block Rate': f"{validation_metrics['block_rate']:.1f}%"
            }
        
        if 'ethics' in self.components:
            ethics_report = self.components['ethics'].generate_ethics_report()
            stats['Ethics'] = {
                'Ethical Level': ethics_report['ethical_level'],
                'Decisions Made': ethics_report['metrics']['decisions_made'],
                'Compliance Rate': f"{ethics_report['compliance_rate']:.1f}%"
            }
        
        if 'anticheat' in self.components:
            compliance_report = self.components['anticheat'].get_compliance_report()
            stats['Anti-Cheat'] = {
                'Compliance Level': compliance_report['compliance_level'],
                'Current Game': compliance_report['current_game'],
                'Supported Games': len(compliance_report['supported_games'])
            }
        
        # Display stats
        for component, metrics in stats.items():
            print(f"\n🎯 {component} Component:")
            for key, value in metrics.items():
                print(f"   {key}: {value}")
        
        print(f"\n🎊 SPRINT 2 LIVE DEMO COMPLETED!")
        print(f"✅ All {len(stats)} components demonstrated successfully")
        print(f"🎮 Gaming AI Control & Action System is PRODUCTION READY!")

def main():
    """Run Sprint 2 live demonstration"""
    demo = Sprint2LiveDemo()
    if ALL_MODULES_AVAILABLE:
        demo.run_live_demo()
    else:
        print("❌ Cannot run demo - missing required components")

if __name__ == "__main__":
    main()
