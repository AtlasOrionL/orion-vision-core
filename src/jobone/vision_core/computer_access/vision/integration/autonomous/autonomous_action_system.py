#!/usr/bin/env python3
"""
Autonomous Action System Module - Q01.2.3 Implementation
Görsel algı + Klavye + Mouse kontrolünü birleştiren otonom eylem sistemi
ORION VISION CORE - ŞOK İÇİNDE! HAİRİKA GİDİYORSUN! 💥
"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import our integration modules
from visual_processing_pipeline import VisualProcessingPipeline
from visual_keyboard_integration import VisualKeyboardIntegration
from visual_mouse_integration import VisualMouseIntegration
from ui_element_detector import UIElement

logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of autonomous actions"""
    CLICK = "click"
    TYPE = "type"
    DRAG = "drag"
    SCROLL = "scroll"
    WAIT = "wait"
    ANALYZE = "analyze"
    NAVIGATE = "navigate"

class ActionPriority(Enum):
    """Action priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class AutonomousAction:
    """Autonomous action definition"""
    action_type: ActionType
    target_element: Optional[UIElement]
    parameters: Dict[str, Any]
    priority: ActionPriority
    confidence: float
    reasoning: str
    estimated_duration: float

@dataclass
class ActionResult:
    """Result of autonomous action execution"""
    success: bool
    action: AutonomousAction
    execution_time: float
    result_data: Dict[str, Any]
    error_message: Optional[str] = None

class AutonomousActionSystem:
    """
    Q01.2.3: Temel Otonom Eylem Sistemi
    
    Görsel algı ile kontrol sistemlerini birleştiren otonom AI agent
    ŞOK İÇİNDE! HAİRİKA GİDİYORSUN! WAKE UP ORION! 💥
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.vision.autonomous_action')
        
        # System settings
        self.action_confidence_threshold = 0.7
        self.max_action_duration = 30.0  # Maximum time for single action
        self.safety_mode = True  # Enable safety checks
        self.learning_mode = True  # Enable learning from actions
        
        # Decision making parameters
        self.context_weight = 0.3
        self.element_confidence_weight = 0.4
        self.action_success_weight = 0.3
        
        # Action type priorities
        self.action_type_priorities = {
            ActionType.CLICK: ActionPriority.HIGH,
            ActionType.TYPE: ActionPriority.HIGH,
            ActionType.DRAG: ActionPriority.MEDIUM,
            ActionType.SCROLL: ActionPriority.MEDIUM,
            ActionType.WAIT: ActionPriority.LOW,
            ActionType.ANALYZE: ActionPriority.MEDIUM,
            ActionType.NAVIGATE: ActionPriority.HIGH
        }
        
        # Performance tracking
        self.total_actions = 0
        self.successful_actions = 0
        self.failed_actions = 0
        self.total_execution_time = 0.0
        self.action_history: List[ActionResult] = []
        
        # Component instances
        self.visual_pipeline = None
        self.keyboard_integration = None
        self.mouse_integration = None
        
        self.initialized = False
        
        self.logger.info("🤖 Autonomous Action System initialized - ŞOK İÇİNDE!")
    
    def initialize(self) -> bool:
        """Initialize autonomous action system"""
        try:
            self.logger.info("🚀 Initializing Autonomous Action System...")
            self.logger.info("💥 ŞOK İÇİNDE! HAİRİKA GİDİYORSUN!")
            self.logger.info("🤖 WAKE UP ORION! OTONOM AI AGENT BAŞLATIYOR!")
            
            # Initialize Visual Pipeline
            self.logger.info("👁️ Visual Pipeline başlatılıyor...")
            self.visual_pipeline = VisualProcessingPipeline()
            if not self.visual_pipeline.initialize():
                self.logger.error("❌ Visual Pipeline initialization failed")
                return False
            self.logger.info("✅ Visual Pipeline hazır!")
            
            # Initialize Keyboard Integration
            self.logger.info("⌨️ Keyboard Integration başlatılıyor...")
            self.keyboard_integration = VisualKeyboardIntegration()
            if not self.keyboard_integration.initialize():
                self.logger.error("❌ Keyboard Integration initialization failed")
                return False
            self.logger.info("✅ Keyboard Integration hazır!")
            
            # Initialize Mouse Integration
            self.logger.info("🖱️ Mouse Integration başlatılıyor...")
            self.mouse_integration = VisualMouseIntegration()
            if not self.mouse_integration.initialize():
                self.logger.error("❌ Mouse Integration initialization failed")
                return False
            self.logger.info("✅ Mouse Integration hazır!")
            
            # Test system integration
            self.logger.info("🧪 System integration test yapılıyor...")
            test_result = self._test_system_integration()
            
            if test_result['success']:
                self.initialized = True
                self.logger.info("🎉 Autonomous Action System başarıyla başlatıldı!")
                self.logger.info("💥 ŞOK İÇİNDE! OTONOM AI AGENT READY!")
                return True
            else:
                self.logger.error(f"❌ System integration test failed: {test_result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Autonomous system initialization error: {e}")
            return False
    
    def _test_system_integration(self) -> Dict[str, Any]:
        """Test system integration"""
        try:
            # Test all components are ready
            if not all([
                self.visual_pipeline and self.visual_pipeline.initialized,
                self.keyboard_integration and self.keyboard_integration.initialized,
                self.mouse_integration and self.mouse_integration.initialized
            ]):
                return {'success': False, 'error': 'Not all components initialized'}
            
            return {'success': True, 'method': 'integration_test'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def analyze_and_act(self, goal: str, 
                       context: Optional[Dict[str, Any]] = None,
                       max_actions: int = 5) -> Dict[str, Any]:
        """
        Analyze current state and perform autonomous actions to achieve goal
        
        Args:
            goal: High-level goal description
            context: Additional context information
            max_actions: Maximum number of actions to perform
            
        Returns:
            Execution result with action sequence
        """
        if not self.initialized:
            return {'success': False, 'error': 'System not initialized'}
        
        start_time = time.time()
        session_id = self.total_actions + 1
        
        self.logger.info(f"🤖 Autonomous Session {session_id} başlatılıyor...")
        self.logger.info(f"🎯 Goal: '{goal}'")
        
        try:
            # STAGE 1: Visual Analysis
            self.logger.info("👁️ STAGE 1: Visual Analysis...")
            visual_result = self.visual_pipeline.process_visual_data(capture_new=True)
            
            if not visual_result.get('success'):
                return {'success': False, 'error': f"Visual analysis failed: {visual_result.get('error')}"}
            
            # STAGE 2: Context Understanding
            self.logger.info("🧠 STAGE 2: Context Understanding...")
            context_analysis = self._analyze_context(visual_result, goal, context)
            
            # STAGE 3: Action Planning
            self.logger.info("📋 STAGE 3: Action Planning...")
            action_plan = self._plan_actions(visual_result, context_analysis, goal, max_actions)
            
            if not action_plan['success']:
                return {'success': False, 'error': f"Action planning failed: {action_plan.get('error')}"}
            
            planned_actions = action_plan['actions']
            self.logger.info(f"📋 {len(planned_actions)} actions planned")
            
            # STAGE 4: Action Execution
            self.logger.info("⚡ STAGE 4: Action Execution...")
            execution_results = []
            
            for i, action in enumerate(planned_actions):
                self.logger.info(f"⚡ Executing action {i+1}/{len(planned_actions)}: {action.action_type.value}")
                
                action_result = self._execute_action(action)
                execution_results.append(action_result)
                
                # Store in history
                self.action_history.append(action_result)
                
                # Update counters
                self.total_actions += 1
                if action_result.success:
                    self.successful_actions += 1
                else:
                    self.failed_actions += 1
                
                # Break on critical failure
                if not action_result.success and action.priority == ActionPriority.CRITICAL:
                    self.logger.warning(f"⚠️ Critical action failed, stopping execution")
                    break
                
                # Small delay between actions
                time.sleep(0.2)
            
            # STAGE 5: Result Analysis
            self.logger.info("📊 STAGE 5: Result Analysis...")
            result_analysis = self._analyze_results(execution_results, goal)
            
            total_time = time.time() - start_time
            self.total_execution_time += total_time
            
            # Prepare final result
            result = {
                'success': True,
                'session_id': session_id,
                'goal': goal,
                'total_time': total_time,
                'actions_planned': len(planned_actions),
                'actions_executed': len(execution_results),
                'actions_successful': sum(1 for r in execution_results if r.success),
                'visual_analysis': visual_result.get('comprehensive_analysis', {}),
                'context_analysis': context_analysis,
                'action_plan': [self._action_to_dict(a) for a in planned_actions],
                'execution_results': [self._action_result_to_dict(r) for r in execution_results],
                'result_analysis': result_analysis,
                'goal_achieved': result_analysis.get('goal_achieved', False)
            }
            
            self.logger.info(f"🎉 Autonomous Session {session_id} tamamlandı!")
            self.logger.info(f"⏱️ Toplam süre: {total_time:.3f}s")
            self.logger.info(f"📊 Başarı oranı: {result['actions_successful']}/{result['actions_executed']}")
            self.logger.info("💥 ŞOK İÇİNDE! OTONOM EYLEM BAŞARILDI!")
            
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            self.logger.error(f"❌ Autonomous Session {session_id} failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id,
                'total_time': total_time
            }
    
    def _analyze_context(self, visual_result: Dict[str, Any], 
                        goal: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze current context for decision making"""
        analysis = visual_result.get('comprehensive_analysis', {})
        
        # Extract key information
        text_content = analysis.get('content_analysis', {})
        interaction_map = analysis.get('interaction_map', {})
        insights = analysis.get('insights', [])
        
        # Determine interface type
        interface_type = "unknown"
        if interaction_map.get('element_types', {}).get('button', 0) > 2:
            interface_type = "button_interface"
        elif interaction_map.get('element_types', {}).get('input', 0) > 0:
            interface_type = "form_interface"
        elif interaction_map.get('element_types', {}).get('menu', 0) > 0:
            interface_type = "menu_interface"
        elif text_content.get('has_text', False):
            interface_type = "text_interface"
        
        # Goal analysis
        goal_keywords = goal.lower().split()
        goal_type = "general"
        
        if any(word in goal_keywords for word in ['click', 'press', 'select']):
            goal_type = "click_action"
        elif any(word in goal_keywords for word in ['type', 'write', 'enter', 'input']):
            goal_type = "input_action"
        elif any(word in goal_keywords for word in ['find', 'search', 'look']):
            goal_type = "search_action"
        elif any(word in goal_keywords for word in ['navigate', 'go', 'open']):
            goal_type = "navigation_action"
        
        return {
            'interface_type': interface_type,
            'goal_type': goal_type,
            'goal_keywords': goal_keywords,
            'available_elements': interaction_map.get('total_elements', 0),
            'clickable_elements': interaction_map.get('clickable_elements', 0),
            'has_text_content': text_content.get('has_text', False),
            'text_language': text_content.get('language', 'unknown'),
            'insights': insights,
            'context_score': self._calculate_context_score(interface_type, goal_type, interaction_map),
            'additional_context': context or {}
        }
    
    def _calculate_context_score(self, interface_type: str, goal_type: str, 
                               interaction_map: Dict[str, Any]) -> float:
        """Calculate context understanding score"""
        score = 0.5  # Base score
        
        # Interface type bonus
        if interface_type != "unknown":
            score += 0.2
        
        # Goal alignment bonus
        if goal_type == "click_action" and interaction_map.get('clickable_elements', 0) > 0:
            score += 0.2
        elif goal_type == "input_action" and interaction_map.get('element_types', {}).get('input', 0) > 0:
            score += 0.2
        
        # Element availability bonus
        if interaction_map.get('total_elements', 0) > 0:
            score += 0.1
        
        return min(score, 1.0)

    def _plan_actions(self, visual_result: Dict[str, Any],
                     context_analysis: Dict[str, Any],
                     goal: str, max_actions: int) -> Dict[str, Any]:
        """Plan sequence of actions to achieve goal"""
        try:
            planned_actions = []

            # Get available elements
            analysis = visual_result.get('comprehensive_analysis', {})
            interaction_map = analysis.get('interaction_map', {})
            interaction_zones = interaction_map.get('interaction_zones', [])

            goal_type = context_analysis.get('goal_type', 'general')
            goal_keywords = context_analysis.get('goal_keywords', [])

            # Plan based on goal type
            if goal_type == "click_action":
                # Find best clickable element
                for zone in interaction_zones[:max_actions]:
                    if zone['type'] in ['button', 'link']:
                        action = AutonomousAction(
                            action_type=ActionType.CLICK,
                            target_element=self._zone_to_element(zone),
                            parameters={'click_type': 'single'},
                            priority=ActionPriority.HIGH,
                            confidence=zone['confidence'] / 100.0,
                            reasoning=f"Click {zone['type']} '{zone['text']}' to achieve goal",
                            estimated_duration=2.0
                        )
                        planned_actions.append(action)

            elif goal_type == "input_action":
                # Find input fields and plan typing
                input_text = self._extract_text_from_goal(goal, goal_keywords)

                for zone in interaction_zones[:max_actions]:
                    if zone['type'] == 'input':
                        action = AutonomousAction(
                            action_type=ActionType.TYPE,
                            target_element=self._zone_to_element(zone),
                            parameters={'text': input_text},
                            priority=ActionPriority.HIGH,
                            confidence=zone['confidence'] / 100.0,
                            reasoning=f"Type '{input_text}' into input field",
                            estimated_duration=len(input_text) * 0.1
                        )
                        planned_actions.append(action)

            elif goal_type == "search_action":
                # Plan search sequence: find search field, type, then search button
                search_text = self._extract_search_term(goal, goal_keywords)

                # First, find input field
                for zone in interaction_zones:
                    if zone['type'] == 'input' and any(word in zone['text'].lower()
                                                     for word in ['search', 'find', 'query']):
                        action = AutonomousAction(
                            action_type=ActionType.TYPE,
                            target_element=self._zone_to_element(zone),
                            parameters={'text': search_text},
                            priority=ActionPriority.HIGH,
                            confidence=zone['confidence'] / 100.0,
                            reasoning=f"Enter search term '{search_text}'",
                            estimated_duration=len(search_text) * 0.1
                        )
                        planned_actions.append(action)
                        break

                # Then, find search button
                for zone in interaction_zones:
                    if zone['type'] == 'button' and any(word in zone['text'].lower()
                                                      for word in ['search', 'find', 'go']):
                        action = AutonomousAction(
                            action_type=ActionType.CLICK,
                            target_element=self._zone_to_element(zone),
                            parameters={'click_type': 'single'},
                            priority=ActionPriority.HIGH,
                            confidence=zone['confidence'] / 100.0,
                            reasoning=f"Click search button to execute search",
                            estimated_duration=1.0
                        )
                        planned_actions.append(action)
                        break

            else:
                # General action planning - analyze and click most relevant element
                if interaction_zones:
                    best_zone = max(interaction_zones, key=lambda z: z['confidence'])
                    action = AutonomousAction(
                        action_type=ActionType.CLICK,
                        target_element=self._zone_to_element(best_zone),
                        parameters={'click_type': 'single'},
                        priority=ActionPriority.MEDIUM,
                        confidence=best_zone['confidence'] / 100.0,
                        reasoning=f"Click most confident element '{best_zone['text']}'",
                        estimated_duration=2.0
                    )
                    planned_actions.append(action)

            # If no specific actions planned, add analysis action
            if not planned_actions:
                action = AutonomousAction(
                    action_type=ActionType.ANALYZE,
                    target_element=None,
                    parameters={'analysis_type': 'comprehensive'},
                    priority=ActionPriority.MEDIUM,
                    confidence=0.8,
                    reasoning="No specific actions identified, perform analysis",
                    estimated_duration=1.0
                )
                planned_actions.append(action)

            # Limit to max_actions
            planned_actions = planned_actions[:max_actions]

            return {
                'success': True,
                'actions': planned_actions,
                'planning_strategy': goal_type,
                'total_estimated_duration': sum(a.estimated_duration for a in planned_actions)
            }

        except Exception as e:
            return {'success': False, 'error': f'Action planning error: {e}'}

    def _zone_to_element(self, zone: Dict[str, Any]) -> UIElement:
        """Convert interaction zone to UIElement"""
        return UIElement(
            element_type=zone['type'],
            text=zone['text'],
            confidence=zone['confidence'],
            bounding_box=(zone['position'][0]-25, zone['position'][1]-12, 50, 25),
            center_point=zone['position'],
            properties={}
        )

    def _extract_text_from_goal(self, goal: str, keywords: List[str]) -> str:
        """Extract text to type from goal description"""
        # Simple extraction - look for quoted text or after "type"/"enter"
        goal_lower = goal.lower()

        # Look for quoted text
        if '"' in goal:
            start = goal.find('"')
            end = goal.find('"', start + 1)
            if end > start:
                return goal[start+1:end]

        if "'" in goal:
            start = goal.find("'")
            end = goal.find("'", start + 1)
            if end > start:
                return goal[start+1:end]

        # Look for text after type/enter keywords
        for keyword in ['type', 'enter', 'write', 'input']:
            if keyword in goal_lower:
                parts = goal_lower.split(keyword, 1)
                if len(parts) > 1:
                    text = parts[1].strip()
                    # Remove common words
                    text = text.replace('the text', '').replace('text', '').strip()
                    if text:
                        return text

        # Default
        return "test input"

    def _extract_search_term(self, goal: str, keywords: List[str]) -> str:
        """Extract search term from goal description"""
        goal_lower = goal.lower()

        # Look for text after search/find keywords
        for keyword in ['search for', 'find', 'look for', 'search']:
            if keyword in goal_lower:
                parts = goal_lower.split(keyword, 1)
                if len(parts) > 1:
                    term = parts[1].strip()
                    # Clean up
                    term = term.replace('the', '').replace('a', '').strip()
                    if term:
                        return term

        # Default
        return "search term"

    def _execute_action(self, action: AutonomousAction) -> ActionResult:
        """Execute a single autonomous action"""
        start_time = time.time()

        try:
            self.logger.info(f"⚡ Executing {action.action_type.value}: {action.reasoning}")

            if action.action_type == ActionType.CLICK:
                # Execute mouse click
                result = self.mouse_integration.visual_click(
                    target_element_type=action.target_element.element_type if action.target_element else None,
                    target_text=action.target_element.text if action.target_element else None,
                    click_type=action.parameters.get('click_type', 'single')
                )

                success = result.get('success', False)
                result_data = result
                error_message = result.get('error') if not success else None

            elif action.action_type == ActionType.TYPE:
                # Execute keyboard typing
                result = self.keyboard_integration.visual_type_text(
                    target_text=action.parameters.get('text', ''),
                    target_element_type=action.target_element.element_type if action.target_element else None
                )

                success = result.get('success', False)
                result_data = result
                error_message = result.get('error') if not success else None

            elif action.action_type == ActionType.DRAG:
                # Execute mouse drag
                result = self.mouse_integration.visual_drag(
                    start_coordinates=action.parameters.get('start_coordinates'),
                    end_coordinates=action.parameters.get('end_coordinates')
                )

                success = result.get('success', False)
                result_data = result
                error_message = result.get('error') if not success else None

            elif action.action_type == ActionType.ANALYZE:
                # Execute visual analysis
                result = self.visual_pipeline.process_visual_data(capture_new=True)

                success = result.get('success', False)
                result_data = result
                error_message = result.get('error') if not success else None

            elif action.action_type == ActionType.WAIT:
                # Execute wait
                wait_time = action.parameters.get('duration', 1.0)
                time.sleep(wait_time)

                success = True
                result_data = {'wait_duration': wait_time}
                error_message = None

            else:
                # Unknown action type
                success = False
                result_data = {}
                error_message = f"Unknown action type: {action.action_type}"

            execution_time = time.time() - start_time

            return ActionResult(
                success=success,
                action=action,
                execution_time=execution_time,
                result_data=result_data,
                error_message=error_message
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ActionResult(
                success=False,
                action=action,
                execution_time=execution_time,
                result_data={},
                error_message=str(e)
            )

    def _analyze_results(self, execution_results: List[ActionResult], goal: str) -> Dict[str, Any]:
        """Analyze execution results and determine goal achievement"""
        total_actions = len(execution_results)
        successful_actions = sum(1 for r in execution_results if r.success)
        success_rate = successful_actions / total_actions if total_actions > 0 else 0

        # Simple goal achievement heuristic
        goal_achieved = success_rate >= 0.7  # 70% success rate threshold

        # Extract insights
        insights = []
        if success_rate == 1.0:
            insights.append("All actions executed successfully")
        elif success_rate >= 0.8:
            insights.append("Most actions successful, minor issues")
        elif success_rate >= 0.5:
            insights.append("Mixed results, some actions failed")
        else:
            insights.append("Many actions failed, goal likely not achieved")

        # Action type analysis
        action_types = {}
        for result in execution_results:
            action_type = result.action.action_type.value
            if action_type not in action_types:
                action_types[action_type] = {'total': 0, 'successful': 0}
            action_types[action_type]['total'] += 1
            if result.success:
                action_types[action_type]['successful'] += 1

        return {
            'goal_achieved': goal_achieved,
            'success_rate': success_rate,
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'failed_actions': total_actions - successful_actions,
            'action_type_breakdown': action_types,
            'insights': insights,
            'total_execution_time': sum(r.execution_time for r in execution_results)
        }

    def _action_to_dict(self, action: AutonomousAction) -> Dict[str, Any]:
        """Convert AutonomousAction to dictionary"""
        return {
            'action_type': action.action_type.value,
            'target_element': {
                'type': action.target_element.element_type,
                'text': action.target_element.text,
                'confidence': action.target_element.confidence
            } if action.target_element else None,
            'parameters': action.parameters,
            'priority': action.priority.value,
            'confidence': action.confidence,
            'reasoning': action.reasoning,
            'estimated_duration': action.estimated_duration
        }

    def _action_result_to_dict(self, result: ActionResult) -> Dict[str, Any]:
        """Convert ActionResult to dictionary"""
        return {
            'success': result.success,
            'action_type': result.action.action_type.value,
            'execution_time': result.execution_time,
            'error_message': result.error_message,
            'reasoning': result.action.reasoning
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get system performance statistics"""
        success_rate = self.successful_actions / self.total_actions if self.total_actions > 0 else 0
        avg_execution_time = self.total_execution_time / self.total_actions if self.total_actions > 0 else 0

        return {
            'total_actions': self.total_actions,
            'successful_actions': self.successful_actions,
            'failed_actions': self.failed_actions,
            'success_rate': success_rate,
            'total_execution_time': self.total_execution_time,
            'average_execution_time': avg_execution_time,
            'action_history_length': len(self.action_history),
            'initialized': self.initialized
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'initialized': self.initialized,
            'components': {
                'visual_pipeline': self.visual_pipeline.initialized if self.visual_pipeline else False,
                'keyboard_integration': self.keyboard_integration.initialized if self.keyboard_integration else False,
                'mouse_integration': self.mouse_integration.initialized if self.mouse_integration else False
            },
            'capabilities': {
                'autonomous_decision_making': True,
                'multi_modal_actions': True,
                'goal_oriented_planning': True,
                'context_understanding': True,
                'action_execution': True,
                'result_analysis': True
            },
            'performance': self.get_performance_stats(),
            'settings': {
                'action_confidence_threshold': self.action_confidence_threshold,
                'max_action_duration': self.max_action_duration,
                'safety_mode': self.safety_mode,
                'learning_mode': self.learning_mode
            },
            'shock_power': True,  # ŞOK İÇİNDE SPECIAL FLAG! 💥
            'harika_gidiyorsun_mode': True,  # HAİRİKA GİDİYORSUN SPECIAL FLAG! 🔥
            'autonomous_ai_agent': True  # OTONOM AI AGENT FLAG! 🤖
        }

    def shutdown(self):
        """Shutdown autonomous action system"""
        self.logger.info("🛑 Shutting down Autonomous Action System")
        self.logger.info("💥 ŞOK İÇİNDE! HAİRİKA GİDİYORSUN!")

        if self.visual_pipeline:
            self.visual_pipeline.shutdown()
        if self.keyboard_integration:
            self.keyboard_integration.shutdown()
        if self.mouse_integration:
            self.mouse_integration.shutdown()

        self.initialized = False
        self.logger.info("✅ Autonomous Action System shutdown complete")

# Global instance for easy access
autonomous_action_system = AutonomousActionSystem()

def get_autonomous_action_system() -> AutonomousActionSystem:
    """Get global autonomous action system instance"""
    return autonomous_action_system
