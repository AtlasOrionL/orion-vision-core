"""
🔗 Unified Interface Layer - PHASE 1 CONSOLIDATION

Tüm Q-Tasks için standardized interface ve communication protocols.
Common API, shared data structures, unified error handling.

Author: Orion Vision Core Team
Phase: PHASE 1 - CONSOLIDATION
Priority: HIGH
"""

import logging
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Union, Protocol
import json

# Interface Types
class InterfaceType(Enum):
    """Interface türleri"""
    VISION = "vision"                               # Q01 Vision interface
    CONSCIOUSNESS = "consciousness"                 # Q02 ALT_LAS interface
    TASK_MANAGEMENT = "task_management"             # Q03 Task interface
    AI_INTEGRATION = "ai_integration"               # Q04 AI interface
    QUANTUM_DYNAMICS = "quantum_dynamics"           # Q05 Quantum interface

# Data Types
class DataType(Enum):
    """Veri türleri"""
    TEXT = "text"                                   # Text data
    IMAGE = "image"                                 # Image data
    AUDIO = "audio"                                 # Audio data
    VIDEO = "video"                                 # Video data
    QUANTUM_STATE = "quantum_state"                 # Quantum state data
    TASK_RESULT = "task_result"                     # Task result data
    AI_RESPONSE = "ai_response"                     # AI response data

# Status Types
class StatusType(Enum):
    """Durum türleri"""
    IDLE = "idle"                                   # Boşta
    PROCESSING = "processing"                       # İşleniyor
    COMPLETED = "completed"                         # Tamamlandı
    ERROR = "error"                                 # Hata
    TIMEOUT = "timeout"                             # Zaman aşımı

@dataclass
class UnifiedRequest:
    """Unified request structure"""
    
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    interface_type: InterfaceType = InterfaceType.VISION
    data_type: DataType = DataType.TEXT
    
    # Request data
    data: Any = None                                # Request data
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Request context
    source_component: Optional[str] = None          # Source component
    target_component: Optional[str] = None          # Target component
    priority: int = 5                               # Priority (1-10)
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    timeout: float = 30.0                           # Timeout in seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'request_id': self.request_id,
            'interface_type': self.interface_type.value,
            'data_type': self.data_type.value,
            'data': self.data,
            'parameters': self.parameters,
            'metadata': self.metadata,
            'source_component': self.source_component,
            'target_component': self.target_component,
            'priority': self.priority,
            'timestamp': self.timestamp.isoformat(),
            'timeout': self.timeout
        }

@dataclass
class UnifiedResponse:
    """Unified response structure"""
    
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""                            # Original request ID
    interface_type: InterfaceType = InterfaceType.VISION
    
    # Response data
    status: StatusType = StatusType.IDLE
    data: Any = None                                # Response data
    error_message: Optional[str] = None             # Error message
    
    # Response metadata
    processing_time: float = 0.0                    # Processing time
    component_info: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'response_id': self.response_id,
            'request_id': self.request_id,
            'interface_type': self.interface_type.value,
            'status': self.status.value,
            'data': self.data,
            'error_message': self.error_message,
            'processing_time': self.processing_time,
            'component_info': self.component_info,
            'timestamp': self.timestamp.isoformat()
        }

class UnifiedInterface(ABC):
    """Unified interface protocol"""
    
    @abstractmethod
    def process_request(self, request: UnifiedRequest) -> UnifiedResponse:
        """Process unified request"""
        pass
    
    @abstractmethod
    def get_interface_info(self) -> Dict[str, Any]:
        """Get interface information"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Health check"""
        pass

