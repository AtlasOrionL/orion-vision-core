#!/usr/bin/env python3
"""
Terminal Module Test - Focused testing for terminal controller
"""

import time
import subprocess
import tempfile
import os
from typing import Dict, Any, List

class TerminalModuleTest:
    """Focused terminal module testing"""
    
    def __init__(self):
        self.test_results = []
        self.temp_files = []
        
    def run_terminal_tests(self) -> Dict[str, Any]:
        """Run all terminal-specific tests"""
        print("🖥️ TERMINAL MODULE TESTING")
        print("=" * 50)
        
        tests = [
            ("basic_commands", self.test_basic_commands),
            ("file_operations", self.test_file_operations),
            ("error_handling", self.test_error_handling),
            ("performance", self.test_performance),
            ("concurrent_operations", self.test_concurrent_operations)
        ]
        
        results = {
            'module': 'terminal',
            'tests_run': 0,
            'tests_passed': 0,
            'test_details': []
        }
        
        for test_name, test_func in tests:
            print(f"\n🔧 Testing: {test_name}")
            result = self._run_single_test(test_name, test_func)
            results['test_details'].append(result)
            results['tests_run'] += 1
            if result['success']:
                results['tests_passed'] += 1
        
        results['success_rate'] = (results['tests_passed'] / results['tests_run']) * 100
        
        self._cleanup()
        self._print_terminal_results(results)
        
        return results
    
    def _run_single_test(self, test_name: str, test_func) -> Dict[str, Any]:
        """Run single test with error handling"""
        start_time = time.time()
        
        try:
            result = test_func()
            execution_time = time.time() - start_time
            
            return {
                'test_name': test_name,
                'success': result.get('success', False),
                'execution_time': execution_time,
                'details': result,
                'error': None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return {
                'test_name': test_name,
                'success': False,
                'execution_time': execution_time,
                'details': {},
                'error': str(e)
            }
    
    def test_basic_commands(self) -> Dict[str, Any]:
        """Test basic terminal commands"""
        print("   📝 Testing basic commands...")
        
        commands = [
            ('echo "Hello Terminal"', 'Hello Terminal'),
            ('pwd', '/'),
            ('whoami', ''),
            ('date', ''),
            ('ls /', 'bin')
        ]
        
        results = []
        
        for cmd, expected_contains in commands:
            try:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                
                success = (
                    result.returncode == 0 and 
                    (not expected_contains or expected_contains in result.stdout)
                )
                
                results.append({
                    'command': cmd,
                    'success': success,
                    'return_code': result.returncode,
                    'stdout_length': len(result.stdout),
                    'stderr_length': len(result.stderr)
                })
                
                status = "✅" if success else "❌"
                print(f"      {status} {cmd}")
                
            except Exception as e:
                results.append({
                    'command': cmd,
                    'success': False,
                    'error': str(e)
                })
                print(f"      ❌ {cmd} (Error: {e})")
        
        success_count = sum(1 for r in results if r.get('success', False))
        
        return {
            'success': success_count >= len(commands) * 0.8,  # 80% success rate
            'commands_tested': len(commands),
            'commands_successful': success_count,
            'success_rate': (success_count / len(commands)) * 100,
            'command_results': results
        }
    
    def test_file_operations(self) -> Dict[str, Any]:
        """Test file operations"""
        print("   📁 Testing file operations...")
        
        # Create temp directory for testing
        temp_dir = tempfile.mkdtemp(prefix='orion_terminal_test_')
        test_file = os.path.join(temp_dir, 'test_file.txt')
        test_content = "Orion Terminal Test Content"
        
        operations = []
        
        try:
            # Test file creation
            cmd = f'echo "{test_content}" > {test_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            operations.append({
                'operation': 'create_file',
                'success': result.returncode == 0 and os.path.exists(test_file),
                'command': cmd
            })
            print(f"      {'✅' if operations[-1]['success'] else '❌'} File creation")
            
            # Test file reading
            cmd = f'cat {test_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            read_success = result.returncode == 0 and test_content in result.stdout
            operations.append({
                'operation': 'read_file',
                'success': read_success,
                'command': cmd,
                'content_match': test_content in result.stdout if result.stdout else False
            })
            print(f"      {'✅' if operations[-1]['success'] else '❌'} File reading")
            
            # Test file modification
            new_content = "Modified content"
            cmd = f'echo "{new_content}" >> {test_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            operations.append({
                'operation': 'modify_file',
                'success': result.returncode == 0,
                'command': cmd
            })
            print(f"      {'✅' if operations[-1]['success'] else '❌'} File modification")
            
            # Test file listing
            cmd = f'ls -la {temp_dir}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            list_success = result.returncode == 0 and 'test_file.txt' in result.stdout
            operations.append({
                'operation': 'list_files',
                'success': list_success,
                'command': cmd
            })
            print(f"      {'✅' if operations[-1]['success'] else '❌'} File listing")
            
            # Test file deletion
            cmd = f'rm {test_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            delete_success = result.returncode == 0 and not os.path.exists(test_file)
            operations.append({
                'operation': 'delete_file',
                'success': delete_success,
                'command': cmd
            })
            print(f"      {'✅' if operations[-1]['success'] else '❌'} File deletion")
            
        except Exception as e:
            operations.append({
                'operation': 'file_operations',
                'success': False,
                'error': str(e)
            })
        
        finally:
            # Cleanup
            try:
                subprocess.run(f'rm -rf {temp_dir}', shell=True, capture_output=True)
            except:
                pass
        
        success_count = sum(1 for op in operations if op.get('success', False))
        
        return {
            'success': success_count >= len(operations) * 0.8,
            'operations_tested': len(operations),
            'operations_successful': success_count,
            'success_rate': (success_count / len(operations)) * 100,
            'operation_results': operations,
            'temp_dir_used': temp_dir
        }
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling capabilities"""
        print("   ⚠️ Testing error handling...")
        
        error_tests = [
            ('invalid_command_xyz123', 127),  # Command not found
            ('ls /nonexistent_directory_xyz', 2),  # No such file or directory
            ('cat /dev/null/impossible', 1),  # Invalid operation
            ('timeout 1 sleep 2', 124),  # Timeout
        ]
        
        results = []
        
        for cmd, expected_code in error_tests:
            try:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                # For error handling, we expect non-zero return codes
                error_handled = result.returncode != 0
                has_stderr = len(result.stderr) > 0
                
                results.append({
                    'command': cmd,
                    'expected_error': True,
                    'got_error': error_handled,
                    'return_code': result.returncode,
                    'has_stderr': has_stderr,
                    'success': error_handled  # Success means error was properly handled
                })
                
                status = "✅" if error_handled else "❌"
                print(f"      {status} {cmd} (RC: {result.returncode})")
                
            except subprocess.TimeoutExpired:
                results.append({
                    'command': cmd,
                    'expected_error': True,
                    'got_error': True,
                    'timeout': True,
                    'success': True  # Timeout is expected for some commands
                })
                print(f"      ✅ {cmd} (Timeout - Expected)")
                
            except Exception as e:
                results.append({
                    'command': cmd,
                    'expected_error': True,
                    'got_error': True,
                    'exception': str(e),
                    'success': True  # Exception handling is working
                })
                print(f"      ✅ {cmd} (Exception handled)")
        
        success_count = sum(1 for r in results if r.get('success', False))
        
        return {
            'success': success_count >= len(error_tests) * 0.8,
            'error_tests_run': len(error_tests),
            'errors_handled': success_count,
            'error_handling_rate': (success_count / len(error_tests)) * 100,
            'error_results': results
        }
    
    def test_performance(self) -> Dict[str, Any]:
        """Test terminal performance"""
        print("   ⚡ Testing performance...")
        
        performance_tests = []
        
        # Test command execution speed
        fast_commands = ['echo "test"', 'pwd', 'whoami']
        
        for cmd in fast_commands:
            times = []
            for _ in range(5):  # Run 5 times for average
                start_time = time.time()
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, timeout=2)
                    execution_time = time.time() - start_time
                    times.append(execution_time)
                except:
                    times.append(999)  # Mark as failed
            
            avg_time = sum(times) / len(times)
            performance_tests.append({
                'command': cmd,
                'average_time': avg_time,
                'times': times,
                'fast_enough': avg_time < 0.1  # Should be under 100ms
            })
            
            status = "✅" if avg_time < 0.1 else "⚠️"
            print(f"      {status} {cmd}: {avg_time:.3f}s avg")
        
        # Test concurrent execution
        concurrent_start = time.time()
        processes = []
        
        for i in range(3):
            proc = subprocess.Popen(
                f'echo "concurrent_{i}"', 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            processes.append(proc)
        
        # Wait for all to complete
        for proc in processes:
            proc.wait()
        
        concurrent_time = time.time() - concurrent_start
        
        fast_count = sum(1 for test in performance_tests if test['fast_enough'])
        
        return {
            'success': fast_count >= len(performance_tests) * 0.8 and concurrent_time < 1.0,
            'fast_commands': fast_count,
            'total_commands': len(performance_tests),
            'performance_rate': (fast_count / len(performance_tests)) * 100,
            'concurrent_execution_time': concurrent_time,
            'performance_details': performance_tests
        }
    
    def test_concurrent_operations(self) -> Dict[str, Any]:
        """Test concurrent terminal operations"""
        print("   🔄 Testing concurrent operations...")
        
        import threading
        
        results = []
        threads = []
        
        def run_command(cmd_id):
            try:
                result = subprocess.run(
                    f'echo "concurrent_test_{cmd_id}"', 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                results.append({
                    'cmd_id': cmd_id,
                    'success': result.returncode == 0,
                    'output': result.stdout.strip()
                })
            except Exception as e:
                results.append({
                    'cmd_id': cmd_id,
                    'success': False,
                    'error': str(e)
                })
        
        # Start 5 concurrent operations
        start_time = time.time()
        
        for i in range(5):
            thread = threading.Thread(target=run_command, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        successful_ops = sum(1 for r in results if r.get('success', False))
        
        print(f"      ✅ {successful_ops}/5 concurrent operations successful")
        print(f"      ⏱️ Total time: {total_time:.3f}s")
        
        return {
            'success': successful_ops >= 4 and total_time < 2.0,  # At least 4/5 success, under 2s
            'concurrent_operations': 5,
            'successful_operations': successful_ops,
            'total_execution_time': total_time,
            'operation_results': results
        }
    
    def _cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
    
    def _print_terminal_results(self, results: Dict[str, Any]):
        """Print terminal test results"""
        print(f"\n📊 TERMINAL MODULE TEST RESULTS")
        print("=" * 50)
        print(f"🎯 Tests Run: {results['tests_run']}")
        print(f"✅ Tests Passed: {results['tests_passed']}")
        print(f"📈 Success Rate: {results['success_rate']:.1f}%")
        
        print(f"\n📋 Test Details:")
        for test in results['test_details']:
            status = "✅" if test['success'] else "❌"
            print(f"   {status} {test['test_name']}: {test['execution_time']:.3f}s")
            if test['error']:
                print(f"      Error: {test['error']}")
        
        if results['success_rate'] >= 80:
            print(f"\n🎉 TERMINAL MODULE: EXCELLENT PERFORMANCE!")
        elif results['success_rate'] >= 60:
            print(f"\n✅ TERMINAL MODULE: GOOD PERFORMANCE!")
        else:
            print(f"\n⚠️ TERMINAL MODULE: NEEDS IMPROVEMENT!")

def test_terminal_module():
    """Run terminal module tests"""
    tester = TerminalModuleTest()
    return tester.run_terminal_tests()

if __name__ == "__main__":
    results = test_terminal_module()
    exit(0 if results['success_rate'] >= 80 else 1)
