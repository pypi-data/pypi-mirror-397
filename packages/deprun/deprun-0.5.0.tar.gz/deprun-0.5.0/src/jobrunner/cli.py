"""Command-line interface for Job Runner."""

import json
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Any, Optional

import click
import yaml
from rich.console import Console
from rich.table import Table

from jobrunner.config import ConfigLoader
from jobrunner.core import JobExecutor, ParallelExecutor
from jobrunner.exceptions import JobRunnerError, ConfigError

# ----------------------------------------------------------------------
# Constants and Enums
# ----------------------------------------------------------------------

class JobType(str, Enum):
    """Job types supported by the runner."""
    BUILD = "build"
    RUN = "run"


SUCCESS_MARK = "✓"
DEFAULT_JOBS_FILE = "jobs.yml"

console = Console()


# ----------------------------------------------------------------------
# Context Management
# ----------------------------------------------------------------------

@dataclass
class CliContext:
    """Context object for CLI state."""
    jobs_file: Path
    verbose: bool
    
    @cached_property
    def loader(self) -> ConfigLoader:
        """Lazy-load and cache the ConfigLoader."""
        if not self.jobs_file.exists():
            raise click.BadParameter(
                f"Path '{self.jobs_file}' does not exist",
                param_hint="'--jobs'"
            )
        return ConfigLoader(self.jobs_file)


# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------

def get_type_value(job: Any) -> str:
    """Extract type value from job, handling both enum and string types."""
    return getattr(job.type, "value", str(job.type))


def model_to_dict(obj: Any, exclude_none: bool = True) -> dict:
    """Convert a Pydantic model to dictionary.
    
    Args:
        obj: Pydantic model instance
        exclude_none: Whether to exclude None values
        
    Returns:
        Dictionary representation
    """
    if hasattr(obj, "model_dump"):
        return obj.model_dump(exclude_none=exclude_none)
    return vars(obj)


def compute_repository(job: Any) -> Optional[str]:
    """Compute full repository path from job configuration."""
    if not job.repo:
        return None
    return f"{job.repo.server}{job.repo.group}{job.repo.name}"


def compute_directory(job: Any) -> Optional[str]:
    """Compute the working directory for a job.
    
    For build jobs with repositories, constructs the local clone path.
    For other jobs, returns the configured directory as-is.
    """
    if not job.directory:
        return None

    # Build jobs compute local repo directory
    if get_type_value(job) == JobType.BUILD.value and job.repo:
        repo_name = Path(job.repo.name).stem
        return str(Path(job.directory) / job.repo.group / repo_name)

    return job.directory


def format_dependencies(job: Any) -> Optional[str]:
    """Format job dependencies as comma-separated string."""
    return ", ".join(job.dependencies) if job.dependencies else None


def get_job_info(job_name: str, job: Any, field: str) -> Optional[str]:
    """Get a specific field from a job.
    
    Args:
        job_name: Name of the job
        job: Job object
        field: Field name to extract
        
    Returns:
        Field value as string, or None if not applicable
    """
    field_getters = {
        "name": lambda: job_name,
        "type": lambda: get_type_value(job),
        "dependencies": lambda: format_dependencies(job),
        "repository": lambda: compute_repository(job),
        "directory": lambda: compute_directory(job),
        "description": lambda: job.description,
    }
    
    getter = field_getters.get(field)
    return getter() if getter else None


def get_available_info_fields() -> list[str]:
    """Get list of available info fields."""
    return ["name", "type", "dependencies", "repository", "directory", "description"]


def get_context(ctx: click.Context) -> CliContext:
    """Retrieve the CliContext from Click context."""
    return ctx.obj


# ----------------------------------------------------------------------
# Root CLI Group
# ----------------------------------------------------------------------

