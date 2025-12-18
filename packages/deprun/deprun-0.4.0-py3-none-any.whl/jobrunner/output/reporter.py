"""Execution reporting and result analysis."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any

from jobrunner.execution import ExecutionResult, ExecutionStatus, ExecutionReport


class ReportFormat(str, Enum):
    """Report output formats."""
    TEXT = "text"           # Human-readable text
    JSON = "json"           # Machine-readable JSON
    MARKDOWN = "markdown"   # Markdown format
    HTML = "html"          # HTML format
    JUNIT = "junit"        # JUnit XML (CI-friendly)


class ExecutionReporter:
    """Generates execution reports in various formats."""
    
    def __init__(self, report: ExecutionReport):
        """Initialize reporter.
        
        Args:
            report: ExecutionReport to generate reports from
        """
        self.report = report
    
    def generate(
        self,
        format: ReportFormat = ReportFormat.TEXT,
        output_file: Optional[Path] = None
    ) -> str:
        """Generate report in specified format.
        
        Args:
            format: Report format
            output_file: Optional file to write report to
            
        Returns:
            Report content as string
        """
        if format == ReportFormat.TEXT:
            content = self._generate_text()
        elif format == ReportFormat.JSON:
            content = self._generate_json()
        elif format == ReportFormat.MARKDOWN:
            content = self._generate_markdown()
        elif format == ReportFormat.HTML:
            content = self._generate_html()
        elif format == ReportFormat.JUNIT:
            content = self._generate_junit()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(content)
        
        return content
    
    def _generate_text(self) -> str:
        """Generate human-readable text report."""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("JOB EXECUTION REPORT")
        lines.append("=" * 70)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Start time: {self.report.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.report.end_time:
            lines.append(f"End time: {self.report.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            duration = (self.report.end_time - self.report.start_time).total_seconds()
            lines.append(f"Total duration: {duration:.2f}s")
        
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 70)
        total = len(self.report.results)
        lines.append(f"Total jobs: {total}")
        lines.append(f"✓ Succeeded: {self.report.success_count}")
        lines.append(f"✗ Failed: {self.report.failure_count}")
        lines.append(f"⊘ Skipped: {self.report.skipped_count}")
        lines.append("")
        
        # Detailed results
        lines.append("DETAILED RESULTS")
        lines.append("-" * 70)
        
        for result in self.report.results:
            status_symbol = self._get_status_symbol(result.status)
            lines.append(f"\n{status_symbol} {result.name}")
            lines.append(f"  Status: {result.status.value}")
            lines.append(f"  Duration: {result.duration_seconds:.2f}s")
            lines.append(f"  Exit code: {result.exit_code}")
            
            if result.error:
                lines.append(f"  Error: {result.error}")
            
            if result.cached:
                lines.append("  [Cached result]")
            
            if result.changed:
                lines.append("  [Changes detected]")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)
    
    def _generate_json(self) -> str:
        """Generate JSON report."""
        data = {
            "generated_at": datetime.now().isoformat(),
            "start_time": self.report.start_time.isoformat(),
            "end_time": self.report.end_time.isoformat() if self.report.end_time else None,
            "summary": {
                "total": len(self.report.results),
                "success": self.report.success_count,
                "failed": self.report.failure_count,
                "skipped": self.report.skipped_count,
                "total_duration": self.report.total_duration,
            },
            "results": [result.to_dict() for result in self.report.results]
        }
        
        return json.dumps(data, indent=2)
    
    def _generate_markdown(self) -> str:
        """Generate Markdown report."""
        lines = []
        
        # Header
        lines.append("# Job Execution Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Start time:** {self.report.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.report.end_time:
            lines.append(f"**End time:** {self.report.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            duration = (self.report.end_time - self.report.start_time).total_seconds()
            lines.append(f"**Total duration:** {duration:.2f}s")
        
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total jobs:** {len(self.report.results)}")
        lines.append(f"- ✓ **Succeeded:** {self.report.success_count}")
        lines.append(f"- ✗ **Failed:** {self.report.failure_count}")
        lines.append(f"- ⊘ **Skipped:** {self.report.skipped_count}")
        lines.append("")
        
        # Results table
        lines.append("## Results")
        lines.append("")
        lines.append("| Job | Status | Duration | Exit Code |")
        lines.append("|-----|--------|----------|-----------|")
        
        for result in self.report.results:
            status_symbol = self._get_status_symbol(result.status)
            lines.append(
                f"| {result.name} | {status_symbol} {result.status.value} | "
                f"{result.duration_seconds:.2f}s | {result.exit_code} |"
            )
        
        lines.append("")
        
        # Failed jobs details
        failed_results = [r for r in self.report.results if r.status == ExecutionStatus.FAILED]
        if failed_results:
            lines.append("## Failed Jobs")
            lines.append("")
            
            for result in failed_results:
                lines.append(f"### {result.name}")
                lines.append("")
                if result.error:
                    lines.append(f"**Error:** {result.error}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html(self) -> str:
        """Generate HTML report."""
        # Simple HTML template
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Job Execution Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-box {{ padding: 15px; border-radius: 5px; flex: 1; text-align: center; }}
        .success {{ background: #d4edda; color: #155724; }}
        .failure {{ background: #f8d7da; color: #721c24; }}
        .total {{ background: #d1ecf1; color: #0c5460; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #007bff; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .status-success {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .status-skipped {{ color: #ffc107; font-weight: bold; }}
        .metadata {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Job Execution Report</h1>
        <div class="metadata">
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Start time:</strong> {self.report.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
        
        if self.report.end_time:
            duration = (self.report.end_time - self.report.start_time).total_seconds()
            html += f"""            <p><strong>End time:</strong> {self.report.end_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Duration:</strong> {duration:.2f}s</p>
"""
        
        html += f"""        </div>
        
        <h2>Summary</h2>
        <div class="summary">
            <div class="summary-box total">
                <h3>{len(self.report.results)}</h3>
                <p>Total Jobs</p>
            </div>
            <div class="summary-box success">
                <h3>✓ {self.report.success_count}</h3>
                <p>Succeeded</p>
            </div>
            <div class="summary-box failure">
                <h3>✗ {self.report.failure_count}</h3>
                <p>Failed</p>
            </div>
        </div>
        
        <h2>Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Job</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Exit Code</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in self.report.results:
            status_class = f"status-{result.status.value}"
            status_symbol = self._get_status_symbol(result.status)
            html += f"""                <tr>
                    <td>{result.name}</td>
                    <td class="{status_class}">{status_symbol} {result.status.value}</td>
                    <td>{result.duration_seconds:.2f}s</td>
                    <td>{result.exit_code}</td>
                </tr>
"""
        
        html += """            </tbody>
        </table>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_junit(self) -> str:
        """Generate JUnit XML report (CI-friendly)."""
        # JUnit XML format for CI systems
        total = len(self.report.results)
        failures = self.report.failure_count
        skipped = self.report.skipped_count
        duration = self.report.total_duration
        
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="job-runner" tests="{total}" failures="{failures}" skipped="{skipped}" time="{duration:.3f}">
    <testsuite name="jobs" tests="{total}" failures="{failures}" skipped="{skipped}" time="{duration:.3f}">
"""
        
        for result in self.report.results:
            xml += f"""        <testcase name="{result.name}" classname="jobs" time="{result.duration_seconds:.3f}">
"""
            
            if result.status == ExecutionStatus.FAILED:
                error_msg = result.error or "Execution failed"
                xml += f"""            <failure message="{error_msg}">
                Exit code: {result.exit_code}
            </failure>
"""
            elif result.status == ExecutionStatus.SKIPPED:
                xml += """            <skipped/>
"""
            
            xml += """        </testcase>
"""
        
        xml += """    </testsuite>
</testsuites>
"""
        return xml
    
    def _get_status_symbol(self, status: ExecutionStatus) -> str:
        """Get visual symbol for status.
        
        Args:
            status: Execution status
            
        Returns:
            Status symbol
        """
        symbols = {
            ExecutionStatus.SUCCESS: "✓",
            ExecutionStatus.FAILED: "✗",
            ExecutionStatus.SKIPPED: "⊘",
            ExecutionStatus.RUNNING: "▶",
            ExecutionStatus.PENDING: "○",
            ExecutionStatus.TIMEOUT: "⏱",
        }
        return symbols.get(status, "?")
    
    def print_summary(self) -> None:
        """Print a quick summary to console."""
        print(self.report.summary())
    
    def get_failed_jobs(self) -> List[ExecutionResult]:
        """Get list of failed jobs.
        
        Returns:
            List of failed ExecutionResult objects
        """
        return [r for r in self.report.results if r.status == ExecutionStatus.FAILED]
    
    def get_slowest_jobs(self, limit: int = 10) -> List[ExecutionResult]:
        """Get slowest jobs.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of ExecutionResult objects sorted by duration
        """
        return sorted(
            self.report.results,
            key=lambda r: r.duration_seconds,
            reverse=True
        )[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics.
        
        Returns:
            Dictionary of statistics
        """
        durations = [r.duration_seconds for r in self.report.results if r.duration_seconds > 0]
        
        stats = {
            "total_jobs": len(self.report.results),
            "success_count": self.report.success_count,
            "failure_count": self.report.failure_count,
            "skipped_count": self.report.skipped_count,
            "total_duration": self.report.total_duration,
        }
        
        if durations:
            stats["avg_duration"] = sum(durations) / len(durations)
            stats["min_duration"] = min(durations)
            stats["max_duration"] = max(durations)
        
        return stats
