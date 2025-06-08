#!/usr/bin/env python3
"""
🎯 Q03.3 - Final Integration: Complete Q03 System
💖 DUYGULANDIK! Q03 FINAL ENTEGRASYON!

ORION Q03 COMPLETE SYSTEM:
- Task Decomposition + Contextual Understanding
- Task Flow Management + Action Verification  
- Error Recovery + Final Integration
- End-to-end command execution pipeline

Author: Orion Vision Core Team
Status: 🎯 Q03 FINAL INTEGRATION
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# All Q03 components
try:
    from q03_task_decomposition import DeliAdamTaskDecomposer
    from q03_contextual_understanding import DeliAdamContextualAnalyzer
    from q03_task_flow_manager import AutomaticTaskFlowManager
    from q03_action_verification import ActionSuccessVerifier
    from q03_error_recovery import ZBozonErrorRecovery
    print("✅ All Q03 components imported for final integration")
except ImportError as e:
    print(f"❌ Q03 final integration import error: {e}")
    exit(1)

class Q03CompleteSystem:
    """🎯 Q03 Tam Entegre Sistem"""
    
    def __init__(self):
        self.logger = logging.getLogger('q03.complete_system')
        
        # Initialize all Q03 components
        self.task_decomposer = DeliAdamTaskDecomposer()
        self.contextual_analyzer = DeliAdamContextualAnalyzer()
        self.task_flow_manager = AutomaticTaskFlowManager()
        self.action_verifier = ActionSuccessVerifier()
        self.error_recovery = ZBozonErrorRecovery()
        
        # System statistics
        self.system_stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'average_execution_time': 0.0,
            'recovery_usage_rate': 0.0
        }
        
        self.execution_history = []
        self.initialized = False
        
        self.logger.info("🎯 Q03 Complete System initialized")
    
    def initialize_complete_system(self) -> bool:
        """Initialize complete Q03 system"""
        try:
            self.logger.info("🚀 Initializing Q03 Complete System...")
            
            # Initialize all components
            components = [
                ("Task Decomposer", self.task_decomposer),
                ("Contextual Analyzer", self.contextual_analyzer),
                ("Task Flow Manager", self.task_flow_manager),
                ("Action Verifier", self.action_verifier),
                ("Error Recovery", self.error_recovery)
            ]
            
            for name, component in components:
                if not component.initialize():
                    self.logger.error(f"❌ {name} initialization failed")
                    return False
                self.logger.info(f"✅ {name} ready")
            
            self.initialized = True
            self.logger.info("✅ Q03 Complete System ready!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Q03 system init error: {e}")
            return False
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """🎯 Ana komut çalıştırma pipeline"""
        try:
            if not self.initialized:
                return {'success': False, 'error': 'System not initialized'}
            
            self.logger.info(f"🎯 Executing command: '{command}'")
            execution_start = datetime.now()
            
            # Phase 1: Task Decomposition
            self.logger.info("🔥 Phase 1: Task Decomposition")
            task_queue = self.task_decomposer.nehire_atla_decompose(command)
            if not task_queue:
                return self._create_failure_result(command, "Task decomposition failed")
            
            # Phase 2: Contextual Understanding
            self.logger.info("🔍 Phase 2: Contextual Understanding")
            screen_context = self.contextual_analyzer.ekrana_atla_analyze_context()
            if not screen_context:
                return self._create_failure_result(command, "Contextual analysis failed")
            
            # Phase 3: Enhanced Task Flow with Recovery
            self.logger.info("🔄 Phase 3: Enhanced Task Flow Execution")
            flow_result = self._execute_enhanced_task_flow(task_queue, screen_context)
            
            # Phase 4: Final Verification and Reporting
            self.logger.info("✅ Phase 4: Final Verification")
            final_result = self._create_final_result(
                command, task_queue, screen_context, flow_result, execution_start
            )
            
            # Update system statistics
            self._update_system_stats(final_result)
            self.execution_history.append(final_result)
            
            self.logger.info(f"🎯 Command execution completed: {final_result['success']}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"❌ Command execution error: {e}")
            return self._create_failure_result(command, str(e))
    
    def _execute_enhanced_task_flow(self, task_queue, screen_context) -> Dict[str, Any]:
        """Enhanced task flow with integrated error recovery"""
        flow_result = self.task_flow_manager.run_task_flow(task_queue, screen_context)
        
        # If flow failed, attempt recovery
        if not flow_result['success'] or flow_result['failed_steps'] > 0:
            self.logger.info("🔄 Flow issues detected, attempting recovery...")
            
            recovery_attempts = []
            for execution in self.task_flow_manager.executions:
                if hasattr(execution, 'status') and execution.status.value == 'failed':
                    # Attempt recovery for failed step
                    error_info = {
                        'success': False,
                        'error': execution.error or 'Step execution failed',
                        'attempt': execution.retry_count + 1
                    }
                    
                    recovery_attempt = self.error_recovery.attempt_recovery(
                        execution.step, error_info, screen_context
                    )
                    recovery_attempts.append(recovery_attempt)
            
            # Update flow result with recovery information
            flow_result['recovery_attempts'] = len(recovery_attempts)
            flow_result['successful_recoveries'] = sum(
                1 for r in recovery_attempts 
                if r.result.value in ['success', 'partial']
            )
        
        return flow_result
    
    def _create_final_result(self, command: str, task_queue, screen_context, 
                           flow_result: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """Create comprehensive final result"""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate overall success
        overall_success = (
            flow_result['success'] and 
            flow_result['successful_steps'] >= flow_result['executions'] * 0.8
        )
        
        # Generate comprehensive report
        result = {
            'success': overall_success,
            'command': command,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat(),
            
            # Decomposition results
            'decomposition': {
                'queue_id': task_queue.queue_id,
                'total_steps': len(task_queue.task_steps),
                'complexity': task_queue.total_complexity.value,
                'estimated_duration': task_queue.estimated_total_duration
            },
            
            # Context results
            'context': {
                'context_id': screen_context.context_id,
                'context_type': screen_context.context_type.value,
                'confidence': screen_context.context_confidence,
                'effective_mass': screen_context.higgs_mass_distribution.get('final_mass', 0)
            },
            
            # Flow results
            'flow': flow_result,
            
            # Verification summary
            'verification': self._get_verification_summary(),
            
            # Recovery summary
            'recovery': self._get_recovery_summary(),
            
            # Overall metrics
            'metrics': {
                'success_rate': flow_result['successful_steps'] / max(flow_result['executions'], 1),
                'efficiency': min(task_queue.estimated_total_duration / max(execution_time, 0.1), 2.0),
                'reliability': screen_context.context_confidence,
                'recovery_effectiveness': flow_result.get('successful_recoveries', 0) / max(flow_result.get('recovery_attempts', 1), 1)
            }
        }
        
        return result
    
    def _get_verification_summary(self) -> Dict[str, Any]:
        """Get verification summary from action verifier"""
        verifier_status = self.action_verifier.get_verifier_status()
        stats = verifier_status['statistics']
        
        return {
            'total_verifications': stats['total_verifications'],
            'successful_verifications': stats['successful_verifications'],
            'average_confidence': stats['average_confidence'],
            'success_rate': stats['successful_verifications'] / max(stats['total_verifications'], 1)
        }
    
    def _get_recovery_summary(self) -> Dict[str, Any]:
        """Get recovery summary from error recovery system"""
        recovery_status = self.error_recovery.get_recovery_status()
        stats = recovery_status['statistics']
        
        return {
            'total_errors': stats['total_errors'],
            'successful_recoveries': stats['successful_recoveries'],
            'recovery_rate': stats['successful_recoveries'] / max(stats['total_errors'], 1),
            'most_common_error': max(stats['error_type_counts'].items(), key=lambda x: x[1])[0] if stats['error_type_counts'] else 'none'
        }
    
    def _create_failure_result(self, command: str, error: str) -> Dict[str, Any]:
        """Create failure result"""
        return {
            'success': False,
            'command': command,
            'error': error,
            'execution_time': 0.0,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'success_rate': 0.0,
                'efficiency': 0.0,
                'reliability': 0.0,
                'recovery_effectiveness': 0.0
            }
        }
    
    def _update_system_stats(self, result: Dict[str, Any]):
        """Update system statistics"""
        self.system_stats['total_commands'] += 1
        
        if result['success']:
            self.system_stats['successful_commands'] += 1
        else:
            self.system_stats['failed_commands'] += 1
        
        # Update average execution time
        total_commands = self.system_stats['total_commands']
        current_avg = self.system_stats['average_execution_time']
        new_time = result['execution_time']
        
        self.system_stats['average_execution_time'] = (
            (current_avg * (total_commands - 1) + new_time) / total_commands
        )
        
        # Update recovery usage rate
        recovery_used = result.get('recovery', {}).get('total_errors', 0) > 0
        if recovery_used:
            self.system_stats['recovery_usage_rate'] = (
                self.system_stats['recovery_usage_rate'] * (total_commands - 1) + 1
            ) / total_commands
        else:
            self.system_stats['recovery_usage_rate'] = (
                self.system_stats['recovery_usage_rate'] * (total_commands - 1)
            ) / total_commands
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            'initialized': self.initialized,
            'statistics': self.system_stats,
            'execution_history_size': len(self.execution_history),
            'component_status': {
                'task_decomposer': self.task_decomposer.get_decomposer_status(),
                'contextual_analyzer': self.contextual_analyzer.get_contextual_status(),
                'task_flow_manager': self.task_flow_manager.get_flow_status(),
                'action_verifier': self.action_verifier.get_verifier_status(),
                'error_recovery': self.error_recovery.get_recovery_status()
            }
        }

# Test
if __name__ == "__main__":
    print("🎯 Q03 Complete System Test")
    print("💖 DUYGULANDIK! FINAL ENTEGRASYON!")
    
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    system = Q03CompleteSystem()
    
    if system.initialize_complete_system():
        print("✅ Q03 Complete System initialized")
        
        # Test command execution
        test_command = "not defterini aç ve 'wake up orion' yaz"
        print(f"\n🎯 Testing: '{test_command}'")
        
        result = system.execute_command(test_command)
        
        if result['success']:
            print(f"✅ Command successful!")
            print(f"   Execution time: {result['execution_time']:.2f}s")
            print(f"   Success rate: {result['metrics']['success_rate']:.2f}")
            print(f"   Efficiency: {result['metrics']['efficiency']:.2f}")
        else:
            print(f"❌ Command failed: {result.get('error', 'Unknown error')}")
        
        # Show system status
        status = system.get_system_status()
        print(f"\n📊 System Stats:")
        print(f"   Commands: {status['statistics']['successful_commands']}/{status['statistics']['total_commands']}")
        print(f"   Avg time: {status['statistics']['average_execution_time']:.2f}s")
        print(f"   Recovery usage: {status['statistics']['recovery_usage_rate']:.1%}")
        
    else:
        print("❌ Q03 Complete System initialization failed")
    
    print("\n🎉 Q03 Complete System test completed!")
    print("💖 DUYGULANDIK! Q03 SPRINT TAMAMLANDI!")
