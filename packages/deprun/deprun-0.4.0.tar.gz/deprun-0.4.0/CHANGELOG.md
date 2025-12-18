# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-12-16

### Added
- Parallel execution support for jobs
  - New `--parallel` / `-p` flag for `run` and `run-all` commands
  - Configurable worker count with `--max-workers` / `-j` option (default: 4)
  - Dependency-aware scheduling: jobs run as soon as their dependencies complete
  - Dynamic parallel queue management for optimal throughput
  - Real-time progress tracking with status indicators
  - Execution metrics: wall time, CPU time, and speedup calculation
  - Thread-safe execution with proper isolation of working directories and environment variables
  - Examples:
    - `job-runner run libamxc --parallel` - Run job with dependencies in parallel
    - `job-runner run-all --parallel -j 8` - Run all jobs in parallel with 8 workers
    - `job-runner run-all --type build --parallel` - Run all build jobs in parallel

### Fixed
- Fixed module import error: `DependencyGraph` now correctly imported from `jobrunner.analysis.graph`
- Fixed parallel execution bugs:
  - Fixed `ExecutionResult` initialization: removed invalid `duration_seconds` parameter (now computed as property)
  - Fixed `_run_scripts` parameter order: corrected to `(scripts, job_name, job)` signature
  - Fixed thread-safety issues: working directory and environment variables now passed directly to subprocess instead of using context managers that modify global process state
  - Prevents race conditions where parallel jobs could run with wrong directory or environment
- Improved `run-all` summary output:
  - Now shows both requested job count and total executed jobs (including dependencies)
  - Example: "Requested: 25 job(s), Executed: 33 job(s) (including dependencies)"
  - Prevents confusion when dependencies cause more jobs to run than explicitly requested

### Changed
- Enhanced parallel execution output with emoji indicators and color coding
- Improved error reporting in parallel mode with clear failure messages
- Updated `ScriptRunner.run_command()` to accept optional `cwd` and `env` parameters for thread-safe execution

## [0.3.0] - 2025-12-13

### Added
- Quiet mode for `run` command (`--quiet`, `-q`)
  - Suppresses all job runner output (progress messages, completion messages)
  - Only shows the actual script output
  - Useful for piping output to other commands or scripts
  - Example: `job-runner run mybuild -q | grep "Build complete"`
- Full dependency graph generation
  - `graph` command now works without a job name to generate graph of all jobs
  - No job duplication in the comprehensive graph
  - Default output: `all-jobs-deps.md` when no job specified
  - Example: `job-runner graph` generates full dependency graph

## [0.2.0] - 2025-12-12

### Added
- Multiple tasks execution support in single command
- Task chaining with comma-separated task list
- "default" keyword to reference job's main script
- New `run-all` command to run multiple jobs in sequence
  - Filter by job type (`--type build` or `--type run`)
  - Filter by name pattern using wildcards (`--pattern "lib*"`)
  - Dry-run mode to preview execution (`--dry-run`)
  - Depth control for dependency traversal (`--depth N`)
  - Smart job tracking: skips jobs already run as dependencies
  - Stops on first failure for fast feedback
  - Progress indicator showing `[N/Total]` for each job
  - Summary report showing successfully completed and skipped jobs

### Changed
- Jobs loaded from `jobs-dir` are now always sorted alphabetically for predictable ordering

## [0.1.0] - 2025-12-11

### Added
- Initial release
- Job dependency resolution with circular dependency handling
- Template system with inheritance
- Git repository fetching
- Task-level execution within jobs
- Conditional configuration with `when` clauses
- Variable substitution system
- Multiple output formats (YAML, JSON, script)
- Dependency graph visualization with Mermaid
- CLI commands: list, run, info, validate, dump, graph
- Environment variable management per job
- Depth-limited dependency traversal
- Multi-file configuration support with jobs-dir

### Features
- Build jobs: Clone repositories and run build scripts
- Run jobs: Execute scripts in specified directories
- Template inheritance chains
- Source tracking for better error messages
- Verbose mode for debugging

[Unreleased]: https://gitlab.com/proj_amx_01/tools/job-runner/-/compare/v0.3.0...main
[0.1.0]: https://gitlab.com/proj_amx_01/tools/job-runner/-/releases/v0.1.0
[0.2.0]: https://gitlab.com/proj_amx_01/tools/job-runner/-/releases/v0.2.0
[0.3.0]: https://gitlab.com/proj_amx_01/tools/job-runner/-/releases/v0.3.0
