"""
📱 Orion Vision Core - Mobile UI Framework
Touch-optimized user interface framework

This module provides mobile UI capabilities:
- Touch-optimized UI components
- Responsive design system
- Mobile gesture recognition
- Adaptive layouts and themes
- Accessibility features

Sprint 9.2: Mobile Integration and Cross-Platform
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime
import json

from .mobile_app_foundation import PlatformType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComponentType(Enum):
    """UI component types"""
    BUTTON = "button"
    TEXT_INPUT = "text_input"
    LABEL = "label"
    IMAGE = "image"
    LIST = "list"
    CARD = "card"
    NAVIGATION = "navigation"
    TAB_BAR = "tab_bar"
    MODAL = "modal"
    ALERT = "alert"
    PROGRESS = "progress"
    SWITCH = "switch"
    SLIDER = "slider"

class GestureType(Enum):
    """Touch gesture types"""
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    PINCH_IN = "pinch_in"
    PINCH_OUT = "pinch_out"
    ROTATE = "rotate"
    PAN = "pan"

class ThemeMode(Enum):
    """UI theme modes"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    HIGH_CONTRAST = "high_contrast"

class LayoutType(Enum):
    """Layout types"""
    LINEAR = "linear"
    GRID = "grid"
    STACK = "stack"
    FLEX = "flex"
    ABSOLUTE = "absolute"

@dataclass
class TouchEvent:
    """Touch event data"""
    gesture_type: GestureType
    x: float
    y: float
    timestamp: datetime = field(default_factory=datetime.now)
    pressure: float = 1.0
    size: float = 1.0
    velocity: Optional[Tuple[float, float]] = None
    target_component: Optional[str] = None

@dataclass
class UIComponent:
    """UI component definition"""
    component_id: str
    component_type: ComponentType
    x: float = 0.0
    y: float = 0.0
    width: float = 100.0
    height: float = 50.0
    visible: bool = True
    enabled: bool = True
    style: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    children: List['UIComponent'] = field(default_factory=list)
    event_handlers: Dict[str, Callable] = field(default_factory=dict)

@dataclass
class Layout:
    """UI layout definition"""
    layout_id: str
    layout_type: LayoutType
    components: List[UIComponent] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    responsive_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Theme:
    """UI theme definition"""
    theme_id: str
    mode: ThemeMode
    colors: Dict[str, str] = field(default_factory=dict)
    fonts: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    spacing: Dict[str, float] = field(default_factory=dict)
    borders: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    shadows: Dict[str, Dict[str, Any]] = field(default_factory=dict)

class TouchHandler:
    """Touch gesture handler"""
    
    def __init__(self):
        """Initialize touch handler"""
        self.gesture_handlers: Dict[GestureType, List[Callable]] = {}
        self.touch_history: List[TouchEvent] = []
        self.gesture_recognition_enabled = True
        
        # Gesture recognition parameters
        self.tap_threshold = 0.3  # seconds
        self.long_press_threshold = 1.0  # seconds
        self.swipe_threshold = 50.0  # pixels
        self.pinch_threshold = 0.1  # scale factor
        
        logger.info("👆 Touch handler initialized")
    
    def register_gesture_handler(self, gesture: GestureType, handler: Callable):
        """Register a gesture event handler"""
        
        if gesture not in self.gesture_handlers:
            self.gesture_handlers[gesture] = []
        
        self.gesture_handlers[gesture].append(handler)
        logger.info(f"📡 Registered handler for {gesture.value}")
    
    async def process_touch_event(self, event: TouchEvent):
        """Process a touch event and recognize gestures"""
        
        if not self.gesture_recognition_enabled:
            return
        
        # Store touch event
        self.touch_history.append(event)
        
        # Limit history size
        if len(self.touch_history) > 100:
            self.touch_history = self.touch_history[-50:]
        
        # Recognize gesture
        recognized_gesture = await self._recognize_gesture(event)
        
        if recognized_gesture:
            await self._trigger_gesture_handlers(recognized_gesture, event)
    
    async def _recognize_gesture(self, current_event: TouchEvent) -> Optional[GestureType]:
        """Recognize gesture from touch events"""
        
        if len(self.touch_history) < 2:
            return current_event.gesture_type
        
        # Simple gesture recognition logic
        # In real implementation, this would be more sophisticated
        
        recent_events = self.touch_history[-5:]  # Last 5 events
        
        # Check for swipe gestures
        if len(recent_events) >= 3:
            start_event = recent_events[0]
            end_event = recent_events[-1]
            
            dx = end_event.x - start_event.x
            dy = end_event.y - start_event.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance > self.swipe_threshold:
                if abs(dx) > abs(dy):
                    return GestureType.SWIPE_RIGHT if dx > 0 else GestureType.SWIPE_LEFT
                else:
                    return GestureType.SWIPE_DOWN if dy > 0 else GestureType.SWIPE_UP
        
        return current_event.gesture_type
    
    async def _trigger_gesture_handlers(self, gesture: GestureType, event: TouchEvent):
        """Trigger registered gesture handlers"""
        
        if gesture in self.gesture_handlers:
            for handler in self.gesture_handlers[gesture]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"❌ Gesture handler error: {e}")

