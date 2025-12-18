"""Dependency resolution for job runner."""

from typing import List, Set, Dict, Optional
from jobrunner.config.models import Job, Config
from jobrunner.exceptions import ExecutionError


class DependencyResolver:
    """Resolves job dependencies and execution order."""
    
    def __init__(self, config: Config):
        """Initialize resolver.
        
        Args:
            config: Configuration object with jobs
        """
        self.config = config
    
    def get_execution_order(
        self, 
        job_name: str,
        max_depth: Optional[int] = None
    ) -> List[str]:
        """Get the order in which jobs should execute.
        
        Args:
            job_name: Starting job name
            max_depth: Maximum depth to follow dependencies
            
        Returns:
            List of job names in execution order (dependencies first)
        """
        order = []
        visited = set()
        
        def visit(name: str, depth: int = 0) -> None:
            """Visit a job and its dependencies."""
            if name in visited:
                return
            
            if max_depth is not None and depth > max_depth:
                return
            
            if name not in self.config.jobs:
                raise ExecutionError(f"Job '{name}' not found")
            
            visited.add(name)
            job = self.config.jobs[name]
            
            # Visit dependencies first
            if job.dependencies:
                for dep in job.dependencies:
                    # Handle task references (job:task)
                    dep_job = dep.split(':')[0]
                    visit(dep_job, depth + 1)
            
            # Add this job after its dependencies
            if name not in order:
                order.append(name)
        
        visit(job_name)
        return order
    
    def validate_dependencies(self) -> List[str]:
        """Validate all job dependencies.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        for job_name, job in self.config.jobs.items():
            if not job.dependencies:
                continue
            
            for dep in job.dependencies:
                # Handle task references
                dep_job = dep.split(':')[0]
                
                # Check if dependency exists
                if dep_job not in self.config.jobs:
                    errors.append(
                        f"Job '{job_name}' has invalid dependency: '{dep}' "
                        f"(job '{dep_job}' not found)"
                    )
                
                # Check for task reference validity
                if ':' in dep:
                    dep_job, dep_task = dep.split(':', 1)
                    if dep_job in self.config.jobs:
                        target_job = self.config.jobs[dep_job]
                        if not target_job.tasks or dep_task not in target_job.tasks:
                            available = ", ".join(target_job.tasks.keys()) if target_job.tasks else "none"
                            errors.append(
                                f"Job '{job_name}' references non-existent task: '{dep}' "
                                f"(available: {available})"
                            )
        
        # Check for circular dependencies
        circular = self._find_circular_dependencies()
        if circular:
            errors.append(f"Circular dependency detected: {' -> '.join(circular)}")
        
        return errors
    
    def _find_circular_dependencies(self) -> Optional[List[str]]:
        """Find circular dependencies in the job graph.
        
        Returns:
            List representing the circular path, or None if no cycle
        """
        visited = set()
        rec_stack = []
        
        def visit(job_name: str) -> Optional[List[str]]:
            """Visit a job looking for cycles."""
            if job_name in rec_stack:
                # Found a cycle
                cycle_start = rec_stack.index(job_name)
                return rec_stack[cycle_start:] + [job_name]
            
            if job_name in visited:
                return None
            
            if job_name not in self.config.jobs:
                return None
            
            visited.add(job_name)
            rec_stack.append(job_name)
            
            job = self.config.jobs[job_name]
            if job.dependencies:
                for dep in job.dependencies:
                    dep_job = dep.split(':')[0]
                    cycle = visit(dep_job)
                    if cycle:
                        return cycle
            
            rec_stack.pop()
            return None
        
        # Check all jobs
        for job_name in self.config.jobs:
            cycle = visit(job_name)
            if cycle:
                return cycle
        
        return None
    
    def get_dependency_tree(self, job_name: str, max_depth: Optional[int] = None) -> Dict:
        """Get dependency tree for visualization.
        
        Args:
            job_name: Starting job name
            max_depth: Maximum depth to follow
            
        Returns:
            Dictionary representing the tree structure
        """
        if job_name not in self.config.jobs:
            raise ExecutionError(f"Job '{job_name}' not found")
        
        def build_tree(name: str, depth: int = 0) -> Dict:
            """Build tree recursively."""
            if max_depth is not None and depth > max_depth:
                return {'name': name, 'truncated': True}
            
            job = self.config.jobs.get(name)
            if not job:
                return {'name': name, 'error': 'not found'}
            
            tree = {'name': name, 'type': job.type.value}
            
            if job.dependencies:
                tree['dependencies'] = [
                    build_tree(dep.split(':')[0], depth + 1)
                    for dep in job.dependencies
                ]
            
            return tree
        
        return build_tree(job_name)
    
    def get_all_dependencies(self, job_name: str) -> Set[str]:
        """Get all transitive dependencies of a job.
        
        Args:
            job_name: Job name
            
        Returns:
            Set of all dependency job names
        """
        deps = set()
        
        def collect(name: str) -> None:
            """Collect dependencies recursively."""
            if name not in self.config.jobs:
                return
            
            job = self.config.jobs[name]
            if job.dependencies:
                for dep in job.dependencies:
                    dep_job = dep.split(':')[0]
                    if dep_job not in deps:
                        deps.add(dep_job)
                        collect(dep_job)
        
        collect(job_name)
        return deps
