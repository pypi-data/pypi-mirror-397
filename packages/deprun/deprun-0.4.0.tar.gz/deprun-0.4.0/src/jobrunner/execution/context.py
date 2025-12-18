"""Execution context for job runs.

Provides context and state for execution, including environment variables,
working directory, and runtime configuration.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime


@dataclass
class ExecutionContext:
    """Context for job execution.
    
    Captures the state and environment for a job run, including
    working directory, environment variables, and runtime metadata.
    """
    
    # Job identification
    job_name: str
    run_id: str
    
    # Execution environment
    work_dir: Path
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    # Runtime configuration
    job_depth: int = 0
    max_depth: Optional[int] = None
    dry_run: bool = False
    verbose: bool = False
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    
    # Parent context (for nested jobs)
    parent: Optional['ExecutionContext'] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize context."""
        if isinstance(self.work_dir, str):
            self.work_dir = Path(self.work_dir)
    
    @property
    def is_root(self) -> bool:
        """Check if this is a root context (no parent)."""
        return self.parent is None
    
    @property
    def depth_exceeded(self) -> bool:
        """Check if max depth has been exceeded."""
        if self.max_depth is None:
            return False
        return self.job_depth >= self.max_depth
    
    def create_child(self, job_name: str, work_dir: Path = None) -> 'ExecutionContext':
        """Create a child context for a dependency.
        
        Args:
            job_name: Name of the child job
            work_dir: Working directory (inherits from parent if not specified)
            
        Returns:
            New ExecutionContext with incremented depth
        """
        return ExecutionContext(
            job_name=job_name,
            run_id=self.run_id,
            work_dir=work_dir or self.work_dir,
            env_vars=self.env_vars.copy(),
            job_depth=self.job_depth + 1,
            max_depth=self.max_depth,
            dry_run=self.dry_run,
            verbose=self.verbose,
            parent=self,
            metadata=self.metadata.copy(),
        )
    
    def get_env(self, key: str, default: str = None) -> Optional[str]:
        """Get environment variable with fallback to parent."""
        if key in self.env_vars:
            return self.env_vars[key]
        if self.parent:
            return self.parent.get_env(key, default)
        return default
    
    def set_env(self, key: str, value: str) -> None:
        """Set environment variable."""
        self.env_vars[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            'job_name': self.job_name,
            'run_id': self.run_id,
            'work_dir': str(self.work_dir),
            'env_vars': self.env_vars,
            'job_depth': self.job_depth,
            'max_depth': self.max_depth,
            'dry_run': self.dry_run,
            'verbose': self.verbose,
            'start_time': self.start_time.isoformat(),
            'is_root': self.is_root,
            'metadata': self.metadata,
        }
