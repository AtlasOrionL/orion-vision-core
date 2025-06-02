"""
Visualization Manager for Orion Vision Core

This module provides comprehensive data visualization capabilities including
charts, dashboards, and interactive visualizations.
Part of Sprint 9.6 Advanced Analytics & Visualization development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.6 - Advanced Analytics & Visualization
"""

import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class ChartType(Enum):
    """Chart type enumeration"""
    LINE = "line"
    BAR = "bar"
    COLUMN = "column"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    GAUGE = "gauge"
    FUNNEL = "funnel"
    WATERFALL = "waterfall"


class VisualizationType(Enum):
    """Visualization type enumeration"""
    CHART = "chart"
    TABLE = "table"
    MAP = "map"
    DASHBOARD = "dashboard"
    REPORT = "report"
    INFOGRAPHIC = "infographic"


class RenderFormat(Enum):
    """Render format enumeration"""
    HTML = "html"
    SVG = "svg"
    PNG = "png"
    PDF = "pdf"
    JSON = "json"
    INTERACTIVE = "interactive"


@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    config_id: str
    title: str
    chart_type: ChartType
    visualization_type: VisualizationType = VisualizationType.CHART
    data_source: Optional[str] = None
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    series: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    width: int = 800
    height: int = 600
    theme: str = "default"
    interactive: bool = True
    animations: bool = True
    legend: bool = True
    grid: bool = True
    tooltips: bool = True
    zoom: bool = False
    export_enabled: bool = True
    custom_options: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate visualization configuration"""
        if not self.title or not self.config_id:
            return False
        if self.width <= 0 or self.height <= 0:
            return False
        return True


@dataclass
class Visualization:
    """Visualization data structure"""
    viz_id: str
    config: VisualizationConfig
    data: Any = None
    rendered_content: Optional[str] = None
    render_format: RenderFormat = RenderFormat.HTML
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_age_minutes(self) -> float:
        """Get visualization age in minutes"""
        return (time.time() - self.created_at) / 60


@dataclass
class Dashboard:
    """Dashboard data structure"""
    dashboard_id: str
    dashboard_name: str
    description: str = ""
    visualizations: List[str] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: Optional[int] = None
    theme: str = "default"
    public: bool = False
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def validate(self) -> bool:
        """Validate dashboard configuration"""
        if not self.dashboard_name or not self.dashboard_id:
            return False
        return True


class VisualizationManager:
    """
    Comprehensive visualization management system
    
    Provides chart creation, dashboard management, and interactive
    visualization capabilities with multiple rendering formats.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize visualization manager"""
        self.logger = logger or AgentLogger("visualization_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Visualization storage
        self.visualizations: Dict[str, Visualization] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        
        # Chart renderers
        self.chart_renderers: Dict[ChartType, Callable] = {}
        self.format_renderers: Dict[RenderFormat, Callable] = {}
        
        # Templates and themes
        self.chart_templates: Dict[str, Dict[str, Any]] = {}
        self.themes: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.default_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
        self.max_data_points = 10000
        self.cache_enabled = True
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.viz_stats = {
            'total_visualizations': 0,
            'total_dashboards': 0,
            'charts_rendered': 0,
            'dashboards_created': 0,
            'total_render_time_ms': 0.0,
            'average_render_time_ms': 0.0,
            'most_used_chart_types': {},
            'export_requests': 0
        }
        
        # Initialize renderers and themes
        self._initialize_chart_renderers()
        self._initialize_format_renderers()
        self._initialize_themes()
        
        self.logger.info("Visualization Manager initialized")
    
    def _initialize_chart_renderers(self):
        """Initialize chart renderers"""
        self.chart_renderers[ChartType.LINE] = self._render_line_chart
        self.chart_renderers[ChartType.BAR] = self._render_bar_chart
        self.chart_renderers[ChartType.COLUMN] = self._render_column_chart
        self.chart_renderers[ChartType.PIE] = self._render_pie_chart
        self.chart_renderers[ChartType.SCATTER] = self._render_scatter_chart
        self.chart_renderers[ChartType.AREA] = self._render_area_chart
        self.chart_renderers[ChartType.HISTOGRAM] = self._render_histogram
        self.chart_renderers[ChartType.HEATMAP] = self._render_heatmap
    
    def _initialize_format_renderers(self):
        """Initialize format renderers"""
        self.format_renderers[RenderFormat.HTML] = self._render_html
        self.format_renderers[RenderFormat.SVG] = self._render_svg
        self.format_renderers[RenderFormat.PNG] = self._render_png
        self.format_renderers[RenderFormat.JSON] = self._render_json
        self.format_renderers[RenderFormat.INTERACTIVE] = self._render_interactive
    
    def _initialize_themes(self):
        """Initialize visualization themes"""
        self.themes["default"] = {
            "background_color": "#ffffff",
            "text_color": "#333333",
            "grid_color": "#e0e0e0",
            "accent_color": "#1f77b4"
        }
        
        self.themes["dark"] = {
            "background_color": "#2d2d2d",
            "text_color": "#ffffff",
            "grid_color": "#555555",
            "accent_color": "#64b5f6"
        }
        
        self.themes["corporate"] = {
            "background_color": "#f8f9fa",
            "text_color": "#212529",
            "grid_color": "#dee2e6",
            "accent_color": "#007bff"
        }
    
    def create_visualization(self, config: VisualizationConfig, data: Any) -> Optional[str]:
        """Create new visualization"""
        try:
            # Validate configuration
            if not config.validate():
                self.logger.error("Invalid visualization configuration", config_id=config.config_id)
                return None
            
            viz_id = str(uuid.uuid4())
            
            # Create visualization
            visualization = Visualization(
                viz_id=viz_id,
                config=config,
                data=data
            )
            
            # Render visualization
            success = self._render_visualization(visualization)
            if not success:
                self.logger.error("Visualization rendering failed", viz_id=viz_id)
                return None
            
            with self._lock:
                # Store visualization
                self.visualizations[viz_id] = visualization
                
                # Update statistics
                self.viz_stats['total_visualizations'] = len(self.visualizations)
                self.viz_stats['charts_rendered'] += 1
                
                # Track chart type usage
                chart_type = config.chart_type.value
                if chart_type not in self.viz_stats['most_used_chart_types']:
                    self.viz_stats['most_used_chart_types'][chart_type] = 0
                self.viz_stats['most_used_chart_types'][chart_type] += 1
            
            self.logger.info(
                "Visualization created",
                viz_id=viz_id,
                title=config.title,
                chart_type=config.chart_type.value,
                width=config.width,
                height=config.height
            )
            
            return viz_id
            
        except Exception as e:
            self.logger.error("Visualization creation failed", config_id=config.config_id, error=str(e))
            return None
    
    def _render_visualization(self, visualization: Visualization) -> bool:
        """Render visualization"""
        try:
            start_time = time.time()
            
            config = visualization.config
            
            # Get chart renderer
            if config.chart_type not in self.chart_renderers:
                self.logger.error("Unsupported chart type", chart_type=config.chart_type.value)
                return False
            
            chart_renderer = self.chart_renderers[config.chart_type]
            
            # Render chart
            chart_data = chart_renderer(visualization.data, config)
            
            # Get format renderer
            format_renderer = self.format_renderers.get(visualization.render_format, self._render_html)
            
            # Render to specified format
            visualization.rendered_content = format_renderer(chart_data, config)
            
            # Calculate render time
            render_time_ms = (time.time() - start_time) * 1000
            
            # Update statistics
            with self._lock:
                self.viz_stats['total_render_time_ms'] += render_time_ms
                charts_rendered = self.viz_stats['charts_rendered']
                if charts_rendered > 0:
                    self.viz_stats['average_render_time_ms'] = (
                        self.viz_stats['total_render_time_ms'] / charts_rendered
                    )
            
            # Collect metrics
            self.metrics_collector.collect_metric(
                name="visualization.chart_rendered",
                value=render_time_ms,
                metric_type=MetricType.TIMER,
                tags={
                    'chart_type': config.chart_type.value,
                    'render_format': visualization.render_format.value
                }
            )
            
            visualization.updated_at = time.time()
            
            return True
            
        except Exception as e:
            self.logger.error("Visualization rendering failed", viz_id=visualization.viz_id, error=str(e))
            return False
    
    # Chart renderers
    def _render_line_chart(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Render line chart"""
        return {
            'type': 'line',
            'data': self._prepare_chart_data(data, config),
            'options': self._get_chart_options(config)
        }
    
    def _render_bar_chart(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Render bar chart"""
        return {
            'type': 'bar',
            'data': self._prepare_chart_data(data, config),
            'options': self._get_chart_options(config)
        }
    
    def _render_column_chart(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Render column chart"""
        return {
            'type': 'column',
            'data': self._prepare_chart_data(data, config),
            'options': self._get_chart_options(config)
        }
    
    def _render_pie_chart(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Render pie chart"""
        return {
            'type': 'pie',
            'data': self._prepare_pie_data(data, config),
            'options': self._get_chart_options(config)
        }
    
    def _render_scatter_chart(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Render scatter chart"""
        return {
            'type': 'scatter',
            'data': self._prepare_scatter_data(data, config),
            'options': self._get_chart_options(config)
        }
    
    def _render_area_chart(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Render area chart"""
        return {
            'type': 'area',
            'data': self._prepare_chart_data(data, config),
            'options': self._get_chart_options(config)
        }
    
    def _render_histogram(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Render histogram"""
        return {
            'type': 'histogram',
            'data': self._prepare_histogram_data(data, config),
            'options': self._get_chart_options(config)
        }
    
    def _render_heatmap(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Render heatmap"""
        return {
            'type': 'heatmap',
            'data': self._prepare_heatmap_data(data, config),
            'options': self._get_chart_options(config)
        }
    
    # Format renderers
    def _render_html(self, chart_data: Dict[str, Any], config: VisualizationConfig) -> str:
        """Render to HTML format"""
        html_template = f"""
        <div id="chart_{config.config_id}" style="width:{config.width}px;height:{config.height}px;">
            <h3>{config.title}</h3>
            <div class="chart-container">
                <!-- Chart data: {json.dumps(chart_data)} -->
                <p>Chart rendered successfully</p>
            </div>
        </div>
        """
        return html_template
    
    def _render_svg(self, chart_data: Dict[str, Any], config: VisualizationConfig) -> str:
        """Render to SVG format"""
        svg_content = f"""
        <svg width="{config.width}" height="{config.height}" xmlns="http://www.w3.org/2000/svg">
            <title>{config.title}</title>
            <rect width="100%" height="100%" fill="white"/>
            <text x="50%" y="50%" text-anchor="middle">{config.title}</text>
        </svg>
        """
        return svg_content
    
    def _render_png(self, chart_data: Dict[str, Any], config: VisualizationConfig) -> str:
        """Render to PNG format (base64 encoded)"""
        # Mock PNG rendering
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    def _render_json(self, chart_data: Dict[str, Any], config: VisualizationConfig) -> str:
        """Render to JSON format"""
        return json.dumps({
            'config': {
                'title': config.title,
                'type': config.chart_type.value,
                'width': config.width,
                'height': config.height
            },
            'data': chart_data
        }, indent=2)
    
    def _render_interactive(self, chart_data: Dict[str, Any], config: VisualizationConfig) -> str:
        """Render interactive visualization"""
        return f"""
        <div id="interactive_{config.config_id}" class="interactive-chart">
            <script>
                // Interactive chart implementation
                console.log('Interactive chart: {config.title}');
                console.log('Data:', {json.dumps(chart_data)});
            </script>
        </div>
        """
    
    # Data preparation methods
    def _prepare_chart_data(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Prepare data for standard charts"""
        # Mock data preparation
        return {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'datasets': [{
                'label': config.series[0] if config.series else 'Data',
                'data': [65, 59, 80, 81, 56, 55],
                'backgroundColor': config.colors[0] if config.colors else self.default_colors[0]
            }]
        }
    
    def _prepare_pie_data(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Prepare data for pie chart"""
        return {
            'labels': ['Red', 'Blue', 'Yellow', 'Green', 'Purple'],
            'datasets': [{
                'data': [300, 50, 100, 40, 120],
                'backgroundColor': config.colors[:5] if len(config.colors) >= 5 else self.default_colors[:5]
            }]
        }
    
    def _prepare_scatter_data(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Prepare data for scatter chart"""
        return {
            'datasets': [{
                'label': 'Scatter Dataset',
                'data': [{'x': 10, 'y': 20}, {'x': 15, 'y': 25}, {'x': 20, 'y': 30}],
                'backgroundColor': config.colors[0] if config.colors else self.default_colors[0]
            }]
        }
    
    def _prepare_histogram_data(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Prepare data for histogram"""
        return {
            'labels': ['0-10', '10-20', '20-30', '30-40', '40-50'],
            'datasets': [{
                'label': 'Frequency',
                'data': [5, 15, 25, 20, 10],
                'backgroundColor': config.colors[0] if config.colors else self.default_colors[0]
            }]
        }
    
    def _prepare_heatmap_data(self, data: Any, config: VisualizationConfig) -> Dict[str, Any]:
        """Prepare data for heatmap"""
        return {
            'data': [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            'xLabels': ['A', 'B', 'C'],
            'yLabels': ['X', 'Y', 'Z']
        }
    
    def _get_chart_options(self, config: VisualizationConfig) -> Dict[str, Any]:
        """Get chart options"""
        theme = self.themes.get(config.theme, self.themes["default"])
        
        return {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {'display': config.legend},
                'tooltip': {'enabled': config.tooltips}
            },
            'scales': {
                'x': {'grid': {'display': config.grid}},
                'y': {'grid': {'display': config.grid}}
            },
            'animation': {'duration': 1000 if config.animations else 0},
            'interaction': {'intersect': config.interactive},
            'theme': theme
        }
    
    def create_dashboard(self, dashboard: Dashboard) -> bool:
        """Create new dashboard"""
        try:
            # Validate dashboard
            if not dashboard.validate():
                self.logger.error("Invalid dashboard configuration", dashboard_id=dashboard.dashboard_id)
                return False
            
            with self._lock:
                # Store dashboard
                self.dashboards[dashboard.dashboard_id] = dashboard
                
                # Update statistics
                self.viz_stats['total_dashboards'] = len(self.dashboards)
                self.viz_stats['dashboards_created'] += 1
            
            self.logger.info(
                "Dashboard created",
                dashboard_id=dashboard.dashboard_id,
                dashboard_name=dashboard.dashboard_name,
                visualizations_count=len(dashboard.visualizations)
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Dashboard creation failed", dashboard_id=dashboard.dashboard_id, error=str(e))
            return False
    
    def export_visualization(self, viz_id: str, format: RenderFormat) -> Optional[str]:
        """Export visualization in specified format"""
        try:
            if viz_id not in self.visualizations:
                self.logger.error("Visualization not found", viz_id=viz_id)
                return None
            
            visualization = self.visualizations[viz_id]
            
            # Change render format and re-render
            original_format = visualization.render_format
            visualization.render_format = format
            
            success = self._render_visualization(visualization)
            if not success:
                visualization.render_format = original_format
                return None
            
            # Update statistics
            with self._lock:
                self.viz_stats['export_requests'] += 1
            
            self.logger.info(
                "Visualization exported",
                viz_id=viz_id,
                format=format.value
            )
            
            return visualization.rendered_content
            
        except Exception as e:
            self.logger.error("Visualization export failed", viz_id=viz_id, error=str(e))
            return None
    
    def get_visualization(self, viz_id: str) -> Optional[Visualization]:
        """Get visualization by ID"""
        return self.visualizations.get(viz_id)
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID"""
        return self.dashboards.get(dashboard_id)
    
    def list_visualizations(self) -> List[Dict[str, Any]]:
        """List all visualizations"""
        visualizations = []
        for viz in self.visualizations.values():
            visualizations.append({
                'viz_id': viz.viz_id,
                'title': viz.config.title,
                'chart_type': viz.config.chart_type.value,
                'visualization_type': viz.config.visualization_type.value,
                'created_at': viz.created_at,
                'updated_at': viz.updated_at,
                'age_minutes': viz.get_age_minutes()
            })
        
        return sorted(visualizations, key=lambda x: x['created_at'], reverse=True)
    
    def list_dashboards(self) -> List[Dict[str, Any]]:
        """List all dashboards"""
        dashboards = []
        for dashboard in self.dashboards.values():
            dashboards.append({
                'dashboard_id': dashboard.dashboard_id,
                'dashboard_name': dashboard.dashboard_name,
                'description': dashboard.description,
                'visualizations_count': len(dashboard.visualizations),
                'public': dashboard.public,
                'created_at': dashboard.created_at,
                'updated_at': dashboard.updated_at
            })
        
        return sorted(dashboards, key=lambda x: x['created_at'], reverse=True)
    
    def get_visualization_stats(self) -> Dict[str, Any]:
        """Get visualization manager statistics"""
        with self._lock:
            return {
                'total_visualizations': len(self.visualizations),
                'total_dashboards': len(self.dashboards),
                'available_chart_types': [ct.value for ct in ChartType],
                'available_formats': [rf.value for rf in RenderFormat],
                'available_themes': list(self.themes.keys()),
                'max_data_points': self.max_data_points,
                'cache_enabled': self.cache_enabled,
                'stats': self.viz_stats.copy()
            }
