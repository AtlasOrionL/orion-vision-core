#!/usr/bin/env python3
"""
File System Manager - Safe File Operations
Sprint 8.3 - Basic Computer Management and First Autonomous Task
Orion Vision Core - Autonomous AI Operating System

This module provides safe file system operations with permission management,
sandboxing, and comprehensive logging for the Orion Vision Core
autonomous AI operating system.

Author: Orion Development Team
Version: 8.3.0
Date: 30 Mayıs 2025
"""

import logging
import os
import shutil
import stat
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FileSystemManager")

class OperationType(Enum):
    """File operation type enumeration"""
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    MOVE = "move"
    COPY = "copy"
    LIST = "list"
    STAT = "stat"

class PermissionLevel(Enum):
    """Permission level enumeration"""
    ALLOWED = "allowed"
    RESTRICTED = "restricted"
    FORBIDDEN = "forbidden"

@dataclass
class FileOperation:
    """File operation record"""
    operation_id: str
    operation_type: OperationType
    source_path: str
    target_path: Optional[str]
    permission_level: PermissionLevel
    success: bool
    error_message: Optional[str]
    timestamp: datetime
    file_size: Optional[int]
    checksum: Optional[str]

class FileSystemManager(QObject):
    """
    Safe file system operations manager.
    
    Features:
    - Permission-based access control
    - Sandboxed file operations
    - Comprehensive logging and auditing
    - File integrity checking
    - Safe path validation
    - Operation history tracking
    """
    
    # Signals
    file_operation_completed = pyqtSignal(dict)  # FileOperation as dict
    permission_denied = pyqtSignal(str, str)  # path, operation
    file_integrity_warning = pyqtSignal(str, str)  # path, issue
    operation_stats_updated = pyqtSignal(dict)  # operation statistics
    
    def __init__(self):
        """Initialize File System Manager"""
        super().__init__()
        
        # Permission configuration
        self.allowed_directories = [
            os.path.expanduser("~"),
            "/tmp",
            "/var/tmp",
            os.getcwd(),
            os.path.join(os.getcwd(), "data"),
            os.path.join(os.getcwd(), "output"),
            os.path.join(os.getcwd(), "workspace")
        ]
        
        self.restricted_directories = [
            "/etc",
            "/var/log",
            "/usr",
            "/opt",
            "/root"
        ]
        
        self.forbidden_directories = [
            "/bin",
            "/sbin",
            "/boot",
            "/dev",
            "/proc",
            "/sys"
        ]
        
        # File type restrictions
        self.allowed_extensions = {
            '.txt', '.md', '.json', '.yaml', '.yml', '.xml', '.csv',
            '.py', '.js', '.html', '.css', '.sql', '.sh', '.bat',
            '.log', '.conf', '.cfg', '.ini', '.properties',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
        }
        
        self.forbidden_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.deb', '.rpm',
            '.msi', '.dmg', '.iso', '.img', '.vhd', '.vmdk'
        }
        
        # Size limits
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.max_directory_size = 1024 * 1024 * 1024  # 1GB
        
        # State management
        self.operation_history: List[FileOperation] = []
        self.operation_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'denied_operations': 0,
            'operations_by_type': {op.value: 0 for op in OperationType},
            'bytes_read': 0,
            'bytes_written': 0,
            'files_created': 0,
            'files_deleted': 0
        }
        self.operation_counter = 0
        
        # Create workspace directories
        self._ensure_workspace_directories()
        
        logger.info("📁 File System Manager initialized")
    
    def _ensure_workspace_directories(self):
        """Ensure workspace directories exist"""
        workspace_dirs = [
            os.path.join(os.getcwd(), "data"),
            os.path.join(os.getcwd(), "output"),
            os.path.join(os.getcwd(), "workspace"),
            os.path.join(os.getcwd(), "temp")
        ]
        
        for directory in workspace_dirs:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"📁 Ensured directory exists: {directory}")
            except Exception as e:
                logger.warning(f"⚠️ Could not create directory {directory}: {e}")
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read file content safely.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            
        Returns:
            File content or None if failed
        """
        try:
            # Validate path and permissions
            if not self._validate_path_permissions(file_path, OperationType.READ):
                return None
            
            # Check file exists
            if not os.path.isfile(file_path):
                self._log_operation(file_path, None, OperationType.READ, 
                                  PermissionLevel.ALLOWED, False, "File not found")
                return None
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                error_msg = f"File too large: {file_size} bytes"
                self._log_operation(file_path, None, OperationType.READ,
                                  PermissionLevel.ALLOWED, False, error_msg)
                return None
            
            # Read file
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Calculate checksum
            checksum = hashlib.md5(content.encode()).hexdigest()
            
            # Log successful operation
            self._log_operation(file_path, None, OperationType.READ,
                              PermissionLevel.ALLOWED, True, None, file_size, checksum)
            
            # Update stats
            self.operation_stats['bytes_read'] += file_size
            
            logger.info(f"📁 Read file: {file_path} ({file_size} bytes)")
            return content
            
        except Exception as e:
            error_msg = f"Error reading file: {e}"
            self._log_operation(file_path, None, OperationType.READ,
                              PermissionLevel.ALLOWED, False, error_msg)
            logger.error(f"❌ {error_msg}")
            return None
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8',
                   create_dirs: bool = True) -> bool:
        """
        Write content to file safely.
        
        Args:
            file_path: Path to file
            content: Content to write
            encoding: File encoding
            create_dirs: Create parent directories if needed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate path and permissions
            operation_type = OperationType.CREATE if not os.path.exists(file_path) else OperationType.WRITE
            
            if not self._validate_path_permissions(file_path, operation_type):
                return False
            
            # Check content size
            content_size = len(content.encode(encoding))
            if content_size > self.max_file_size:
                error_msg = f"Content too large: {content_size} bytes"
                self._log_operation(file_path, None, operation_type,
                                  PermissionLevel.ALLOWED, False, error_msg)
                return False
            
            # Create parent directories if needed
            if create_dirs:
                parent_dir = os.path.dirname(file_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Calculate checksum
            checksum = hashlib.md5(content.encode()).hexdigest()
            
            # Log successful operation
            self._log_operation(file_path, None, operation_type,
                              PermissionLevel.ALLOWED, True, None, content_size, checksum)
            
            # Update stats
            self.operation_stats['bytes_written'] += content_size
            if operation_type == OperationType.CREATE:
                self.operation_stats['files_created'] += 1
            
            logger.info(f"📁 Wrote file: {file_path} ({content_size} bytes)")
            return True
            
        except Exception as e:
            error_msg = f"Error writing file: {e}"
            self._log_operation(file_path, None, operation_type,
                              PermissionLevel.ALLOWED, False, error_msg)
            logger.error(f"❌ {error_msg}")
            return False
    
    def copy_file(self, source_path: str, target_path: str) -> bool:
        """
        Copy file safely.
        
        Args:
            source_path: Source file path
            target_path: Target file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate paths and permissions
            if not self._validate_path_permissions(source_path, OperationType.READ):
                return False
            
            if not self._validate_path_permissions(target_path, OperationType.CREATE):
                return False
            
            # Check source file exists
            if not os.path.isfile(source_path):
                error_msg = "Source file not found"
                self._log_operation(source_path, target_path, OperationType.COPY,
                                  PermissionLevel.ALLOWED, False, error_msg)
                return False
            
            # Check file size
            file_size = os.path.getsize(source_path)
            if file_size > self.max_file_size:
                error_msg = f"File too large: {file_size} bytes"
                self._log_operation(source_path, target_path, OperationType.COPY,
                                  PermissionLevel.ALLOWED, False, error_msg)
                return False
            
            # Create target directory if needed
            target_dir = os.path.dirname(target_path)
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, target_path)
            
            # Verify copy integrity
            if not self._verify_file_integrity(source_path, target_path):
                error_msg = "File integrity check failed"
                self._log_operation(source_path, target_path, OperationType.COPY,
                                  PermissionLevel.ALLOWED, False, error_msg)
                return False
            
            # Log successful operation
            self._log_operation(source_path, target_path, OperationType.COPY,
                              PermissionLevel.ALLOWED, True, None, file_size)
            
            # Update stats
            self.operation_stats['files_created'] += 1
            
            logger.info(f"📁 Copied file: {source_path} → {target_path}")
            return True
            
        except Exception as e:
            error_msg = f"Error copying file: {e}"
            self._log_operation(source_path, target_path, OperationType.COPY,
                              PermissionLevel.ALLOWED, False, error_msg)
            logger.error(f"❌ {error_msg}")
            return False
    
    def delete_file(self, file_path: str, force: bool = False) -> bool:
        """
        Delete file safely.
        
        Args:
            file_path: Path to file
            force: Force deletion without additional checks
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate path and permissions
            if not self._validate_path_permissions(file_path, OperationType.DELETE):
                return False
            
            # Check file exists
            if not os.path.exists(file_path):
                error_msg = "File not found"
                self._log_operation(file_path, None, OperationType.DELETE,
                                  PermissionLevel.ALLOWED, False, error_msg)
                return False
            
            # Additional safety checks for non-forced deletion
            if not force:
                # Check if file is in a critical location
                if any(file_path.startswith(forbidden) for forbidden in self.forbidden_directories):
                    error_msg = "Cannot delete files in forbidden directories"
                    self._log_operation(file_path, None, OperationType.DELETE,
                                      PermissionLevel.FORBIDDEN, False, error_msg)
                    return False
            
            # Get file size before deletion
            file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
            
            # Delete file or directory
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            
            # Log successful operation
            self._log_operation(file_path, None, OperationType.DELETE,
                              PermissionLevel.ALLOWED, True, None, file_size)
            
            # Update stats
            self.operation_stats['files_deleted'] += 1
            
            logger.info(f"📁 Deleted: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Error deleting file: {e}"
            self._log_operation(file_path, None, OperationType.DELETE,
                              PermissionLevel.ALLOWED, False, error_msg)
            logger.error(f"❌ {error_msg}")
            return False
    
    def list_directory(self, directory_path: str, include_hidden: bool = False) -> Optional[List[Dict[str, Any]]]:
        """
        List directory contents safely.
        
        Args:
            directory_path: Path to directory
            include_hidden: Include hidden files
            
        Returns:
            List of file information dictionaries or None if failed
        """
        try:
            # Validate path and permissions
            if not self._validate_path_permissions(directory_path, OperationType.LIST):
                return None
            
            # Check directory exists
            if not os.path.isdir(directory_path):
                error_msg = "Directory not found"
                self._log_operation(directory_path, None, OperationType.LIST,
                                  PermissionLevel.ALLOWED, False, error_msg)
                return None
            
            # List directory contents
            items = []
            for item_name in os.listdir(directory_path):
                if not include_hidden and item_name.startswith('.'):
                    continue
                
                item_path = os.path.join(directory_path, item_name)
                try:
                    stat_info = os.stat(item_path)
                    
                    item_info = {
                        'name': item_name,
                        'path': item_path,
                        'type': 'directory' if os.path.isdir(item_path) else 'file',
                        'size': stat_info.st_size,
                        'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        'permissions': oct(stat_info.st_mode)[-3:],
                        'readable': os.access(item_path, os.R_OK),
                        'writable': os.access(item_path, os.W_OK),
                        'executable': os.access(item_path, os.X_OK)
                    }
                    
                    items.append(item_info)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not stat {item_path}: {e}")
            
            # Log successful operation
            self._log_operation(directory_path, None, OperationType.LIST,
                              PermissionLevel.ALLOWED, True, None)
            
            logger.info(f"📁 Listed directory: {directory_path} ({len(items)} items)")
            return items
            
        except Exception as e:
            error_msg = f"Error listing directory: {e}"
            self._log_operation(directory_path, None, OperationType.LIST,
                              PermissionLevel.ALLOWED, False, error_msg)
            logger.error(f"❌ {error_msg}")
            return None
    
    def _validate_path_permissions(self, path: str, operation: OperationType) -> bool:
        """Validate path permissions for operation"""
        try:
            # Normalize path
            abs_path = os.path.abspath(path)
            
            # Check forbidden directories
            for forbidden_dir in self.forbidden_directories:
                if abs_path.startswith(os.path.abspath(forbidden_dir)):
                    self.permission_denied.emit(path, operation.value)
                    self._log_operation(path, None, operation, PermissionLevel.FORBIDDEN, False,
                                      f"Path in forbidden directory: {forbidden_dir}")
                    return False
            
            # Check file extension for write operations
            if operation in [OperationType.WRITE, OperationType.CREATE]:
                _, ext = os.path.splitext(path)
                if ext.lower() in self.forbidden_extensions:
                    self.permission_denied.emit(path, operation.value)
                    self._log_operation(path, None, operation, PermissionLevel.FORBIDDEN, False,
                                      f"Forbidden file extension: {ext}")
                    return False
            
            # Check if path is in allowed directories
            path_allowed = False
            for allowed_dir in self.allowed_directories:
                if abs_path.startswith(os.path.abspath(allowed_dir)):
                    path_allowed = True
                    break
            
            if not path_allowed:
                # Check if it's in restricted directories (may require special handling)
                for restricted_dir in self.restricted_directories:
                    if abs_path.startswith(os.path.abspath(restricted_dir)):
                        if operation in [OperationType.READ, OperationType.LIST]:
                            return True  # Allow read operations in restricted directories
                        else:
                            self.permission_denied.emit(path, operation.value)
                            self._log_operation(path, None, operation, PermissionLevel.RESTRICTED, False,
                                              f"Write operation not allowed in restricted directory")
                            return False
                
                # Path not in any allowed or restricted directory
                self.permission_denied.emit(path, operation.value)
                self._log_operation(path, None, operation, PermissionLevel.FORBIDDEN, False,
                                  "Path not in allowed directories")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating path permissions: {e}")
            return False
    
    def _verify_file_integrity(self, source_path: str, target_path: str) -> bool:
        """Verify file integrity after copy operation"""
        try:
            # Compare file sizes
            source_size = os.path.getsize(source_path)
            target_size = os.path.getsize(target_path)
            
            if source_size != target_size:
                self.file_integrity_warning.emit(target_path, "Size mismatch")
                return False
            
            # Compare checksums for small files
            if source_size < 10 * 1024 * 1024:  # 10MB
                with open(source_path, 'rb') as f:
                    source_hash = hashlib.md5(f.read()).hexdigest()
                
                with open(target_path, 'rb') as f:
                    target_hash = hashlib.md5(f.read()).hexdigest()
                
                if source_hash != target_hash:
                    self.file_integrity_warning.emit(target_path, "Checksum mismatch")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verifying file integrity: {e}")
            return False
    
    def _log_operation(self, source_path: str, target_path: Optional[str],
                      operation_type: OperationType, permission_level: PermissionLevel,
                      success: bool, error_message: Optional[str] = None,
                      file_size: Optional[int] = None, checksum: Optional[str] = None):
        """Log file operation"""
        try:
            self.operation_counter += 1
            operation_id = f"fs_op_{self.operation_counter:06d}"
            
            operation = FileOperation(
                operation_id=operation_id,
                operation_type=operation_type,
                source_path=source_path,
                target_path=target_path,
                permission_level=permission_level,
                success=success,
                error_message=error_message,
                timestamp=datetime.now(),
                file_size=file_size,
                checksum=checksum
            )
            
            # Add to history
            self.operation_history.append(operation)
            if len(self.operation_history) > 1000:  # Keep last 1000 operations
                self.operation_history.pop(0)
            
            # Update statistics
            self.operation_stats['total_operations'] += 1
            self.operation_stats['operations_by_type'][operation_type.value] += 1
            
            if success:
                self.operation_stats['successful_operations'] += 1
            else:
                if permission_level == PermissionLevel.FORBIDDEN:
                    self.operation_stats['denied_operations'] += 1
                else:
                    self.operation_stats['failed_operations'] += 1
            
            # Emit signals
            self.file_operation_completed.emit(self._operation_to_dict(operation))
            self.operation_stats_updated.emit(self.operation_stats.copy())
            
        except Exception as e:
            logger.error(f"❌ Error logging operation: {e}")
    
    def _operation_to_dict(self, operation: FileOperation) -> dict:
        """Convert FileOperation to dictionary"""
        return {
            'operation_id': operation.operation_id,
            'operation_type': operation.operation_type.value,
            'source_path': operation.source_path,
            'target_path': operation.target_path,
            'permission_level': operation.permission_level.value,
            'success': operation.success,
            'error_message': operation.error_message,
            'timestamp': operation.timestamp.isoformat(),
            'file_size': operation.file_size,
            'checksum': operation.checksum
        }
    
    def get_operation_history(self, limit: int = 100) -> List[dict]:
        """Get file operation history"""
        history = self.operation_history[-limit:] if limit > 0 else self.operation_history
        return [self._operation_to_dict(op) for op in history]
    
    def get_operation_stats(self) -> dict:
        """Get operation statistics"""
        return self.operation_stats.copy()
    
    def get_workspace_info(self) -> dict:
        """Get workspace information"""
        workspace_info = {
            'allowed_directories': self.allowed_directories,
            'restricted_directories': self.restricted_directories,
            'forbidden_directories': self.forbidden_directories,
            'allowed_extensions': sorted(list(self.allowed_extensions)),
            'forbidden_extensions': sorted(list(self.forbidden_extensions)),
            'max_file_size': self.max_file_size,
            'max_directory_size': self.max_directory_size
        }
        
        # Add directory sizes
        for directory in self.allowed_directories:
            if os.path.exists(directory):
                try:
                    total_size = sum(
                        os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, dirnames, filenames in os.walk(directory)
                        for filename in filenames
                    )
                    workspace_info[f'size_{os.path.basename(directory)}'] = total_size
                except Exception:
                    workspace_info[f'size_{os.path.basename(directory)}'] = 0
        
        return workspace_info

# Singleton instance
_file_system_manager = None

def get_file_system_manager() -> FileSystemManager:
    """Get the singleton File System Manager instance"""
    global _file_system_manager
    if _file_system_manager is None:
        _file_system_manager = FileSystemManager()
    return _file_system_manager
