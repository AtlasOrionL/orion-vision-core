#!/usr/bin/env python3
"""
Terminal Module Test Suite - Comprehensive testing for terminal functionality
"""

import unittest
import time
import platform
import tempfile
import os
from unittest.mock import Mock, patch

# Import terminal modules
from .terminal_controller import TerminalController, CommandStatus
from .command_executor import CommandExecutor, ExecutionMode
from .output_parser import OutputParser, OutputType
from .session_manager import SessionManager, SessionState

class TestTerminalController(unittest.TestCase):
    """Test cases for TerminalController"""
    
    def setUp(self):
        """Set up test environment"""
        self.controller = TerminalController()
        self.controller.initialize()
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'controller'):
            self.controller.shutdown()
    
    def test_initialization(self):
        """Test terminal controller initialization"""
        self.assertTrue(self.controller.initialized)
        self.assertTrue(self.controller.is_ready())
        self.assertIsNotNone(self.controller.shell_config)
    
    def test_basic_command_execution(self):
        """Test basic command execution"""
        if platform.system() == "Windows":
            command = "echo Hello World"
        else:
            command = "echo 'Hello World'"
        
        result = self.controller.execute_command({'command': command})
        
        self.assertEqual(result.status, CommandStatus.COMPLETED)
        self.assertEqual(result.return_code, 0)
        self.assertIn("Hello World", result.stdout)
    
    def test_command_with_error(self):
        """Test command that produces error"""
        # Use a command that should fail on all platforms
        command = "nonexistent_command_12345"
        
        result = self.controller.execute_command({'command': command})
        
        self.assertEqual(result.status, CommandStatus.FAILED)
        self.assertNotEqual(result.return_code, 0)
        self.assertNotEqual(result.stderr, "")
    
    def test_command_timeout(self):
        """Test command timeout handling"""
        if platform.system() == "Windows":
            command = "timeout 5"  # Windows timeout command
        else:
            command = "sleep 5"    # Unix sleep command
        
        result = self.controller.execute_command({
            'command': command,
            'timeout': 1.0  # 1 second timeout
        })
        
        self.assertEqual(result.status, CommandStatus.TIMEOUT)
    
    def test_command_history(self):
        """Test command history tracking"""
        initial_count = len(self.controller.get_command_history())
        
        # Execute a few commands
        commands = ["echo test1", "echo test2", "echo test3"]
        for cmd in commands:
            self.controller.execute_command({'command': cmd})
        
        history = self.controller.get_command_history()
        self.assertEqual(len(history), initial_count + len(commands))
    
    def test_platform_compatibility(self):
        """Test platform-specific functionality"""
        current_platform = platform.system()
        self.assertIn(current_platform, ["Windows", "Linux", "Darwin"])
        
        # Test platform-specific shell configuration
        shell_config = self.controller.shell_config
        self.assertIn('default_shell', shell_config)
        self.assertIn('shells', shell_config)