@click.group()
@click.option(
    "--jobs",
    type=click.Path(path_type=Path),
    default=DEFAULT_JOBS_FILE,
    envvar="JOBS_FILE",
    help="Path to the jobs definition file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, jobs: Path, verbose: bool):
    """Job Runner - Multi-repository task automation."""
    ctx.obj = CliContext(jobs_file=jobs, verbose=verbose)


# ----------------------------------------------------------------------
# list Command
# ----------------------------------------------------------------------

@cli.command()
@click.pass_context
def list(ctx: click.Context):
    """List all available jobs."""
    try:
        cli_ctx = get_context(ctx)
        config = cli_ctx.loader.config

        if not config.jobs:
            console.print("[yellow]No jobs found.[/yellow]")
            return

        for name in sorted(config.jobs.keys()):
            print(name)

    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# run Command
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name")
@click.argument("tasks", required=False, default=None)
@click.option("--depth", type=int, default=None, help="Maximum dependency depth (unlimited if not specified)")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all output except script output")
@click.option("--parallel", "-p", is_flag=True, help="Execute independent jobs in parallel")
@click.option("--max-workers", type=int, default=4, help="Maximum parallel workers (default: 4)")
@click.option("--arg", "-a", multiple=True, help="Pass arguments as environment variables (format: NAME=value)")
@click.pass_context
def run(ctx: click.Context, job_name: str, tasks: Optional[str], depth: Optional[int], quiet: bool, parallel: bool, max_workers: int, arg: tuple):
    """Run a job with its dependencies, or specific tasks within a job.
    
    TASKS can be a single task name or comma-separated list of tasks.
    Use "default" to refer to the job's main script.
    
    The --quiet flag suppresses all job runner output (progress messages, etc.)
    and only shows the output from the actual scripts. This is useful for
    piping output to other commands or scripts.
    
    The --parallel flag enables parallel execution of independent jobs.
    Jobs with no dependencies or jobs at the same dependency level will
    run concurrently. Use --max-workers to control parallelism (default: 4).
    
    The --arg/-a option allows passing arguments as environment variables to jobs.
    Multiple arguments can be provided. Arguments override job environment variables.
    
    Examples:
        job-runner run libamxc                  # Run the job's main script
        job-runner run libamxc clean            # Run the 'clean' task
        job-runner run libamxc test             # Run the 'test' task
        job-runner run libamxc clean,default    # Run 'clean' task then main script
        job-runner run libamxc clean,test       # Run 'clean' then 'test' tasks
        job-runner run libamxc default          # Same as: job-runner run libamxc
        job-runner run libamxc --quiet          # Only show script output
        job-runner run libamxc -q | grep error  # Pipe script output to grep
        job-runner run libamxc --parallel       # Run independent jobs in parallel
        job-runner run libamxc -p -j 8          # Use 8 parallel workers
        job-runner run prplos-build -a nproc=4  # Pass nproc=4 as env variable
        job-runner run myjob -a VAR1=val1 -a VAR2=val2  # Multiple arguments
    """
    try:
        cli_ctx = get_context(ctx)
        
        # Parse custom arguments
        custom_args = {}
        for arg_str in arg:
            if '=' not in arg_str:
                raise click.BadParameter(
                    f"Argument must be in format NAME=value, got: {arg_str}",
                    param_hint="'--arg'"
                )
            name, value = arg_str.split('=', 1)
            custom_args[name.strip()] = value.strip()
        
        # Use ParallelExecutor if --parallel flag is set
        if parallel:
            executor = ParallelExecutor(
                cli_ctx.loader, 
                verbose=cli_ctx.verbose, 
                quiet=quiet,
                max_workers=max_workers,
                custom_args=custom_args
            )
        else:
            executor = JobExecutor(cli_ctx.loader, verbose=cli_ctx.verbose, quiet=quiet, custom_args=custom_args)

        if tasks:
            # Parse comma-separated task list
            task_list = [t.strip() for t in tasks.split(',')]
            
            if len(task_list) == 1:
                task_name = task_list[0]
                if not quiet:
                    console.print(f"[bold green]Running task '{task_name}' in job:[/bold green] {job_name}")
                executor.run_task(job_name, task_name, max_depth=depth)
                if not quiet:
                    console.print(f"[bold green]{SUCCESS_MARK} Task completed:[/bold green] {job_name}:{task_name}")
            else:
                task_display = ", ".join(task_list)
                if not quiet:
                    console.print(f"[bold green]Running tasks in job {job_name}:[/bold green] {task_display}")
                executor.run_tasks(job_name, task_list, max_depth=depth)
                if not quiet:
                    console.print(f"[bold green]{SUCCESS_MARK} Tasks completed:[/bold green] {job_name}")
        else:
            if not quiet:
                console.print(f"[bold green]Running job:[/bold green] {job_name}")
            executor.run(job_name, max_depth=depth)
            if not quiet:
                console.print(f"[bold green]{SUCCESS_MARK} Job completed:[/bold green] {job_name}")

    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# run-all Command
# ----------------------------------------------------------------------

@cli.command("run-all")
@click.option(
    "--type", "-t",
    type=click.Choice(["build", "run"], case_sensitive=False),
    default=None,
    help="Filter jobs by type (build or run)",
)
@click.option(
    "--pattern", "-p",
    type=str,
    default=None,
    help="Filter jobs by name pattern (supports wildcards: *, ?)",
)
@click.option(
    "--depth",
    type=int,
    default=None,
    help="Maximum dependency depth (unlimited if not specified)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show which jobs would be run without executing them",
)
@click.option(
    "--parallel", "-p",
    is_flag=True,
    help="Execute independent jobs in parallel",
)
@click.option(
    "--max-workers", "-j",
    type=int,
    default=4,
    help="Maximum parallel workers (default: 4)",
)
@click.option("--arg", "-a", multiple=True, help="Pass arguments as environment variables (format: NAME=value)")
@click.pass_context
def run_all(ctx: click.Context, type: Optional[str], pattern: Optional[str], depth: Optional[int], dry_run: bool, parallel: bool, max_workers: int, arg: tuple):
    """Run all jobs or a filtered subset of jobs.
    
    By default, runs all jobs in the configuration. You can filter by:
    - Job type (build or run)
    - Name pattern using wildcards (* and ?)
    
    Jobs are executed in sequence by default, and execution stops on first failure.
    Jobs that were already executed (as dependencies) will be skipped.
    
    Use --parallel to run independent jobs concurrently for faster execution.
    
    Examples:
        job-runner run-all                      # Run all jobs
        job-runner run-all --type build         # Run all build jobs
        job-runner run-all --pattern "lib*"     # Run jobs starting with 'lib'
        job-runner run-all -t build -p "amx*"   # Run build jobs starting with 'amx'
        job-runner run-all --dry-run            # Preview which jobs would run
        job-runner run-all --parallel           # Run in parallel (4 workers)
        job-runner run-all -p -j 8              # Run in parallel (8 workers)
    """
    import fnmatch
    
    try:
        cli_ctx = get_context(ctx)
        config = cli_ctx.loader.config
        
        # Parse custom arguments
        custom_args = {}
        for arg_str in arg:
            if '=' not in arg_str:
                raise click.BadParameter(
                    f"Argument must be in format NAME=value, got: {arg_str}",
                    param_hint="'--arg'"
                )
            name, value = arg_str.split('=', 1)
            custom_args[name.strip()] = value.strip()
        
        if not config.jobs:
            console.print("[yellow]No jobs found.[/yellow]")
            return
        
        # Filter jobs based on criteria
        filtered_jobs = []
        for job_name in sorted(config.jobs.keys()):
            job = config.jobs[job_name]
            
            # Filter by type if specified
            if type and get_type_value(job) != type:
                continue
            
            # Filter by pattern if specified
            if pattern and not fnmatch.fnmatch(job_name, pattern):
                continue
            
            filtered_jobs.append(job_name)
        
        if not filtered_jobs:
            filter_desc = []
            if type:
                filter_desc.append(f"type={type}")
            if pattern:
                filter_desc.append(f"pattern={pattern}")
            filter_str = " with " + ", ".join(filter_desc) if filter_desc else ""
            console.print(f"[yellow]No jobs found{filter_str}.[/yellow]")
            return
        
        # Show what will be run
        console.print(f"[bold cyan]Jobs to run ({len(filtered_jobs)}):[/bold cyan]")
        for job_name in filtered_jobs:
            job = config.jobs[job_name]
            job_type = get_type_value(job)
            console.print(f"  • {job_name} [{job_type}]")
        
        if dry_run:
            console.print("\n[yellow]Dry run - no jobs were executed[/yellow]")
            return
        
        # Use parallel or sequential executor
        console.print(f"\n[bold green]Running {len(filtered_jobs)} job(s){'in parallel' if parallel else ''}...[/bold green]\n")
        
        if parallel:
            # Use ParallelExecutor for concurrent execution
            executor = ParallelExecutor(cli_ctx.loader, verbose=cli_ctx.verbose, max_workers=max_workers, custom_args=custom_args)
            
            # Run all filtered jobs in parallel
            results = executor.run_parallel(filtered_jobs, max_depth=depth)
            
            # Show summary
            success_count = sum(1 for r in results.values() if r.status.value == 'success')
            failed_count = sum(1 for r in results.values() if r.status.value == 'failed')
            total_executed = len(results)
            
            console.print(f"\n[bold]Summary:[/bold]")
            console.print(f"  Requested: {len(filtered_jobs)} job(s)")
            console.print(f"  Executed: {total_executed} job(s) (including dependencies)")
            console.print(f"  Success: {success_count}/{total_executed}")
            if failed_count > 0:
                console.print(f"  Failed: {failed_count}")
                raise click.ClickException(f"{failed_count} job(s) failed")
        else:
            # Sequential execution (original behavior)
            executor = JobExecutor(cli_ctx.loader, verbose=cli_ctx.verbose, custom_args=custom_args)
            
            jobs_attempted = 0
            jobs_skipped = 0
            
            for i, job_name in enumerate(filtered_jobs, 1):
                # Check if job was already completed (as a dependency of previous job)
                if job_name in executor.completed:
                    console.print(f"[bold cyan][{i}/{len(filtered_jobs)}][/bold cyan] [dim]Skipping {job_name} (already completed)[/dim]")
                    jobs_skipped += 1
                    continue
                
                jobs_attempted += 1
                console.print(f"[bold cyan][{i}/{len(filtered_jobs)}][/bold cyan] Running job: {job_name}")
                
                # Run the job - this will handle dependencies and update executor.completed
                # If it fails, the exception will be caught and we stop immediately
                executor.run(job_name, max_depth=depth)
                console.print(f"[green]{SUCCESS_MARK} Completed:[/green] {job_name}\n")
            
            # Summary for sequential execution
            console.print("[bold]Summary:[/bold]")
            console.print(f"  [green]Successfully completed: {jobs_attempted}[/green]")
            if jobs_skipped > 0:
                console.print(f"  [dim]Skipped (already run): {jobs_skipped}[/dim]")
            console.print(f"\n[bold green]{SUCCESS_MARK} All jobs completed successfully![/bold green]")
        
    except JobRunnerError as e:
        # Stop on first failure
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# fetch Command
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name")
@click.pass_context
def fetch(ctx: click.Context, job_name: str):
    """Fetch (clone) a repository for a build job without running scripts.
    
    This command only works on build jobs and will clone the repository
    to the correct directory without executing any build scripts.
    
    Example:
        job-runner fetch libamxc    # Clone the repository only
    """
    try:
        cli_ctx = get_context(ctx)
        executor = JobExecutor(cli_ctx.loader, verbose=cli_ctx.verbose)
        
        console.print(f"[bold green]Fetching job:[/bold green] {job_name}")
        executor.fetch(job_name)
        console.print(f"[bold green]{SUCCESS_MARK} Fetch completed:[/bold green] {job_name}")
        
    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# info Command
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name")
@click.argument("info_type", required=False)
@click.pass_context
def info(ctx: click.Context, job_name: str, info_type: Optional[str]):
    """Show information about a job.

    INFO_TYPE can be one of: name, type, dependencies, repository, directory, description.
    If not specified, shows all information.
    """
    try:
        cli_ctx = get_context(ctx)
        config = cli_ctx.loader.config
        job = config.jobs.get(job_name)

        if not job:
            raise click.ClickException(f"Job not found: {job_name}")

        available_fields = get_available_info_fields()

        # If a specific field is requested, validate and print it
        if info_type:
            field = info_type.lower()
            if field not in available_fields:
                valid_fields = ", ".join(available_fields)
                raise click.ClickException(
                    f"Invalid info type: {info_type}. Valid: {valid_fields}"
                )
            value = get_job_info(job_name, job, field)
            if value is not None:
                click.echo(value)
            return

        # Show full table
        table = Table(title=f"Job Information: {job_name}", header_style="bold cyan")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        for field in available_fields:
            value = get_job_info(job_name, job, field)
            if value is not None:
                table.add_row(field.capitalize(), value)

        console.print(table)

    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# help Command
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name")
@click.pass_context
def help(ctx: click.Context, job_name: str):
    """Show help information for a job.
    
    Displays the job description and any required arguments.
    
    Examples:
        job-runner help libamxb        # Show help for libamxb job
        job-runner help prplos-build   # Show help for prplos-build job
    """
    try:
        cli_ctx = get_context(ctx)
        config = cli_ctx.loader.config
        job = config.jobs.get(job_name)

        if not job:
            raise click.ClickException(f"Job not found: {job_name}")

        # Job header
        console.print(f"\n[bold cyan]Job:[/bold cyan] {job_name}")
        console.print(f"[bold cyan]Type:[/bold cyan] {get_type_value(job)}")
        
        # Description
        if job.description:
            console.print(f"\n[bold]Description:[/bold]")
            console.print(f"  {job.description}")
        else:
            console.print(f"\n[dim]No description available.[/dim]")
        
        # Required arguments
        if job.needs:
            console.print(f"\n[bold]Arguments:[/bold]")
            
            has_required = any(arg.required for arg in job.needs)
            has_optional = any(not arg.required for arg in job.needs)
            
            if has_required:
                console.print("\n  [bold yellow]Required:[/bold yellow]")
                for arg_spec in job.needs:
                    if arg_spec.required:
                        console.print(f"    [cyan]{arg_spec.name}[/cyan]: {arg_spec.description}")
            
            if has_optional:
                console.print("\n  [bold]Optional:[/bold]")
                for arg_spec in job.needs:
                    if not arg_spec.required:
                        console.print(f"    [cyan]{arg_spec.name}[/cyan]: {arg_spec.description}")
            
            console.print(f"\n[bold]Usage:[/bold]")
            required_args = [arg.name for arg in job.needs if arg.required]
            if required_args:
                arg_example = " ".join([f"--arg {name}=<value>" for name in required_args[:2]])
                console.print(f"  job-runner run {job_name} {arg_example}")
            else:
                console.print(f"  job-runner run {job_name}")
        
        # Dependencies
        if job.dependencies:
            console.print(f"\n[bold]Dependencies:[/bold]")
            for dep in job.dependencies:
                console.print(f"  • {dep}")
        
        # Tasks
        if job.tasks:
            console.print(f"\n[bold]Available tasks:[/bold]")
            for task_name in job.tasks.keys():
                console.print(f"  • {task_name}")
        
        console.print()  # Empty line at the end

    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# validate Command
# ----------------------------------------------------------------------

@cli.command()
@click.pass_context
def validate(ctx: click.Context):
    """Validate jobs configuration."""
    try:
        cli_ctx = get_context(ctx)
        _ = cli_ctx.loader.config
        console.print(f"[green]{SUCCESS_MARK} Configuration is valid[/green]")
    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# dump Command (Refactored)
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name")
@click.option(
    "--format", "-f",
    type=click.Choice(["yaml", "json", "script"], case_sensitive=False),
    default="yaml",
    help="Output format (default: yaml)",
)
@click.pass_context
def dump(ctx: click.Context, job_name: str, format: str):
    """Dump a job definition in YAML, JSON, or script form.
    
    Examples:
        job-runner dump libamxc                # YAML format (default)
        job-runner dump libamxc --format json  # JSON format
        job-runner dump libamxc -f script      # Script of the job
    """
    try:
        cli_ctx = get_context(ctx)
        config = cli_ctx.loader.config
        job = config.jobs.get(job_name)

        if not job:
            raise click.ClickException(f"Job not found: {job_name}")

        # Build job dictionary
        job_dict = model_to_dict(job)
        job_dict["type"] = get_type_value(job)

        if getattr(job, "repo", None):
            job_dict["repo"] = model_to_dict(job.repo)

        if getattr(job, "tasks", None):
            job_dict["tasks"] = {
                name: model_to_dict(task)
                for name, task in job.tasks.items()
            }

        # Format output
        if format == "json":
            output = json.dumps({job_name: job_dict}, indent=2)
        elif format == "script":
            output = "\n".join(job.script) if job.script else "# No script defined"
        else:  # YAML
            output = yaml.dump(
                {job_name: job_dict},
                default_flow_style=False,
                sort_keys=False
            )

        console.print(output, markup=False, highlight=False)

    except ConfigError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# graph Command
# ----------------------------------------------------------------------

@cli.command()
@click.argument("job_name", required=False)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file path (default: <job_name>-deps.md or all-jobs-deps.md)"
)
@click.pass_context
def graph(ctx: click.Context, job_name: Optional[str], output: Optional[Path]):
    """Generate a Mermaid dependency graph for a job or all jobs.
    
    If JOB_NAME is provided, generates a graph for that specific job and its dependencies.
    If JOB_NAME is omitted, generates a comprehensive graph showing all jobs and their
    dependencies without duplicates.
    
    Creates a Markdown file with a Mermaid flowchart.
    
    Examples:
        job-runner graph libamxc              # Graph for libamxc
        job-runner graph                      # Graph for all jobs
        job-runner graph --output deps.md     # All jobs to deps.md
        job-runner graph libamxc -o my.md     # Specific job to my.md
    """
    try:
        # Lazy import to avoid import errors when graph module is not available
        from jobrunner.analysis.graph import DependencyGraph
        
        cli_ctx = get_context(ctx)
        dep_graph = DependencyGraph(cli_ctx.loader)
        
        if job_name:
            # Generate graph for specific job
            if job_name not in cli_ctx.loader.config.jobs:
                raise click.ClickException(f"Job not found: {job_name}")
            
            # Default output filename for specific job
            if not output:
                output = Path(f"{job_name}-deps.md")
            
            dep_graph.generate(job_name, output)
            console.print(f"[green]{SUCCESS_MARK} Dependency graph for '{job_name}' written to:[/green] {output}")
        else:
            # Generate graph for all jobs
            if not cli_ctx.loader.config.jobs:
                raise click.ClickException("No jobs found in configuration")
            
            # Default output filename for all jobs
            if not output:
                output = Path("all-jobs-deps.md")
            
            dep_graph.generate_all(output)
            console.print(f"[green]{SUCCESS_MARK} Full dependency graph written to:[/green] {output}")
        
    except JobRunnerError as e:
        raise click.ClickException(str(e))


# ----------------------------------------------------------------------
# Main Entry Point
# ----------------------------------------------------------------------

def main() -> None:
    """Main entry point for the CLI."""
    cli(obj=None)


if __name__ == "__main__":
    main()
