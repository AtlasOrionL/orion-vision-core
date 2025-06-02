"""
Agent Logger for Orion Vision Core

This module provides structured logging functionality for agents.
Extracted from agent_core.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import logging
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class AgentLogger:
    """Structured logger for agent operations with terminal-readable output"""
    
    def __init__(self, agent_id: str, log_level: str = "INFO"):
        self.agent_id = agent_id
        self.log_level = log_level
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging with file and console handlers"""
        logger_name = f"orion.agent.{self.agent_id}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, self.log_level.upper()))
        
        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Console handler for terminal output
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = self._create_terminal_formatter()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler for detailed logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / f"agent_{self.agent_id}.log")
        file_formatter = self._create_file_formatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _create_terminal_formatter(self) -> logging.Formatter:
        """Create AI-readable terminal formatter"""
        class TerminalFormatter(logging.Formatter):
            def format(self, record):
                try:
                    log_data = json.loads(record.getMessage())
                    return self._format_for_terminal(log_data)
                except (json.JSONDecodeError, KeyError):
                    return super().format(record)
            
            def _format_for_terminal(self, log_data: Dict[str, Any]) -> str:
                lines = []
                timestamp = log_data.get('timestamp', datetime.now().isoformat())
                level = log_data.get('level', 'INFO')
                agent_id = log_data.get('agent_id', 'unknown')
                message = log_data.get('message', '')
                
                # Main log line
                lines.append(f"[{timestamp}] {level} | agent.{agent_id} | {message}")
                
                # Context information
                context = log_data.get('context', {})
                if context:
                    context_items = list(context.items())
                    for i, (key, value) in enumerate(context_items):
                        prefix = "└──" if i == len(context_items) - 1 else "├──"
                        lines.append(f"{prefix} {key}: {value}")
                
                return "\n".join(lines)
        
        return TerminalFormatter()
    
    def _create_file_formatter(self) -> logging.Formatter:
        """Create detailed file formatter"""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _create_log_entry(self, level: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured log entry"""
        return {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'agent_id': self.agent_id,
            'message': message,
            'context': context
        }
    
    def info(self, message: str, **context):
        """Log info message with context"""
        log_entry = self._create_log_entry("INFO", message, context)
        self.logger.info(json.dumps(log_entry))
    
    def error(self, message: str, **context):
        """Log error message with context"""
        log_entry = self._create_log_entry("ERROR", message, context)
        self.logger.error(json.dumps(log_entry))
    
    def warning(self, message: str, **context):
        """Log warning message with context"""
        log_entry = self._create_log_entry("WARNING", message, context)
        self.logger.warning(json.dumps(log_entry))
    
    def debug(self, message: str, **context):
        """Log debug message with context"""
        log_entry = self._create_log_entry("DEBUG", message, context)
        self.logger.debug(json.dumps(log_entry))
    
    def critical(self, message: str, **context):
        """Log critical message with context"""
        log_entry = self._create_log_entry("CRITICAL", message, context)
        self.logger.critical(json.dumps(log_entry))
