"""
Spark Task Module

Handles DVT spark management commands:
- check: Show PySpark version, Java compatibility, and cluster info
- set-version: Interactive selection to install PySpark version
- match-cluster: Detect cluster version and suggest compatible PySpark

v0.51.3: New module for comprehensive Spark management.
v0.58.8: Enhanced set-version with uninstall-first approach and rollback.
"""

import os
import subprocess
import sys
from typing import Optional, Tuple

import click

from dbt.compute.java_compat import (
    PYSPARK_JAVA_COMPATIBILITY,
    PYSPARK_VERSIONS,
    check_java_pyspark_compatibility,
    detect_spark_cluster_version,
    get_current_java,
    get_pyspark_info,
)


class SparkTask:
    """Task for managing Spark/PySpark installations."""

    def check(self) -> bool:
        """
        Check PySpark installation, Java compatibility, and show status.

        Returns:
            bool: True if PySpark is installed and Java is compatible
        """
        click.echo()
        click.echo(click.style("PySpark Status", fg="cyan", bold=True))
        click.echo("-" * 40)

        # Get PySpark info
        pyspark = get_pyspark_info()
        if pyspark:
            click.echo(f"  Version:       {pyspark.version}")
            click.echo(f"  Major.Minor:   {pyspark.major_minor}")
            click.echo(f"  Required Java: {', '.join(str(v) for v in pyspark.java_supported)}")
            click.echo(f"  Recommended:   Java {pyspark.java_recommended}")
        else:
            click.echo(click.style("  PySpark not installed!", fg="red"))
            click.echo()
            click.echo("  Install with: pip install pyspark")
            click.echo("  Or run 'dvt spark set-version' to select a version")
            click.echo()
            return False

        click.echo()
        click.echo(click.style("Java Compatibility", fg="cyan", bold=True))
        click.echo("-" * 40)

        # Get current Java
        java = get_current_java()
        if java:
            click.echo(f"  JAVA_HOME: {java.path}")
            click.echo(f"  Version:   Java {java.version}")
            click.echo(f"  Vendor:    {java.vendor}")

            # Check compatibility
            is_compat, msg = check_java_pyspark_compatibility(java.version, pyspark.major_minor)
            click.echo()
            if is_compat:
                click.echo(click.style(f"  {msg}", fg="green"))
            else:
                click.echo(click.style(f"  {msg}", fg="red"))
                click.echo()
                click.echo("  Run 'dvt java set' to select a compatible Java version")
        else:
            click.echo(click.style("  Java not found!", fg="red"))
            click.echo()
            supported = ", ".join(str(v) for v in pyspark.java_supported)
            click.echo(f"  PySpark {pyspark.version} requires Java {supported}")
            click.echo()
            click.echo("  Run 'dvt java search' to find Java installations")
            click.echo("  Run 'dvt java install' for installation guide")
            click.echo()
            return False

        click.echo()
        return is_compat if java else False

    def _uninstall_pyspark(self) -> Tuple[bool, Optional[str]]:
        """
        Uninstall current PySpark installation.

        Returns:
            Tuple of (success, previous_version or None)
        """
        pyspark = get_pyspark_info()
        if not pyspark:
            return True, None

        previous_version = pyspark.version
        click.echo(f"  Uninstalling PySpark {previous_version}...")

        try:
            cmd = [sys.executable, "-m", "pip", "uninstall", "pyspark", "-y"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                click.echo(click.style(f"  Removed PySpark {previous_version}", fg="yellow"))
                return True, previous_version
            else:
                click.echo(click.style(f"  Warning: Could not uninstall PySpark", fg="yellow"))
                return True, previous_version  # Continue anyway

        except Exception as e:
            click.echo(click.style(f"  Error uninstalling: {str(e)}", fg="red"))
            return True, previous_version  # Continue anyway

    def _install_pyspark(self, version: str) -> bool:
        """
        Install a specific PySpark version.

        Args:
            version: PySpark version to install (e.g., "4.0.1")

        Returns:
            bool: True if installation successful
        """
        click.echo(f"  Installing PySpark {version}...")

        try:
            cmd = [sys.executable, "-m", "pip", "install", f"pyspark=={version}"]
            result = subprocess.run(cmd, capture_output=False, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def _test_pyspark_java(self) -> Tuple[bool, str]:
        """
        Test if PySpark can initialize with current Java.

        Returns:
            Tuple of (success, error_message)
        """
        click.echo("  Testing PySpark + Java compatibility...")

        try:
            # Simple test: create a SparkSession and stop it
            test_code = '''
import os
os.environ.setdefault("SPARK_HOME", "")
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[1]").appName("DVT-Test").config("spark.ui.enabled", "false").getOrCreate()
print("OK")
spark.stop()
'''
            result = subprocess.run(
                [sys.executable, "-c", test_code],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "PYSPARK_PYTHON": sys.executable}
            )

            if result.returncode == 0 and "OK" in result.stdout:
                return True, ""
            else:
                # Extract Java-related errors
                error_output = result.stderr or result.stdout
                if "java" in error_output.lower() or "jvm" in error_output.lower():
                    return False, "Java compatibility error"
                elif "UnsupportedClassVersionError" in error_output:
                    return False, "Java version mismatch"
                else:
                    return False, error_output[:200] if error_output else "Unknown error"

        except subprocess.TimeoutExpired:
            return False, "Test timed out"
        except Exception as e:
            return False, str(e)

    def set_version(self) -> bool:
        """
        Interactive selection to install a specific PySpark version.

        v0.58.8 improvements:
        - Uninstalls current PySpark first (DVT needs only ONE version)
        - Tests Java compatibility after installation
        - Rolls back on Java errors

        Returns:
            bool: True if installation successful
        """
        click.echo()
        click.echo(click.style("Select PySpark Version to Install", fg="cyan", bold=True))
        click.echo("=" * 50)
        click.echo()

        # Get current Java for compatibility display
        java = get_current_java()
        current_java_version = java.version if java else None

        # Get current PySpark for rollback
        current_pyspark = get_pyspark_info()
        if current_pyspark:
            click.echo(f"  Current PySpark: {current_pyspark.version}")
            click.echo()

        # Display available versions
        for i, (version, major_minor, tag) in enumerate(PYSPARK_VERSIONS, 1):
            compat = PYSPARK_JAVA_COMPATIBILITY.get(major_minor, {})
            supported = compat.get("supported", [])
            supported_str = ", ".join(str(v) for v in supported)

            # Tag display
            if tag == "latest":
                tag_display = click.style(" (latest)", fg="green")
            elif tag == "stable":
                tag_display = click.style(" (stable)", fg="blue")
            else:
                tag_display = ""

            # Compatibility indicator
            if current_java_version and supported:
                if current_java_version in supported:
                    compat_marker = click.style(" [OK]", fg="green")
                else:
                    compat_marker = click.style(" [!]", fg="red")
            else:
                compat_marker = ""

            # Current marker
            current_marker = ""
            if current_pyspark and current_pyspark.version == version:
                current_marker = click.style(" * CURRENT", fg="cyan")

            click.echo(f"  [{i}] PySpark {version}{tag_display}{compat_marker}{current_marker}")
            click.echo(f"      Requires Java: {supported_str}")
            click.echo()

        click.echo(f"  [{len(PYSPARK_VERSIONS) + 1}] Custom version")
        click.echo()

        # Show current Java info
        if java:
            click.echo(f"  Your Java: {java.version} ({java.vendor})")
            click.echo(f"  [OK] = compatible, [!] = requires different Java")
            click.echo()

        # Get user choice
        while True:
            try:
                choice = click.prompt("Your choice", type=int)
                if 1 <= choice <= len(PYSPARK_VERSIONS) + 1:
                    break
                click.echo(click.style(f"Enter 1-{len(PYSPARK_VERSIONS) + 1}", fg="yellow"))
            except click.Abort:
                click.echo("\nAborted.")
                return False

        # Determine version to install
        if choice <= len(PYSPARK_VERSIONS):
            version_to_install, major_minor, _ = PYSPARK_VERSIONS[choice - 1]
        else:
            # Custom version
            version_to_install = click.prompt("Enter PySpark version (e.g., 3.4.1)")
            parts = version_to_install.split(".")
            major_minor = f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else parts[0]

        # Skip if same version
        if current_pyspark and current_pyspark.version == version_to_install:
            click.echo()
            click.echo(click.style(f"PySpark {version_to_install} is already installed", fg="green"))
            click.echo()
            return True

        # Check Java compatibility before installing
        compat = PYSPARK_JAVA_COMPATIBILITY.get(major_minor, {})
        supported = compat.get("supported", [])

        if java and supported and java.version not in supported:
            click.echo()
            click.echo(click.style(f"Warning: PySpark {major_minor} requires Java {', '.join(str(v) for v in supported)}", fg="yellow"))
            click.echo(f"   Your Java: {java.version}")
            click.echo()
            click.echo("   Options:")
            click.echo("     1. Install anyway (will fail until you switch Java)")
            click.echo("     2. Run 'dvt java set' first to switch Java")
            click.echo()
            if not click.confirm("Install anyway?", default=False):
                return False

        # Perform installation
        click.echo()
        click.echo(click.style("Installing PySpark...", fg="cyan", bold=True))
        click.echo()

        # Step 1: Uninstall current version
        previous_version = None
        if current_pyspark:
            success, previous_version = self._uninstall_pyspark()
            if not success:
                click.echo(click.style("Failed to uninstall current PySpark", fg="red"))
                return False

        # Step 2: Install new version
        if not self._install_pyspark(version_to_install):
            click.echo()
            click.echo(click.style(f"Failed to install PySpark {version_to_install}", fg="red"))

            # Rollback to previous version
            if previous_version:
                click.echo()
                click.echo(click.style(f"Rolling back to PySpark {previous_version}...", fg="yellow"))
                if self._install_pyspark(previous_version):
                    click.echo(click.style(f"Restored PySpark {previous_version}", fg="green"))
                else:
                    click.echo(click.style("Rollback failed! Run 'dvt spark set-version' again", fg="red"))
            return False

        # Step 3: Test Java compatibility
        click.echo()
        test_ok, error_msg = self._test_pyspark_java()

        if not test_ok and "java" in error_msg.lower():
            # Java error - offer rollback
            click.echo()
            click.echo(click.style(f"Java compatibility error: {error_msg}", fg="red"))
            click.echo()
            click.echo("   This PySpark version doesn't work with your current Java.")
            click.echo(f"   PySpark {major_minor} requires Java {', '.join(str(v) for v in supported)}")
            click.echo()

            if previous_version and click.confirm(f"Rollback to PySpark {previous_version}?", default=True):
                click.echo()
                click.echo(click.style("Rolling back...", fg="yellow"))
                self._uninstall_pyspark()
                if self._install_pyspark(previous_version):
                    click.echo(click.style(f"Restored PySpark {previous_version}", fg="green"))
                    click.echo()
                    click.echo("   To use the new version, first run:")
                    click.echo("     dvt java set")
                    click.echo()
                    return False
                else:
                    click.echo(click.style("Rollback failed!", fg="red"))
                    return False
            else:
                click.echo()
                click.echo("   To fix this, run:")
                click.echo("     dvt java set")
                click.echo()
                return False

        # Success
        click.echo()
        click.echo(click.style(f"PySpark {version_to_install} installed successfully", fg="green"))

        if test_ok:
            click.echo(click.style("  Java compatibility verified", fg="green"))
        else:
            click.echo(click.style(f"  Note: {error_msg}", fg="yellow"))

        click.echo()
        return True

    def match_cluster(self, compute_name: str) -> bool:
        """
        Detect Spark version from a cluster and suggest compatible PySpark.

        Reads the compute configuration from computes.yml, connects to the
        cluster, and compares versions with locally installed PySpark.

        Args:
            compute_name: Name of compute engine in computes.yml

        Returns:
            bool: True if versions match, False if mismatch or error
        """
        from dbt.config.compute import ComputeRegistry

        click.echo()
        click.echo(click.style(f"Checking cluster compatibility: {compute_name}", fg="cyan", bold=True))
        click.echo("=" * 50)
        click.echo()

        # Load compute configuration
        try:
            registry = ComputeRegistry()
            compute_cluster = registry.get(compute_name)
            if not compute_cluster:
                click.echo(click.style(f"Compute '{compute_name}' not found in computes.yml", fg="red"))
                click.echo()
                click.echo("  Run 'dvt compute list' to see available compute engines")
                click.echo()
                return False
        except Exception as e:
            click.echo(click.style(f"Error loading compute config: {str(e)}", fg="red"))
            click.echo()
            return False

        # Get cluster info (ComputeCluster has config attribute)
        config = compute_cluster.config if hasattr(compute_cluster, 'config') else {}
        master_url = config.get("master")
        host = config.get("host")
        compute_type = compute_cluster.type if hasattr(compute_cluster, 'type') else 'spark'

        click.echo(f"  Compute:     {compute_name}")
        click.echo(f"  Type:        {compute_type}")
        if master_url:
            click.echo(f"  Master URL:  {master_url}")
        if host:
            click.echo(f"  Host:        {host}")

        # Detect cluster version
        click.echo()
        click.echo("Connecting to cluster...")

        cluster_version = None
        if master_url and master_url.startswith("spark://"):
            # Standalone cluster
            cluster_version = detect_spark_cluster_version(master_url)
        elif master_url == "local[*]" or (master_url and master_url.startswith("local")):
            # Local mode - just use PySpark version
            pyspark = get_pyspark_info()
            if pyspark:
                cluster_version = pyspark.version
                click.echo(click.style("  (Local mode - using PySpark version)", fg="blue"))
        elif host and "databricks" in host.lower():
            # Databricks - requires databricks-connect
            click.echo(click.style("  Databricks cluster detected", fg="blue"))
            click.echo("  Note: Version detection requires active connection")
            # Try to get version via Databricks Connect if installed
            try:
                from databricks.connect import DatabricksSession
                # We can't actually connect without full config, so just note it
                click.echo("  Run 'dvt compute test {compute_name}' to verify connectivity")
            except ImportError:
                click.echo("  Install databricks-connect for full support")

        if cluster_version:
            click.echo()
            click.echo(click.style("Cluster Information", fg="cyan", bold=True))
            click.echo("-" * 40)
            click.echo(f"  Spark Version: {cluster_version}")

            # Extract major.minor
            parts = cluster_version.split(".")
            cluster_major_minor = f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else parts[0]

            # Compare with local PySpark
            pyspark = get_pyspark_info()
            click.echo()
            click.echo(click.style("Version Comparison", fg="cyan", bold=True))
            click.echo("-" * 40)

            if pyspark:
                click.echo(f"  Driver (local): PySpark {pyspark.version}")
                click.echo(f"  Cluster:        Spark {cluster_version}")

                if pyspark.major_minor == cluster_major_minor:
                    click.echo()
                    click.echo(click.style("  Versions match!", fg="green"))
                    click.echo()
                    return True
                else:
                    click.echo()
                    click.echo(click.style("  VERSION MISMATCH!", fg="red", bold=True))
                    click.echo()
                    click.echo(f"  Driver (local): PySpark {pyspark.major_minor}")
                    click.echo(f"  Cluster:        Spark {cluster_major_minor}")
                    click.echo()
                    click.echo(click.style("Recommendation:", fg="yellow"))
                    click.echo(f"  Run 'dvt spark set-version' and select PySpark {cluster_major_minor}.x")
                    click.echo()

                    # Check Java requirements for target version
                    target_compat = PYSPARK_JAVA_COMPATIBILITY.get(cluster_major_minor)
                    if target_compat:
                        java = get_current_java()
                        supported = target_compat["supported"]
                        click.echo(click.style("Java Note:", fg="yellow"))
                        click.echo(f"  PySpark {cluster_major_minor} requires Java {', '.join(str(v) for v in supported)}")
                        if java:
                            if java.version in supported:
                                click.echo(f"  Current Java {java.version} is compatible")
                            else:
                                click.echo(f"  Current Java {java.version} is NOT compatible")
                                click.echo(f"  Run 'dvt java set' to select a compatible version")
                        click.echo()

                    return False
            else:
                click.echo(click.style("  PySpark not installed locally", fg="red"))
                click.echo()
                click.echo(f"  Run 'dvt spark set-version' and select PySpark {cluster_major_minor}.x")
                click.echo()
                return False
        else:
            click.echo()
            click.echo(click.style("  Could not detect cluster version", fg="yellow"))
            click.echo()
            click.echo("  Possible reasons:")
            click.echo("    - Cluster is not running")
            click.echo("    - Network connectivity issues")
            click.echo("    - Firewall blocking connection")
            click.echo()
            click.echo("  Try:")
            click.echo(f"    - Start the cluster")
            click.echo(f"    - Run 'dvt compute test {compute_name}' to verify connectivity")
            click.echo()
            return False

    def show_versions(self) -> None:
        """
        Display PySpark/Java compatibility matrix.

        Shows all available PySpark versions and their Java requirements.
        """
        click.echo()
        click.echo(click.style("PySpark/Java Compatibility Matrix", fg="cyan", bold=True))
        click.echo("=" * 60)
        click.echo()

        # Get current versions
        pyspark = get_pyspark_info()
        java = get_current_java()

        click.echo("Available PySpark Versions:")
        click.echo()

        for version, major_minor, tag in PYSPARK_VERSIONS:
            compat = PYSPARK_JAVA_COMPATIBILITY.get(major_minor, {})
            supported = compat.get("supported", [])
            recommended = compat.get("recommended", supported[0] if supported else "?")

            # Current marker
            current_marker = ""
            if pyspark and pyspark.version == version:
                current_marker = click.style(" * INSTALLED", fg="green")

            # Tag
            if tag == "latest":
                tag_display = click.style(" (latest)", fg="green")
            elif tag == "stable":
                tag_display = click.style(" (stable)", fg="blue")
            else:
                tag_display = ""

            click.echo(f"  PySpark {version}{tag_display}{current_marker}")
            click.echo(f"    Java Required:    {', '.join(str(v) for v in supported)}")
            click.echo(f"    Java Recommended: {recommended}")
            click.echo()

        # Show current status
        click.echo("-" * 60)
        click.echo()
        click.echo("Current Environment:")
        if pyspark:
            click.echo(f"  PySpark: {pyspark.version}")
        else:
            click.echo("  PySpark: not installed")
        if java:
            click.echo(f"  Java:    {java.version} ({java.vendor})")
        else:
            click.echo("  Java:    not found")
        click.echo()
