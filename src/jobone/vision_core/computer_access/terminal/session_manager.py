#!/usr/bin/env python3
"""
Session Manager - Terminal session lifecycle management
"""

import logging
import time
import threading
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class SessionState(Enum):
    """Terminal session states"""
    INACTIVE = "inactive"
    STARTING = "starting"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATING = "terminating"
    TERMINATED = "terminated"
    ERROR = "error"

@dataclass
class TerminalSession:
    """Terminal session information"""
    session_id: str
    state: SessionState
    shell: str
    working_directory: str
    environment: Dict[str, str]
    created_at: float
    last_activity: float
    command_count: int
    process_id: Optional[int] = None

class SessionManager:
    """
    Terminal session lifecycle manager
    Handles persistent terminal sessions and state management
    """
    
    def __init__(self, terminal_controller):
        self.logger = logging.getLogger('orion.computer_access.terminal.session')
        self.terminal_controller = terminal_controller
        
        # Session management
        self.sessions = {}
        self.active_session = None
        self.session_lock = threading.Lock()
        
        # Configuration
        self.max_sessions = 10
        self.session_timeout = 3600  # 1 hour
        self.cleanup_interval = 300  # 5 minutes
        
        # Statistics
        self.total_sessions_created = 0
        self.sessions_terminated = 0
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_sessions, daemon=True)
        self.cleanup_thread.start()
        
        self.logger.info("📋 SessionManager initialized")
    
    def create_session(self, shell: str = None, working_dir: str = None, env: Dict[str, str] = None) -> str:
        """
        Create a new terminal session
        
        Args:
            shell: Shell to use (optional)
            working_dir: Working directory (optional)
            env: Environment variables (optional)
            
        Returns:
            str: Session ID
        """
        with self.session_lock:
            if len(self.sessions) >= self.max_sessions:
                # Remove oldest inactive session
                self._cleanup_oldest_session()
            
            session_id = str(uuid.uuid4())
            
            # Use defaults if not specified
            if shell is None:
                shell = self.terminal_controller.shell_config['default_shell']
            if working_dir is None:
                working_dir = "."
            if env is None:
                env = {}
            
            session = TerminalSession(
                session_id=session_id,
                state=SessionState.STARTING,
                shell=shell,
                working_directory=working_dir,
                environment=env,
                created_at=time.time(),
                last_activity=time.time(),
                command_count=0
            )
            
            self.sessions[session_id] = session
            self.total_sessions_created += 1
            
            # Set as active session if none exists
            if self.active_session is None:
                self.active_session = session_id
            
            self.logger.info(f"📋 Session created: {session_id}")
            
            # Initialize session
            try:
                self._initialize_session(session)
                session.state = SessionState.ACTIVE
                self.logger.info(f"✅ Session activated: {session_id}")
            except Exception as e:
                session.state = SessionState.ERROR
                self.logger.error(f"❌ Session initialization failed: {session_id} - {e}")
            
            return session_id
    
    def _initialize_session(self, session: TerminalSession):
        """Initialize a terminal session"""
        # Set working directory
        if session.working_directory != ".":
            cd_command = f"cd {session.working_directory}"
            self.terminal_controller.execute_command({
                'command': cd_command,
                'shell': session.shell
            })
        
        # Set environment variables
        for key, value in session.environment.items():
            if self.terminal_controller.platform == "Windows":
                env_command = f"set {key}={value}"
            else:
                env_command = f"export {key}={value}"
            
            self.terminal_controller.execute_command({
                'command': env_command,
                'shell': session.shell
            })
    
    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get session by ID"""
        with self.session_lock:
            return self.sessions.get(session_id)
    
    def set_active_session(self, session_id: str) -> bool:
        """Set active session"""
        with self.session_lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                if session.state == SessionState.ACTIVE:
                    self.active_session = session_id
                    session.last_activity = time.time()
                    self.logger.info(f"🎯 Active session set: {session_id}")
                    return True
                else:
                    self.logger.warning(f"⚠️ Cannot set inactive session as active: {session_id}")
                    return False
            else:
                self.logger.error(f"❌ Session not found: {session_id}")
                return False
    
    def get_active_session(self) -> Optional[TerminalSession]:
        """Get current active session"""
        if self.active_session:
            return self.get_session(self.active_session)
        return None
    
    def execute_in_session(self, session_id: str, command: str, **kwargs) -> Any:
        """
        Execute command in specific session
        
        Args:
            session_id: Session ID
            command: Command to execute
            **kwargs: Additional parameters
            
        Returns:
            Command execution result
        """
        with self.session_lock:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            
            if session.state != SessionState.ACTIVE:
                raise RuntimeError(f"Session not active: {session_id} (state: {session.state.value})")
            
            # Update session activity
            session.last_activity = time.time()
            session.command_count += 1
            
            # Prepare command parameters
            params = {
                'command': command,
                'shell': session.shell,
                'working_dir': session.working_directory,
                **kwargs
            }
            
            # Add environment variables
            if session.environment:
                env = kwargs.get('env', {})
                env.update(session.environment)
                params['env'] = env
            
            self.logger.info(f"🎯 Executing in session {session_id}: {command}")
            
            # Execute command
            result = self.terminal_controller.execute_command(params)
            
            return result
    
    def suspend_session(self, session_id: str) -> bool:
        """Suspend a session"""
        with self.session_lock:
            session = self.sessions.get(session_id)
            if session and session.state == SessionState.ACTIVE:
                session.state = SessionState.SUSPENDED
                if self.active_session == session_id:
                    self.active_session = None
                self.logger.info(f"⏸️ Session suspended: {session_id}")
                return True
            return False
    
    def resume_session(self, session_id: str) -> bool:
        """Resume a suspended session"""
        with self.session_lock:
            session = self.sessions.get(session_id)
            if session and session.state == SessionState.SUSPENDED:
                try:
                    # Re-initialize session
                    self._initialize_session(session)
                    session.state = SessionState.ACTIVE
                    session.last_activity = time.time()
                    self.logger.info(f"▶️ Session resumed: {session_id}")
                    return True
                except Exception as e:
                    session.state = SessionState.ERROR
                    self.logger.error(f"❌ Session resume failed: {session_id} - {e}")
                    return False
            return False
    
    def terminate_session(self, session_id: str) -> bool:
        """Terminate a session"""
        with self.session_lock:
            session = self.sessions.get(session_id)
            if session:
                session.state = SessionState.TERMINATING
                
                # Remove from active session if needed
                if self.active_session == session_id:
                    self.active_session = None
                
                # Mark as terminated
                session.state = SessionState.TERMINATED
                self.sessions_terminated += 1
                
                self.logger.info(f"🛑 Session terminated: {session_id}")
                return True
            return False
    
    def list_sessions(self) -> List[TerminalSession]:
        """List all sessions"""
        with self.session_lock:
            return list(self.sessions.values())
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        with self.session_lock:
            active_count = sum(1 for s in self.sessions.values() if s.state == SessionState.ACTIVE)
            suspended_count = sum(1 for s in self.sessions.values() if s.state == SessionState.SUSPENDED)
            error_count = sum(1 for s in self.sessions.values() if s.state == SessionState.ERROR)
            
            return {
                'total_sessions': len(self.sessions),
                'active_sessions': active_count,
                'suspended_sessions': suspended_count,
                'error_sessions': error_count,
                'total_created': self.total_sessions_created,
                'total_terminated': self.sessions_terminated,
                'active_session_id': self.active_session
            }
    
    def _cleanup_sessions(self):
        """Background thread to cleanup expired sessions"""
        while True:
            try:
                time.sleep(self.cleanup_interval)
                current_time = time.time()
                
                with self.session_lock:
                    expired_sessions = []
                    
                    for session_id, session in self.sessions.items():
                        # Check for timeout
                        if (current_time - session.last_activity) > self.session_timeout:
                            if session.state in [SessionState.ACTIVE, SessionState.SUSPENDED]:
                                expired_sessions.append(session_id)
                        
                        # Remove terminated sessions
                        elif session.state == SessionState.TERMINATED:
                            expired_sessions.append(session_id)
                    
                    # Remove expired sessions
                    for session_id in expired_sessions:
                        self.logger.info(f"🧹 Cleaning up expired session: {session_id}")
                        self.sessions.pop(session_id, None)
                        if self.active_session == session_id:
                            self.active_session = None
                
            except Exception as e:
                self.logger.error(f"❌ Session cleanup error: {e}")
    
    def _cleanup_oldest_session(self):
        """Remove oldest inactive session to make room"""
        oldest_session = None
        oldest_time = float('inf')
        
        for session_id, session in self.sessions.items():
            if session.state != SessionState.ACTIVE and session.last_activity < oldest_time:
                oldest_time = session.last_activity
                oldest_session = session_id
        
        if oldest_session:
            self.logger.info(f"🧹 Removing oldest session: {oldest_session}")
            self.sessions.pop(oldest_session, None)
    
    def shutdown(self):
        """Shutdown session manager"""
        self.logger.info("🛑 Shutting down session manager")
        
        with self.session_lock:
            # Terminate all active sessions
            for session_id in list(self.sessions.keys()):
                self.terminate_session(session_id)
            
            self.sessions.clear()
            self.active_session = None
        
        self.logger.info("✅ Session manager shutdown complete")
