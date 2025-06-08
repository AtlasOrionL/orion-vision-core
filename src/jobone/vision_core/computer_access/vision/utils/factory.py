#!/usr/bin/env python3
"""
🏭 Orion Vision Core - Component Factory System
💖 DUYGULANDIK! SEN YAPARSIN! FACTORY POWER!

Bu modül tüm vision bileşenlerini merkezi olarak oluşturur ve yönetir.
Design patterns kullanarak temiz ve sürdürülebilir kod sağlar.

Author: Orion Vision Core Team
Status: 🚀 ACTIVE DEVELOPMENT
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from enum import Enum

try:
    from config.config import get_config, VisionConfig
except ImportError:
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from config.config import get_config, VisionConfig
    except ImportError:
        get_config = None
        VisionConfig = None

# Import all components with new modular structure
try:
    from core.capture.screen_capture import ScreenCapture
    from core.ocr.ocr_engine import OCREngine
    from core.detection.ui_element_detector import UIElementDetector
    from core.pipeline.visual_processing_pipeline import VisualProcessingPipeline
    from integration.keyboard.visual_keyboard_integration import VisualKeyboardIntegration
    from integration.mouse.visual_mouse_integration import VisualMouseIntegration
    from integration.autonomous.autonomous_action_system import AutonomousActionSystem
    from execution.tasks.task_execution_engine import TaskExecutionEngine
    from execution.chat.simple_chat_executor import SimpleChatExecutor
except ImportError as e:
    logging.warning(f"⚠️ Import warning: {e}")
    # Set to None if import fails
    ScreenCapture = None
    OCREngine = None
    UIElementDetector = None
    VisualProcessingPipeline = None
    VisualKeyboardIntegration = None
    VisualMouseIntegration = None
    AutonomousActionSystem = None
    TaskExecutionEngine = None
    SimpleChatExecutor = None

class ComponentType(Enum):
    """🎯 Vision Component Types"""
    SCREEN_CAPTURE = "screen_capture"
    OCR_ENGINE = "ocr_engine"
    UI_DETECTOR = "ui_detector"
    VISUAL_PIPELINE = "visual_pipeline"
    KEYBOARD_INTEGRATION = "keyboard_integration"
    MOUSE_INTEGRATION = "mouse_integration"
    AUTONOMOUS_ACTION = "autonomous_action"
    TASK_ENGINE = "task_engine"
    CHAT_EXECUTOR = "chat_executor"

class VisionComponent(ABC):
    """🎯 Abstract base class for all vision components"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """🚀 Initialize the component"""
        pass
    
    @abstractmethod
    def shutdown(self):
        """🛑 Shutdown the component"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """📊 Get component status"""
        pass

class ComponentFactory:
    """🏭 Factory for creating vision components"""
    
    _component_registry: Dict[ComponentType, Type] = {}
    _instances: Dict[ComponentType, Any] = {}
    
    @classmethod
    def register_component(cls, component_type: ComponentType, component_class: Type):
        """📝 Register a component class"""
        cls._component_registry[component_type] = component_class
        logging.info(f"✅ Registered component: {component_type.value}")
    
    @classmethod
    def create_component(cls, component_type: ComponentType, **kwargs) -> Optional[Any]:
        """🏭 Create a component instance"""
        if component_type not in cls._component_registry:
            logging.error(f"❌ Unknown component type: {component_type.value}")
            return None
        
        try:
            component_class = cls._component_registry[component_type]
            instance = component_class(**kwargs)
            logging.info(f"✅ Created component: {component_type.value}")
            return instance
        except Exception as e:
            logging.error(f"❌ Failed to create {component_type.value}: {e}")
            return None
    
    @classmethod
    def get_singleton(cls, component_type: ComponentType, **kwargs) -> Optional[Any]:
        """🎯 Get singleton instance of component"""
        if component_type not in cls._instances:
            instance = cls.create_component(component_type, **kwargs)
            if instance:
                cls._instances[component_type] = instance
        
        return cls._instances.get(component_type)
    
    @classmethod
    def clear_singletons(cls):
        """🧹 Clear all singleton instances"""
        for component_type, instance in cls._instances.items():
            try:
                if hasattr(instance, 'shutdown'):
                    instance.shutdown()
            except Exception as e:
                logging.warning(f"⚠️ Shutdown warning for {component_type.value}: {e}")
        
        cls._instances.clear()
        logging.info("🧹 All singletons cleared")

class VisionSystemFactory:
    """🎬 High-level factory for vision systems"""
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config or (get_config() if get_config else None)
        self.logger = logging.getLogger('orion.vision.factory')
        self._register_default_components()
    
    def _register_default_components(self):
        """📝 Register all default components"""
        try:
            ComponentFactory.register_component(ComponentType.SCREEN_CAPTURE, ScreenCapture)
            ComponentFactory.register_component(ComponentType.OCR_ENGINE, OCREngine)
            ComponentFactory.register_component(ComponentType.UI_DETECTOR, UIElementDetector)
            ComponentFactory.register_component(ComponentType.VISUAL_PIPELINE, VisualProcessingPipeline)
            ComponentFactory.register_component(ComponentType.KEYBOARD_INTEGRATION, VisualKeyboardIntegration)
            ComponentFactory.register_component(ComponentType.MOUSE_INTEGRATION, VisualMouseIntegration)
            ComponentFactory.register_component(ComponentType.AUTONOMOUS_ACTION, AutonomousActionSystem)
            ComponentFactory.register_component(ComponentType.TASK_ENGINE, TaskExecutionEngine)
            ComponentFactory.register_component(ComponentType.CHAT_EXECUTOR, SimpleChatExecutor)
            
            self.logger.info("✅ All default components registered")
        except Exception as e:
            self.logger.warning(f"⚠️ Component registration warning: {e}")
    
    def create_screen_capture(self) -> Optional[Any]:
        """📸 Create screen capture component"""
        return ComponentFactory.create_component(ComponentType.SCREEN_CAPTURE)
    
    def create_ocr_engine(self) -> Optional[Any]:
        """🔤 Create OCR engine component"""
        return ComponentFactory.create_component(ComponentType.OCR_ENGINE)
    
    def create_ui_detector(self) -> Optional[Any]:
        """🎯 Create UI detector component"""
        return ComponentFactory.create_component(ComponentType.UI_DETECTOR)
    
    def create_visual_pipeline(self) -> Optional[Any]:
        """🎬 Create visual pipeline component"""
        return ComponentFactory.create_component(ComponentType.VISUAL_PIPELINE)
    
    def create_keyboard_integration(self) -> Optional[Any]:
        """⌨️ Create keyboard integration component"""
        return ComponentFactory.create_component(ComponentType.KEYBOARD_INTEGRATION)
    
    def create_mouse_integration(self) -> Optional[Any]:
        """🖱️ Create mouse integration component"""
        return ComponentFactory.create_component(ComponentType.MOUSE_INTEGRATION)
    
    def create_autonomous_action(self) -> Optional[Any]:
        """🤖 Create autonomous action component"""
        return ComponentFactory.create_component(ComponentType.AUTONOMOUS_ACTION)
    
    def create_task_engine(self) -> Optional[Any]:
        """📝 Create task engine component"""
        return ComponentFactory.create_component(ComponentType.TASK_ENGINE)
    
    def create_chat_executor(self) -> Optional[Any]:
        """💬 Create chat executor component"""
        return ComponentFactory.create_component(ComponentType.CHAT_EXECUTOR)
    
    def create_complete_system(self) -> Dict[str, Any]:
        """🎯 Create complete vision system"""
        self.logger.info("🎬 Creating complete vision system...")
        
        system = {}
        
        # Core components
        system['screen_capture'] = self.create_screen_capture()
        system['ocr_engine'] = self.create_ocr_engine()
        system['ui_detector'] = self.create_ui_detector()
        system['visual_pipeline'] = self.create_visual_pipeline()
        
        # Integration components
        system['keyboard_integration'] = self.create_keyboard_integration()
        system['mouse_integration'] = self.create_mouse_integration()
        
        # High-level components
        system['autonomous_action'] = self.create_autonomous_action()
        system['task_engine'] = self.create_task_engine()
        system['chat_executor'] = self.create_chat_executor()
        
        # Initialize all components
        initialized_count = 0
        for name, component in system.items():
            if component and hasattr(component, 'initialize'):
                try:
                    if component.initialize():
                        initialized_count += 1
                        self.logger.info(f"✅ {name} initialized")
                    else:
                        self.logger.warning(f"⚠️ {name} initialization failed")
                except Exception as e:
                    self.logger.error(f"❌ {name} initialization error: {e}")
        
        self.logger.info(f"🎉 Complete system created: {initialized_count}/{len(system)} components initialized")
        return system
    
    def get_singleton_system(self) -> Dict[str, Any]:
        """🎯 Get singleton instances of all components"""
        system = {}
        
        for component_type in ComponentType:
            component = ComponentFactory.get_singleton(component_type)
            if component:
                system[component_type.value] = component
        
        return system

# Global factory instance
vision_factory = VisionSystemFactory()

def create_screen_capture():
    """📸 Create screen capture component"""
    return vision_factory.create_screen_capture()

def create_ocr_engine():
    """🔤 Create OCR engine component"""
    return vision_factory.create_ocr_engine()

def create_ui_detector():
    """🎯 Create UI detector component"""
    return vision_factory.create_ui_detector()

def create_visual_pipeline():
    """🎬 Create visual pipeline component"""
    return vision_factory.create_visual_pipeline()

def create_autonomous_action():
    """🤖 Create autonomous action component"""
    return vision_factory.create_autonomous_action()

def create_task_engine():
    """📝 Create task engine component"""
    return vision_factory.create_task_engine()

def create_chat_executor():
    """💬 Create chat executor component"""
    return vision_factory.create_chat_executor()

def create_complete_system():
    """🎯 Create complete vision system"""
    return vision_factory.create_complete_system()

# Example usage and testing
if __name__ == "__main__":
    print("🏭 Vision Component Factory Test")
    print("💖 DUYGULANDIK! SEN YAPARSIN!")
    
    # Test individual component creation
    screen_capture = create_screen_capture()
    if screen_capture:
        print("✅ Screen capture created")
    
    # Test complete system creation
    system = create_complete_system()
    print(f"🎯 Complete system created with {len(system)} components")
    
    # Test singleton pattern
    singleton_system = vision_factory.get_singleton_system()
    print(f"🎯 Singleton system has {len(singleton_system)} components")
    
    print("🎉 Factory system test completed!")
