# =============================================================================
# DVT Run Task with Rich UI
# =============================================================================
# Wrapper around standard RunTask that adds Rich progress display.
#
# DVT v0.58.0: Enhanced CLI output with Rich library
#
# IMPORTANT: This wrapper does NOT modify core dbt execution logic.
# All DVT compute rules are enforced in run.py's ModelRunner.execute().
#
# DVT Compute Rules (implemented in run.py):
#   1. Pushdown Preference: Same-target -> Adapter pushdown (no Spark)
#   2. Federation Path: Cross-target -> Spark execution
#   3. Compute Hierarchy: default < model config < CLI --target-compute
#   4. Target Hierarchy: default < model config < CLI --target
#
# =============================================================================

from __future__ import annotations

import sys
import time
import threading
from typing import Any, Dict, List, Optional, AbstractSet

from dbt.artifacts.schemas.results import NodeStatus
from dbt.artifacts.schemas.run import RunExecutionResult, RunResult
from dbt.cli.flags import Flags
from dbt.config import RuntimeConfig
from dbt.contracts.graph.manifest import Manifest
from dbt.task.run import RunTask, ModelRunner
from dbt.task.dvt_output import DVTProgressDisplay, HAS_RICH

# Lock for thread-safe Rich console updates
_console_lock = threading.Lock()


class DVTRunTask(RunTask):
    """
    DVT Run Task with Rich UI progress display.

    This class wraps the standard RunTask to add beautiful CLI output
    while preserving all dbt-core and DVT compute logic.

    Features:
    - Rich progress bar with spinner
    - Per-model result display with execution path (PUSHDOWN/FEDERATION)
    - Summary panel with pass/fail/skip counts
    - Graceful fallback to standard output if Rich unavailable

    Usage:
        task = DVTRunTask(args, config, manifest)
        results = task.run()
    """

    def __init__(
        self,
        args: Flags,
        config: RuntimeConfig,
        manifest: Manifest,
        batch_map: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(args, config, manifest, batch_map)
        self._display: Optional[DVTProgressDisplay] = None
        self._use_rich_output = HAS_RICH and not getattr(args, 'QUIET', False)
        self._model_start_times: Dict[str, float] = {}
        self._execution_paths: Dict[str, str] = {}  # Track pushdown vs federation

    def _get_target_info(self) -> str:
        """Get the current target name for display."""
        cli_target = getattr(self.config.args, 'TARGET', None)
        return cli_target or self.config.target_name or "default"

    def _get_compute_info(self) -> str:
        """Get the current compute engine for display."""
        cli_compute = getattr(self.config.args, 'TARGET_COMPUTE', None)
        return cli_compute or "auto"

    def before_run(self, adapter, selected_uids: AbstractSet[str]):
        """Called before running models - initialize Rich display."""
        # Call parent first (handles schemas, cache, hooks, metadata)
        result = super().before_run(adapter, selected_uids)

        # Initialize Rich display if available
        if self._use_rich_output and self.num_nodes > 0:
            try:
                self._display = DVTProgressDisplay(
                    title="DVT Run",
                    subtitle="Executing models with DVT compute rules",
                )
                self._display.print_header(
                    target=self._get_target_info(),
                    compute=self._get_compute_info(),
                )
                self._display.start_progress(
                    total=self.num_nodes,
                    description="Running models..."
                )
            except Exception:
                # Fall back to standard output on any Rich error
                self._display = None
                self._use_rich_output = False

        return result

    def _handle_result(self, result) -> None:
        """Handle a single model result - update Rich display."""
        # Call parent handler first (fires standard dbt events for logging)
        super()._handle_result(result)

        # Update Rich progress bar (but don't print per-model results to avoid duplication)
        # dbt already prints detailed per-model output via fire_event(LogModelResult)
        # We only advance the progress bar and track stats for the summary
        if self._display and result.node:
            try:
                # Determine status for stats tracking
                if result.status in (NodeStatus.Error, NodeStatus.Fail):
                    status = "error"
                elif result.status == NodeStatus.Skipped:
                    status = "skip"
                elif result.status == NodeStatus.Warn:
                    status = "warn"
                else:
                    status = "success"

                # Track execution path for summary
                message = result.message or ""
                if "Federated" in message:
                    self._execution_paths[result.node.unique_id] = "FEDERATION"
                elif result.status in (NodeStatus.Success, NodeStatus.Pass):
                    self._execution_paths[result.node.unique_id] = "PUSHDOWN"

                # Thread-safe progress update (just advance the bar)
                with _console_lock:
                    self._display.advance(status)
            except Exception:
                # Silently ignore Rich display errors
                pass

    def after_run(self, adapter, results) -> None:
        """Called after all models complete - show summary."""
        # Stop Rich progress display
        if self._display:
            try:
                self._display.stop_progress()

                # Calculate execution path stats for additional info
                additional_info = {}
                pushdown_count = sum(
                    1 for path in self._execution_paths.values() if path == "PUSHDOWN"
                )
                federation_count = sum(
                    1 for path in self._execution_paths.values() if path == "FEDERATION"
                )
                if pushdown_count > 0:
                    additional_info["Pushdown"] = f"{pushdown_count} models"
                if federation_count > 0:
                    additional_info["Federation"] = f"{federation_count} models"

                self._display.print_summary(additional_info=additional_info)
            except Exception:
                pass

        # Call parent (handles end hooks)
        super().after_run(adapter, results)

    def task_end_messages(self, results) -> None:
        """Override to prevent duplicate output when using Rich."""
        if self._display:
            # Rich display handles summary, skip default messages
            return

        # Fall back to standard dbt output
        super().task_end_messages(results)


def create_dvt_run_task(
    args: Flags,
    config: RuntimeConfig,
    manifest: Manifest,
    batch_map: Optional[Dict[str, Any]] = None,
) -> RunTask:
    """
    Factory function to create appropriate run task.

    Returns DVTRunTask with Rich UI if available and not in quiet mode,
    otherwise returns standard RunTask.

    Args:
        args: CLI flags
        config: Runtime configuration
        manifest: Project manifest
        batch_map: Optional batch map for retry

    Returns:
        RunTask instance (DVTRunTask or standard RunTask)
    """
    # Check if we should use Rich output
    use_rich = HAS_RICH and not getattr(args, 'QUIET', False)

    if use_rich:
        return DVTRunTask(args, config, manifest, batch_map)
    else:
        return RunTask(args, config, manifest, batch_map)
