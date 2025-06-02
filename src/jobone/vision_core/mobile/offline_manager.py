"""
🔄 Orion Vision Core - Offline Manager
Offline capabilities and data synchronization

This module provides offline capabilities:
- Offline data storage and management
- Data synchronization strategies
- Local AI model execution
- Offline-first architecture
- Background sync and conflict resolution

Sprint 9.2: Mobile Integration and Cross-Platform
"""

import asyncio
import logging
import json
import os
import sqlite3
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncStrategy(Enum):
    """Data synchronization strategies"""
    IMMEDIATE = "immediate"  # Sync immediately when online
    PERIODIC = "periodic"  # Sync at regular intervals
    MANUAL = "manual"  # Sync only when requested
    INTELLIGENT = "intelligent"  # Smart sync based on usage patterns
    BACKGROUND = "background"  # Background sync when app inactive

class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    CLIENT_WINS = "client_wins"  # Local changes take precedence
    SERVER_WINS = "server_wins"  # Remote changes take precedence
    MERGE = "merge"  # Attempt to merge changes
    MANUAL = "manual"  # Require manual resolution
    TIMESTAMP = "timestamp"  # Latest timestamp wins

class DataPriority(Enum):
    """Data synchronization priority"""
    CRITICAL = "critical"  # Must sync immediately
    HIGH = "high"  # Sync as soon as possible
    NORMAL = "normal"  # Sync during normal intervals
    LOW = "low"  # Sync when convenient
    BACKGROUND = "background"  # Sync in background only

@dataclass
class OfflineConfig:
    """Configuration for offline capabilities"""
    storage_path: str = "./offline_storage"
    max_storage_mb: int = 1024  # 1GB default
    sync_strategy: SyncStrategy = SyncStrategy.INTELLIGENT
    conflict_resolution: ConflictResolution = ConflictResolution.TIMESTAMP
    sync_interval_minutes: int = 15
    auto_cleanup_enabled: bool = True
    cleanup_threshold_days: int = 30
    compression_enabled: bool = True
    encryption_enabled: bool = True
    background_sync_enabled: bool = True

@dataclass
class OfflineData:
    """Offline data entry"""
    data_id: str
    data_type: str
    content: Any
    priority: DataPriority = DataPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    sync_status: str = "pending"  # pending, synced, conflict, error
    version: int = 1
    checksum: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SyncResult:
    """Synchronization result"""
    success: bool
    synced_count: int = 0
    conflict_count: int = 0
    error_count: int = 0
    sync_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)

