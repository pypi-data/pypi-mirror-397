"""Progress tracking for job execution.

Provides visual progress indicators and status updates during execution,
including progress bars, spinners, and live updates.
"""

from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum


class ProgressStyle(str, Enum):
    """Progress display styles."""
    NONE = "none"           # No progress display
    SIMPLE = "simple"       # Simple text updates
    BAR = "bar"             # Progress bar
    SPINNER = "spinner"     # Spinner animation
    LIVE = "live"           # Live updating display


class ProgressTracker:
    """Track and display progress of job execution.
    
    Provides various progress indicators to give users feedback
    during long-running operations.
    """
    
    def __init__(self, style: ProgressStyle = ProgressStyle.SIMPLE):
        """Initialize progress tracker.
        
        Args:
            style: Display style for progress
        """
        self.style = style
        self.jobs: Dict[str, Dict] = {}
        self.start_time = None
        self.current_job = None
        
    def start(self, total_jobs: int) -> None:
        """Start tracking progress.
        
        Args:
            total_jobs: Total number of jobs to track
        """
        self.start_time = datetime.now()
        self.total_jobs = total_jobs
        self.completed_jobs = 0
        
        if self.style != ProgressStyle.NONE:
            print(f"\n🚀 Starting execution of {total_jobs} job(s)...\n")
    
    def start_job(self, job_name: str, tasks: Optional[List[str]] = None) -> None:
        """Mark a job as started.
        
        Args:
            job_name: Name of the job
            tasks: List of task names (optional)
        """
        self.current_job = job_name
        self.jobs[job_name] = {
            'status': 'running',
            'start_time': datetime.now(),
            'tasks': tasks or [],
            'completed_tasks': 0,
        }
        
        if self.style == ProgressStyle.SIMPLE:
            print(f"⏳ Starting: {job_name}")
        elif self.style == ProgressStyle.BAR:
            self._update_progress_bar()
        elif self.style == ProgressStyle.SPINNER:
            print(f"⠋ {job_name}...", end='\r')
    
    def update_task(self, job_name: str, task_name: str) -> None:
        """Update progress for a task within a job.
        
        Args:
            job_name: Name of the job
            task_name: Name of the task that completed
        """
        if job_name in self.jobs:
            self.jobs[job_name]['completed_tasks'] += 1
            
            if self.style == ProgressStyle.SIMPLE:
                tasks = self.jobs[job_name]['tasks']
                completed = self.jobs[job_name]['completed_tasks']
                if tasks:
                    print(f"  └─ {task_name} ({completed}/{len(tasks)})")
    
    def complete_job(self, job_name: str, success: bool = True) -> None:
        """Mark a job as completed.
        
        Args:
            job_name: Name of the job
            success: Whether the job succeeded
        """
        if job_name in self.jobs:
            self.jobs[job_name]['status'] = 'success' if success else 'failed'
            self.jobs[job_name]['end_time'] = datetime.now()
            self.completed_jobs += 1
            
            if self.style == ProgressStyle.SIMPLE:
                icon = "✅" if success else "❌"
                duration = self._get_duration(job_name)
                print(f"{icon} {job_name} ({duration:.1f}s)")
            elif self.style == ProgressStyle.BAR:
                self._update_progress_bar()
    
    def finish(self) -> None:
        """Finish tracking and show summary."""
        if self.start_time and self.style != ProgressStyle.NONE:
            duration = (datetime.now() - self.start_time).total_seconds()
            success_count = sum(1 for j in self.jobs.values() 
                              if j['status'] == 'success')
            failed_count = sum(1 for j in self.jobs.values() 
                             if j['status'] == 'failed')
            
            print(f"\n{'='*60}")
            print(f"✨ Execution complete!")
            print(f"   Total time: {duration:.1f}s")
            print(f"   Success: {success_count}/{self.total_jobs}")
            if failed_count > 0:
                print(f"   Failed: {failed_count}")
            print(f"{'='*60}\n")
    
    def _get_duration(self, job_name: str) -> float:
        """Get duration of a job in seconds."""
        job = self.jobs.get(job_name, {})
        if 'start_time' in job and 'end_time' in job:
            return (job['end_time'] - job['start_time']).total_seconds()
        return 0.0
    
    def _update_progress_bar(self) -> None:
        """Update progress bar display."""
        if self.total_jobs == 0:
            return
            
        percent = (self.completed_jobs / self.total_jobs) * 100
        bar_length = 40
        filled = int(bar_length * self.completed_jobs / self.total_jobs)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\rProgress: |{bar}| {percent:.0f}% ({self.completed_jobs}/{self.total_jobs})", 
              end='', flush=True)
        
        if self.completed_jobs == self.total_jobs:
            print()  # New line when complete


class LiveProgressDisplay:
    """Live updating progress display.
    
    Shows real-time updates of running jobs, completed jobs,
    and overall progress in a rich terminal UI.
    """
    
    def __init__(self):
        """Initialize live display."""
        self.jobs: Dict[str, Dict] = {}
        self.enabled = False
    
    def start(self) -> None:
        """Start live display."""
        try:
            # Could integrate with rich.live here
            self.enabled = True
        except ImportError:
            self.enabled = False
    
    def update(self, job_name: str, status: str, details: str = "") -> None:
        """Update live display.
        
        Args:
            job_name: Name of the job
            status: Current status
            details: Additional details
        """
        if not self.enabled:
            return
            
        self.jobs[job_name] = {
            'status': status,
            'details': details,
            'updated': datetime.now(),
        }
        self._refresh()
    
    def _refresh(self) -> None:
        """Refresh the display."""
        # Implementation would use rich.live or similar
        pass
    
    def stop(self) -> None:
        """Stop live display."""
        self.enabled = False
