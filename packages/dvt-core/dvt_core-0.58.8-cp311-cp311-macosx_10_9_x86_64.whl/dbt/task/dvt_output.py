# =============================================================================
# DVT Rich Output Helpers
# =============================================================================
# Beautiful CLI output using Rich library for DVT commands.
#
# DVT v0.58.0: Unified output styling for all DVT commands
# DVT v0.58.1: Enhanced for dvt run integration
# DVT v0.58.8: Polished output - aligned model names, row counts on right
# =============================================================================

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable

# Try to import Rich - graceful fallback if not available
try:
    from rich.console import Console
    from rich.progress import (
        Progress,
        TextColumn,
        BarColumn,
        MofNCompleteColumn,
        TimeElapsedColumn,
        SpinnerColumn,
        TaskProgressColumn,
    )
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.columns import Columns
    from rich.text import Text
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    Console = None
    Progress = None

# Constants for output formatting
MODEL_NAME_WIDTH = 45  # Fixed width for model names (left-aligned)
STATUS_WIDTH = 6       # Width for status indicator
PATH_WIDTH = 12        # Width for execution path (PUSHDOWN/FEDERATION)


@dataclass
class DVTRunStats:
    """Statistics for a DVT run execution."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    warned: int = 0
    errored: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0

    @property
    def duration_seconds(self) -> float:
        return self.end_time - self.start_time if self.end_time else 0.0

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 100.0
        return (self.passed / self.total) * 100


class DVTProgressDisplay:
    """
    Rich progress display for DVT commands.

    Provides a beautiful CLI UI with:
    - Header panel with command info
    - Progress bar with spinner and current task
    - Per-model result lines with aligned columns
    - Summary table at the end

    DVT v0.58.1: Enhanced for dvt run integration with per-model progress.
    DVT v0.58.8: Polished output with aligned columns and row counts.

    Output format (v0.58.8):
    ```
    [1/10] dim_customers ...................... OK [PUSHDOWN] 1,234 rows (2.5s)
    [2/10] fact_orders ....................... OK [FEDERATION] 45,678 rows (12.3s)
    ```
    """

    def __init__(self, title: str = "DVT Run", subtitle: str = ""):
        self.title = title
        self.subtitle = subtitle
        self._console = None
        self._progress = None
        self._task_id = None
        self._use_rich = HAS_RICH
        self.stats = DVTRunStats()
        self._model_results: List[Dict[str, Any]] = []
        self._current_index = 0

        if self._use_rich:
            self._console = Console()

    def print_header(self, mode: str = "", target: str = "", compute: str = ""):
        """Print a beautiful header panel."""
        if not self._use_rich:
            print(f"\n{'=' * 70}")
            print(f"  {self.title}")
            if self.subtitle:
                print(f"  {self.subtitle}")
            if target:
                print(f"  Target: {target}")
            if compute:
                print(f"  Compute: {compute}")
            print(f"{'=' * 70}\n")
            return

        # Build info line
        info_parts = []
        if target:
            info_parts.append(f"[bold cyan]Target:[/bold cyan] [yellow]{target}[/yellow]")
        if compute:
            info_parts.append(f"[bold cyan]Compute:[/bold cyan] [yellow]{compute}[/yellow]")
        if mode:
            info_parts.append(f"[bold cyan]Mode:[/bold cyan] [yellow]{mode}[/yellow]")

        info_line = "  |  ".join(info_parts) if info_parts else ""

        header_panel = Panel(
            info_line or "[dim]Processing models...[/dim]",
            title=f"[bold magenta]{self.title}[/bold magenta]",
            subtitle=f"[dim]{self.subtitle}[/dim]" if self.subtitle else None,
            border_style="magenta",
            box=box.DOUBLE,
        )
        self._console.print()
        self._console.print(header_panel)
        self._console.print()

    def start_progress(self, total: int, description: str = "Running models..."):
        """Start the progress bar."""
        self.stats.total = total
        self.stats.start_time = time.time()
        self._current_index = 0

        if not self._use_rich:
            print(f"Starting: {description} ({total} total)")
            return

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self._console,
        )
        self._progress.__enter__()
        self._task_id = self._progress.add_task(f"[cyan]{description}", total=total)

    def update_current(self, model_name: str, status: str = "running"):
        """Update the current model being processed."""
        if not self._use_rich or not self._progress:
            if status == "running":
                print(f"  [{self.stats.passed + self.stats.errored + 1}/{self.stats.total}] {model_name}...")
            return

        # Color based on status
        status_colors = {
            "running": "cyan",
            "success": "green",
            "error": "red",
            "skip": "yellow",
            "warn": "yellow",
        }
        color = status_colors.get(status, "white")

        self._progress.update(
            self._task_id,
            description=f"[{color}]{status.upper()}[/{color}] [bold]{model_name}[/bold]"
        )

    def advance(self, status: str = "success"):
        """Advance the progress bar and update stats."""
        self._current_index += 1

        if status == "success" or status == "pass":
            self.stats.passed += 1
        elif status == "error" or status == "fail":
            self.stats.errored += 1
        elif status == "skip":
            self.stats.skipped += 1
        elif status == "warn":
            self.stats.warned += 1
        else:
            self.stats.passed += 1

        if self._use_rich and self._progress:
            self._progress.advance(self._task_id)

    def stop_progress(self):
        """Stop the progress bar."""
        self.stats.end_time = time.time()
        if self._use_rich and self._progress:
            self._progress.__exit__(None, None, None)
            self._progress = None

    def _format_row_count(self, rows: Optional[int]) -> str:
        """Format row count with thousands separator."""
        if rows is None or rows == 0:
            return ""
        return f"{rows:,} rows"

    def _format_duration(self, duration_ms: float) -> str:
        """Format duration in human-readable format."""
        if duration_ms < 1000:
            return f"{duration_ms:.0f}ms"
        elif duration_ms < 60000:
            return f"{duration_ms/1000:.1f}s"
        else:
            minutes = int(duration_ms / 60000)
            seconds = (duration_ms % 60000) / 1000
            return f"{minutes}m {seconds:.0f}s"

    def _create_dot_fill(self, name_len: int, target_width: int = MODEL_NAME_WIDTH) -> str:
        """Create dot fill to align output."""
        dots_needed = max(2, target_width - name_len)
        return " " + "." * dots_needed + " "

    def print_model_result(
        self,
        model_name: str,
        status: str,
        duration_ms: float = 0,
        message: str = "",
        materialization: str = "",
        execution_path: str = "",
        row_count: Optional[int] = None,
        index: Optional[int] = None,
        total: Optional[int] = None,
    ):
        """Print a single model result line with aligned columns.

        Output format:
        [N/M] model_name ...................... STATUS [PATH] rows (duration)

        Args:
            model_name: Name of the model
            status: Execution status (success, error, skip, warn)
            duration_ms: Execution time in milliseconds
            message: Additional message (e.g., error details)
            materialization: Materialization type (table, view, incremental)
            execution_path: DVT execution path (PUSHDOWN or FEDERATION)
            row_count: Number of rows affected (optional)
            index: Current model index (1-based)
            total: Total number of models
        """
        # Store result for summary
        self._model_results.append({
            "name": model_name,
            "status": status,
            "duration_ms": duration_ms,
            "message": message,
            "materialization": materialization,
            "execution_path": execution_path,
            "row_count": row_count,
        })

        # Use provided index/total or fall back to tracked values
        idx = index or self._current_index
        tot = total or self.stats.total

        # Format index prefix
        index_prefix = f"[{idx}/{tot}]" if idx and tot else ""

        if not self._use_rich:
            # Plain text output
            status_symbol = "OK" if status in ("success", "pass") else "FAIL" if status in ("error", "fail") else "SKIP"
            path_str = f" [{execution_path}]" if execution_path else ""
            row_str = f" {self._format_row_count(row_count)}" if row_count else ""
            duration_str = f" ({self._format_duration(duration_ms)})"

            # Create aligned output
            name_with_prefix = f"{index_prefix} {model_name}" if index_prefix else model_name
            dots = self._create_dot_fill(len(name_with_prefix))

            print(f"  {name_with_prefix}{dots}{status_symbol}{path_str}{row_str}{duration_str}")
            return

        # Rich formatted output with alignment
        status_styles = {
            "success": ("[bold green]OK[/bold green]", "green"),
            "pass": ("[bold green]OK[/bold green]", "green"),
            "error": ("[bold red]FAIL[/bold red]", "red"),
            "fail": ("[bold red]FAIL[/bold red]", "red"),
            "skip": ("[bold yellow]SKIP[/bold yellow]", "yellow"),
            "warn": ("[bold yellow]WARN[/bold yellow]", "yellow"),
        }

        # Execution path styling
        path_styles = {
            "PUSHDOWN": "[blue]PUSHDOWN[/blue]",
            "FEDERATION": "[magenta]FEDERATION[/magenta]",
        }

        symbol, color = status_styles.get(status, ("[white]--[/white]", "white"))

        # Build components
        prefix = f"[dim]{index_prefix}[/dim] " if index_prefix else "  "
        name_display = f"[{color}]{model_name}[/{color}]"

        # Calculate dot fill (accounting for Rich markup removal)
        clean_prefix_len = len(index_prefix) + 1 if index_prefix else 2
        clean_name_len = len(model_name)
        dots = self._create_dot_fill(clean_prefix_len + clean_name_len)

        # Execution path
        path_display = ""
        if execution_path:
            styled_path = path_styles.get(execution_path, f"[dim]{execution_path}[/dim]")
            path_display = f" [{styled_path}]"

        # Row count
        row_display = ""
        if row_count and row_count > 0:
            row_display = f" [cyan]{self._format_row_count(row_count)}[/cyan]"

        # Duration
        duration_display = f" [dim]({self._format_duration(duration_ms)})[/dim]"

        # Error message on separate line if present
        error_line = ""
        if status in ("error", "fail") and message:
            error_line = f"\n    [red]{message}[/red]"

        self._console.print(
            f"{prefix}{name_display}{dots}{symbol}{path_display}{row_display}{duration_display}{error_line}"
        )

    def print_summary(self, additional_info: Dict[str, Any] = None):
        """Print a beautiful summary panel."""
        duration = self.stats.duration_seconds

        if not self._use_rich:
            print(f"\n{'=' * 70}")
            print(f"  SUMMARY")
            print(f"  Passed: {self.stats.passed}/{self.stats.total}")
            if self.stats.errored:
                print(f"  Failed: {self.stats.errored}")
            if self.stats.skipped:
                print(f"  Skipped: {self.stats.skipped}")
            print(f"  Duration: {duration:.2f}s")
            print(f"{'=' * 70}\n")
            return

        # Create summary panel
        self._console.print()

        # Status indicator
        if self.stats.errored > 0:
            status_icon = "[bold red]FAILED[/bold red]"
            status_text = f"[bold red]{self.stats.errored} of {self.stats.total} models failed[/bold red]"
            border_color = "red"
        elif self.stats.warned > 0:
            status_icon = "[bold yellow]WARNING[/bold yellow]"
            status_text = f"[bold yellow]{self.stats.warned} warnings[/bold yellow]"
            border_color = "yellow"
        else:
            status_icon = "[bold green]SUCCESS[/bold green]"
            status_text = f"[bold green]All {self.stats.passed} models completed successfully[/bold green]"
            border_color = "green"

        # Build summary content
        lines = [
            f"{status_text}",
            "",
            f"[bold]Passed:[/bold]   {self.stats.passed}",
        ]
        if self.stats.errored:
            lines.append(f"[bold red]Failed:[/bold red]   {self.stats.errored}")
        if self.stats.skipped:
            lines.append(f"[bold yellow]Skipped:[/bold yellow]  {self.stats.skipped}")
        if self.stats.warned:
            lines.append(f"[bold yellow]Warned:[/bold yellow]   {self.stats.warned}")
        lines.append("")
        lines.append(f"[dim]Duration: {duration:.2f}s[/dim]")

        if additional_info:
            lines.append("")
            for key, value in additional_info.items():
                lines.append(f"[dim]{key}: {value}[/dim]")

        summary_content = "\n".join(lines)

        summary_panel = Panel(
            summary_content,
            title=f"[bold]{self.title} Complete[/bold]",
            border_style=border_color,
            box=box.ROUNDED,
        )
        self._console.print(summary_panel)
        self._console.print()


def create_progress_callback(display: DVTProgressDisplay) -> Callable:
    """Create a callback function for use with dbt's event system."""
    def callback(event):
        # This would integrate with dbt's event system
        # For now, it's a placeholder
        pass
    return callback


def create_dvt_run_display(target: str = "", compute: str = "") -> DVTProgressDisplay:
    """
    Factory function to create a DVT run display.

    Usage:
        display = create_dvt_run_display(target="postgres", compute="spark-local")
        display.print_header()
        display.start_progress(total=10)
        for i, model in enumerate(models, 1):
            display.update_current(model.name, "running")
            # ... execute model ...
            display.print_model_result(
                model.name, "success",
                duration_ms=123,
                materialization="table",
                execution_path="PUSHDOWN",
                row_count=1234,
                index=i,
                total=len(models)
            )
            display.advance("success")
        display.stop_progress()
        display.print_summary()
    """
    display = DVTProgressDisplay(
        title="DVT Run",
        subtitle="Executing models with DVT compute rules",
    )
    return display
