# =============================================================================
# DVT Rich Output Helpers
# =============================================================================
# Beautiful CLI output using Rich library for DVT commands.
#
# DVT v0.58.0: Unified output styling for all DVT commands
# DVT v0.58.1: Enhanced for dvt run integration
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
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    Console = None
    Progress = None


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
    - Per-model result lines
    - Summary table at the end

    DVT v0.58.1: Enhanced for dvt run integration with per-model progress.
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

        if self._use_rich:
            self._console = Console()

    def print_header(self, mode: str = "", target: str = "", compute: str = ""):
        """Print a beautiful header panel."""
        if not self._use_rich:
            print(f"\n{'=' * 60}")
            print(f"  {self.title}")
            if self.subtitle:
                print(f"  {self.subtitle}")
            if target:
                print(f"  Target: {target}")
            if compute:
                print(f"  Compute: {compute}")
            print(f"{'=' * 60}\n")
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

    def print_model_result(
        self,
        model_name: str,
        status: str,
        duration_ms: float = 0,
        message: str = "",
        materialization: str = "",
        execution_path: str = "",
    ):
        """Print a single model result line.

        Args:
            model_name: Name of the model
            status: Execution status (success, error, skip, warn)
            duration_ms: Execution time in milliseconds
            message: Additional message (e.g., row count, error)
            materialization: Materialization type (table, view, incremental)
            execution_path: DVT execution path (PUSHDOWN or FEDERATION)
        """
        # Store result for summary
        self._model_results.append({
            "name": model_name,
            "status": status,
            "duration_ms": duration_ms,
            "message": message,
            "materialization": materialization,
            "execution_path": execution_path,
        })

        # Determine execution path indicator
        path_str = ""
        if execution_path:
            path_str = f"[{execution_path}]"

        if not self._use_rich:
            status_symbol = "OK" if status in ("success", "pass") else "FAIL" if status in ("error", "fail") else "SKIP"
            mat_str = f" [{materialization}]" if materialization else ""
            path_display = f" {path_str}" if path_str else ""
            msg_display = f" {message}" if message else ""
            print(f"    {status_symbol} {model_name}{path_display}{mat_str} ({duration_ms:.0f}ms){msg_display}")
            return

        # Rich formatted output
        status_styles = {
            "success": ("[green]OK[/green]", "green"),
            "pass": ("[green]OK[/green]", "green"),
            "error": ("[red]FAIL[/red]", "red"),
            "fail": ("[red]FAIL[/red]", "red"),
            "skip": ("[yellow]SKIP[/yellow]", "yellow"),
            "warn": ("[yellow]WARN[/yellow]", "yellow"),
        }

        # Execution path styling
        path_styles = {
            "PUSHDOWN": "[bold blue]PUSHDOWN[/bold blue]",
            "FEDERATION": "[bold magenta]FEDERATION[/bold magenta]",
        }

        symbol, color = status_styles.get(status, ("[white]--[/white]", "white"))
        mat_str = f" [dim][{materialization}][/dim]" if materialization else ""

        # Build execution path display
        path_display = ""
        if execution_path:
            styled_path = path_styles.get(execution_path, f"[dim]{execution_path}[/dim]")
            path_display = f" [{styled_path}]"

        # Build message display (e.g., row count, error details)
        msg_str = ""
        if message and execution_path != message:  # Avoid duplicating execution_path
            msg_str = f" [dim]{message}[/dim]"

        self._console.print(
            f"  {symbol} [{color}]{model_name}[/{color}]{path_display}{mat_str} "
            f"[dim]({duration_ms:.0f}ms)[/dim]{msg_str}"
        )

    def print_summary(self, additional_info: Dict[str, Any] = None):
        """Print a beautiful summary panel."""
        duration = self.stats.duration_seconds

        if not self._use_rich:
            print(f"\n{'=' * 60}")
            print(f"  SUMMARY")
            print(f"  Passed: {self.stats.passed}/{self.stats.total}")
            if self.stats.errored:
                print(f"  Failed: {self.stats.errored}")
            if self.stats.skipped:
                print(f"  Skipped: {self.stats.skipped}")
            print(f"  Duration: {duration:.2f}s")
            print(f"{'=' * 60}\n")
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
        for model in models:
            display.update_current(model.name, "running")
            # ... execute model ...
            display.print_model_result(model.name, "success", duration_ms=123, materialization="table")
            display.advance("success")
        display.stop_progress()
        display.print_summary()
    """
    display = DVTProgressDisplay(
        title="DVT Run",
        subtitle="Executing models with DVT compute rules",
    )
    return display
