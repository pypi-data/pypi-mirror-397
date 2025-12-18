"""Execution result tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class ExecutionStatus(str, Enum):
    """Status of job/task execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class ExecutionResult:
    """Result of job/task execution."""
    name: str
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    exit_code: int = 0
    error: Optional[str] = None
    output: List[str] = field(default_factory=list)
    changed: bool = False
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.SUCCESS
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'status': self.status.value,
            'duration': self.duration_seconds,
            'exit_code': self.exit_code,
            'error': self.error,
            'changed': self.changed,
            'cached': self.cached,
            'metadata': self.metadata,
        }


class ExecutionReport:
    """Report of full execution run."""
    
    def __init__(self):
        self.results: List[ExecutionResult] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
    
    def add_result(self, result: ExecutionResult) -> None:
        """Add a result to the report."""
        self.results.append(result)
    
    @property
    def total_duration(self) -> float:
        """Total duration of all jobs."""
        return sum(r.duration_seconds for r in self.results)
    
    @property
    def success_count(self) -> int:
        """Number of successful jobs."""
        return sum(1 for r in self.results 
                  if r.status == ExecutionStatus.SUCCESS)
    
    @property
    def failure_count(self) -> int:
        """Number of failed jobs."""
        return sum(1 for r in self.results 
                  if r.status == ExecutionStatus.FAILED)
    
    @property
    def skipped_count(self) -> int:
        """Number of skipped jobs."""
        return sum(1 for r in self.results 
                  if r.status == ExecutionStatus.SKIPPED)
    
    def finalize(self) -> None:
        """Mark report as complete."""
        self.end_time = datetime.now()
    
    def summary(self) -> str:
        """Generate a summary string."""
        total = len(self.results)
        return (
            f"Execution Report: {total} jobs\n"
            f"  Success: {self.success_count}\n"
            f"  Failed: {self.failure_count}\n"
            f"  Skipped: {self.skipped_count}\n"
            f"  Total Time: {self.total_duration:.2f}s"
        )
