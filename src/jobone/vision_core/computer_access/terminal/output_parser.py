#!/usr/bin/env python3
"""
Output Parser - Intelligent terminal output analysis and parsing
"""

import re
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class OutputType(Enum):
    """Types of terminal output"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PROMPT = "prompt"
    DATA = "data"
    UNKNOWN = "unknown"

@dataclass
class ParsedOutput:
    """Parsed terminal output structure"""
    raw_output: str
    output_type: OutputType
    structured_data: Dict[str, Any]
    error_details: Optional[str]
    warnings: List[str]
    extracted_values: Dict[str, Any]
    confidence: float

class OutputParser:
    """
    Intelligent terminal output parser
    Analyzes command output and extracts structured information
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.computer_access.terminal.parser')
        
        # Parsing patterns
        self.error_patterns = [
            r'error[:]\s*(.*)',
            r'failed[:]\s*(.*)',
            r'exception[:]\s*(.*)',
            r'cannot\s+(.*)',
            r'permission\s+denied',
            r'no\s+such\s+file\s+or\s+directory',
            r'command\s+not\s+found',
            r'access\s+denied'
        ]
        
        self.warning_patterns = [
            r'warning[:]\s*(.*)',
            r'deprecated[:]\s*(.*)',
            r'caution[:]\s*(.*)',
            r'note[:]\s*(.*)'
        ]
        
        self.success_patterns = [
            r'success[:]\s*(.*)',
            r'completed[:]\s*(.*)',
            r'done[:]\s*(.*)',
            r'finished[:]\s*(.*)',
            r'ok[:]\s*(.*)'
        ]
        
        # Data extraction patterns
        self.data_patterns = {
            'file_size': r'(\d+)\s+bytes?',
            'percentage': r'(\d+(?:\.\d+)?)%',
            'time_duration': r'(\d+(?:\.\d+)?)\s*(seconds?|minutes?|hours?)',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'url': r'https?://[^\s]+',
            'file_path': r'[/\\]?(?:[^/\\:\*\?"<>\|]+[/\\])*[^/\\:\*\?"<>\|]*',
            'process_id': r'pid[:]\s*(\d+)',
            'port_number': r'port[:]\s*(\d+)',
            'memory_usage': r'(\d+(?:\.\d+)?)\s*(KB|MB|GB)',
            'cpu_usage': r'cpu[:]\s*(\d+(?:\.\d+)?)%'
        }
        
        # Command-specific parsers
        self.command_parsers = {
            'ls': self._parse_ls_output,
            'dir': self._parse_dir_output,
            'ps': self._parse_ps_output,
            'top': self._parse_top_output,
            'df': self._parse_df_output,
            'ping': self._parse_ping_output,
            'curl': self._parse_curl_output,
            'wget': self._parse_wget_output
        }
        
        self.logger.info("📊 OutputParser initialized")
    
    def parse_output(self, output: str, command: str = "") -> ParsedOutput:
        """
        Parse terminal output and extract structured information
        
        Args:
            output: Raw terminal output
            command: Original command (for context)
            
        Returns:
            ParsedOutput: Structured parsing result
        """
        if not output:
            return ParsedOutput(
                raw_output="",
                output_type=OutputType.UNKNOWN,
                structured_data={},
                error_details=None,
                warnings=[],
                extracted_values={},
                confidence=0.0
            )
        
        # Determine output type
        output_type = self._classify_output(output)
        
        # Extract structured data
        structured_data = {}
        error_details = None
        warnings = []
        extracted_values = {}
        
        # Parse based on output type
        if output_type == OutputType.ERROR:
            error_details = self._extract_error_details(output)
            structured_data['error'] = error_details
        
        # Extract warnings
        warnings = self._extract_warnings(output)
        if warnings:
            structured_data['warnings'] = warnings
        
        # Extract data values
        extracted_values = self._extract_data_values(output)
        if extracted_values:
            structured_data['extracted_data'] = extracted_values
        
        # Command-specific parsing
        if command:
            command_name = command.split()[0] if command.split() else ""
            if command_name in self.command_parsers:
                try:
                    command_data = self.command_parsers[command_name](output)
                    structured_data['command_specific'] = command_data
                except Exception as e:
                    self.logger.warning(f"⚠️ Command-specific parsing failed for {command_name}: {e}")
        
        # Calculate confidence
        confidence = self._calculate_confidence(output, output_type, structured_data)
        
        result = ParsedOutput(
            raw_output=output,
            output_type=output_type,
            structured_data=structured_data,
            error_details=error_details,
            warnings=warnings,
            extracted_values=extracted_values,
            confidence=confidence
        )
        
        self.logger.debug(f"📊 Parsed output: {output_type.value} (confidence: {confidence:.2f})")
        return result
    
    def _classify_output(self, output: str) -> OutputType:
        """Classify output type based on content"""
        output_lower = output.lower()
        
        # Check for errors
        for pattern in self.error_patterns:
            if re.search(pattern, output_lower, re.IGNORECASE):
                return OutputType.ERROR
        
        # Check for warnings
        for pattern in self.warning_patterns:
            if re.search(pattern, output_lower, re.IGNORECASE):
                return OutputType.WARNING
        
        # Check for success indicators
        for pattern in self.success_patterns:
            if re.search(pattern, output_lower, re.IGNORECASE):
                return OutputType.SUCCESS
        
        # Check for prompts
        if re.search(r'[\$#>]\s*$', output) or re.search(r':\s*$', output):
            return OutputType.PROMPT
        
        # Check if output contains structured data
        if self._has_structured_data(output):
            return OutputType.DATA
        
        # Default to info
        return OutputType.INFO
    
    def _extract_error_details(self, output: str) -> str:
        """Extract detailed error information"""
        for pattern in self.error_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        return output.strip()
    
    def _extract_warnings(self, output: str) -> List[str]:
        """Extract warning messages"""
        warnings = []
        for pattern in self.warning_patterns:
            matches = re.finditer(pattern, output, re.IGNORECASE)
            for match in matches:
                warning = match.group(1) if match.groups() else match.group(0)
                warnings.append(warning.strip())
        return warnings
    
    def _extract_data_values(self, output: str) -> Dict[str, Any]:
        """Extract structured data values"""
        extracted = {}
        
        for data_type, pattern in self.data_patterns.items():
            matches = re.finditer(pattern, output, re.IGNORECASE)
            values = []
            for match in matches:
                if match.groups():
                    values.append(match.group(1))
                else:
                    values.append(match.group(0))
            
            if values:
                extracted[data_type] = values if len(values) > 1 else values[0]
        
        return extracted
    
    def _has_structured_data(self, output: str) -> bool:
        """Check if output contains structured data"""
        # Check for common structured data indicators
        indicators = [
            r'\|\s*\w+\s*\|',  # Table format
            r'\w+:\s*\w+',      # Key-value pairs
            r'^\s*\d+\s+\w+',   # Numbered lists
            r'^\s*[-*+]\s+',    # Bullet points
            r'{\s*".*":\s*',    # JSON-like
            r'<\w+.*>',         # XML-like
        ]
        
        for indicator in indicators:
            if re.search(indicator, output, re.MULTILINE):
                return True
        
        return False
    
    def _calculate_confidence(self, output: str, output_type: OutputType, structured_data: Dict) -> float:
        """Calculate parsing confidence score"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on successful pattern matches
        if output_type != OutputType.UNKNOWN:
            confidence += 0.2
        
        if structured_data:
            confidence += 0.2
        
        if 'extracted_data' in structured_data:
            confidence += 0.1
        
        # Decrease confidence for very short or very long outputs
        if len(output) < 10:
            confidence -= 0.2
        elif len(output) > 10000:
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    # Command-specific parsers
    def _parse_ls_output(self, output: str) -> Dict[str, Any]:
        """Parse ls command output"""
        lines = output.strip().split('\n')
        files = []
        
        for line in lines:
            if line.strip():
                # Simple parsing - can be enhanced for detailed ls -l output
                files.append(line.strip())
        
        return {'files': files, 'count': len(files)}
    
    def _parse_dir_output(self, output: str) -> Dict[str, Any]:
        """Parse Windows dir command output"""
        lines = output.strip().split('\n')
        files = []
        directories = []
        
        for line in lines:
            if '<DIR>' in line:
                directories.append(line.strip())
            elif line.strip() and not line.startswith(' '):
                files.append(line.strip())
        
        return {
            'files': files,
            'directories': directories,
            'total_files': len(files),
            'total_directories': len(directories)
        }
    
    def _parse_ps_output(self, output: str) -> Dict[str, Any]:
        """Parse ps command output"""
        lines = output.strip().split('\n')
        processes = []
        
        if len(lines) > 1:
            header = lines[0]
            for line in lines[1:]:
                if line.strip():
                    processes.append(line.strip())
        
        return {'processes': processes, 'count': len(processes)}
    
    def _parse_top_output(self, output: str) -> Dict[str, Any]:
        """Parse top command output"""
        # Extract system information from top output
        cpu_match = re.search(r'%Cpu\(s\):\s*([\d.]+)', output)
        mem_match = re.search(r'KiB Mem:\s*([\d.]+)', output)
        
        result = {}
        if cpu_match:
            result['cpu_usage'] = float(cpu_match.group(1))
        if mem_match:
            result['memory_total'] = float(mem_match.group(1))
        
        return result
    
    def _parse_df_output(self, output: str) -> Dict[str, Any]:
        """Parse df command output"""
        lines = output.strip().split('\n')
        filesystems = []
        
        if len(lines) > 1:
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 6:
                        filesystems.append({
                            'filesystem': parts[0],
                            'size': parts[1],
                            'used': parts[2],
                            'available': parts[3],
                            'use_percent': parts[4],
                            'mounted_on': parts[5]
                        })
        
        return {'filesystems': filesystems}
    
    def _parse_ping_output(self, output: str) -> Dict[str, Any]:
        """Parse ping command output"""
        # Extract ping statistics
        packet_loss = re.search(r'(\d+)% packet loss', output)
        avg_time = re.search(r'avg = ([\d.]+)', output)
        
        result = {}
        if packet_loss:
            result['packet_loss'] = int(packet_loss.group(1))
        if avg_time:
            result['average_time'] = float(avg_time.group(1))
        
        return result
    
    def _parse_curl_output(self, output: str) -> Dict[str, Any]:
        """Parse curl command output"""
        # Basic curl output parsing
        result = {'response_received': bool(output.strip())}
        
        # Check for HTTP status codes
        status_match = re.search(r'HTTP/[\d.]+\s+(\d+)', output)
        if status_match:
            result['http_status'] = int(status_match.group(1))
        
        return result
    
    def _parse_wget_output(self, output: str) -> Dict[str, Any]:
        """Parse wget command output"""
        # Extract download information
        saved_match = re.search(r"'(.+)' saved", output)
        size_match = re.search(r'\[(\d+/\d+)\]', output)
        
        result = {}
        if saved_match:
            result['saved_file'] = saved_match.group(1)
        if size_match:
            result['download_progress'] = size_match.group(1)
        
        return result
