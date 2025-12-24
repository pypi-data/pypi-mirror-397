"""Shell utilities for command execution.

Provides helper functions for shell operations, command validation,
and working directory management.
"""

import os
import shlex
from pathlib import Path
from typing import Dict, Optional, List


class ShellUtils:
    """Utilities for shell command operations."""
    
    @staticmethod
    def resolve_command(command: str, variables: Dict[str, str]) -> str:
        """Resolve template variables in command.
        
        Args:
            command: Command string with template variables
            variables: Dictionary of variable values
            
        Returns:
            Resolved command string
        """
        resolved = command
        for key, value in variables.items():
            placeholder = f"${{{key}}}"
            resolved = resolved.replace(placeholder, value)
        return resolved
    
    @staticmethod
    def validate_command(command: str) -> bool:
        """Validate if command is safe to execute.
        
        Args:
            command: Command to validate
            
        Returns:
            True if command appears safe
        """
        # Basic validation - can be extended
        if not command or not command.strip():
            return False
        return True
    
    @staticmethod
    def get_work_dir(base_path: Path, job_directory: Optional[str] = None) -> Path:
        """Get working directory for job execution.
        
        Args:
            base_path: Base directory path
            job_directory: Optional subdirectory for job
            
        Returns:
            Resolved working directory path
        """
        work_dir = base_path
        if job_directory:
            work_dir = base_path / job_directory
        
        # Create if it doesn't exist
        work_dir.mkdir(parents=True, exist_ok=True)
        return work_dir
    
    @staticmethod
    def format_command_for_display(command: str, max_length: int = 80) -> str:
        """Format command for display, truncating if needed.
        
        Args:
            command: Command to format
            max_length: Maximum display length
            
        Returns:
            Formatted command string
        """
        if len(command) <= max_length:
            return command
        return command[:max_length-3] + "..."
    
    @staticmethod
    def parse_env_vars(env_list: Optional[List[str]]) -> Dict[str, str]:
        """Parse environment variables from list of KEY=VALUE strings.
        
        Args:
            env_list: List of "KEY=VALUE" strings
            
        Returns:
            Dictionary of environment variables
        """
        if not env_list:
            return {}
        
        env_dict = {}
        for item in env_list:
            if '=' in item:
                key, value = item.split('=', 1)
                env_dict[key.strip()] = value.strip()
        return env_dict
    
    @staticmethod
    def merge_env(base_env: Optional[Dict[str, str]], 
                  additional_env: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Merge environment variables.
        
        Args:
            base_env: Base environment (usually os.environ)
            additional_env: Additional variables to add/override
            
        Returns:
            Merged environment dictionary
        """
        if base_env is None:
            base_env = os.environ.copy()
        else:
            base_env = base_env.copy()
        
        if additional_env:
            base_env.update(additional_env)
        
        return base_env
