#!/usr/bin/env python3
"""Example: Using the refactored job-runner with new features."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from jobrunner.config import ConfigLoader
from jobrunner.core import JobExecutor, DependencyResolver
from jobrunner.plugins import TimingPlugin, LoggingPlugin


def example_basic_usage():
    """Example 1: Basic usage (backward compatible)."""
    print("=== Example 1: Basic Usage (Backward Compatible) ===\n")
    
    # Load config and create executor (works exactly as before)
    config = ConfigLoader('jobs.yml')
    executor = JobExecutor(config, verbose=False, quiet=False)
    
    # Run a job (works exactly as before)
    try:
        executor.run('libamxc')
        print("✓ Job completed successfully")
    except Exception as e:
        print(f"✗ Job failed: {e}")


def example_with_plugins():
    """Example 2: Using plugins for enhanced functionality."""
    print("\n=== Example 2: Using Plugins ===\n")
    
    config = ConfigLoader('jobs.yml')
    executor = JobExecutor(config, verbose=False)
    
    # NEW: Register plugins
    timing_plugin = TimingPlugin()
    logging_plugin = LoggingPlugin('job-runner.log')
    
    executor.register_plugin(timing_plugin)
    executor.register_plugin(logging_plugin)
    
    # Run job with plugins active
    try:
        executor.run('libamxc')
        
        # NEW: Print timing report
        timing_plugin.print_report()
        print("✓ Logs written to job-runner.log")
    except Exception as e:
        print(f"✗ Job failed: {e}")


def example_with_results():
    """Example 3: Using execution results."""
    print("\n=== Example 3: Execution Results ===\n")
    
    config = ConfigLoader('jobs.yml')
    executor = JobExecutor(config, verbose=False)
    
    # Run multiple jobs
    jobs = ['libamxc', 'libamxd', 'libamxo']
    
    for job in jobs:
        try:
            result = executor.run(job)
            if result:
                print(f"  {job}: {result.status.value} ({result.duration_seconds:.2f}s)")
        except Exception:
            print(f"  {job}: failed")
    
    # NEW: Access all results
    print(f"\n✓ Total jobs executed: {len(executor.results)}")
    print(f"  Total time: {sum(r.duration_seconds for r in executor.results):.2f}s")


def example_dependency_analysis():
    """Example 4: Analyzing dependencies."""
    print("\n=== Example 4: Dependency Analysis ===\n")
    
    config = ConfigLoader('jobs.yml')
    resolver = DependencyResolver(config.config)
    
    # Validate all dependencies
    errors = resolver.validate_dependencies()
    if errors:
        print("⚠ Dependency errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ All dependencies are valid")
    
    # Get execution order
    job_name = 'libamxc'
    order = resolver.get_execution_order(job_name)
    print(f"\nExecution order for '{job_name}':")
    for i, job in enumerate(order, 1):
        print(f"  {i}. {job}")
    
    # Get all dependencies
    deps = resolver.get_all_dependencies(job_name)
    print(f"\nAll dependencies of '{job_name}': {', '.join(deps) if deps else 'none'}")


def example_advanced_features():
    """Example 5: Combining multiple features."""
    print("\n=== Example 5: Advanced Features ===\n")
    
    config = ConfigLoader('jobs.yml')
    
    # Validate dependencies first
    resolver = DependencyResolver(config.config)
    errors = resolver.validate_dependencies()
    if errors:
        print("⚠ Cannot proceed - dependency errors:")
        for error in errors:
            print(f"  {error}")
        return
    
    # Create executor with plugins
    executor = JobExecutor(config, verbose=False)
    timing = TimingPlugin()
    executor.register_plugin(timing)
    
    # Run with result tracking
    try:
        result = executor.run('libamxc', max_depth=1)
        
        # Analyze results
        if result and result.success:
            print(f"✓ Job completed in {result.duration_seconds:.2f}s")
            print(f"  Total jobs executed: {len(executor.results)}")
            timing.print_report()
        else:
            print("✗ Job failed")
            
    except Exception as e:
        print(f"✗ Execution error: {e}")


if __name__ == '__main__':
    print("Job-Runner Refactoring Examples")
    print("=" * 60)
    
    # Choose which example to run
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == '1':
            example_basic_usage()
        elif example_num == '2':
            example_with_plugins()
        elif example_num == '3':
            example_with_results()
        elif example_num == '4':
            example_dependency_analysis()
        elif example_num == '5':
            example_advanced_features()
        else:
            print(f"Unknown example: {example_num}")
            print("Usage: python examples.py [1-5]")
    else:
        # Run all examples
        example_basic_usage()
        example_with_plugins()
        example_with_results()
        example_dependency_analysis()
        example_advanced_features()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