class MobileUIFramework:
    """
    Touch-optimized mobile UI framework for Orion Vision Core.
    
    Provides comprehensive mobile UI capabilities with:
    - Touch-optimized UI components
    - Responsive design system
    - Mobile gesture recognition
    - Adaptive layouts and themes
    - Cross-platform compatibility
    """
    
    def __init__(self, platform: PlatformType):
        """
        Initialize the mobile UI framework.
        
        Args:
            platform: Target platform type
        """
        self.platform = platform
        self.touch_handler = TouchHandler()
        
        # UI state
        self.components: Dict[str, UIComponent] = {}
        self.layouts: Dict[str, Layout] = {}
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        
        # Screen properties
        self.screen_width = 375.0  # Default iPhone width
        self.screen_height = 812.0  # Default iPhone height
        self.screen_density = 2.0
        self.safe_area_insets = {"top": 44, "bottom": 34, "left": 0, "right": 0}
        
        # Framework state
        self.is_initialized = False
        self.accessibility_enabled = True
        self.animation_enabled = True
        
        # Performance metrics
        self.ui_metrics = {
            "components_rendered": 0,
            "gestures_processed": 0,
            "layout_calculations": 0,
            "theme_switches": 0,
            "average_render_time": 0.0
        }
        
        # Initialize default themes
        self._initialize_default_themes()
        
        logger.info(f"📱 Mobile UI Framework initialized for {platform.value}")
    
    def _initialize_default_themes(self):
        """Initialize default UI themes"""
        
        # Light theme
        light_theme = Theme(
            theme_id="light",
            mode=ThemeMode.LIGHT,
            colors={
                "primary": "#007AFF",
                "secondary": "#5856D6",
                "background": "#FFFFFF",
                "surface": "#F2F2F7",
                "text_primary": "#000000",
                "text_secondary": "#8E8E93",
                "accent": "#FF3B30",
                "success": "#34C759",
                "warning": "#FF9500",
                "error": "#FF3B30"
            },
            fonts={
                "title": {"family": "SF Pro Display", "size": 28, "weight": "bold"},
                "headline": {"family": "SF Pro Display", "size": 22, "weight": "semibold"},
                "body": {"family": "SF Pro Text", "size": 17, "weight": "regular"},
                "caption": {"family": "SF Pro Text", "size": 12, "weight": "regular"}
            },
            spacing={
                "xs": 4.0,
                "sm": 8.0,
                "md": 16.0,
                "lg": 24.0,
                "xl": 32.0
            },
            borders={
                "thin": {"width": 1, "color": "#E5E5EA"},
                "medium": {"width": 2, "color": "#D1D1D6"},
                "thick": {"width": 4, "color": "#C7C7CC"}
            },
            shadows={
                "small": {"x": 0, "y": 1, "blur": 3, "color": "rgba(0,0,0,0.1)"},
                "medium": {"x": 0, "y": 4, "blur": 6, "color": "rgba(0,0,0,0.1)"},
                "large": {"x": 0, "y": 8, "blur": 16, "color": "rgba(0,0,0,0.15)"}
            }
        )
        
        # Dark theme
        dark_theme = Theme(
            theme_id="dark",
            mode=ThemeMode.DARK,
            colors={
                "primary": "#0A84FF",
                "secondary": "#5E5CE6",
                "background": "#000000",
                "surface": "#1C1C1E",
                "text_primary": "#FFFFFF",
                "text_secondary": "#8E8E93",
                "accent": "#FF453A",
                "success": "#30D158",
                "warning": "#FF9F0A",
                "error": "#FF453A"
            },
            fonts=light_theme.fonts,  # Same fonts
            spacing=light_theme.spacing,  # Same spacing
            borders={
                "thin": {"width": 1, "color": "#38383A"},
                "medium": {"width": 2, "color": "#48484A"},
                "thick": {"width": 4, "color": "#58585A"}
            },
            shadows={
                "small": {"x": 0, "y": 1, "blur": 3, "color": "rgba(0,0,0,0.3)"},
                "medium": {"x": 0, "y": 4, "blur": 6, "color": "rgba(0,0,0,0.3)"},
                "large": {"x": 0, "y": 8, "blur": 16, "color": "rgba(0,0,0,0.4)"}
            }
        )
        
        # Store themes
        self.themes = {
            "light": light_theme,
            "dark": dark_theme
        }
        
        # Set default theme
        self.current_theme = light_theme
    
    async def initialize(self, screen_width: float, screen_height: float, screen_density: float = 2.0) -> bool:
        """
        Initialize the UI framework with screen properties.
        
        Args:
            screen_width: Screen width in points
            screen_height: Screen height in points
            screen_density: Screen density multiplier
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.screen_width = screen_width
            self.screen_height = screen_height
            self.screen_density = screen_density
            
            # Calculate safe area insets based on platform
            await self._calculate_safe_area_insets()
            
            # Initialize touch handling
            await self._initialize_touch_handling()
            
            # Setup accessibility
            await self._setup_accessibility()
            
            self.is_initialized = True
            
            logger.info(f"✅ UI Framework initialized: {screen_width}x{screen_height} @{screen_density}x")
            return True
            
        except Exception as e:
            logger.error(f"❌ UI Framework initialization failed: {e}")
            return False
    
    async def _calculate_safe_area_insets(self):
        """Calculate safe area insets based on platform"""
        
        if self.platform == PlatformType.IOS:
            # iPhone safe area insets (simplified)
            if self.screen_height >= 812:  # iPhone X and newer
                self.safe_area_insets = {"top": 44, "bottom": 34, "left": 0, "right": 0}
            else:  # Older iPhones
                self.safe_area_insets = {"top": 20, "bottom": 0, "left": 0, "right": 0}
        elif self.platform == PlatformType.ANDROID:
            # Android safe area (simplified)
            self.safe_area_insets = {"top": 24, "bottom": 0, "left": 0, "right": 0}
        else:
            # Default safe area
            self.safe_area_insets = {"top": 0, "bottom": 0, "left": 0, "right": 0}
    
    async def _initialize_touch_handling(self):
        """Initialize touch event handling"""
        
        # Register default gesture handlers
        self.touch_handler.register_gesture_handler(GestureType.TAP, self._handle_tap)
        self.touch_handler.register_gesture_handler(GestureType.SWIPE_LEFT, self._handle_swipe_left)
        self.touch_handler.register_gesture_handler(GestureType.SWIPE_RIGHT, self._handle_swipe_right)
        
        logger.info("👆 Touch handling initialized")
    
    async def _setup_accessibility(self):
        """Setup accessibility features"""
        
        if self.accessibility_enabled:
            # Setup accessibility features
            logger.info("♿ Accessibility features enabled")
    
    async def _handle_tap(self, event: TouchEvent):
        """Handle tap gesture"""
        logger.info(f"👆 Tap at ({event.x}, {event.y})")
        self.ui_metrics["gestures_processed"] += 1
    
    async def _handle_swipe_left(self, event: TouchEvent):
        """Handle swipe left gesture"""
        logger.info("👈 Swipe left detected")
        self.ui_metrics["gestures_processed"] += 1
    
    async def _handle_swipe_right(self, event: TouchEvent):
        """Handle swipe right gesture"""
        logger.info("👉 Swipe right detected")
        self.ui_metrics["gestures_processed"] += 1
    
    def create_component(self, component_id: str, component_type: ComponentType, 
                        x: float = 0, y: float = 0, width: float = 100, height: float = 50,
                        **properties) -> UIComponent:
        """
        Create a UI component.
        
        Args:
            component_id: Unique component identifier
            component_type: Type of component
            x, y: Position coordinates
            width, height: Component dimensions
            **properties: Additional component properties
            
        Returns:
            Created UIComponent
        """
        component = UIComponent(
            component_id=component_id,
            component_type=component_type,
            x=x,
            y=y,
            width=width,
            height=height,
            properties=properties
        )
        
        # Apply theme styling
        if self.current_theme:
            component.style = self._apply_theme_styling(component_type)
        
        self.components[component_id] = component
        self.ui_metrics["components_rendered"] += 1
        
        logger.info(f"🔧 Created component: {component_id} ({component_type.value})")
        return component
    
    def _apply_theme_styling(self, component_type: ComponentType) -> Dict[str, Any]:
        """Apply theme styling to component"""
        
        if not self.current_theme:
            return {}
        
        theme = self.current_theme
        
        # Base styling for all components
        base_style = {
            "background_color": theme.colors.get("surface", "#FFFFFF"),
            "text_color": theme.colors.get("text_primary", "#000000"),
            "border_color": theme.borders.get("thin", {}).get("color", "#E5E5EA")
        }
        
        # Component-specific styling
        if component_type == ComponentType.BUTTON:
            base_style.update({
                "background_color": theme.colors.get("primary", "#007AFF"),
                "text_color": "#FFFFFF",
                "border_radius": 8,
                "padding": theme.spacing.get("md", 16)
            })
        elif component_type == ComponentType.TEXT_INPUT:
            base_style.update({
                "background_color": theme.colors.get("background", "#FFFFFF"),
                "border_width": 1,
                "border_radius": 8,
                "padding": theme.spacing.get("md", 16)
            })
        
        return base_style
    
    def create_layout(self, layout_id: str, layout_type: LayoutType, 
                     components: Optional[List[UIComponent]] = None) -> Layout:
        """
        Create a UI layout.
        
        Args:
            layout_id: Unique layout identifier
            layout_type: Type of layout
            components: List of components in layout
            
        Returns:
            Created Layout
        """
        layout = Layout(
            layout_id=layout_id,
            layout_type=layout_type,
            components=components or []
        )
        
        self.layouts[layout_id] = layout
        self.ui_metrics["layout_calculations"] += 1
        
        logger.info(f"📐 Created layout: {layout_id} ({layout_type.value})")
        return layout
    
    async def switch_theme(self, theme_id: str) -> bool:
        """
        Switch to a different theme.
        
        Args:
            theme_id: Theme identifier
            
        Returns:
            True if switch successful, False otherwise
        """
        if theme_id not in self.themes:
            logger.error(f"❌ Theme not found: {theme_id}")
            return False
        
        try:
            old_theme = self.current_theme.theme_id if self.current_theme else "none"
            self.current_theme = self.themes[theme_id]
            
            # Re-apply styling to all components
            await self._reapply_theme_styling()
            
            self.ui_metrics["theme_switches"] += 1
            
            logger.info(f"🎨 Theme switched: {old_theme} → {theme_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Theme switch failed: {e}")
            return False
    
    async def _reapply_theme_styling(self):
        """Re-apply theme styling to all components"""
        
        for component in self.components.values():
            component.style = self._apply_theme_styling(component.component_type)
    
    async def process_touch_event(self, x: float, y: float, gesture: GestureType):
        """
        Process a touch event.
        
        Args:
            x, y: Touch coordinates
            gesture: Gesture type
        """
        event = TouchEvent(
            gesture_type=gesture,
            x=x,
            y=y,
            target_component=self._find_component_at_position(x, y)
        )
        
        await self.touch_handler.process_touch_event(event)
    
    def _find_component_at_position(self, x: float, y: float) -> Optional[str]:
        """Find component at given position"""
        
        for component_id, component in self.components.items():
            if (component.x <= x <= component.x + component.width and
                component.y <= y <= component.y + component.height and
                component.visible):
                return component_id
        
        return None
    
    def get_component(self, component_id: str) -> Optional[UIComponent]:
        """Get component by ID"""
        return self.components.get(component_id)
    
    def get_layout(self, layout_id: str) -> Optional[Layout]:
        """Get layout by ID"""
        return self.layouts.get(layout_id)
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get current theme"""
        return self.current_theme
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme IDs"""
        return list(self.themes.keys())
    
    def get_screen_info(self) -> Dict[str, Any]:
        """Get screen information"""
        return {
            "width": self.screen_width,
            "height": self.screen_height,
            "density": self.screen_density,
            "safe_area_insets": self.safe_area_insets,
            "platform": self.platform.value
        }
    
    def get_ui_metrics(self) -> Dict[str, Any]:
        """Get UI framework metrics"""
        return {
            **self.ui_metrics,
            "total_components": len(self.components),
            "total_layouts": len(self.layouts),
            "available_themes": len(self.themes),
            "current_theme": self.current_theme.theme_id if self.current_theme else None,
            "accessibility_enabled": self.accessibility_enabled,
            "animation_enabled": self.animation_enabled
        }
    
    def get_framework_info(self) -> Dict[str, Any]:
        """Get comprehensive framework information"""
        return {
            "platform": self.platform.value,
            "initialized": self.is_initialized,
            "screen_info": self.get_screen_info(),
            "ui_metrics": self.get_ui_metrics(),
            "touch_handler": {
                "gesture_recognition_enabled": self.touch_handler.gesture_recognition_enabled,
                "registered_gestures": len(self.touch_handler.gesture_handlers),
                "touch_history_size": len(self.touch_handler.touch_history)
            },
            "components": {
                component_id: {
                    "type": component.component_type.value,
                    "visible": component.visible,
                    "enabled": component.enabled,
                    "position": {"x": component.x, "y": component.y},
                    "size": {"width": component.width, "height": component.height}
                } for component_id, component in self.components.items()
            },
            "layouts": {
                layout_id: {
                    "type": layout.layout_type.value,
                    "components_count": len(layout.components)
                } for layout_id, layout in self.layouts.items()
            }
        }