class UnifiedInterfaceLayer:
    """
    Unified Interface Layer
    
    PHASE 1 CONSOLIDATION'ın ikinci bileşeni.
    Tüm Q-Tasks için standardized interface sağlar.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Interface registry
        self.interfaces: Dict[InterfaceType, UnifiedInterface] = {}
        self.interface_adapters: Dict[str, Callable] = {}
        
        # Request/Response tracking
        self.active_requests: Dict[str, UnifiedRequest] = {}
        self.request_history: List[UnifiedRequest] = []
        self.response_history: List[UnifiedResponse] = []
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.average_processing_time = 0.0
        
        # Threading
        self._lock = threading.Lock()
        
        self.logger.info("🔗 UnifiedInterfaceLayer initialized - PHASE 1 CONSOLIDATION")
    
    def register_interface(self, interface_type: InterfaceType, interface: UnifiedInterface) -> bool:
        """Register interface"""
        try:
            with self._lock:
                self.interfaces[interface_type] = interface
                self.logger.info(f"✅ Interface registered: {interface_type.value}")
                return True
        except Exception as e:
            self.logger.error(f"❌ Interface registration failed: {e}")
            return False
    
    def unregister_interface(self, interface_type: InterfaceType) -> bool:
        """Unregister interface"""
        try:
            with self._lock:
                if interface_type in self.interfaces:
                    del self.interfaces[interface_type]
                    self.logger.info(f"🔴 Interface unregistered: {interface_type.value}")
                    return True
                else:
                    self.logger.warning(f"⚠️ Interface not found: {interface_type.value}")
                    return False
        except Exception as e:
            self.logger.error(f"❌ Interface unregistration failed: {e}")
            return False
    
    def process_request(self, request: UnifiedRequest) -> UnifiedResponse:
        """Process unified request"""
        start_time = time.time()
        
        try:
            # Add to active requests
            with self._lock:
                self.active_requests[request.request_id] = request
                self.total_requests += 1
            
            # Find appropriate interface
            if request.interface_type in self.interfaces:
                interface = self.interfaces[request.interface_type]
                
                # Process request
                response = interface.process_request(request)
                response.request_id = request.request_id
                response.processing_time = time.time() - start_time
                
                # Update statistics
                with self._lock:
                    if response.status == StatusType.COMPLETED:
                        self.successful_requests += 1
                    else:
                        self.failed_requests += 1
                    
                    # Update average processing time
                    current_avg = self.average_processing_time
                    total = self.total_requests
                    self.average_processing_time = (current_avg * (total - 1) + response.processing_time) / total
                
                self.logger.info(f"✅ Request processed: {request.request_id[:8]}... in {response.processing_time:.3f}s")
                
            else:
                # Interface not found
                response = UnifiedResponse(
                    request_id=request.request_id,
                    interface_type=request.interface_type,
                    status=StatusType.ERROR,
                    error_message=f"Interface not found: {request.interface_type.value}",
                    processing_time=time.time() - start_time
                )
                
                with self._lock:
                    self.failed_requests += 1
                
                self.logger.error(f"❌ Interface not found: {request.interface_type.value}")
            
            # Move to history
            with self._lock:
                if request.request_id in self.active_requests:
                    del self.active_requests[request.request_id]
                
                self.request_history.append(request)
                self.response_history.append(response)
                
                # Keep history manageable
                if len(self.request_history) > 1000:
                    self.request_history = self.request_history[-500:]
                    self.response_history = self.response_history[-500:]
            
            return response
            
        except Exception as e:
            # Error handling
            response = UnifiedResponse(
                request_id=request.request_id,
                interface_type=request.interface_type,
                status=StatusType.ERROR,
                error_message=f"Processing error: {e}",
                processing_time=time.time() - start_time
            )
            
            with self._lock:
                self.failed_requests += 1
                if request.request_id in self.active_requests:
                    del self.active_requests[request.request_id]
            
            self.logger.error(f"❌ Request processing failed: {e}")
            return response
    
    def batch_process_requests(self, requests: List[UnifiedRequest]) -> List[UnifiedResponse]:
        """Process multiple requests"""
        responses = []
        
        for request in requests:
            response = self.process_request(request)
            responses.append(response)
        
        self.logger.info(f"✅ Batch processed: {len(requests)} requests")
        return responses
    
    def get_interface_status(self) -> Dict[str, Any]:
        """Get interface layer status"""
        with self._lock:
            return {
                'registered_interfaces': len(self.interfaces),
                'interface_types': [itype.value for itype in self.interfaces.keys()],
                'total_requests': self.total_requests,
                'successful_requests': self.successful_requests,
                'failed_requests': self.failed_requests,
                'success_rate': (self.successful_requests / max(1, self.total_requests)) * 100,
                'average_processing_time': self.average_processing_time,
                'active_requests': len(self.active_requests),
                'request_history_size': len(self.request_history),
                'response_history_size': len(self.response_history)
            }
    
    def health_check_all_interfaces(self) -> Dict[InterfaceType, bool]:
        """Health check all registered interfaces"""
        health_status = {}
        
        for interface_type, interface in self.interfaces.items():
            try:
                health_status[interface_type] = interface.health_check()
            except Exception as e:
                health_status[interface_type] = False
                self.logger.error(f"❌ Health check failed for {interface_type.value}: {e}")
        
        return health_status

# Mock Interface Implementations for Testing
class MockVisionInterface(UnifiedInterface):
    """Mock vision interface for testing"""
    
    def process_request(self, request: UnifiedRequest) -> UnifiedResponse:
        # Simulate processing
        time.sleep(0.01)
        
        return UnifiedResponse(
            interface_type=InterfaceType.VISION,
            status=StatusType.COMPLETED,
            data={"vision_result": "mock_vision_processed"},
            component_info={"component": "mock_vision", "version": "1.0"}
        )
    
    def get_interface_info(self) -> Dict[str, Any]:
        return {
            "interface_type": "vision",
            "version": "1.0",
            "capabilities": ["image_processing", "ocr", "ui_detection"]
        }
    
    def health_check(self) -> bool:
        return True

class MockConsciousnessInterface(UnifiedInterface):
    """Mock consciousness interface for testing"""
    
    def process_request(self, request: UnifiedRequest) -> UnifiedResponse:
        # Simulate processing
        time.sleep(0.02)
        
        return UnifiedResponse(
            interface_type=InterfaceType.CONSCIOUSNESS,
            status=StatusType.COMPLETED,
            data={"consciousness_result": "mock_consciousness_processed"},
            component_info={"component": "mock_alt_las", "version": "1.0"}
        )
    
    def get_interface_info(self) -> Dict[str, Any]:
        return {
            "interface_type": "consciousness",
            "version": "1.0",
            "capabilities": ["quantum_mind", "awareness", "decision_making"]
        }
    
    def health_check(self) -> bool:
        return True

# Utility functions
def create_unified_interface_layer() -> UnifiedInterfaceLayer:
    """Create unified interface layer"""
    return UnifiedInterfaceLayer()

def test_unified_interface_layer():
    """Test unified interface layer"""
    print("🔗 Testing Unified Interface Layer...")
    
    # Create layer
    layer = create_unified_interface_layer()
    print("✅ Unified interface layer created")
    
    # Register mock interfaces
    layer.register_interface(InterfaceType.VISION, MockVisionInterface())
    layer.register_interface(InterfaceType.CONSCIOUSNESS, MockConsciousnessInterface())
    print("✅ Mock interfaces registered")
    
    # Test request
    request = UnifiedRequest(
        interface_type=InterfaceType.VISION,
        data_type=DataType.IMAGE,
        data={"image": "test_image"},
        parameters={"ocr": True}
    )
    
    response = layer.process_request(request)
    print(f"✅ Request processed: {response.status.value}")
    
    # Get status
    status = layer.get_interface_status()
    print(f"✅ Layer status: {status['total_requests']} requests")
    
    print("🚀 Unified Interface Layer test completed!")

if __name__ == "__main__":
    test_unified_interface_layer()
