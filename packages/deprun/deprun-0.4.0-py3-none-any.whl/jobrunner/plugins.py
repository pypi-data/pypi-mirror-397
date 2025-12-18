"""Plugin system for job-runner."""

from abc import ABC, abstractmethod
from typing import Optional

from jobrunner.config.models import Job
from jobrunner.execution import ExecutionResult


class DeprunPlugin(ABC):
    """Base class for deprun plugins."""
    
    @property
    def name(self) -> str:
        """Return plugin name."""
        return self.__class__.__name__
    
    def on_job_start(self, job_name: str, job: Job) -> None:
        """Called before a job starts execution.
        
        Args:
            job_name: Name of the job
            job: Job object
        """
        pass
    
    def on_job_end(self, job_name: str, result: ExecutionResult) -> None:
        """Called after a job completes execution.
        
        Args:
            job_name: Name of the job
            result: Execution result
        """
        pass
    
    def on_task_start(self, job_name: str, task_name: str, job: Job) -> None:
        """Called before a task starts execution.
        
        Args:
            job_name: Name of the job
            task_name: Name of the task
            job: Job object
        """
        pass
    
    def on_task_end(self, job_name: str, task_name: str, result: ExecutionResult) -> None:
        """Called after a task completes execution.
        
        Args:
            job_name: Name of the job
            task_name: Name of the task
            result: Execution result
        """
        pass
    
    def on_command_start(self, command: str, job_name: str) -> None:
        """Called before a command executes.
        
        Args:
            command: Shell command
            job_name: Name of the job
        """
        pass
    
    def on_command_end(self, command: str, result: ExecutionResult) -> None:
        """Called after a command completes.
        
        Args:
            command: Shell command
            result: Execution result
        """
        pass
    
    def on_error(self, error: Exception, context: dict) -> Optional[bool]:
        """Called when an error occurs.
        
        Args:
            error: The exception that occurred
            context: Dictionary with context (job_name, task_name, etc.)
            
        Returns:
            True to suppress error, False/None to propagate
        """
        return None


class LoggingPlugin(DeprunPlugin):
    """Example plugin: Enhanced logging."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize logging plugin.
        
        Args:
            log_file: Optional file to write logs to
        """
        self.log_file = log_file
        self._log_handle = None
        
        if log_file:
            self._log_handle = open(log_file, 'a')
    
    def _log(self, message: str) -> None:
        """Write log message."""
        if self._log_handle:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            self._log_handle.write(f"[{timestamp}] {message}\n")
            self._log_handle.flush()
    
    def on_job_start(self, job_name: str, job: Job) -> None:
        """Log job start."""
        self._log(f"Starting job: {job_name}")
    
    def on_job_end(self, job_name: str, result: ExecutionResult) -> None:
        """Log job end."""
        self._log(
            f"Completed job: {job_name} "
            f"(status={result.status.value}, duration={result.duration_seconds:.2f}s)"
        )
    
    def __del__(self):
        """Close log file."""
        if self._log_handle:
            self._log_handle.close()


class TimingPlugin(DeprunPlugin):
    """Example plugin: Track execution timing."""
    
    def __init__(self):
        """Initialize timing plugin."""
        self.timings = {}
    
    def on_job_end(self, job_name: str, result: ExecutionResult) -> None:
        """Record job timing."""
        self.timings[job_name] = result.duration_seconds
    
    def print_report(self) -> None:
        """Print timing report."""
        print("\n=== Timing Report ===")
        for job, duration in sorted(self.timings.items(), key=lambda x: x[1], reverse=True):
            print(f"  {job}: {duration:.2f}s")
        print(f"Total: {sum(self.timings.values()):.2f}s")
