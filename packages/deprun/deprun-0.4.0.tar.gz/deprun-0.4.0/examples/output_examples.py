#!/usr/bin/env python3
"""Example: Using output formatting and reporting features."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from jobrunner.config import ConfigLoader
from jobrunner.core import JobExecutor
from jobrunner.output import OutputFormatter, OutputStyle, ExecutionReporter, ReportFormat
from jobrunner.execution import ExecutionReport, ExecutionResult, ExecutionStatus
from datetime import datetime, timedelta


def example_output_formatting():
    """Example 1: Different output styles."""
    print("=== Example 1: Output Formatting ===\n")
    
    formatter = OutputFormatter(style=OutputStyle.STANDARD, use_color=True)
    
    # Job start
    print(formatter.format_job_start("libamxc", is_task=False))
    
    # Command
    print(formatter.format_command("make clean && make"))
    
    # Job end
    print(formatter.format_job_end("libamxc", success=True, duration=12.5))
    
    print("\n--- Verbose Style ---")
    formatter_verbose = OutputFormatter(style=OutputStyle.VERBOSE, use_color=True)
    print(formatter_verbose.format_job_start("libamxd", is_task=False))
    print(formatter_verbose.format_command("gcc -o test test.c"))
    print(formatter_verbose.format_job_end("libamxd", success=True, duration=3.2))
    
    print("\n--- Compact Style ---")
    formatter_compact = OutputFormatter(style=OutputStyle.COMPACT, use_color=True)
    print(formatter_compact.format_job_start("libamxo", is_task=False))
    print(formatter_compact.format_job_end("libamxo", success=True, duration=1.8))


def example_error_formatting():
    """Example 2: Error message formatting."""
    print("\n=== Example 2: Error Formatting ===\n")
    
    formatter = OutputFormatter(style=OutputStyle.STANDARD, use_color=True)
    
    error_msg = formatter.format_error(
        "Command failed with exit code 1",
        context={
            "job": "libamxc",
            "command": "make test",
            "exit_code": 1
        },
        suggestion="Check if all dependencies are installed"
    )
    print(error_msg)


def example_summary_formatting():
    """Example 3: Execution summary."""
    print("\n=== Example 3: Summary Formatting ===\n")
    
    formatter = OutputFormatter(style=OutputStyle.STANDARD, use_color=True)
    
    summary = formatter.format_summary(
        total=10,
        success=8,
        failed=2,
        skipped=0,
        duration=45.7
    )
    print(summary)


def example_text_report():
    """Example 4: Generate text report."""
    print("\n=== Example 4: Text Report ===\n")
    
    # Create mock execution report
    report = ExecutionReport()
    
    # Add some results
    start = datetime.now()
    
    result1 = ExecutionResult(
        name="libamxc",
        status=ExecutionStatus.SUCCESS,
        start_time=start,
        end_time=start + timedelta(seconds=12.5),
        exit_code=0
    )
    report.add_result(result1)
    
    result2 = ExecutionResult(
        name="libamxd",
        status=ExecutionStatus.SUCCESS,
        start_time=start + timedelta(seconds=12.5),
        end_time=start + timedelta(seconds=16.2),
        exit_code=0
    )
    report.add_result(result2)
    
    result3 = ExecutionResult(
        name="libamxo",
        status=ExecutionStatus.FAILED,
        start_time=start + timedelta(seconds=16.2),
        end_time=start + timedelta(seconds=18.1),
        exit_code=1,
        error="Make failed with exit code 1"
    )
    report.add_result(result3)
    
    report.finalize()
    
    # Generate text report
    reporter = ExecutionReporter(report)
    text_report = reporter.generate(ReportFormat.TEXT)
    print(text_report)


def example_json_report():
    """Example 5: Generate JSON report."""
    print("\n=== Example 5: JSON Report ===\n")
    
    # Create mock execution report
    report = ExecutionReport()
    start = datetime.now()
    
    result = ExecutionResult(
        name="libamxc",
        status=ExecutionStatus.SUCCESS,
        start_time=start,
        end_time=start + timedelta(seconds=10.5),
        exit_code=0
    )
    report.add_result(result)
    report.finalize()
    
    # Generate JSON report
    reporter = ExecutionReporter(report)
    json_report = reporter.generate(ReportFormat.JSON)
    print(json_report)


def example_markdown_report():
    """Example 6: Generate Markdown report."""
    print("\n=== Example 6: Markdown Report ===\n")
    
    # Create mock execution report
    report = ExecutionReport()
    start = datetime.now()
    
    for i, name in enumerate(['libamxc', 'libamxd', 'libamxo']):
        result = ExecutionResult(
            name=name,
            status=ExecutionStatus.SUCCESS,
            start_time=start + timedelta(seconds=i*5),
            end_time=start + timedelta(seconds=(i+1)*5),
            exit_code=0
        )
        report.add_result(result)
    
    report.finalize()
    
    # Generate Markdown report
    reporter = ExecutionReporter(report)
    md_report = reporter.generate(ReportFormat.MARKDOWN)
    print(md_report)


def example_html_report():
    """Example 7: Generate HTML report to file."""
    print("\n=== Example 7: HTML Report ===\n")
    
    # Create mock execution report
    report = ExecutionReport()
    start = datetime.now()
    
    jobs = [
        ("libamxc", ExecutionStatus.SUCCESS, 12.5),
        ("libamxd", ExecutionStatus.SUCCESS, 8.3),
        ("libamxo", ExecutionStatus.FAILED, 2.1),
        ("libamxp", ExecutionStatus.SUCCESS, 15.7),
    ]
    
    for name, status, duration in jobs:
        result = ExecutionResult(
            name=name,
            status=status,
            start_time=start,
            end_time=start + timedelta(seconds=duration),
            exit_code=0 if status == ExecutionStatus.SUCCESS else 1
        )
        if status == ExecutionStatus.FAILED:
            result.error = "Build failed"
        report.add_result(result)
        start = start + timedelta(seconds=duration)
    
    report.finalize()
    
    # Generate HTML report to file
    reporter = ExecutionReporter(report)
    output_file = Path("/tmp/job-runner-report.html")
    reporter.generate(ReportFormat.HTML, output_file)
    
    print(f"✓ HTML report generated: {output_file}")
    print(f"  Open with: file://{output_file}")


def example_with_real_execution():
    """Example 8: Real execution with report generation."""
    print("\n=== Example 8: Real Execution with Reports ===\n")
    
    try:
        config = ConfigLoader('jobs.yml')
        executor = JobExecutor(config, verbose=False)
        
        # Run a job
        print("Running job...")
        executor.run('libamxc')
        
        # Generate reports
        print("\n--- Text Report ---")
        executor.print_summary()
        
        print("\n--- Generating Files ---")
        executor.generate_report('json', Path('/tmp/job-report.json'))
        print("✓ JSON report: /tmp/job-report.json")
        
        executor.generate_report('markdown', Path('/tmp/job-report.md'))
        print("✓ Markdown report: /tmp/job-report.md")
        
        executor.generate_report('html', Path('/tmp/job-report.html'))
        print("✓ HTML report: /tmp/job-report.html")
        
    except Exception as e:
        print(f"Note: Real execution requires jobs.yml: {e}")


def example_junit_report():
    """Example 9: Generate JUnit XML for CI/CD."""
    print("\n=== Example 9: JUnit XML Report ===\n")
    
    # Create mock execution report
    report = ExecutionReport()
    start = datetime.now()
    
    jobs = [
        ("test_build", ExecutionStatus.SUCCESS, 5.2),
        ("test_unit", ExecutionStatus.SUCCESS, 12.8),
        ("test_integration", ExecutionStatus.FAILED, 3.5),
    ]
    
    for name, status, duration in jobs:
        result = ExecutionResult(
            name=name,
            status=status,
            start_time=start,
            end_time=start + timedelta(seconds=duration),
            exit_code=0 if status == ExecutionStatus.SUCCESS else 1
        )
        if status == ExecutionStatus.FAILED:
            result.error = "Test assertion failed"
        report.add_result(result)
        start = start + timedelta(seconds=duration)
    
    report.finalize()
    
    # Generate JUnit report
    reporter = ExecutionReporter(report)
    junit_xml = reporter.generate(ReportFormat.JUNIT)
    print(junit_xml)
    
    # Save to file
    output_file = Path("/tmp/junit-report.xml")
    reporter.generate(ReportFormat.JUNIT, output_file)
    print(f"\n✓ JUnit XML saved: {output_file}")


if __name__ == '__main__':
    print("Job-Runner Output & Reporting Examples")
    print("=" * 60)
    
    # Choose which example to run
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples = {
            '1': example_output_formatting,
            '2': example_error_formatting,
            '3': example_summary_formatting,
            '4': example_text_report,
            '5': example_json_report,
            '6': example_markdown_report,
            '7': example_html_report,
            '8': example_with_real_execution,
            '9': example_junit_report,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Unknown example: {example_num}")
            print("Usage: python output_examples.py [1-9]")
    else:
        # Run key examples
        example_output_formatting()
        example_error_formatting()
        example_summary_formatting()
        example_text_report()
        example_json_report()
        example_html_report()
        example_junit_report()
        
        print("\n" + "=" * 60)
        print("✓ All examples completed!")
