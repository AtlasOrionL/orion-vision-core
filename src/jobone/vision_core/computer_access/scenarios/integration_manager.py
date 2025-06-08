#!/usr/bin/env python3
"""
Integration Manager - Module integration and coordination
"""

import logging
import time
from typing import Dict, List, Any, Optional

from . import scenarios_metrics

class IntegrationManager:
    """
    Module integration and coordination manager
    Provides unified interface to all computer access modules
    """
    
    def __init__(self, computer_access_manager):
        self.logger = logging.getLogger('orion.computer_access.scenarios.integration')
        
        # Computer access manager reference
        self.computer_access_manager = computer_access_manager
        
        # Module references (will be set during initialization)
        self.terminal = None
        self.mouse = None
        self.keyboard = None
        self.screen = None
        self.input_coordinator = None
        
        self.initialized = False
        
        self.logger.info("🔗 IntegrationManager initialized")
    
    def initialize(self) -> bool:
        """
        Initialize integration manager
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing integration manager...")
            
            # Get module references from computer access manager
            if not self.computer_access_manager.initialized:
                raise RuntimeError("Computer access manager not initialized")
            
            self.terminal = self.computer_access_manager.terminal
            self.mouse = self.computer_access_manager.mouse
            self.keyboard = self.computer_access_manager.keyboard
            self.screen = self.computer_access_manager.screen
            
            # Initialize input coordinator if available
            try:
                from ..input.input_coordinator import InputCoordinator
                self.input_coordinator = InputCoordinator()
                self.input_coordinator.initialize(self.mouse, self.keyboard)
            except Exception as e:
                self.logger.warning(f"⚠️ Input coordinator initialization failed: {e}")
            
            # Verify all required modules are available
            required_modules = ['terminal', 'mouse', 'keyboard', 'screen']
            for module_name in required_modules:
                module = getattr(self, module_name)
                if not module or not module.is_ready():
                    raise RuntimeError(f"Module {module_name} not ready")
            
            self.initialized = True
            self.logger.info("✅ Integration manager initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Integration manager initialization failed: {e}")
            return False
    
    def execute_terminal_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute terminal action"""
        start_time = time.time()
        
        try:
            self.logger.info(f"🖥️ Terminal action: {action}")
            
            if action == 'execute_command':
                command = parameters.get('command')
                if not command:
                    raise ValueError("Command parameter required")
                
                result = self.terminal.execute_command({'command': command})
                
                return {
                    'success': result.status.value == 'completed',
                    'output': result.stdout,
                    'error': result.stderr,
                    'return_code': result.return_code,
                    'execution_time': result.execution_time
                }
            
            elif action == 'create_file':
                filename = parameters.get('filename')
                content = parameters.get('content', '')
                
                if not filename:
                    raise ValueError("Filename parameter required")
                
                # Create file using echo command
                command = f'echo "{content}" > {filename}'
                result = self.terminal.execute_command({'command': command})
                
                return {
                    'success': result.status.value == 'completed',
                    'filename': filename,
                    'content': content
                }
            
            elif action == 'write_content':
                filename = parameters.get('filename')
                content = parameters.get('content', '')
                append = parameters.get('append', False)
                
                if not filename:
                    raise ValueError("Filename parameter required")
                
                # Write content to file
                operator = '>>' if append else '>'
                command = f'echo "{content}" {operator} {filename}'
                result = self.terminal.execute_command({'command': command})
                
                return {
                    'success': result.status.value == 'completed',
                    'filename': filename,
                    'content': content,
                    'append': append
                }
            
            elif action == 'read_file':
                filename = parameters.get('filename')
                
                if not filename:
                    raise ValueError("Filename parameter required")
                
                # Read file content
                command = f'cat {filename}'
                result = self.terminal.execute_command({'command': command})
                
                return {
                    'success': result.status.value == 'completed',
                    'filename': filename,
                    'content': result.stdout,
                    'error': result.stderr
                }
            
            else:
                raise ValueError(f"Unknown terminal action: {action}")
                
        except Exception as e:
            overhead_time = time.time() - start_time
            scenarios_metrics.record_integration_overhead(overhead_time)
            
            self.logger.error(f"❌ Terminal action failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_mouse_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mouse action"""
        start_time = time.time()
        
        try:
            self.logger.info(f"🖱️ Mouse action: {action}")
            
            if action == 'click':
                x = parameters.get('x')
                y = parameters.get('y')
                button = parameters.get('button', 'left')
                click_type = parameters.get('click_type', 'single')
                
                if x is None or y is None:
                    raise ValueError("X and Y coordinates required")
                
                result = self.mouse.execute_action({
                    'action_type': 'click',
                    'x': x,
                    'y': y,
                    'button': button,
                    'click_type': click_type
                })
                
                return result
            
            elif action == 'move':
                x = parameters.get('x')
                y = parameters.get('y')
                movement_type = parameters.get('movement_type', 'smooth')
                
                if x is None or y is None:
                    raise ValueError("X and Y coordinates required")
                
                result = self.mouse.execute_action({
                    'action_type': 'move',
                    'x': x,
                    'y': y,
                    'movement_type': movement_type
                })
                
                return result
            
            elif action == 'drag':
                start_x = parameters.get('start_x')
                start_y = parameters.get('start_y')
                end_x = parameters.get('end_x')
                end_y = parameters.get('end_y')
                
                if any(coord is None for coord in [start_x, start_y, end_x, end_y]):
                    raise ValueError("Start and end coordinates required")
                
                result = self.mouse.execute_action({
                    'action_type': 'drag',
                    'start_x': start_x,
                    'start_y': start_y,
                    'end_x': end_x,
                    'end_y': end_y
                })
                
                return result
            
            else:
                raise ValueError(f"Unknown mouse action: {action}")
                
        except Exception as e:
            overhead_time = time.time() - start_time
            scenarios_metrics.record_integration_overhead(overhead_time)
            
            self.logger.error(f"❌ Mouse action failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_keyboard_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute keyboard action"""
        start_time = time.time()
        
        try:
            self.logger.info(f"⌨️ Keyboard action: {action}")
            
            if action == 'type_text':
                text = parameters.get('text')
                typing_speed = parameters.get('typing_speed', 50)
                
                if not text:
                    raise ValueError("Text parameter required")
                
                result = self.keyboard.execute_action({
                    'action_type': 'type_text',
                    'text': text,
                    'typing_speed': typing_speed
                })
                
                return result
            
            elif action == 'press_key':
                key = parameters.get('key')
                duration = parameters.get('duration', 0.0)
                
                if not key:
                    raise ValueError("Key parameter required")
                
                result = self.keyboard.execute_action({
                    'action_type': 'press_key',
                    'key': key,
                    'duration': duration
                })
                
                return result
            
            elif action == 'shortcut':
                shortcut_name = parameters.get('shortcut_name')
                keys = parameters.get('keys')
                
                if shortcut_name:
                    result = self.keyboard.execute_action({
                        'action_type': 'shortcut',
                        'shortcut_name': shortcut_name
                    })
                elif keys:
                    result = self.keyboard.execute_action({
                        'action_type': 'key_combination',
                        'keys': keys
                    })
                else:
                    raise ValueError("Shortcut name or keys required")
                
                return result
            
            else:
                raise ValueError(f"Unknown keyboard action: {action}")
                
        except Exception as e:
            overhead_time = time.time() - start_time
            scenarios_metrics.record_integration_overhead(overhead_time)
            
            self.logger.error(f"❌ Keyboard action failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_vision_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute vision action"""
        start_time = time.time()
        
        try:
            self.logger.info(f"👁️ Vision action: {action}")
            
            if action == 'capture_screen':
                region = parameters.get('region')
                
                result = self.screen.capture_and_analyze({
                    'region': region
                })
                
                return result
            
            elif action == 'find_element':
                element_type = parameters.get('element')
                confidence = parameters.get('confidence', 0.7)
                
                result = self.screen.capture_and_analyze({
                    'detection_types': ['ui_elements'],
                    'confidence_threshold': confidence
                })
                
                if result['success']:
                    # Filter for specific element type
                    elements = result['analysis'].elements
                    matching_elements = [
                        elem for elem in elements 
                        if elem.element_type == element_type
                    ]
                    
                    return {
                        'success': len(matching_elements) > 0,
                        'elements': matching_elements,
                        'count': len(matching_elements)
                    }
                
                return result
            
            elif action == 'read_text':
                region = parameters.get('region')
                
                result = self.screen.capture_and_analyze({
                    'region': region,
                    'detection_types': ['text_ocr']
                })
                
                if result['success']:
                    return {
                        'success': True,
                        'text': result['analysis'].text_content
                    }
                
                return result
            
            else:
                raise ValueError(f"Unknown vision action: {action}")
                
        except Exception as e:
            overhead_time = time.time() - start_time
            scenarios_metrics.record_integration_overhead(overhead_time)
            
            self.logger.error(f"❌ Vision action failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_coordinated_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coordinated input action"""
        start_time = time.time()
        
        try:
            if not self.input_coordinator:
                raise RuntimeError("Input coordinator not available")
            
            self.logger.info(f"🎯 Coordinated action: {action}")
            
            if action == 'click_and_type':
                from ..input.input_coordinator import CoordinatedTask, CoordinatedAction
                
                task = CoordinatedTask(
                    task_id=f"coord_{int(time.time())}",
                    action_type=CoordinatedAction.CLICK_AND_TYPE,
                    parameters=parameters
                )
                
                result = self.input_coordinator.execute_coordinated_action(task)
                return result
            
            elif action == 'fill_form':
                from ..input.input_coordinator import CoordinatedTask, CoordinatedAction
                
                task = CoordinatedTask(
                    task_id=f"form_{int(time.time())}",
                    action_type=CoordinatedAction.FORM_FILLING,
                    parameters=parameters
                )
                
                result = self.input_coordinator.execute_coordinated_action(task)
                return result
            
            else:
                raise ValueError(f"Unknown coordinated action: {action}")
                
        except Exception as e:
            overhead_time = time.time() - start_time
            scenarios_metrics.record_integration_overhead(overhead_time)
            
            self.logger.error(f"❌ Coordinated action failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def is_ready(self) -> bool:
        """Check if integration manager is ready"""
        return (self.initialized and 
                self.terminal and self.terminal.is_ready() and
                self.mouse and self.mouse.is_ready() and
                self.keyboard and self.keyboard.is_ready() and
                self.screen and self.screen.is_ready())
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration manager status"""
        return {
            'initialized': self.initialized,
            'modules_ready': {
                'terminal': self.terminal.is_ready() if self.terminal else False,
                'mouse': self.mouse.is_ready() if self.mouse else False,
                'keyboard': self.keyboard.is_ready() if self.keyboard else False,
                'screen': self.screen.is_ready() if self.screen else False,
                'input_coordinator': self.input_coordinator.is_ready() if self.input_coordinator else False
            },
            'computer_access_manager_ready': self.computer_access_manager.initialized if self.computer_access_manager else False
        }
    
    def shutdown(self):
        """Shutdown integration manager"""
        self.logger.info("🛑 Shutting down integration manager")
        
        if self.input_coordinator:
            self.input_coordinator.shutdown()
        
        self.initialized = False
        self.logger.info("✅ Integration manager shutdown complete")
