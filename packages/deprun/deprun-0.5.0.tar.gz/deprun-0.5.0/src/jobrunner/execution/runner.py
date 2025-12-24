"""Script execution runner."""

import os
import subprocess
from typing import Optional, List
from datetime import datetime

from jobrunner.exceptions import ExecutionError
from .result import ExecutionResult, ExecutionStatus


class ScriptRunner:
    """Handles script command execution."""
    
    def __init__(self, verbose: bool = False, quiet: bool = False):
        """Initialize script runner.
        
        Args:
            verbose: Enable verbose output
            quiet: Suppress command echo but show script output
        """
        self.verbose = verbose
        self.quiet = quiet
    
    def run_command(
        self,
        command: str,
        job_name: str,
        capture: bool = True,
        indent_level: int = 0,
        cwd: Optional[str] = None,
        env: Optional[dict] = None
    ) -> ExecutionResult:
        """Execute a shell command and return result.
        
        Args:
            command: Shell command to execute
            job_name: Name of job (for result tracking)
            capture: Whether to capture output
            indent_level: Indentation level for output
            cwd: Working directory for command execution (optional)
            env: Environment variables for command execution (optional)
            
        Returns:
            ExecutionResult with command execution details
        """
        result = ExecutionResult(
            name=job_name,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.now()
        )
        
        # Print command if not quiet
        if not self.quiet:
            self._print_command(command, indent_level)
        
        # Prepare environment: merge with current env if provided
        exec_env = None
        if env:
            exec_env = os.environ.copy()
            # Clean environment variable names (remove ^ prefix if present)
            clean_env = {k.lstrip("^"): v for k, v in env.items()}
            exec_env.update(clean_env)
        
        try:
            # Execute command
            process = subprocess.run(
                command,
                shell=True,
                capture_output=capture,
                text=True,
                check=True,
                cwd=cwd,
                env=exec_env
            )
            
            result.status = ExecutionStatus.SUCCESS
            result.exit_code = process.returncode
            
            if capture and process.stdout:
                result.output = process.stdout.splitlines()
            
        except subprocess.CalledProcessError as e:
            result.status = ExecutionStatus.FAILED
            result.exit_code = e.returncode
            result.error = f"Command failed with exit code {e.returncode}"
            
            if e.stderr:
                result.output = e.stderr.splitlines()
            
            raise ExecutionError(
                f"Command failed with exit code {e.returncode}: {command}"
            ) from e
        
        finally:
            result.end_time = datetime.now()
        
        return result
    
    def _print_command(self, command: str, indent_level: int) -> None:
        """Print command with appropriate formatting.
        
        Args:
            command: Command to print
            indent_level: Indentation level
        """
        if self.verbose:
            print(f"$ {command}")
        else:
            # Print command with indentation (preserve multiline for readability)
            cmd_lines = command.split('\n')
            indent = "  " * (indent_level + 1)
            
            if len(cmd_lines) > 1:
                # Multiline command - show with proper indentation
                for i, line in enumerate(cmd_lines):
                    stripped = line.strip()
                    if stripped:  # Skip empty lines
                        if i == 0:
                            print(f"{indent}$ {stripped}")
                        else:
                            print(f"{indent}  {stripped}")
            else:
                # Single line command
                print(f"{indent}$ {command.strip()}")
    
    def run_commands(
        self,
        commands: List[str],
        job_name: str,
        indent_level: int = 0
    ) -> List[ExecutionResult]:
        """Execute multiple commands sequentially.
        
        Args:
            commands: List of shell commands to execute
            job_name: Name of job (for result tracking)
            indent_level: Indentation level for output
            
        Returns:
            List of ExecutionResult objects
        """
        results = []
        
        for cmd in commands:
            # Determine if we should capture output
            capture = not (self.verbose or self.quiet)
            
            result = self.run_command(cmd, job_name, capture, indent_level)
            results.append(result)
        
        return results
