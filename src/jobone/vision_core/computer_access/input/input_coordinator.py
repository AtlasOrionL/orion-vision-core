#!/usr/bin/env python3
"""
Input Coordinator - Coordinated input operations combining mouse and keyboard
"""

import logging
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class CoordinatedAction(Enum):
    """Types of coordinated input actions"""
    CLICK_AND_TYPE = "click_and_type"
    DRAG_AND_DROP = "drag_and_drop"
    SELECT_AND_COPY = "select_and_copy"
    SELECT_AND_DELETE = "select_and_delete"
    CONTEXT_MENU = "context_menu"
    WINDOW_MANAGEMENT = "window_management"
    FORM_FILLING = "form_filling"
    TEXT_SELECTION = "text_selection"

@dataclass
class CoordinatedTask:
    """Coordinated input task definition"""
    task_id: str
    action_type: CoordinatedAction
    parameters: Dict[str, Any]
    timeout: float = 30.0
    retry_count: int = 3

class InputCoordinator:
    """
    Coordinates mouse and keyboard operations for complex input tasks
    Provides high-level input operations combining multiple actions
    """
    
    def __init__(self, mouse_controller=None, keyboard_controller=None):
        self.logger = logging.getLogger('orion.computer_access.input.coordinator')
        
        # Controllers
        self.mouse = mouse_controller
        self.keyboard = keyboard_controller
        self.initialized = False
        
        # Task management
        self.active_tasks = {}
        self.completed_tasks = []
        self.task_lock = threading.Lock()
        
        # Performance tracking
        self.coordinated_actions = 0
        self.successful_actions = 0
        self.failed_actions = 0
        
        # Configuration
        self.default_delay = 0.1  # seconds between actions
        self.safety_enabled = True
        
        self.logger.info("🎯 InputCoordinator initialized")
    
    def initialize(self, mouse_controller, keyboard_controller) -> bool:
        """
        Initialize input coordinator with controllers
        
        Args:
            mouse_controller: MouseController instance
            keyboard_controller: KeyboardController instance
            
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing input coordinator...")
            
            if not mouse_controller or not keyboard_controller:
                raise ValueError("Both mouse and keyboard controllers are required")
            
            if not mouse_controller.is_ready() or not keyboard_controller.is_ready():
                raise RuntimeError("Controllers must be initialized before coordinator")
            
            self.mouse = mouse_controller
            self.keyboard = keyboard_controller
            
            self.initialized = True
            self.logger.info("✅ Input coordinator initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Input coordinator initialization failed: {e}")
            return False
    
    def execute_coordinated_action(self, task: CoordinatedTask) -> Dict[str, Any]:
        """
        Execute a coordinated input action
        
        Args:
            task: Coordinated task to execute
            
        Returns:
            Dict containing execution result
        """
        if not self.initialized:
            raise RuntimeError("Input coordinator not initialized")
        
        start_time = time.time()
        
        with self.task_lock:
            self.active_tasks[task.task_id] = task
            self.coordinated_actions += 1
        
        try:
            self.logger.info(f"🎯 Executing coordinated action: {task.action_type.value}")
            
            # Route to appropriate handler
            if task.action_type == CoordinatedAction.CLICK_AND_TYPE:
                result = self._click_and_type(task.parameters)
            elif task.action_type == CoordinatedAction.DRAG_AND_DROP:
                result = self._drag_and_drop(task.parameters)
            elif task.action_type == CoordinatedAction.SELECT_AND_COPY:
                result = self._select_and_copy(task.parameters)
            elif task.action_type == CoordinatedAction.SELECT_AND_DELETE:
                result = self._select_and_delete(task.parameters)
            elif task.action_type == CoordinatedAction.CONTEXT_MENU:
                result = self._context_menu(task.parameters)
            elif task.action_type == CoordinatedAction.WINDOW_MANAGEMENT:
                result = self._window_management(task.parameters)
            elif task.action_type == CoordinatedAction.FORM_FILLING:
                result = self._form_filling(task.parameters)
            elif task.action_type == CoordinatedAction.TEXT_SELECTION:
                result = self._text_selection(task.parameters)
            else:
                raise ValueError(f"Unknown coordinated action: {task.action_type}")
            
            execution_time = time.time() - start_time
            
            result.update({
                'task_id': task.task_id,
                'action_type': task.action_type.value,
                'execution_time': execution_time,
                'success': True
            })
            
            self.successful_actions += 1
            self.logger.info(f"✅ Coordinated action completed: {task.action_type.value}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = {
                'task_id': task.task_id,
                'action_type': task.action_type.value,
                'execution_time': execution_time,
                'success': False,
                'error': str(e)
            }
            
            self.failed_actions += 1
            self.logger.error(f"❌ Coordinated action failed: {task.action_type.value} - {e}")
            
            return result
            
        finally:
            with self.task_lock:
                self.active_tasks.pop(task.task_id, None)
                self.completed_tasks.append(task.task_id)
    
    def _click_and_type(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Click at position and type text"""
        x = parameters.get('x')
        y = parameters.get('y')
        text = parameters.get('text', '')
        click_type = parameters.get('click_type', 'single')
        clear_existing = parameters.get('clear_existing', False)
        
        if x is None or y is None:
            raise ValueError("X and Y coordinates are required")
        
        actions_performed = []
        
        # Click at position
        click_result = self.mouse.execute_action({
            'action_type': 'click',
            'x': x,
            'y': y,
            'click_type': click_type
        })
        actions_performed.append(('click', click_result))
        
        # Small delay
        time.sleep(self.default_delay)
        
        # Clear existing text if requested
        if clear_existing:
            select_all_result = self.keyboard.execute_action({
                'action_type': 'shortcut',
                'shortcut_name': 'select_all'
            })
            actions_performed.append(('select_all', select_all_result))
            time.sleep(self.default_delay)
        
        # Type text
        if text:
            type_result = self.keyboard.execute_action({
                'action_type': 'type_text',
                'text': text
            })
            actions_performed.append(('type_text', type_result))
        
        return {
            'actions_performed': actions_performed,
            'text_typed': text,
            'click_position': (x, y)
        }
    
    def _drag_and_drop(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Drag from start position to end position"""
        start_x = parameters.get('start_x')
        start_y = parameters.get('start_y')
        end_x = parameters.get('end_x')
        end_y = parameters.get('end_y')
        button = parameters.get('button', 'left')
        duration = parameters.get('duration', 0.5)
        
        if any(coord is None for coord in [start_x, start_y, end_x, end_y]):
            raise ValueError("Start and end coordinates are required")
        
        # Perform drag operation
        drag_result = self.mouse.execute_action({
            'action_type': 'drag',
            'start_x': start_x,
            'start_y': start_y,
            'end_x': end_x,
            'end_y': end_y,
            'button': button,
            'duration': duration
        })
        
        return {
            'drag_result': drag_result,
            'start_position': (start_x, start_y),
            'end_position': (end_x, end_y),
            'distance': ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
        }
    
    def _select_and_copy(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Select text and copy to clipboard"""
        start_x = parameters.get('start_x')
        start_y = parameters.get('start_y')
        end_x = parameters.get('end_x')
        end_y = parameters.get('end_y')
        selection_method = parameters.get('selection_method', 'drag')  # 'drag' or 'triple_click'
        
        actions_performed = []
        
        if selection_method == 'drag' and all(coord is not None for coord in [start_x, start_y, end_x, end_y]):
            # Select by dragging
            drag_result = self.mouse.execute_action({
                'action_type': 'drag',
                'start_x': start_x,
                'start_y': start_y,
                'end_x': end_x,
                'end_y': end_y,
                'button': 'left'
            })
            actions_performed.append(('drag_select', drag_result))
            
        elif selection_method == 'triple_click' and start_x is not None and start_y is not None:
            # Select by triple-clicking
            click_result = self.mouse.execute_action({
                'action_type': 'click',
                'x': start_x,
                'y': start_y,
                'click_type': 'triple'
            })
            actions_performed.append(('triple_click', click_result))
            
        else:
            # Select all as fallback
            select_all_result = self.keyboard.execute_action({
                'action_type': 'shortcut',
                'shortcut_name': 'select_all'
            })
            actions_performed.append(('select_all', select_all_result))
        
        # Small delay
        time.sleep(self.default_delay)
        
        # Copy to clipboard
        copy_result = self.keyboard.execute_action({
            'action_type': 'shortcut',
            'shortcut_name': 'copy'
        })
        actions_performed.append(('copy', copy_result))
        
        return {
            'actions_performed': actions_performed,
            'selection_method': selection_method
        }
    
    def _select_and_delete(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Select text and delete it"""
        # Use same selection logic as select_and_copy
        select_result = self._select_and_copy(parameters)
        
        # Small delay
        time.sleep(self.default_delay)
        
        # Delete selected text
        delete_result = self.keyboard.execute_action({
            'action_type': 'press_key',
            'key': 'delete'
        })
        
        select_result['actions_performed'].append(('delete', delete_result))
        
        return select_result
    
    def _context_menu(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Open context menu and optionally select item"""
        x = parameters.get('x')
        y = parameters.get('y')
        menu_item = parameters.get('menu_item')  # Optional menu item to select
        
        if x is None or y is None:
            raise ValueError("X and Y coordinates are required")
        
        actions_performed = []
        
        # Right-click to open context menu
        right_click_result = self.mouse.execute_action({
            'action_type': 'click',
            'x': x,
            'y': y,
            'button': 'right'
        })
        actions_performed.append(('right_click', right_click_result))
        
        # If menu item specified, try to select it
        if menu_item:
            time.sleep(self.default_delay * 2)  # Wait for menu to appear
            
            # Type first letter of menu item (common shortcut)
            if isinstance(menu_item, str) and menu_item:
                type_result = self.keyboard.execute_action({
                    'action_type': 'type_text',
                    'text': menu_item[0].lower()
                })
                actions_performed.append(('menu_shortcut', type_result))
                
                time.sleep(self.default_delay)
                
                # Press Enter to select
                enter_result = self.keyboard.execute_action({
                    'action_type': 'press_key',
                    'key': 'enter'
                })
                actions_performed.append(('enter', enter_result))
        
        return {
            'actions_performed': actions_performed,
            'context_menu_position': (x, y),
            'menu_item': menu_item
        }
    
    def _window_management(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform window management operations"""
        operation = parameters.get('operation')  # 'minimize', 'maximize', 'close', 'switch'
        
        if not operation:
            raise ValueError("Window operation is required")
        
        actions_performed = []
        
        if operation == 'minimize':
            # Alt + Space, then N
            alt_space_result = self.keyboard.execute_action({
                'action_type': 'key_combination',
                'keys': ['alt', 'space']
            })
            actions_performed.append(('alt_space', alt_space_result))
            
            time.sleep(self.default_delay)
            
            n_result = self.keyboard.execute_action({
                'action_type': 'press_key',
                'key': 'n'
            })
            actions_performed.append(('minimize', n_result))
            
        elif operation == 'maximize':
            # Alt + Space, then X
            alt_space_result = self.keyboard.execute_action({
                'action_type': 'key_combination',
                'keys': ['alt', 'space']
            })
            actions_performed.append(('alt_space', alt_space_result))
            
            time.sleep(self.default_delay)
            
            x_result = self.keyboard.execute_action({
                'action_type': 'press_key',
                'key': 'x'
            })
            actions_performed.append(('maximize', x_result))
            
        elif operation == 'close':
            # Alt + F4
            close_result = self.keyboard.execute_action({
                'action_type': 'key_combination',
                'keys': ['alt', 'f4']
            })
            actions_performed.append(('close', close_result))
            
        elif operation == 'switch':
            # Alt + Tab
            switch_result = self.keyboard.execute_action({
                'action_type': 'shortcut',
                'shortcut_name': 'alt_tab'
            })
            actions_performed.append(('switch', switch_result))
        
        return {
            'actions_performed': actions_performed,
            'operation': operation
        }
    
    def _form_filling(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fill form fields"""
        fields = parameters.get('fields', [])  # List of field definitions
        
        if not fields:
            raise ValueError("Fields list is required")
        
        actions_performed = []
        
        for field in fields:
            field_x = field.get('x')
            field_y = field.get('y')
            field_value = field.get('value', '')
            field_type = field.get('type', 'text')  # 'text', 'select', 'checkbox'
            
            if field_x is None or field_y is None:
                continue
            
            # Click on field
            click_result = self.mouse.execute_action({
                'action_type': 'click',
                'x': field_x,
                'y': field_y
            })
            actions_performed.append(('click_field', click_result))
            
            time.sleep(self.default_delay)
            
            if field_type == 'text':
                # Clear and type value
                select_all_result = self.keyboard.execute_action({
                    'action_type': 'shortcut',
                    'shortcut_name': 'select_all'
                })
                actions_performed.append(('select_all', select_all_result))
                
                type_result = self.keyboard.execute_action({
                    'action_type': 'type_text',
                    'text': field_value
                })
                actions_performed.append(('type_value', type_result))
                
            elif field_type == 'checkbox':
                # Just click (toggle)
                pass  # Already clicked above
                
            # Tab to next field
            tab_result = self.keyboard.execute_action({
                'action_type': 'press_key',
                'key': 'tab'
            })
            actions_performed.append(('tab_next', tab_result))
        
        return {
            'actions_performed': actions_performed,
            'fields_filled': len(fields)
        }
    
    def _text_selection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced text selection operations"""
        selection_type = parameters.get('selection_type')  # 'word', 'line', 'paragraph', 'all'
        x = parameters.get('x')
        y = parameters.get('y')
        
        actions_performed = []
        
        if x is not None and y is not None:
            # Click at position first
            click_result = self.mouse.execute_action({
                'action_type': 'click',
                'x': x,
                'y': y
            })
            actions_performed.append(('click', click_result))
            time.sleep(self.default_delay)
        
        if selection_type == 'word':
            # Double-click to select word
            if x is not None and y is not None:
                double_click_result = self.mouse.execute_action({
                    'action_type': 'click',
                    'x': x,
                    'y': y,
                    'click_type': 'double'
                })
                actions_performed.append(('double_click', double_click_result))
                
        elif selection_type == 'line':
            # Triple-click to select line
            if x is not None and y is not None:
                triple_click_result = self.mouse.execute_action({
                    'action_type': 'click',
                    'x': x,
                    'y': y,
                    'click_type': 'triple'
                })
                actions_performed.append(('triple_click', triple_click_result))
                
        elif selection_type == 'paragraph':
            # Ctrl+Shift+Down to select paragraph
            select_paragraph_result = self.keyboard.execute_action({
                'action_type': 'key_combination',
                'keys': ['ctrl', 'shift', 'down']
            })
            actions_performed.append(('select_paragraph', select_paragraph_result))
            
        elif selection_type == 'all':
            # Ctrl+A to select all
            select_all_result = self.keyboard.execute_action({
                'action_type': 'shortcut',
                'shortcut_name': 'select_all'
            })
            actions_performed.append(('select_all', select_all_result))
        
        return {
            'actions_performed': actions_performed,
            'selection_type': selection_type,
            'position': (x, y) if x is not None and y is not None else None
        }
    
    def is_ready(self) -> bool:
        """Check if input coordinator is ready"""
        return self.initialized and self.mouse and self.keyboard
    
    def get_status(self) -> Dict[str, Any]:
        """Get input coordinator status"""
        return {
            'initialized': self.initialized,
            'coordinated_actions': self.coordinated_actions,
            'successful_actions': self.successful_actions,
            'failed_actions': self.failed_actions,
            'success_rate': (self.successful_actions / max(self.coordinated_actions, 1)) * 100,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'controllers_ready': {
                'mouse': self.mouse.is_ready() if self.mouse else False,
                'keyboard': self.keyboard.is_ready() if self.keyboard else False
            }
        }
    
    def shutdown(self):
        """Shutdown input coordinator"""
        self.logger.info("🛑 Shutting down input coordinator")
        self.initialized = False
        self.logger.info("✅ Input coordinator shutdown complete")
