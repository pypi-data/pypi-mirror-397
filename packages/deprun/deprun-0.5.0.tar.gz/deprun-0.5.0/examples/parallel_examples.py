#!/usr/bin/env python3
"""Example: Parallel job execution."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from jobrunner.config import ConfigLoader
from jobrunner.core import ParallelExecutor


def example_parallel_execution():
    """Example: Run independent jobs in parallel."""
    print("=== Parallel Execution Example ===\n")
    
    # Create a test config with independent jobs
    config_content = """
jobs:
  # Independent jobs (can run in parallel)
  prepare-a:
    type: run
    script:
      - echo "Preparing A..."
      - sleep 2
      - echo "A ready!"
  
  prepare-b:
    type: run
    script:
      - echo "Preparing B..."
      - sleep 2
      - echo "B ready!"
  
  prepare-c:
    type: run
    script:
      - echo "Preparing C..."
      - sleep 2
      - echo "C ready!"
  
  # Job with dependencies (runs after prepare-a and prepare-b)
  build:
    dependencies:
      - prepare-a
      - prepare-b
    type: run
    script:
      - echo "Building..."
      - sleep 1
      - echo "Build complete!"
  
  # Another job depending on build
  test:
    dependencies:
      - build
    type: run
    script:
      - echo "Testing..."
      - sleep 1
      - echo "Tests passed!"
  
  # Independent of the main chain
  docs:
    type: run
    script:
      - echo "Building docs..."
      - sleep 1
      - echo "Docs ready!"
"""
    
    # Write test config
    config_file = Path("/tmp/parallel_test.yml")
    config_file.write_text(config_content)
    
    # Load config
    config = ConfigLoader(config_file)
    
    # Create parallel executor
    executor = ParallelExecutor(config, max_workers=4, verbose=True)
    
    # Run all jobs in parallel where possible
    print("Running all jobs with parallel execution...\n")
    results = executor.run_parallel(['test', 'docs'])
    
    print("\n" + "="*60)
    print("Results:")
    for job_name, result in results.items():
        status = "✅" if result.status == "success" else "❌"
        print(f"  {status} {job_name}: {result.duration_seconds:.1f}s")
    print("="*60)


def example_speedup_comparison():
    """Example: Compare sequential vs parallel execution."""
    print("\n\n=== Sequential vs Parallel Comparison ===\n")
    
    config_content = """
jobs:
  job-1:
    type: run
    script:
      - sleep 1
  
  job-2:
    type: run
    script:
      - sleep 1
  
  job-3:
    type: run
    script:
      - sleep 1
  
  job-4:
    type: run
    script:
      - sleep 1
"""
    
    config_file = Path("/tmp/speedup_test.yml")
    config_file.write_text(config_content)
    config = ConfigLoader(config_file)
    
    print("Sequential execution (expected: ~4 seconds):")
    from jobrunner.core import JobExecutor
    from time import time
    
    start = time()
    executor = JobExecutor(config, quiet=True)
    for i in range(1, 5):
        executor.run(f"job-{i}")
    sequential_time = time() - start
    
    print(f"  Time: {sequential_time:.1f}s\n")
    
    print("Parallel execution (expected: ~1 second):")
    start = time()
    parallel_executor = ParallelExecutor(config, max_workers=4)
    parallel_executor.run_parallel([f"job-{i}" for i in range(1, 5)])
    parallel_time = time() - start
    
    print(f"\nSpeedup: {sequential_time/parallel_time:.2f}x faster!")


if __name__ == "__main__":
    example_parallel_execution()
    example_speedup_comparison()
