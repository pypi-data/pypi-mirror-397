"""Parallel job execution with dependency-aware scheduling.

Implements a proper dependency scheduler that:
1. Analyzes the full dependency graph
2. Identifies jobs ready to run (dependencies satisfied)
3. Executes ready jobs in parallel
4. Dynamically updates the ready queue as jobs complete
"""

import os
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import List, Dict, Set, Optional
from datetime import datetime

from jobrunner.core.executor import JobExecutor
from jobrunner.core.resolver import DependencyResolver
from jobrunner.execution import ExecutionResult, ExecutionStatus
from jobrunner.config.models import Job


class ParallelExecutor(JobExecutor):
    """Dependency-aware parallel executor.
    
    Schedules jobs based on dependency graph:
    - Jobs with satisfied dependencies run immediately (in parallel)
    - As jobs complete, newly-ready jobs are added to execution queue
    - Maximizes parallelism while respecting dependencies
    """
    
    def __init__(self, config, max_workers: int = None, **kwargs):
        """Initialize parallel executor.
        
        Args:
            config: Configuration object
            max_workers: Maximum number of parallel workers (default: CPU count)
            **kwargs: Additional arguments passed to JobExecutor
        """
        super().__init__(config, **kwargs)
        self.max_workers = max_workers or os.cpu_count() or 4
        self.lock = threading.Lock()  # Thread-safe state updates
    
    def run(self, job_name: str, max_depth: Optional[int] = None) -> ExecutionResult:
        """Run a job and its dependencies in parallel.
        
        Args:
            job_name: Name of the job to run
            max_depth: Maximum dependency depth (None for unlimited)
            
        Returns:
            ExecutionResult for the requested job
        """
        # Get all jobs in execution order (includes dependencies)
        resolver = DependencyResolver(self.config)
        all_jobs = resolver.get_execution_order(job_name)
        
        # Run all jobs with parallel scheduling
        results = self.run_parallel(all_jobs, max_depth)
        
        # Return result for the requested job
        return results.get(job_name)
    
    def run_parallel(self, job_names: List[str], max_depth: Optional[int] = None) -> Dict[str, ExecutionResult]:
        """Run multiple jobs with dependency-aware parallel scheduling.
        
        Algorithm:
        1. Build dependency map for all jobs
        2. Identify initially ready jobs (no dependencies)
        3. Submit ready jobs to thread pool
        4. When a job completes, check which jobs became ready
        5. Submit newly ready jobs to thread pool
        6. Repeat until all jobs complete or failure occurs
        
        Args:
            job_names: List of job names to execute
            max_depth: Maximum dependency depth to process
            
        Returns:
            Dictionary mapping job names to their execution results
        """
        resolver = DependencyResolver(self.config)
        
        # Build complete dependency graph
        all_jobs = set()
        for job_name in job_names:
            all_jobs.update(resolver.get_all_dependencies(job_name))
            all_jobs.add(job_name)
        
        # Build dependency map: job -> set of dependencies
        dep_map = self._build_dependency_map(all_jobs)
        
        # Track state
        completed: Set[str] = set()      # Jobs that finished successfully
        failed: Set[str] = set()          # Jobs that failed
        running: Set[str] = set()         # Jobs currently executing
        pending: Set[str] = all_jobs.copy()  # Jobs not yet started
        results: Dict[str, ExecutionResult] = {}
        
        print(f"\n🚀 Parallel execution: {len(all_jobs)} job(s), max {self.max_workers} workers\n")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Map futures to job names
            futures: Dict[Future, str] = {}
            
            # Initial submission: jobs with no dependencies
            ready = self._get_ready_jobs(pending, completed, failed, dep_map)
            for job_name in ready:
                future = executor.submit(self._execute_job, job_name, max_depth)
                futures[future] = job_name
                running.add(job_name)
                pending.discard(job_name)
                print(f"  ⏳ Started: {job_name}")
            
            # Process completions and submit new jobs dynamically
            while futures:
                # Wait for next job to complete
                done_futures = []
                for future in futures:
                    if future.done():
                        done_futures.append(future)
                
                if not done_futures:
                    # No jobs finished yet, wait a bit
                    import time
                    time.sleep(0.1)
                    continue
                
                # Process completed jobs
                for future in done_futures:
                    job_name = futures.pop(future)
                    running.discard(job_name)
                    
                    try:
                        result = future.result()
                        results[job_name] = result
                        
                        if result.status == ExecutionStatus.SUCCESS:
                            completed.add(job_name)
                            print(f"  ✅ Completed: {job_name} ({result.duration_seconds:.1f}s)")
                        else:
                            failed.add(job_name)
                            print(f"  ❌ Failed: {job_name} - {result.error}")
                            # Stop submitting new jobs on failure
                            pending.clear()
                            
                    except Exception as e:
                        failed.add(job_name)
                        print(f"  ❌ Exception: {job_name} - {e}")
                        pending.clear()
                
                # Check if more jobs are ready to run
                if pending and not failed:
                    ready = self._get_ready_jobs(pending, completed, failed, dep_map)
                    for job_name in ready:
                        future = executor.submit(self._execute_job, job_name, max_depth)
                        futures[future] = job_name
                        running.add(job_name)
                        pending.discard(job_name)
                        print(f"  ⏳ Started: {job_name}")
        
        # Print summary
        self._print_summary(results, all_jobs)
        
        return results
    
    def _build_dependency_map(self, job_names: Set[str]) -> Dict[str, Set[str]]:
        """Build map of each job's direct dependencies.
        
        Args:
            job_names: Set of all job names
            
        Returns:
            Dictionary mapping job name to set of its dependencies
        """
        dep_map = {}
        for job_name in job_names:
            job = self.config.jobs.get(job_name)
            if job and job.dependencies:
                # Filter to only include dependencies that are in our job set
                deps = set(job.dependencies) & job_names
                dep_map[job_name] = deps
            else:
                dep_map[job_name] = set()
        return dep_map
    
    def _get_ready_jobs(self, pending: Set[str], completed: Set[str], 
                       failed: Set[str], dep_map: Dict[str, Set[str]]) -> List[str]:
        """Get jobs that are ready to run (all dependencies satisfied).
        
        Args:
            pending: Jobs not yet started
            completed: Jobs that completed successfully
            failed: Jobs that failed
            dep_map: Dependency map
            
        Returns:
            List of job names ready to execute
        """
        ready = []
        for job_name in pending:
            dependencies = dep_map.get(job_name, set())
            
            # Check if any dependency failed
            if dependencies & failed:
                continue
            
            # Check if all dependencies completed
            if dependencies.issubset(completed):
                ready.append(job_name)
        
        return ready
    
    def _execute_job(self, job_name: str, max_depth: Optional[int]) -> ExecutionResult:
        """Execute a single job (called by thread pool).
        
        IMPORTANT: This method must be thread-safe since it runs in parallel threads.
        We pass cwd and env directly to subprocess instead of using context managers
        that modify global process state (os.chdir, os.environ), which would cause
        race conditions between threads.
        
        Args:
            job_name: Name of job to execute
            max_depth: Maximum dependency depth
            
        Returns:
            ExecutionResult
        """
        start_time = datetime.now()
        
        try:
            if job_name not in self.config.jobs:
                raise RuntimeError(f"Job '{job_name}' not found")
            
            job = self.config.jobs[job_name]
            
            # Execute the job's scripts (dependencies already handled)
            with self.lock:
                self._print_start(job_name)
            
            if job.script:
                work_dir = self._get_work_dir(job_name, job)
                
                # Thread-safe execution: pass cwd and env directly to subprocess
                # instead of using context managers that modify global process state
                self._run_scripts(
                    job.script, 
                    job_name, 
                    job,
                    cwd=str(work_dir) if work_dir else None,
                    env=job.env if job.env else None
                )
            
            # Create success result
            end_time = datetime.now()
            result = ExecutionResult(
                name=job_name,
                status=ExecutionStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                exit_code=0
            )
            
            with self.lock:
                self.completed.add(job_name)
                self.results.append(result)
                self.report.add_result(result)
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            result = ExecutionResult(
                name=job_name,
                status=ExecutionStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                exit_code=1,
                error=str(e)
            )
            
            with self.lock:
                self.results.append(result)
                self.report.add_result(result)
            
            return result
    
    def _print_summary(self, results: Dict[str, ExecutionResult], all_jobs: Set[str]) -> None:
        """Print execution summary.
        
        Args:
            results: Dictionary of execution results
            all_jobs: Set of all job names
        """
        if not results:
            return
        
        start_time = min((r.start_time for r in results.values()), default=datetime.now())
        end_time = max((r.end_time for r in results.values()), default=datetime.now())
        wall_time = (end_time - start_time).total_seconds()
        
        success_count = sum(1 for r in results.values() if r.status == ExecutionStatus.SUCCESS)
        failed_count = sum(1 for r in results.values() if r.status == ExecutionStatus.FAILED)
        
        total_job_time = sum(r.duration_seconds for r in results.values())
        speedup = total_job_time / wall_time if wall_time > 0 else 1.0
        
        print(f"\n{'='*60}")
        print(f"✨ Execution Complete!")
        print(f"   Wall time: {wall_time:.1f}s")
        print(f"   Total CPU time: {total_job_time:.1f}s")
        print(f"   Speedup: {speedup:.2f}x")
        print(f"   Success: {success_count}/{len(all_jobs)}")
        if failed_count > 0:
            print(f"   Failed: {failed_count}")
        print(f"{'='*60}\n")
