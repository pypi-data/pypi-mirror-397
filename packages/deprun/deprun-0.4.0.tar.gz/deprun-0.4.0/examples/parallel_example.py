#!/usr/bin/env python3
"""Example: Parallel job execution."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from jobrunner import ConfigLoader, ParallelExecutor


def example_parallel_execution():
    """Example: Running independent jobs in parallel."""
    print("=== Parallel Execution Example ===\n")
    
    # Create a sample config with independent jobs
    config_content = """
variables:
  version: "1.0"

jobs:
  # These jobs have no dependencies - can run in parallel
  lib1:
    type: run
    script:
      - echo "Building lib1..."
      - sleep 2
      - echo "lib1 complete"
  
  lib2:
    type: run
    script:
      - echo "Building lib2..."
      - sleep 2
      - echo "lib2 complete"
  
  lib3:
    type: run
    script:
      - echo "Building lib3..."
      - sleep 2
      - echo "lib3 complete"
  
  # This job depends on all libs - will run after them
  app:
    type: run
    dependencies:
      - lib1
      - lib2
      - lib3
    script:
      - echo "Building app (needs all libs)..."
      - sleep 1
      - echo "app complete"
"""
    
    # Write config
    config_file = Path("/tmp/parallel_jobs.yml")
    config_file.write_text(config_content)
    
    # Load config
    config = ConfigLoader(config_file)
    
    # Create parallel executor with 3 workers
    print("🚀 Starting parallel execution with 3 workers\n")
    executor = ParallelExecutor(config, max_workers=3, verbose=False)
    
    # Run the app job - dependencies will run in parallel
    executor.run("app")
    
    print("\n✅ Parallel execution complete!")
    print(f"   Total jobs: {len(executor.results)}")
    print(f"   Time saved by parallelization!")
    

def example_sequential_vs_parallel():
    """Compare sequential vs parallel execution times."""
    from jobrunner import JobExecutor
    import time
    
    print("\n=== Sequential vs Parallel Comparison ===\n")
    
    config_content = """
jobs:
  task1:
    type: run
    script:
      - sleep 1
  
  task2:
    type: run
    script:
      - sleep 1
  
  task3:
    type: run
    script:
      - sleep 1
  
  final:
    type: run
    dependencies: [task1, task2, task3]
    script:
      - echo "All done"
"""
    
    config_file = Path("/tmp/comparison_jobs.yml")
    config_file.write_text(config_content)
    config = ConfigLoader(config_file)
    
    # Sequential execution
    print("📌 Sequential execution:")
    start = time.time()
    executor_seq = JobExecutor(config, quiet=True)
    executor_seq.run("final")
    seq_time = time.time() - start
    print(f"   Time: {seq_time:.2f}s\n")
    
    # Parallel execution
    print("⚡ Parallel execution (3 workers):")
    start = time.time()
    executor_par = ParallelExecutor(config, max_workers=3, quiet=True)
    executor_par.run("final")
    par_time = time.time() - start
    print(f"   Time: {par_time:.2f}s\n")
    
    speedup = seq_time / par_time
    print(f"🎯 Speedup: {speedup:.2f}x faster with parallel execution!")


if __name__ == "__main__":
    example_parallel_execution()
    example_sequential_vs_parallel()