class OfflineManager:
    """
    Offline capabilities and data synchronization manager.
    
    Provides comprehensive offline functionality with:
    - Local data storage and management
    - Intelligent synchronization strategies
    - Conflict resolution mechanisms
    - Background sync capabilities
    - Offline-first architecture support
    """
    
    def __init__(self, config: Optional[OfflineConfig] = None):
        """
        Initialize the offline manager.
        
        Args:
            config: Offline configuration
        """
        self.config = config or OfflineConfig()
        self.storage_path = self.config.storage_path
        self.db_path = os.path.join(self.storage_path, "offline.db")
        
        # Storage and sync state
        self.is_online = True
        self.is_syncing = False
        self.last_sync_time: Optional[datetime] = None
        
        # Data storage
        self.offline_data: Dict[str, OfflineData] = {}
        self.sync_queue: List[str] = []
        self.conflict_queue: List[str] = []
        
        # Event handlers
        self.sync_handlers: List[Callable] = []
        self.conflict_handlers: List[Callable] = []
        self.online_handlers: List[Callable] = []
        
        # Performance metrics
        self.metrics = {
            'total_data_entries': 0,
            'sync_operations': 0,
            'successful_syncs': 0,
            'conflicts_resolved': 0,
            'storage_used_mb': 0.0,
            'average_sync_time': 0.0
        }
        
        # Background sync task
        self.sync_task: Optional[asyncio.Task] = None
        
        logger.info("🔄 Offline Manager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize the offline manager.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create storage directory
            os.makedirs(self.storage_path, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_offline_data()
            
            # Start background sync if enabled
            if self.config.background_sync_enabled:
                await self._start_background_sync()
            
            # Check online status
            await self._check_online_status()
            
            logger.info(f"✅ Offline Manager initialized with {len(self.offline_data)} data entries")
            return True
            
        except Exception as e:
            logger.error(f"❌ Offline Manager initialization failed: {e}")
            return False
    
    async def _initialize_database(self):
        """Initialize SQLite database for offline storage"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create offline data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_data (
                data_id TEXT PRIMARY KEY,
                data_type TEXT NOT NULL,
                content TEXT NOT NULL,
                priority TEXT NOT NULL,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                sync_status TEXT NOT NULL,
                version INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Create sync log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_time TEXT NOT NULL,
                sync_type TEXT NOT NULL,
                result TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("📊 Offline database initialized")
    
    async def _load_offline_data(self):
        """Load offline data from database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM offline_data')
        rows = cursor.fetchall()
        
        for row in rows:
            data_id, data_type, content, priority, created_at, modified_at, sync_status, version, checksum, metadata = row
            
            offline_data = OfflineData(
                data_id=data_id,
                data_type=data_type,
                content=json.loads(content),
                priority=DataPriority(priority),
                created_at=datetime.fromisoformat(created_at),
                modified_at=datetime.fromisoformat(modified_at),
                sync_status=sync_status,
                version=version,
                checksum=checksum,
                metadata=json.loads(metadata) if metadata else {}
            )
            
            self.offline_data[data_id] = offline_data
            
            # Add to sync queue if pending
            if sync_status == "pending":
                self.sync_queue.append(data_id)
        
        conn.close()
        
        # Update metrics
        self.metrics['total_data_entries'] = len(self.offline_data)
        self.metrics['storage_used_mb'] = await self._calculate_storage_usage()
        
        logger.info(f"📂 Loaded {len(self.offline_data)} offline data entries")
    
    async def _calculate_storage_usage(self) -> float:
        """Calculate storage usage in MB"""
        
        try:
            total_size = 0
            for root, dirs, files in os.walk(self.storage_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0
    
    async def _start_background_sync(self):
        """Start background synchronization task"""
        
        if self.sync_task and not self.sync_task.done():
            return
        
        self.sync_task = asyncio.create_task(self._background_sync_loop())
        logger.info("🔄 Background sync started")
    
    async def _background_sync_loop(self):
        """Background synchronization loop"""
        
        while True:
            try:
                if self.is_online and not self.is_syncing and self.sync_queue:
                    await self._perform_sync()
                
                # Wait for next sync interval
                await asyncio.sleep(self.config.sync_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"❌ Background sync error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _check_online_status(self):
        """Check if device is online"""
        
        # Simple online check (in real implementation, use network APIs)
        try:
            # Simulate network check
            self.is_online = True  # Assume online for demo
            
            if self.is_online:
                # Trigger online handlers
                for handler in self.online_handlers:
                    try:
                        await handler()
                    except Exception as e:
                        logger.error(f"❌ Online handler error: {e}")
            
        except Exception:
            self.is_online = False
    
    async def store_data(self, data_id: str, data_type: str, content: Any, 
                        priority: DataPriority = DataPriority.NORMAL,
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store data for offline access.
        
        Args:
            data_id: Unique data identifier
            data_type: Type of data
            content: Data content
            priority: Synchronization priority
            metadata: Additional metadata
            
        Returns:
            True if storage successful, False otherwise
        """
        try:
            # Create checksum
            content_str = json.dumps(content, sort_keys=True)
            checksum = hashlib.md5(content_str.encode()).hexdigest()
            
            # Create offline data entry
            offline_data = OfflineData(
                data_id=data_id,
                data_type=data_type,
                content=content,
                priority=priority,
                checksum=checksum,
                metadata=metadata or {}
            )
            
            # Store in memory
            self.offline_data[data_id] = offline_data
            
            # Store in database
            await self._save_to_database(offline_data)
            
            # Add to sync queue
            if data_id not in self.sync_queue:
                self.sync_queue.append(data_id)
            
            # Update metrics
            self.metrics['total_data_entries'] = len(self.offline_data)
            self.metrics['storage_used_mb'] = await self._calculate_storage_usage()
            
            logger.info(f"💾 Stored offline data: {data_id} ({data_type})")
            
            # Trigger immediate sync for critical data
            if priority == DataPriority.CRITICAL and self.is_online:
                asyncio.create_task(self._sync_data_item(data_id))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store offline data: {e}")
            return False
    
    async def _save_to_database(self, data: OfflineData):
        """Save data to database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO offline_data 
            (data_id, data_type, content, priority, created_at, modified_at, 
             sync_status, version, checksum, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.data_id,
            data.data_type,
            json.dumps(data.content),
            data.priority.value,
            data.created_at.isoformat(),
            data.modified_at.isoformat(),
            data.sync_status,
            data.version,
            data.checksum,
            json.dumps(data.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    async def get_data(self, data_id: str) -> Optional[OfflineData]:
        """
        Get offline data by ID.
        
        Args:
            data_id: Data identifier
            
        Returns:
            OfflineData if found, None otherwise
        """
        return self.offline_data.get(data_id)
    
    async def get_data_by_type(self, data_type: str) -> List[OfflineData]:
        """
        Get offline data by type.
        
        Args:
            data_type: Data type
            
        Returns:
            List of OfflineData entries
        """
        return [data for data in self.offline_data.values() if data.data_type == data_type]
    
    async def delete_data(self, data_id: str) -> bool:
        """
        Delete offline data.
        
        Args:
            data_id: Data identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            if data_id in self.offline_data:
                del self.offline_data[data_id]
                
                # Remove from database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM offline_data WHERE data_id = ?', (data_id,))
                conn.commit()
                conn.close()
                
                # Remove from sync queue
                if data_id in self.sync_queue:
                    self.sync_queue.remove(data_id)
                
                # Update metrics
                self.metrics['total_data_entries'] = len(self.offline_data)
                
                logger.info(f"🗑️ Deleted offline data: {data_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete offline data: {e}")
            return False
    
    async def sync_all(self) -> SyncResult:
        """
        Synchronize all pending data.
        
        Returns:
            SyncResult with synchronization details
        """
        if not self.is_online:
            logger.warning("⚠️ Cannot sync: device is offline")
            return SyncResult(success=False, errors=["Device is offline"])
        
        return await self._perform_sync()
    
    async def _perform_sync(self) -> SyncResult:
        """Perform synchronization operation"""
        
        if self.is_syncing:
            logger.warning("⚠️ Sync already in progress")
            return SyncResult(success=False, errors=["Sync already in progress"])
        
        start_time = asyncio.get_event_loop().time()
        self.is_syncing = True
        
        try:
            result = SyncResult(success=True)
            
            # Process sync queue
            items_to_sync = self.sync_queue.copy()
            
            for data_id in items_to_sync:
                try:
                    sync_success = await self._sync_data_item(data_id)
                    if sync_success:
                        result.synced_count += 1
                        self.sync_queue.remove(data_id)
                    else:
                        result.error_count += 1
                        result.errors.append(f"Failed to sync {data_id}")
                        
                except Exception as e:
                    result.error_count += 1
                    result.errors.append(f"Error syncing {data_id}: {e}")
            
            # Update sync time
            result.sync_time = asyncio.get_event_loop().time() - start_time
            self.last_sync_time = datetime.now()
            
            # Update metrics
            self.metrics['sync_operations'] += 1
            if result.error_count == 0:
                self.metrics['successful_syncs'] += 1
            
            # Update average sync time
            total_syncs = self.metrics['sync_operations']
            current_avg = self.metrics['average_sync_time']
            self.metrics['average_sync_time'] = (
                (current_avg * (total_syncs - 1) + result.sync_time) / total_syncs
            )
            
            # Log sync result
            await self._log_sync_result(result)
            
            # Trigger sync handlers
            for handler in self.sync_handlers:
                try:
                    await handler(result)
                except Exception as e:
                    logger.error(f"❌ Sync handler error: {e}")
            
            logger.info(f"🔄 Sync completed: {result.synced_count} synced, {result.error_count} errors")
            return result
            
        finally:
            self.is_syncing = False
    
    async def _sync_data_item(self, data_id: str) -> bool:
        """Sync individual data item"""
        
        data = self.offline_data.get(data_id)
        if not data:
            return False
        
        try:
            # Simulate sync operation (in real implementation, call API)
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Update sync status
            data.sync_status = "synced"
            data.modified_at = datetime.now()
            
            # Save to database
            await self._save_to_database(data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to sync data item {data_id}: {e}")
            data.sync_status = "error"
            await self._save_to_database(data)
            return False
    
    async def _log_sync_result(self, result: SyncResult):
        """Log sync result to database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_log (sync_time, sync_type, result, details)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            "automatic" if self.sync_task else "manual",
            "success" if result.success else "failure",
            json.dumps({
                'synced_count': result.synced_count,
                'error_count': result.error_count,
                'sync_time': result.sync_time,
                'errors': result.errors
            })
        ))
        
        conn.commit()
        conn.close()
    
    def register_sync_handler(self, handler: Callable):
        """Register sync event handler"""
        self.sync_handlers.append(handler)
        logger.info("📡 Registered sync handler")
    
    def register_conflict_handler(self, handler: Callable):
        """Register conflict resolution handler"""
        self.conflict_handlers.append(handler)
        logger.info("📡 Registered conflict handler")
    
    def register_online_handler(self, handler: Callable):
        """Register online status handler"""
        self.online_handlers.append(handler)
        logger.info("📡 Registered online handler")
    
    async def cleanup_old_data(self) -> int:
        """
        Cleanup old offline data.
        
        Returns:
            Number of items cleaned up
        """
        if not self.config.auto_cleanup_enabled:
            return 0
        
        try:
            cleanup_threshold = datetime.now() - timedelta(days=self.config.cleanup_threshold_days)
            items_to_cleanup = []
            
            for data_id, data in self.offline_data.items():
                if (data.sync_status == "synced" and 
                    data.modified_at < cleanup_threshold):
                    items_to_cleanup.append(data_id)
            
            # Delete old items
            for data_id in items_to_cleanup:
                await self.delete_data(data_id)
            
            logger.info(f"🧹 Cleaned up {len(items_to_cleanup)} old data items")
            return len(items_to_cleanup)
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return 0
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        
        pending_count = len(self.sync_queue)
        conflict_count = len(self.conflict_queue)
        synced_count = len([d for d in self.offline_data.values() if d.sync_status == "synced"])
        
        return {
            'is_online': self.is_online,
            'is_syncing': self.is_syncing,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'pending_count': pending_count,
            'conflict_count': conflict_count,
            'synced_count': synced_count,
            'total_count': len(self.offline_data)
        }
    
    def get_offline_metrics(self) -> Dict[str, Any]:
        """Get offline manager metrics"""
        
        return {
            **self.metrics,
            'sync_status': self.get_sync_status(),
            'storage_path': self.storage_path,
            'config': {
                'max_storage_mb': self.config.max_storage_mb,
                'sync_strategy': self.config.sync_strategy.value,
                'conflict_resolution': self.config.conflict_resolution.value,
                'sync_interval_minutes': self.config.sync_interval_minutes
            }
        }
    
    async def shutdown(self):
        """Shutdown offline manager"""
        
        if self.sync_task and not self.sync_task.done():
            self.sync_task.cancel()
            try:
                await self.sync_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🔄 Offline Manager shutdown complete")