class TestCommandExecutor(unittest.TestCase):
    """Test cases for CommandExecutor"""
    
    def setUp(self):
        """Set up test environment"""
        self.controller = Mock()
        self.executor = CommandExecutor(self.controller)
    
    def test_blocking_execution(self):
        """Test blocking command execution"""
        if platform.system() == "Windows":
            command = "echo Blocking Test"
        else:
            command = "echo 'Blocking Test'"
        
        result = self.executor.execute_blocking(command)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['return_code'], 0)
        self.assertIn("Blocking Test", result['stdout'])
        self.assertEqual(result['mode'], ExecutionMode.BLOCKING.value)
    
    def test_interactive_execution(self):
        """Test interactive command execution"""
        if platform.system() == "Windows":
            command = "findstr test"
            input_data = "test line\nanother line\ntest again\n"
        else:
            command = "grep test"
            input_data = "test line\nanother line\ntest again\n"
        
        result = self.executor.execute_interactive(command, input_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['mode'], ExecutionMode.INTERACTIVE.value)
        self.assertIn("test", result['stdout'])
    
    def test_streaming_execution(self):
        """Test streaming command execution"""
        output_lines = []
        
        def stream_callback(output):
            output_lines.append(output.line)
        
        if platform.system() == "Windows":
            command = "echo Line1 && echo Line2 && echo Line3"
        else:
            command = "echo 'Line1'; echo 'Line2'; echo 'Line3'"
        
        process_id = self.executor.execute_streaming(command, stream_callback)
        
        # Wait for completion
        time.sleep(2)
        
        self.assertIsInstance(process_id, int)
        self.assertGreater(len(output_lines), 0)
    
    def test_process_management(self):
        """Test process management functionality"""
        # Start a long-running process
        if platform.system() == "Windows":
            command = "timeout 10"
        else:
            command = "sleep 10"
        
        def dummy_callback(output):
            pass
        
        process_id = self.executor.execute_streaming(command, dummy_callback)
        
        # Check process is running
        running_processes = self.executor.get_running_processes()
        self.assertIn(process_id, running_processes)
        
        # Terminate process
        success = self.executor.terminate_process(process_id)
        self.assertTrue(success)
        
        # Wait a bit and check process is gone
        time.sleep(1)
        running_processes = self.executor.get_running_processes()
        self.assertNotIn(process_id, running_processes)

class TestOutputParser(unittest.TestCase):
    """Test cases for OutputParser"""
    
    def setUp(self):
        """Set up test environment"""
        self.parser = OutputParser()
    
    def test_success_output_parsing(self):
        """Test parsing of successful command output"""
        output = "Operation completed successfully\nFiles processed: 5"
        result = self.parser.parse_output(output)
        
        self.assertEqual(result.output_type, OutputType.SUCCESS)
        self.assertGreater(result.confidence, 0.5)
    
    def test_error_output_parsing(self):
        """Test parsing of error output"""
        output = "Error: File not found\nFailed to process request"
        result = self.parser.parse_output(output)
        
        self.assertEqual(result.output_type, OutputType.ERROR)
        self.assertIsNotNone(result.error_details)
        self.assertIn("File not found", result.error_details)
    
    def test_warning_output_parsing(self):
        """Test parsing of warning output"""
        output = "Warning: Deprecated function used\nContinuing with operation"
        result = self.parser.parse_output(output)
        
        self.assertEqual(result.output_type, OutputType.WARNING)
        self.assertGreater(len(result.warnings), 0)
    
    def test_data_extraction(self):
        """Test data value extraction"""
        output = "File size: 1024 bytes\nProgress: 75%\nTime: 2.5 seconds"
        result = self.parser.parse_output(output)
        
        self.assertIn('file_size', result.extracted_values)
        self.assertIn('percentage', result.extracted_values)
        self.assertIn('time_duration', result.extracted_values)
    
    def test_command_specific_parsing(self):
        """Test command-specific output parsing"""
        # Test ls command parsing
        ls_output = "file1.txt\nfile2.txt\ndirectory1\nfile3.log"
        result = self.parser.parse_output(ls_output, "ls -la")
        
        if 'command_specific' in result.structured_data:
            self.assertIn('files', result.structured_data['command_specific'])
    
    def test_empty_output(self):
        """Test handling of empty output"""
        result = self.parser.parse_output("")
        
        self.assertEqual(result.output_type, OutputType.UNKNOWN)
        self.assertEqual(result.confidence, 0.0)

