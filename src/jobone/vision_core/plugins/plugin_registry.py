"""
🔌 Orion Vision Core - Plugin Registry
Plugin discovery and registration system

This module provides plugin registry capabilities:
- Plugin discovery and cataloging
- Plugin metadata management
- Plugin dependency tracking
- Plugin version management
- Plugin marketplace integration

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import json
import os
from pathlib import Path

from .base_plugin import PluginType, PluginCapability

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PluginDependency:
    """Plugin dependency information"""
    name: str
    version_requirement: str = "*"  # Semantic version requirement
    optional: bool = False
    description: str = ""

@dataclass
class PluginInfo:
    """Comprehensive plugin information"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    capabilities: List[PluginCapability]
    dependencies: List[PluginDependency] = field(default_factory=list)
    file_path: Optional[str] = None
    package_path: Optional[str] = None
    entry_point: str = "main"
    min_system_version: str = "9.1.0"
    max_system_version: Optional[str] = None
    license: str = "MIT"
    homepage: Optional[str] = None
    repository: Optional[str] = None
    documentation: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    size_bytes: int = 0
    checksum: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    download_count: int = 0
    rating: float = 0.0
    verified: bool = False

class PluginRegistry:
    """
    Plugin registry for discovery and management.
    
    Maintains a catalog of available plugins with:
    - Plugin metadata and information
    - Dependency tracking and resolution
    - Version management
    - Plugin discovery and search
    - Marketplace integration
    """
    
    def __init__(self, registry_file: str = "src/jobone/vision_core/plugins/registry.json"):
        """
        Initialize the plugin registry.
        
        Args:
            registry_file: Path to the registry storage file
        """
        self.registry_file = Path(registry_file)
        self.plugins: Dict[str, PluginInfo] = {}
        self.plugin_index: Dict[str, Set[str]] = {
            'by_type': {},
            'by_capability': {},
            'by_author': {},
            'by_tag': {}
        }
        
        # Ensure registry directory exists
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📋 Plugin Registry initialized with file: {registry_file}")
    
    async def initialize(self) -> bool:
        """
        Initialize the plugin registry.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Load existing registry if available
            if self.registry_file.exists():
                await self._load_registry()
            
            logger.info("✅ Plugin Registry initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Plugin Registry initialization failed: {e}")
            return False
    
    async def register_plugin(self, plugin_info: PluginInfo) -> bool:
        """
        Register a plugin in the registry.
        
        Args:
            plugin_info: Plugin information to register
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            plugin_key = f"{plugin_info.name}_{plugin_info.version}"
            
            # Check if plugin already exists
            if plugin_key in self.plugins:
                logger.warning(f"⚠️ Plugin {plugin_key} already registered, updating...")
            
            # Store plugin info
            self.plugins[plugin_key] = plugin_info
            
            # Update indexes
            await self._update_indexes(plugin_info)
            
            # Save registry
            await self._save_registry()
            
            logger.info(f"📝 Registered plugin: {plugin_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register plugin {plugin_info.name}: {e}")
            return False
    
    async def unregister_plugin(self, plugin_name: str, version: str = None) -> bool:
        """
        Unregister a plugin from the registry.
        
        Args:
            plugin_name: Name of the plugin to unregister
            version: Specific version to unregister (optional)
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            if version:
                plugin_key = f"{plugin_name}_{version}"
                if plugin_key in self.plugins:
                    plugin_info = self.plugins[plugin_key]
                    del self.plugins[plugin_key]
                    await self._remove_from_indexes(plugin_info)
                    logger.info(f"🗑️ Unregistered plugin: {plugin_key}")
            else:
                # Remove all versions of the plugin
                keys_to_remove = [key for key in self.plugins.keys() if key.startswith(f"{plugin_name}_")]
                for key in keys_to_remove:
                    plugin_info = self.plugins[key]
                    del self.plugins[key]
                    await self._remove_from_indexes(plugin_info)
                logger.info(f"🗑️ Unregistered all versions of plugin: {plugin_name}")
            
            # Save registry
            await self._save_registry()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unregister plugin {plugin_name}: {e}")
            return False
    
    async def get_plugin_info(self, plugin_name: str, version: str = None) -> Optional[PluginInfo]:
        """
        Get plugin information.
        
        Args:
            plugin_name: Name of the plugin
            version: Specific version (optional, returns latest if not specified)
            
        Returns:
            PluginInfo object or None if not found
        """
        if version:
            plugin_key = f"{plugin_name}_{version}"
            return self.plugins.get(plugin_key)
        else:
            # Find latest version
            matching_plugins = [
                (key, info) for key, info in self.plugins.items()
                if key.startswith(f"{plugin_name}_")
            ]
            
            if matching_plugins:
                # Sort by version (simple string comparison for now)
                latest = max(matching_plugins, key=lambda x: x[1].version)
                return latest[1]
            
            return None
    
    async def search_plugins(self, query: str = "", plugin_type: Optional[PluginType] = None,
                           capabilities: Optional[List[PluginCapability]] = None,
                           author: Optional[str] = None, tags: Optional[List[str]] = None) -> List[PluginInfo]:
        """
        Search for plugins based on criteria.
        
        Args:
            query: Text search query
            plugin_type: Filter by plugin type
            capabilities: Filter by required capabilities
            author: Filter by author
            tags: Filter by tags
            
        Returns:
            List of matching PluginInfo objects
        """
        results = []
        
        for plugin_info in self.plugins.values():
            # Text search
            if query:
                search_text = f"{plugin_info.name} {plugin_info.description} {' '.join(plugin_info.tags)}".lower()
                if query.lower() not in search_text:
                    continue
            
            # Type filter
            if plugin_type and plugin_info.plugin_type != plugin_type:
                continue
            
            # Capabilities filter
            if capabilities:
                if not all(cap in plugin_info.capabilities for cap in capabilities):
                    continue
            
            # Author filter
            if author and plugin_info.author.lower() != author.lower():
                continue
            
            # Tags filter
            if tags:
                if not any(tag in plugin_info.tags for tag in tags):
                    continue
            
            results.append(plugin_info)
        
        # Sort by relevance (simple implementation)
        results.sort(key=lambda p: (p.rating, p.download_count), reverse=True)
        
        return results
    
    async def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInfo]:
        """Get all plugins of a specific type"""
        return [info for info in self.plugins.values() if info.plugin_type == plugin_type]
    
    async def get_plugins_by_capability(self, capability: PluginCapability) -> List[PluginInfo]:
        """Get all plugins with a specific capability"""
        return [info for info in self.plugins.values() if capability in info.capabilities]
    
    async def get_plugins_by_author(self, author: str) -> List[PluginInfo]:
        """Get all plugins by a specific author"""
        return [info for info in self.plugins.values() if info.author.lower() == author.lower()]
    
    async def resolve_dependencies(self, plugin_info: PluginInfo) -> List[PluginInfo]:
        """
        Resolve plugin dependencies.
        
        Args:
            plugin_info: Plugin to resolve dependencies for
            
        Returns:
            List of required plugin dependencies
        """
        dependencies = []
        
        for dep in plugin_info.dependencies:
            dep_plugin = await self.get_plugin_info(dep.name)
            if dep_plugin:
                dependencies.append(dep_plugin)
                # Recursively resolve dependencies
                sub_deps = await self.resolve_dependencies(dep_plugin)
                dependencies.extend(sub_deps)
            elif not dep.optional:
                logger.warning(f"⚠️ Required dependency {dep.name} not found for {plugin_info.name}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_deps = []
        for dep in dependencies:
            dep_key = f"{dep.name}_{dep.version}"
            if dep_key not in seen:
                seen.add(dep_key)
                unique_deps.append(dep)
        
        return unique_deps
    
    async def validate_plugin(self, plugin_info: PluginInfo) -> Dict[str, Any]:
        """
        Validate plugin information and dependencies.
        
        Args:
            plugin_info: Plugin to validate
            
        Returns:
            Validation result with status and issues
        """
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': []
        }
        
        # Check required fields
        required_fields = ['name', 'version', 'description', 'author', 'plugin_type']
        for field in required_fields:
            if not getattr(plugin_info, field):
                validation_result['valid'] = False
                validation_result['issues'].append(f"Missing required field: {field}")
        
        # Check file/package existence
        if plugin_info.file_path and not os.path.exists(plugin_info.file_path):
            validation_result['valid'] = False
            validation_result['issues'].append(f"Plugin file not found: {plugin_info.file_path}")
        
        if plugin_info.package_path and not os.path.exists(plugin_info.package_path):
            validation_result['valid'] = False
            validation_result['issues'].append(f"Plugin package not found: {plugin_info.package_path}")
        
        # Check dependencies
        for dep in plugin_info.dependencies:
            dep_plugin = await self.get_plugin_info(dep.name)
            if not dep_plugin and not dep.optional:
                validation_result['valid'] = False
                validation_result['issues'].append(f"Required dependency not found: {dep.name}")
            elif not dep_plugin and dep.optional:
                validation_result['warnings'].append(f"Optional dependency not found: {dep.name}")
        
        return validation_result
    
    async def _update_indexes(self, plugin_info: PluginInfo):
        """Update search indexes for a plugin"""
        
        # Index by type
        type_key = plugin_info.plugin_type.value
        if type_key not in self.plugin_index['by_type']:
            self.plugin_index['by_type'][type_key] = set()
        self.plugin_index['by_type'][type_key].add(f"{plugin_info.name}_{plugin_info.version}")
        
        # Index by capabilities
        for capability in plugin_info.capabilities:
            cap_key = capability.value
            if cap_key not in self.plugin_index['by_capability']:
                self.plugin_index['by_capability'][cap_key] = set()
            self.plugin_index['by_capability'][cap_key].add(f"{plugin_info.name}_{plugin_info.version}")
        
        # Index by author
        author_key = plugin_info.author.lower()
        if author_key not in self.plugin_index['by_author']:
            self.plugin_index['by_author'][author_key] = set()
        self.plugin_index['by_author'][author_key].add(f"{plugin_info.name}_{plugin_info.version}")
        
        # Index by tags
        for tag in plugin_info.tags:
            tag_key = tag.lower()
            if tag_key not in self.plugin_index['by_tag']:
                self.plugin_index['by_tag'][tag_key] = set()
            self.plugin_index['by_tag'][tag_key].add(f"{plugin_info.name}_{plugin_info.version}")
    
    async def _remove_from_indexes(self, plugin_info: PluginInfo):
        """Remove plugin from search indexes"""
        plugin_key = f"{plugin_info.name}_{plugin_info.version}"
        
        # Remove from all indexes
        for index_type in self.plugin_index.values():
            for key_set in index_type.values():
                key_set.discard(plugin_key)
    
    async def _load_registry(self):
        """Load registry from file"""
        try:
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
            
            # Convert data back to PluginInfo objects
            for plugin_data in data.get('plugins', []):
                plugin_info = self._dict_to_plugin_info(plugin_data)
                plugin_key = f"{plugin_info.name}_{plugin_info.version}"
                self.plugins[plugin_key] = plugin_info
                await self._update_indexes(plugin_info)
            
            logger.info(f"📁 Loaded {len(self.plugins)} plugins from registry")
            
        except Exception as e:
            logger.error(f"❌ Failed to load registry: {e}")
    
    async def _save_registry(self):
        """Save registry to file"""
        try:
            data = {
                'version': '1.0',
                'updated_at': datetime.now().isoformat(),
                'plugins': [self._plugin_info_to_dict(info) for info in self.plugins.values()]
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Failed to save registry: {e}")
    
    def _plugin_info_to_dict(self, plugin_info: PluginInfo) -> Dict[str, Any]:
        """Convert PluginInfo to dictionary for JSON serialization"""
        return {
            'name': plugin_info.name,
            'version': plugin_info.version,
            'description': plugin_info.description,
            'author': plugin_info.author,
            'plugin_type': plugin_info.plugin_type.value,
            'capabilities': [cap.value for cap in plugin_info.capabilities],
            'dependencies': [
                {
                    'name': dep.name,
                    'version_requirement': dep.version_requirement,
                    'optional': dep.optional,
                    'description': dep.description
                } for dep in plugin_info.dependencies
            ],
            'file_path': plugin_info.file_path,
            'package_path': plugin_info.package_path,
            'entry_point': plugin_info.entry_point,
            'min_system_version': plugin_info.min_system_version,
            'max_system_version': plugin_info.max_system_version,
            'license': plugin_info.license,
            'homepage': plugin_info.homepage,
            'repository': plugin_info.repository,
            'documentation': plugin_info.documentation,
            'tags': plugin_info.tags,
            'size_bytes': plugin_info.size_bytes,
            'checksum': plugin_info.checksum,
            'created_at': plugin_info.created_at.isoformat(),
            'updated_at': plugin_info.updated_at.isoformat(),
            'download_count': plugin_info.download_count,
            'rating': plugin_info.rating,
            'verified': plugin_info.verified
        }
    
    def _dict_to_plugin_info(self, data: Dict[str, Any]) -> PluginInfo:
        """Convert dictionary to PluginInfo object"""
        return PluginInfo(
            name=data['name'],
            version=data['version'],
            description=data['description'],
            author=data['author'],
            plugin_type=PluginType(data['plugin_type']),
            capabilities=[PluginCapability(cap) for cap in data['capabilities']],
            dependencies=[
                PluginDependency(
                    name=dep['name'],
                    version_requirement=dep['version_requirement'],
                    optional=dep['optional'],
                    description=dep['description']
                ) for dep in data.get('dependencies', [])
            ],
            file_path=data.get('file_path'),
            package_path=data.get('package_path'),
            entry_point=data.get('entry_point', 'main'),
            min_system_version=data.get('min_system_version', '9.1.0'),
            max_system_version=data.get('max_system_version'),
            license=data.get('license', 'MIT'),
            homepage=data.get('homepage'),
            repository=data.get('repository'),
            documentation=data.get('documentation'),
            tags=data.get('tags', []),
            size_bytes=data.get('size_bytes', 0),
            checksum=data.get('checksum'),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            download_count=data.get('download_count', 0),
            rating=data.get('rating', 0.0),
            verified=data.get('verified', False)
        )
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            'total_plugins': len(self.plugins),
            'plugins_by_type': {
                ptype: len(plugins) for ptype, plugins in self.plugin_index['by_type'].items()
            },
            'plugins_by_capability': {
                cap: len(plugins) for cap, plugins in self.plugin_index['by_capability'].items()
            },
            'total_authors': len(self.plugin_index['by_author']),
            'total_tags': len(self.plugin_index['by_tag'])
        }
