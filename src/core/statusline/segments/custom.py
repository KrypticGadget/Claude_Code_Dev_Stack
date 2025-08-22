"""
Custom Segment

Allows users to create custom segments with their own data sources,
formatting, and display logic. Supports scripts, commands, and API calls.
"""

import os
import subprocess
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Callable

from .base import BaseSegment, SegmentData
from ..utils import ColorUtils
from ..themes import Theme


class CustomSegment(BaseSegment):
    """Segment that allows custom data sources and formatting"""
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        super().__init__(config, color_utils, theme)
        
        # Data source configuration
        self.data_source_type = config.get('data_source_type', 'command')
        self.data_source = config.get('data_source', '')
        self.data_format = config.get('data_format', 'text')
        
        # Command-specific options
        self.command_timeout = config.get('command_timeout', 10)
        self.command_shell = config.get('command_shell', True)
        self.command_cwd = config.get('command_cwd', os.getcwd())
        
        # File-specific options
        self.file_path = config.get('file_path', '')
        self.file_encoding = config.get('file_encoding', 'utf-8')
        
        # API-specific options
        self.api_url = config.get('api_url', '')
        self.api_method = config.get('api_method', 'GET')
        self.api_headers = config.get('api_headers', {})
        self.api_timeout = config.get('api_timeout', 10)
        
        # Environment variable options
        self.env_variable = config.get('env_variable', '')
        self.env_default = config.get('env_default', '')
        
        # Script options
        self.script_path = config.get('script_path', '')
        self.script_args = config.get('script_args', [])
        self.script_interpreter = config.get('script_interpreter', 'python')
        
        # Formatting options
        self.format_template = config.get('format_template', '{data}')
        self.prefix = config.get('prefix', '')
        self.suffix = config.get('suffix', '')
        self.show_label = config.get('show_label', False)
        self.label = config.get('label', 'Custom')
        
        # Value processing
        self.value_type = config.get('value_type', 'string')
        self.numeric_precision = config.get('numeric_precision', 2)
        self.unit = config.get('unit', '')
        
        # Status thresholds (for numeric values)
        self.warning_threshold = config.get('warning_threshold')
        self.critical_threshold = config.get('critical_threshold')
        self.threshold_comparison = config.get('threshold_comparison', 'greater')  # greater, less, equal
        
        # Error handling
        self.error_text = config.get('error_text', 'Error')
        self.show_errors = config.get('show_errors', True)
        
        # Custom function registry
        self._custom_functions: Dict[str, Callable] = {}
        
        # Data validation
        self._validate_config()
    
    def _validate_config(self):
        """Validate custom segment configuration"""
        if self.data_source_type == 'command' and not self.data_source:
            raise ValueError("Command data source requires 'data_source' to be specified")
        
        if self.data_source_type == 'file' and not self.file_path:
            raise ValueError("File data source requires 'file_path' to be specified")
        
        if self.data_source_type == 'api' and not self.api_url:
            raise ValueError("API data source requires 'api_url' to be specified")
        
        if self.data_source_type == 'env' and not self.env_variable:
            raise ValueError("Environment data source requires 'env_variable' to be specified")
        
        if self.data_source_type == 'script' and not self.script_path:
            raise ValueError("Script data source requires 'script_path' to be specified")
    
    def _collect_data(self) -> SegmentData:
        """Collect data from configured source"""
        try:
            # Get raw data based on source type
            raw_data = self._get_raw_data()
            
            if raw_data is None:
                return self._create_error_data("No data available")
            
            # Process the data
            processed_data = self._process_data(raw_data)
            
            # Format for display
            formatted_content = self._format_content(processed_data)
            
            # Determine status
            status = self._determine_status(processed_data)
            
            # Generate tooltip
            tooltip = self._generate_tooltip(processed_data, raw_data)
            
            return SegmentData(
                content=formatted_content,
                status=status,
                tooltip=tooltip,
                clickable=True
            )
            
        except Exception as e:
            return self._create_error_data(str(e))
    
    def _format_data(self, data: SegmentData) -> str:
        """Format custom data for display"""
        return data.content
    
    def _get_raw_data(self) -> Any:
        """Get raw data from the configured source"""
        if self.data_source_type == 'command':
            return self._get_command_data()
        elif self.data_source_type == 'file':
            return self._get_file_data()
        elif self.data_source_type == 'api':
            return self._get_api_data()
        elif self.data_source_type == 'env':
            return self._get_env_data()
        elif self.data_source_type == 'script':
            return self._get_script_data()
        elif self.data_source_type == 'function':
            return self._get_function_data()
        else:
            raise ValueError(f"Unknown data source type: {self.data_source_type}")
    
    def _get_command_data(self) -> Optional[str]:
        """Execute command and return output"""
        try:
            result = subprocess.run(
                self.data_source,
                shell=self.command_shell,
                capture_output=True,
                text=True,
                timeout=self.command_timeout,
                cwd=self.command_cwd
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
                
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None
    
    def _get_file_data(self) -> Optional[str]:
        """Read data from file"""
        try:
            if not os.path.exists(self.file_path):
                return None
            
            with open(self.file_path, 'r', encoding=self.file_encoding) as f:
                return f.read().strip()
                
        except Exception:
            return None
    
    def _get_api_data(self) -> Optional[Any]:
        """Get data from API endpoint"""
        try:
            request = urllib.request.Request(
                self.api_url,
                method=self.api_method
            )
            
            # Add headers
            for key, value in self.api_headers.items():
                request.add_header(key, value)
            
            response = urllib.request.urlopen(request, timeout=self.api_timeout)
            data = response.read().decode('utf-8')
            
            # Try to parse as JSON
            if self.data_format == 'json':
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    return data
            
            return data
            
        except Exception:
            return None
    
    def _get_env_data(self) -> Optional[str]:
        """Get data from environment variable"""
        return os.getenv(self.env_variable, self.env_default)
    
    def _get_script_data(self) -> Optional[str]:
        """Execute script and return output"""
        try:
            if not os.path.exists(self.script_path):
                return None
            
            cmd = [self.script_interpreter, self.script_path] + self.script_args
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.command_timeout,
                cwd=self.command_cwd
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
                
        except Exception:
            return None
    
    def _get_function_data(self) -> Any:
        """Get data from custom function"""
        function_name = self.data_source
        if function_name in self._custom_functions:
            try:
                return self._custom_functions[function_name]()
            except Exception:
                return None
        
        return None
    
    def _process_data(self, raw_data: Any) -> Any:
        """Process raw data based on configuration"""
        if raw_data is None:
            return None
        
        # Handle JSON data extraction
        if self.data_format == 'json' and isinstance(raw_data, dict):
            json_path = self.config.get('json_path', '')
            if json_path:
                return self._extract_json_value(raw_data, json_path)
        
        # Convert data type
        if self.value_type == 'number':
            try:
                if isinstance(raw_data, str):
                    # Extract numeric value from string
                    import re
                    match = re.search(r'[-+]?\d*\.?\d+', raw_data)
                    if match:
                        return float(match.group())
                elif isinstance(raw_data, (int, float)):
                    return float(raw_data)
            except (ValueError, TypeError):
                pass
        
        elif self.value_type == 'boolean':
            if isinstance(raw_data, str):
                return raw_data.lower() in ('true', 'yes', '1', 'on', 'enabled')
            elif isinstance(raw_data, bool):
                return raw_data
        
        # Return as string by default
        return str(raw_data)
    
    def _extract_json_value(self, data: dict, path: str) -> Any:
        """Extract value from JSON data using dot notation path"""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        
        return current
    
    def _format_content(self, processed_data: Any) -> str:
        """Format processed data for display"""
        if processed_data is None:
            return self.error_text
        
        # Format numeric values
        if self.value_type == 'number' and isinstance(processed_data, (int, float)):
            formatted_value = f"{processed_data:.{self.numeric_precision}f}"
            if self.unit:
                formatted_value += self.unit
        else:
            formatted_value = str(processed_data)
        
        # Apply template
        content = self.format_template.format(
            data=formatted_value,
            value=processed_data,
            label=self.label
        )
        
        # Add prefix and suffix
        if self.prefix:
            content = self.prefix + content
        if self.suffix:
            content = content + self.suffix
        
        # Add label if enabled
        if self.show_label:
            content = f"{self.label}: {content}"
        
        return content
    
    def _determine_status(self, processed_data: Any) -> str:
        """Determine status based on data and thresholds"""
        if processed_data is None:
            return 'error'
        
        # Check thresholds for numeric values
        if (self.value_type == 'number' and 
            isinstance(processed_data, (int, float)) and 
            (self.warning_threshold is not None or self.critical_threshold is not None)):
            
            value = float(processed_data)
            
            # Check critical threshold first
            if self.critical_threshold is not None:
                if self._compare_threshold(value, self.critical_threshold):
                    return 'critical'
            
            # Check warning threshold
            if self.warning_threshold is not None:
                if self._compare_threshold(value, self.warning_threshold):
                    return 'warning'
            
            return 'normal'
        
        # Boolean status
        if self.value_type == 'boolean':
            return 'active' if processed_data else 'inactive'
        
        # Default status
        return 'normal'
    
    def _compare_threshold(self, value: float, threshold: float) -> bool:
        """Compare value against threshold using configured comparison"""
        if self.threshold_comparison == 'greater':
            return value > threshold
        elif self.threshold_comparison == 'less':
            return value < threshold
        elif self.threshold_comparison == 'equal':
            return abs(value - threshold) < 0.001  # Floating point tolerance
        else:
            return False
    
    def _generate_tooltip(self, processed_data: Any, raw_data: Any) -> str:
        """Generate tooltip with detailed information"""
        lines = []
        
        # Basic info
        lines.append(f"Custom Segment: {self.label}")
        lines.append(f"Data Source: {self.data_source_type}")
        
        # Source details
        if self.data_source_type == 'command':
            lines.append(f"Command: {self.data_source}")
        elif self.data_source_type == 'file':
            lines.append(f"File: {self.file_path}")
        elif self.data_source_type == 'api':
            lines.append(f"API: {self.api_url}")
        elif self.data_source_type == 'env':
            lines.append(f"Environment: {self.env_variable}")
        elif self.data_source_type == 'script':
            lines.append(f"Script: {self.script_path}")
        
        # Data info
        if processed_data is not None:
            lines.append(f"Value: {processed_data}")
            if self.value_type == 'number' and isinstance(processed_data, (int, float)):
                lines.append(f"Type: Number")
                if self.warning_threshold is not None:
                    lines.append(f"Warning threshold: {self.warning_threshold}")
                if self.critical_threshold is not None:
                    lines.append(f"Critical threshold: {self.critical_threshold}")
        
        # Raw data (if different)
        if raw_data != processed_data and raw_data is not None:
            raw_str = str(raw_data)
            if len(raw_str) > 100:
                raw_str = raw_str[:97] + '...'
            lines.append(f"Raw data: {raw_str}")
        
        # Last update
        lines.append(f"Last updated: {time.strftime('%H:%M:%S')}")
        
        return '\n'.join(lines)
    
    def _create_error_data(self, error_message: str) -> SegmentData:
        """Create SegmentData for error conditions"""
        if self.show_errors:
            content = self.error_text
            tooltip = f"Error in custom segment '{self.label}': {error_message}"
        else:
            content = ""
            tooltip = "Custom segment error (hidden)"
        
        return SegmentData(
            content=content,
            status='error',
            tooltip=tooltip
        )
    
    def register_function(self, name: str, function: Callable):
        """Register a custom function as a data source"""
        self._custom_functions[name] = function
    
    def unregister_function(self, name: str):
        """Unregister a custom function"""
        if name in self._custom_functions:
            del self._custom_functions[name]
    
    def test_data_source(self) -> Dict[str, Any]:
        """Test the data source and return diagnostic information"""
        test_result = {
            'source_type': self.data_source_type,
            'source': self.data_source,
            'timestamp': time.time(),
            'success': False,
            'raw_data': None,
            'processed_data': None,
            'error': None
        }
        
        try:
            # Test raw data collection
            raw_data = self._get_raw_data()
            test_result['raw_data'] = raw_data
            
            if raw_data is not None:
                # Test data processing
                processed_data = self._process_data(raw_data)
                test_result['processed_data'] = processed_data
                test_result['success'] = True
            else:
                test_result['error'] = "No data returned from source"
                
        except Exception as e:
            test_result['error'] = str(e)
        
        return test_result
    
    def get_data_source_info(self) -> Dict[str, Any]:
        """Get information about the configured data source"""
        info = {
            'type': self.data_source_type,
            'source': self.data_source,
            'format': self.data_format,
            'value_type': self.value_type
        }
        
        if self.data_source_type == 'command':
            info.update({
                'timeout': self.command_timeout,
                'shell': self.command_shell,
                'cwd': self.command_cwd
            })
        elif self.data_source_type == 'file':
            info.update({
                'file_path': self.file_path,
                'encoding': self.file_encoding,
                'exists': os.path.exists(self.file_path)
            })
        elif self.data_source_type == 'api':
            info.update({
                'url': self.api_url,
                'method': self.api_method,
                'headers': self.api_headers,
                'timeout': self.api_timeout
            })
        elif self.data_source_type == 'env':
            info.update({
                'variable': self.env_variable,
                'default': self.env_default,
                'current_value': os.getenv(self.env_variable)
            })
        elif self.data_source_type == 'script':
            info.update({
                'script_path': self.script_path,
                'interpreter': self.script_interpreter,
                'args': self.script_args,
                'exists': os.path.exists(self.script_path)
            })
        
        return info
    
    def update_data_source(self, source_type: str = None, source: str = None, **kwargs):
        """Update data source configuration"""
        if source_type:
            self.data_source_type = source_type
        if source:
            self.data_source = source
        
        # Update other parameters
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Validate new configuration
        self._validate_config()
        
        # Clear cache to force refresh
        self.clear_cache()