class TestSessionManager(unittest.TestCase):
    """Test cases for SessionManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.controller = Mock()
        self.controller.shell_config = {
            'default_shell': 'bash' if platform.system() != "Windows" else 'cmd'
        }
        self.controller.platform = platform.system()
        self.session_manager = SessionManager(self.controller)
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'session_manager'):
            self.session_manager.shutdown()
    
    def test_session_creation(self):
        """Test session creation"""
        session_id = self.session_manager.create_session()
        
        self.assertIsNotNone(session_id)
        session = self.session_manager.get_session(session_id)
        self.assertIsNotNone(session)
        self.assertEqual(session.state, SessionState.ACTIVE)
    
    def test_active_session_management(self):
        """Test active session management"""
        session_id = self.session_manager.create_session()
        
        # Should be automatically set as active
        active_session = self.session_manager.get_active_session()
        self.assertIsNotNone(active_session)
        self.assertEqual(active_session.session_id, session_id)
        
        # Create another session
        session_id2 = self.session_manager.create_session()
        
        # Set as active
        success = self.session_manager.set_active_session(session_id2)
        self.assertTrue(success)
        
        active_session = self.session_manager.get_active_session()
        self.assertEqual(active_session.session_id, session_id2)
    
    def test_session_suspension_and_resume(self):
        """Test session suspension and resume"""
        session_id = self.session_manager.create_session()
        
        # Suspend session
        success = self.session_manager.suspend_session(session_id)
        self.assertTrue(success)
        
        session = self.session_manager.get_session(session_id)
        self.assertEqual(session.state, SessionState.SUSPENDED)
        
        # Resume session
        success = self.session_manager.resume_session(session_id)
        self.assertTrue(success)
        
        session = self.session_manager.get_session(session_id)
        self.assertEqual(session.state, SessionState.ACTIVE)
    
    def test_session_termination(self):
        """Test session termination"""
        session_id = self.session_manager.create_session()
        
        success = self.session_manager.terminate_session(session_id)
        self.assertTrue(success)
        
        session = self.session_manager.get_session(session_id)
        self.assertEqual(session.state, SessionState.TERMINATED)
    
    def test_session_statistics(self):
        """Test session statistics"""
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            session_id = self.session_manager.create_session()
            session_ids.append(session_id)
        
        stats = self.session_manager.get_session_statistics()
        
        self.assertEqual(stats['total_sessions'], 3)
        self.assertEqual(stats['active_sessions'], 3)
        self.assertGreaterEqual(stats['total_created'], 3)

class TestTerminalIntegration(unittest.TestCase):
    """Integration tests for terminal module"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.controller = TerminalController()
        self.controller.initialize()
    
    def tearDown(self):
        """Clean up integration test environment"""
        if hasattr(self, 'controller'):
            self.controller.shutdown()
    
    def test_file_operations(self):
        """Test file operations through terminal"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            test_file = f.name
            f.write("Test content")
        
        try:
            # Test file reading
            if platform.system() == "Windows":
                command = f"type {test_file}"
            else:
                command = f"cat {test_file}"
            
            result = self.controller.execute_command({'command': command})
            
            self.assertEqual(result.status, CommandStatus.COMPLETED)
            self.assertIn("Test content", result.stdout)
            
        finally:
            # Clean up
            os.unlink(test_file)
    
    def test_directory_operations(self):
        """Test directory operations"""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # List directory contents
            if platform.system() == "Windows":
                command = f"dir {temp_dir}"
            else:
                command = f"ls -la {temp_dir}"
            
            result = self.controller.execute_command({'command': command})
            
            self.assertEqual(result.status, CommandStatus.COMPLETED)
    
    def test_environment_variables(self):
        """Test environment variable handling"""
        if platform.system() == "Windows":
            set_command = "set TEST_VAR=test_value"
            get_command = "echo %TEST_VAR%"
        else:
            set_command = "export TEST_VAR=test_value"
            get_command = "echo $TEST_VAR"
        
        # Set environment variable
        result1 = self.controller.execute_command({'command': set_command})
        self.assertEqual(result1.status, CommandStatus.COMPLETED)
        
        # Get environment variable
        result2 = self.controller.execute_command({'command': get_command})
        self.assertEqual(result2.status, CommandStatus.COMPLETED)
        # Note: Environment variables may not persist between separate command executions

def run_terminal_tests():
    """Run all terminal module tests"""
    print("🧪 Running Terminal Module Test Suite...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestTerminalController))
    test_suite.addTest(unittest.makeSuite(TestCommandExecutor))
    test_suite.addTest(unittest.makeSuite(TestOutputParser))
    test_suite.addTest(unittest.makeSuite(TestSessionManager))
    test_suite.addTest(unittest.makeSuite(TestTerminalIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_terminal_tests()
    exit(0 if success else 1)
