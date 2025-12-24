"""Output formatting utilities."""

from enum import Enum
from typing import Optional


class OutputStyle(str, Enum):
    """Output formatting styles."""
    MINIMAL = "minimal"      # Minimal output (quiet mode)
    STANDARD = "standard"    # Standard output (default)
    VERBOSE = "verbose"      # Verbose output
    TREE = "tree"           # Tree-style output with indentation
    COMPACT = "compact"     # Compact single-line output


class OutputFormatter:
    """Formats output messages for different verbosity levels."""
    
    # Visual elements
    TREE_CHAR = "├─ "
    TREE_LAST = "└─ "
    TREE_PIPE = "│  "
    SEPARATOR = "=" * 60
    SUCCESS_MARK = "✓"
    FAILURE_MARK = "✗"
    RUNNING_MARK = "▶"
    SKIPPED_MARK = "⊘"
    
    # ANSI color codes (optional, can be disabled)
    COLOR_RESET = "\033[0m"
    COLOR_GREEN = "\033[32m"
    COLOR_RED = "\033[31m"
    COLOR_YELLOW = "\033[33m"
    COLOR_BLUE = "\033[34m"
    COLOR_GRAY = "\033[90m"
    COLOR_BOLD = "\033[1m"
    
    def __init__(
        self,
        style: OutputStyle = OutputStyle.STANDARD,
        use_color: bool = True,
        indent_level: int = 0
    ):
        """Initialize formatter.
        
        Args:
            style: Output style to use
            use_color: Whether to use ANSI colors
            indent_level: Current indentation level
        """
        self.style = style
        self.use_color = use_color
        self.indent_level = indent_level
    
    def format_job_start(self, job_name: str, is_task: bool = False) -> str:
        """Format job/task start message.
        
        Args:
            job_name: Name of job or task
            is_task: Whether this is a task (vs job)
            
        Returns:
            Formatted message
        """
        entity_type = "task" if is_task else "job"
        
        if self.style == OutputStyle.MINIMAL:
            return ""
        
        elif self.style == OutputStyle.VERBOSE:
            return (
                f"\n{self.SEPARATOR}\n"
                f"Executing {entity_type}: {job_name}\n"
                f"{self.SEPARATOR}"
            )
        
        elif self.style == OutputStyle.COMPACT:
            mark = self._colorize(self.RUNNING_MARK, self.COLOR_BLUE)
            return f"{mark} {job_name}"
        
        else:  # STANDARD or TREE
            indent = self._get_indent()
            mark = self._colorize(self.RUNNING_MARK, self.COLOR_BLUE)
            return f"{indent}[{job_name}] {mark} Running {entity_type}..."
    
    def format_job_end(
        self,
        job_name: str,
        success: bool = True,
        duration: Optional[float] = None,
        is_task: bool = False
    ) -> str:
        """Format job/task completion message.
        
        Args:
            job_name: Name of job or task
            success: Whether execution succeeded
            duration: Duration in seconds
            is_task: Whether this is a task (vs job)
            
        Returns:
            Formatted message
        """
        if self.style == OutputStyle.MINIMAL:
            return ""
        
        entity_type = "Task" if is_task else "Job"
        
        if success:
            mark = self._colorize(self.SUCCESS_MARK, self.COLOR_GREEN)
            status = self._colorize("completed", self.COLOR_GREEN)
        else:
            mark = self._colorize(self.FAILURE_MARK, self.COLOR_RED)
            status = self._colorize("failed", self.COLOR_RED)
        
        duration_str = ""
        if duration is not None:
            duration_str = self._colorize(f" ({duration:.2f}s)", self.COLOR_GRAY)
        
        if self.style == OutputStyle.COMPACT:
            return f"{mark} {job_name}{duration_str}"
        
        elif self.style == OutputStyle.VERBOSE:
            return f"\n{mark} {entity_type} '{job_name}' {status}{duration_str}\n"
        
        else:  # STANDARD or TREE
            indent = self._get_indent()
            return f"{indent}[{job_name}] {mark} {entity_type} {status}{duration_str}"
    
    def format_command(self, command: str, multiline: bool = False) -> str:
        """Format command for display.
        
        Args:
            command: Shell command
            multiline: Whether command spans multiple lines
            
        Returns:
            Formatted command
        """
        if self.style == OutputStyle.MINIMAL:
            return ""
        
        indent = self._get_indent()
        
        if self.style == OutputStyle.VERBOSE:
            prompt = self._colorize("$", self.COLOR_BLUE)
            return f"{prompt} {command}"
        
        if multiline:
            lines = command.split('\n')
            formatted_lines = []
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped:
                    if i == 0:
                        formatted_lines.append(f"{indent}  $ {stripped}")
                    else:
                        formatted_lines.append(f"{indent}    {stripped}")
            return "\n".join(formatted_lines)
        else:
            return f"{indent}  $ {command.strip()}"
    
    def format_error(
        self,
        message: str,
        context: Optional[dict] = None,
        suggestion: Optional[str] = None
    ) -> str:
        """Format error message.
        
        Args:
            message: Error message
            context: Optional context dict
            suggestion: Optional suggestion
            
        Returns:
            Formatted error message
        """
        mark = self._colorize(self.FAILURE_MARK, self.COLOR_RED)
        lines = [f"{mark} {self._colorize(message, self.COLOR_RED)}"]
        
        if context and self.style != OutputStyle.MINIMAL:
            lines.append(self._colorize("\nContext:", self.COLOR_GRAY))
            for key, value in context.items():
                lines.append(self._colorize(f"  {key}: {value}", self.COLOR_GRAY))
        
        if suggestion and self.style != OutputStyle.MINIMAL:
            bulb = "💡" if self.use_color else "Hint:"
            lines.append(f"\n{bulb} {suggestion}")
        
        return "\n".join(lines)
    
    def format_dependency_tree(
        self,
        job_name: str,
        dependencies: list,
        level: int = 0
    ) -> str:
        """Format dependency tree.
        
        Args:
            job_name: Root job name
            dependencies: List of dependency names
            level: Current tree level
            
        Returns:
            Formatted tree string
        """
        if self.style == OutputStyle.MINIMAL:
            return ""
        
        indent = "  " * level
        lines = [f"{indent}{job_name}"]
        
        for i, dep in enumerate(dependencies):
            is_last = i == len(dependencies) - 1
            prefix = self.TREE_LAST if is_last else self.TREE_CHAR
            lines.append(f"{indent}{prefix}{dep}")
        
        return "\n".join(lines)
    
    def format_summary(
        self,
        total: int,
        success: int,
        failed: int,
        skipped: int = 0,
        duration: Optional[float] = None
    ) -> str:
        """Format execution summary.
        
        Args:
            total: Total jobs
            success: Successful jobs
            failed: Failed jobs
            skipped: Skipped jobs
            duration: Total duration in seconds
            
        Returns:
            Formatted summary
        """
        if self.style == OutputStyle.MINIMAL:
            return ""
        
        lines = ["\n" + self.SEPARATOR]
        lines.append(self._colorize("Execution Summary", self.COLOR_BOLD))
        lines.append(self.SEPARATOR)
        
        # Stats
        lines.append(f"Total jobs: {total}")
        
        if success > 0:
            success_str = self._colorize(f"{success} succeeded", self.COLOR_GREEN)
            lines.append(f"  {self.SUCCESS_MARK} {success_str}")
        
        if failed > 0:
            failed_str = self._colorize(f"{failed} failed", self.COLOR_RED)
            lines.append(f"  {self.FAILURE_MARK} {failed_str}")
        
        if skipped > 0:
            skipped_str = self._colorize(f"{skipped} skipped", self.COLOR_YELLOW)
            lines.append(f"  {self.SKIPPED_MARK} {skipped_str}")
        
        if duration is not None:
            duration_str = self._colorize(f"{duration:.2f}s", self.COLOR_GRAY)
            lines.append(f"Total time: {duration_str}")
        
        lines.append(self.SEPARATOR)
        return "\n".join(lines)
    
    def format_progress(
        self,
        current: int,
        total: int,
        job_name: Optional[str] = None
    ) -> str:
        """Format progress indicator.
        
        Args:
            current: Current job number
            total: Total jobs
            job_name: Optional current job name
            
        Returns:
            Formatted progress
        """
        if self.style == OutputStyle.MINIMAL:
            return ""
        
        percentage = (current / total * 100) if total > 0 else 0
        bar_width = 20
        filled = int(bar_width * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        
        progress = f"[{current}/{total}] {bar} {percentage:.0f}%"
        
        if job_name:
            progress += f" - {job_name}"
        
        return progress
    
    def _get_indent(self) -> str:
        """Get indentation string based on current level."""
        return "  " * self.indent_level
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled.
        
        Args:
            text: Text to colorize
            color: ANSI color code
            
        Returns:
            Colorized text (or plain if colors disabled)
        """
        if not self.use_color:
            return text
        return f"{color}{text}{self.COLOR_RESET}"
    
    def set_indent(self, level: int) -> None:
        """Set indentation level.
        
        Args:
            level: New indentation level
        """
        self.indent_level = level
    
    def increase_indent(self) -> None:
        """Increase indentation by one level."""
        self.indent_level += 1
    
    def decrease_indent(self) -> None:
        """Decrease indentation by one level."""
        self.indent_level = max(0, self.indent_level - 1)
