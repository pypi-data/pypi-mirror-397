"""Job execution orchestrator - delegates to specialized components."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Set, Iterator
from datetime import datetime

from jobrunner.config import ConfigLoader
from jobrunner.exceptions import ExecutionError
from jobrunner.integrations.git import GitManager
from jobrunner.config.models import Job, JobType
from jobrunner.execution import ScriptRunner, ExecutionResult, ExecutionStatus, ExecutionReport
from jobrunner.core.resolver import DependencyResolver
from jobrunner.output import OutputFormatter, OutputStyle, ExecutionReporter
from jobrunner.plugins import DeprunPlugin
from jobrunner.utils import ShellUtils


class JobExecutor:
    """Orchestrates job execution by delegating to specialized components.
    
    Responsibilities:
    - Job lifecycle management (start/end)
    - Dependency coordination
    - Component orchestration
    
    Delegates to:
    - ScriptRunner: Command execution
    - OutputFormatter: Console output
    - ExecutionReporter: Report generation
    - DependencyResolver: Dependency analysis
    - GitManager: Repository management
    """

    def __init__(
        self,
        config: ConfigLoader,
        verbose: bool = False,
        jobs_dir: Optional[Path] = None,
        quiet: bool = False,
        custom_args: Optional[dict] = None,
    ) -> None:
        """Initialize the executor.
        
        Args:
            config: Configuration loader instance
            verbose: Enable verbose output
            jobs_dir: Directory for repository clones
            quiet: Suppress all output except script output
            custom_args: Custom arguments to pass as environment variables
        """
        # Configuration
        self.config = config.config if hasattr(config, 'config') else config
        self.verbose = verbose
        self.quiet = quiet
        self.jobs_dir = jobs_dir or Path.home() / "job-runner-repos"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.custom_args = custom_args or {}
        
        # State tracking
        self.completed: Set[str] = set()
        self.current_depth = 0
        
        # Components (dependency injection)
        self.git = GitManager(config, verbose and not quiet)
        self.runner = ScriptRunner(verbose=verbose, quiet=quiet)
        self.resolver = DependencyResolver(self.config)
        
        style = OutputStyle.MINIMAL if quiet else (
            OutputStyle.VERBOSE if verbose else OutputStyle.STANDARD
        )
        self.formatter = OutputFormatter(style=style, use_color=True)
        
        # Results tracking
        self.results: List[ExecutionResult] = []
        self.report = ExecutionReport()
        
        # Plugin system
        self.plugins: List[DeprunPlugin] = []
    
    # ------------------------------------------------------------------
    # Plugin Management
    # ------------------------------------------------------------------
    
    def register_plugin(self, plugin: DeprunPlugin) -> None:
        """Register a plugin for execution hooks.
        
        Args:
            plugin: DeprunPlugin instance
        """
        if not isinstance(plugin, DeprunPlugin):
            raise TypeError(f"Plugin must be instance of DeprunPlugin, got {type(plugin)}")
        self.plugins.append(plugin)
    
    def _trigger_hook(self, hook_name: str, *args, **kwargs) -> None:
        """Trigger plugin hook."""
        for plugin in self.plugins:
            try:
                hook = getattr(plugin, hook_name, None)
                if hook:
                    hook(*args, **kwargs)
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Plugin {plugin.name} error in {hook_name}: {e}")
    
    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    
    def generate_report(self, format: str = "text", output_file: Optional[Path] = None) -> str:
        """Generate execution report.
        
        Args:
            format: Report format (text, json, markdown, html, junit)
            output_file: Optional file to write report to
            
        Returns:
            Report content as string
        """
        from jobrunner.output import ReportFormat
        
        self.report.finalize()
        reporter = ExecutionReporter(self.report)
        format_enum = ReportFormat(format.lower())
        return reporter.generate(format_enum, output_file)
    
    def print_summary(self) -> None:
        """Print execution summary to console."""
        reporter = ExecutionReporter(self.report)
        reporter.print_summary()

    
    # ------------------------------------------------------------------
    # Public API - Job Execution
    # ------------------------------------------------------------------

    def run(self, job_name: str, max_depth: Optional[int] = None) -> ExecutionResult:
        """Run a job with its dependencies.
        
        Args:
            job_name: Name of the job to run
            max_depth: Maximum dependency depth to follow (None = unlimited)
            
        Returns:
            ExecutionResult object
        """
        if job_name in self.completed:
            return None

        if job_name not in self.config.jobs:
            raise ExecutionError(f"Job '{job_name}' not found")
        
        job = self.config.jobs[job_name]
        
        # Validate required arguments
        self._validate_job_arguments(job_name, job)
        
        result = ExecutionResult(
            name=job_name,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            self._print_start(job_name, is_task=False)
            self._trigger_hook('on_job_start', job_name, job)
            
            # Run dependencies
            if self._should_process_deps(job.dependencies, max_depth):
                self._run_dependencies(job.dependencies, max_depth)

            # Execute the job
            self._execute_job(job_name, job)
            self.completed.add(job_name)
            
            self._print_end(job_name, is_task=False)
            
            result.status = ExecutionStatus.SUCCESS
            self._trigger_hook('on_job_end', job_name, result)
            
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
            raise
        
        finally:
            result.end_time = datetime.now()
            self.results.append(result)
            self.report.add_result(result)
        
        return result
    
    def fetch(self, job_name: str) -> None:
        """Fetch (clone) a repository for a build job without running scripts.
        
        Args:
            job_name: Name of the build job to fetch
        """
        if job_name not in self.config.jobs:
            raise ExecutionError(f"Job '{job_name}' not found")
        
        job = self.config.jobs[job_name]
        
        if job.type != JobType.BUILD:
            raise ExecutionError(
                f"Job '{job_name}' is not a build job (type: {job.type}). "
                f"Only build jobs can be fetched."
            )
        
        if not job.repo:
            raise ExecutionError(f"Build job '{job_name}' has no repository configuration")
        
        # Output
        if not self.quiet:
            message = self.formatter.format_job_start(job_name, is_task=False)
            if message:
                print(message)
        
        self.git.ensure_repository(job_name, job)
        repo_path = self.git.get_repo_path(job)
        
        if not self.quiet:
            print(f"  Repository fetched: {repo_path}")

    def run_tasks(self, job_name: str, task_names: List[str], max_depth: Optional[int] = None) -> None:
        """Run multiple tasks within a job."""
        if job_name not in self.config.jobs:
            raise ExecutionError(f"Job '{job_name}' not found")
        
        job = self.config.jobs[job_name]
        
        # Run job dependencies once
        if self._should_process_deps(job.dependencies, max_depth):
            self._run_dependencies(job.dependencies, max_depth)
        
        # Run each task
        for task_name in task_names:
            if task_name == "default":
                self._print_start(job_name, is_task=False)
                self._execute_job(job_name, job)
                self._print_end(job_name, is_task=False)
            else:
                self._run_single_task(job_name, job, task_name, max_depth)

    def run_task(self, job_name: str, task_name: str, max_depth: Optional[int] = None) -> None:
        """Run a specific task within a job."""
        self.run_tasks(job_name, [task_name], max_depth)

    
    # ------------------------------------------------------------------
    # Internal Execution Logic
    # ------------------------------------------------------------------
    
    def _validate_job_arguments(self, job_name: str, job: Job) -> None:
        """Validate that required arguments are provided for the job.
        
        Checks multiple sources in order:
        1. Command-line arguments (--arg)
        2. Job environment variables
        3. YAML global variables
        4. System environment variables
        
        Args:
            job_name: Name of the job
            job: Job configuration object
            
        Raises:
            ExecutionError: If required arguments are missing from all sources
        """
        if not job.needs:
            return
        
        missing_args = []
        for arg_spec in job.needs:
            arg_name = arg_spec.name
            
            # Check all possible sources for the argument
            is_available = (
                arg_name in self.custom_args or           # 1. Command-line --arg
                arg_name in job.env or                     # 2. Job env (includes template inheritance)
                arg_name in self.config.variables or       # 3. YAML global variables
                arg_name in os.environ                     # 4. System environment variables
            )
            
            if not is_available and arg_spec.required:
                missing_args.append(f"  - {arg_name}: {arg_spec.description}")
        
        if missing_args:
            args_list = "\n".join(missing_args)
            raise ExecutionError(
                f"Job '{job_name}' requires the following arguments that were not provided:\n"
                f"{args_list}\n\n"
                f"Arguments can be provided via:\n"
                f"  1. Command line: job-runner run {job_name} --arg {job.needs[0].name if job.needs else 'NAME'}=value\n"
                f"  2. Job env: section in YAML\n"
                f"  3. Global variables: section in YAML\n"
                f"  4. System environment variables"
            )
    
    def _execute_job(self, name: str, job: Job) -> None:
        """Execute a single job."""
        # Merge environment: job.env < custom_args (custom_args takes precedence)
        merged_env = {**job.env, **self.custom_args}
        
        with self._env_context(merged_env):
            work_dir = self._get_work_dir(name, job)
            
            if work_dir:
                with self._working_dir(work_dir):
                    self._run_scripts(job.script, name, job)
            else:
                self._run_scripts(job.script, name, job)
    
    def _run_single_task(self, job_name: str, job: Job, task_name: str, max_depth: Optional[int]) -> None:
        """Run a single task."""
        if not job.tasks or task_name not in job.tasks:
            available = ", ".join(job.tasks.keys()) if job.tasks else "none"
            raise ExecutionError(
                f"Task '{task_name}' not found in job '{job_name}'. "
                f"Available tasks: {available}"
            )
        
        task = job.tasks[task_name]
        full_name = f"{job_name}:{task_name}"
        
        # Run task dependencies
        task_deps = getattr(task, 'dependencies', None)
        if self._should_process_deps(task_deps, max_depth):
            self._run_dependencies(task_deps, max_depth)
        
        # Execute task
        self._print_start(full_name, is_task=True)
        
        # Merge environment: job.env < task.env < custom_args (custom_args takes precedence)
        merged_env = {**job.env}
        if hasattr(task, 'env') and task.env:
            merged_env.update(task.env)
        merged_env.update(self.custom_args)
        
        with self._env_context(merged_env):
            work_dir = self._get_work_dir(job_name, job)
            
            task_script = getattr(task, 'script', None)
            if not task_script:
                raise ExecutionError(f"Task '{task_name}' has no script to execute")
            
            if work_dir:
                with self._working_dir(work_dir):
                    self._run_scripts(task_script, job_name, job)
            else:
                self._run_scripts(task_script, job_name, job)
        
        self._print_end(full_name, is_task=True)
    
    def _run_scripts(
        self, 
        scripts: Optional[List[str]], 
        job_name: str, 
        job: Job,
        cwd: Optional[str] = None,
        env: Optional[dict] = None
    ) -> None:
        """Execute scripts using ScriptRunner.
        
        Args:
            scripts: List of script commands to execute
            job_name: Name of the job
            job: Job configuration object
            cwd: Working directory (optional, for thread-safe parallel execution)
            env: Environment variables (optional, for thread-safe parallel execution)
        """
        if not scripts:
            return
        
        for cmd in scripts:
            resolved_cmd = self._resolve_command(cmd, job_name, job)
            self.runner.run_command(
                resolved_cmd,
                job_name,
                capture=not (self.verbose or self.quiet),
                indent_level=self.current_depth,
                cwd=cwd,
                env=env
            )

    
    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------
    
    def _should_process_deps(self, dependencies: Optional[List[str]], max_depth: Optional[int]) -> bool:
        """Check if dependencies should be processed."""
        return bool(dependencies and (max_depth is None or max_depth > 0))
    
    def _run_dependencies(self, dependencies: List[str], max_depth: Optional[int]) -> None:
        """Run all dependencies."""
        self.current_depth += 1
        self.git.current_depth = self.current_depth
        new_depth = None if max_depth is None else max_depth - 1
        
        for dep in dependencies:
            if ':' in dep:
                dep_job, dep_task = dep.split(':', 1)
                self.run_task(dep_job, dep_task, new_depth)
            else:
                self.run(dep, new_depth)
        
        self.current_depth -= 1
        self.git.current_depth = self.current_depth
    
    def _get_work_dir(self, name: str, job: Job) -> Optional[Path]:
        """Get working directory for a job."""
        if job.type == JobType.BUILD:
            if not job.repo:
                raise ExecutionError(f"Build job '{name}' missing repository configuration")
            self.git.ensure_repository(name, job)
            return self.git.get_repo_path(job)
        elif job.type == JobType.RUN and job.directory:
            return ShellUtils.get_work_dir(Path.cwd(), job.directory)
        return None
    
    def _resolve_command(self, cmd: str, job_name: str, job: Job) -> str:
        """Resolve variables and special markers in command."""
        sudo_cmd = "" if os.geteuid() == 0 else "sudo"
        
        # First resolve template variables
        variables = {**self.config.variables, **job.env, 'name': job_name}
        resolved = cmd.format(**variables)
        
        # Then replace $$ with sudo (or empty if root)
        resolved = resolved.replace("$$", sudo_cmd)
        
        return " ".join(resolved.split())
    
    def _print_start(self, name: str, is_task: bool = False) -> None:
        """Print execution start message."""
        if self.quiet:
            return
        
        self.formatter.set_indent(self.current_depth)
        message = self.formatter.format_job_start(name, is_task)
        if message:
            print(message)
    
    def _print_end(self, name: str, is_task: bool = False) -> None:
        """Print execution completion message."""
        if self.quiet:
            return
        
        self.formatter.set_indent(self.current_depth)
        
        duration = None
        if self.results and self.results[-1].name == name:
            duration = self.results[-1].duration_seconds
        
        message = self.formatter.format_job_end(name, success=True, duration=duration, is_task=is_task)
        if message:
            print(message)
    
    # ------------------------------------------------------------------
    # Context Managers
    # ------------------------------------------------------------------
    
    @contextmanager
    def _env_context(self, env_vars: dict) -> Iterator[None]:
        """Context manager for temporary environment variables."""
        if not env_vars:
            yield
            return

        original = {}
        clean_vars = {k.lstrip("^"): v for k, v in env_vars.items()}
        
        for key, value in clean_vars.items():
            original[key] = os.environ.get(key)
            os.environ[key] = value
        
        try:
            yield
        finally:
            for key, orig_value in original.items():
                if orig_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = orig_value

    @contextmanager
    def _working_dir(self, path: Path) -> Iterator[None]:
        """Context manager for temporary directory changes."""
        original = Path.cwd()
        try:
            os.chdir(path)
            if self.verbose and not self.quiet:
                print(f"Working directory: {path}")
            yield
        finally:
            os.chdir(original)
