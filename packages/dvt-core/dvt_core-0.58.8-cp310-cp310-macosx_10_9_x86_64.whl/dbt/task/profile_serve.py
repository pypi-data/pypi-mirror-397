# =============================================================================
# DVT Profile Serve - Web UI for Profiling Results
# =============================================================================
# Serves a beautiful web interface to view profiling results stored in
# metadata_store.duckdb, similar to PipeRider's report viewer.
#
# Usage:
#   dvt profile serve              # Start server on http://localhost:8580
#   dvt profile serve --port 9000  # Custom port
#   dvt profile serve --no-browser # Don't auto-open browser
#
# Installation:
#   Copy this file to: core/dbt/task/profile_serve.py
#
# DVT v0.58.0: New web UI for profiling results
# =============================================================================

from __future__ import annotations

import json
import threading
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

# Try to import Rich for CLI output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich import box
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None


class ProfileAPIHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the Profile Viewer API and static files."""

    def __init__(self, *args, metadata_store_path: Path = None, **kwargs):
        self.metadata_store_path = metadata_store_path
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        # API endpoints
        if path == "/api/profiles":
            self._serve_profiles_list()
        elif path == "/api/profile":
            query = parse_qs(parsed.query)
            table_name = query.get("table", [None])[0]
            self._serve_profile_detail(table_name)
        elif path == "/api/summary":
            self._serve_summary()
        elif path == "/" or path == "/index.html":
            self._serve_html()
        else:
            # Serve static files
            super().do_GET()

    def _serve_json(self, data: Any, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def _serve_html(self):
        """Serve the main HTML page."""
        html = self._generate_html()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _get_connection(self):
        """Get DuckDB connection to metadata store."""
        try:
            import duckdb
            return duckdb.connect(str(self.metadata_store_path), read_only=True)
        except Exception as e:
            return None

    def _serve_profiles_list(self):
        """Serve list of all profiled tables."""
        conn = self._get_connection()
        if not conn:
            self._serve_json({"error": "Could not connect to metadata store"}, 500)
            return

        try:
            # Query profile results
            result = conn.execute("""
                SELECT DISTINCT
                    source_name,
                    table_name,
                    adapter_name,
                    connection_name,
                    COUNT(*) as column_count,
                    MAX(last_refreshed) as last_profiled
                FROM column_metadata
                GROUP BY source_name, table_name, adapter_name, connection_name
                ORDER BY source_name, table_name
            """).fetchall()

            profiles = []
            for row in result:
                profiles.append({
                    "source_name": row[0],
                    "table_name": row[1],
                    "adapter_name": row[2],
                    "connection_name": row[3],
                    "column_count": row[4],
                    "last_profiled": row[5],
                })

            self._serve_json({"profiles": profiles})
        except Exception as e:
            self._serve_json({"profiles": [], "error": str(e)})
        finally:
            conn.close()

    def _serve_profile_detail(self, table_name: str):
        """Serve detailed profile for a specific table."""
        if not table_name:
            self._serve_json({"error": "table parameter required"}, 400)
            return

        conn = self._get_connection()
        if not conn:
            self._serve_json({"error": "Could not connect to metadata store"}, 500)
            return

        try:
            # Query column metadata
            result = conn.execute("""
                SELECT
                    column_name,
                    adapter_type,
                    spark_type,
                    is_nullable,
                    is_primary_key,
                    ordinal_position,
                    last_refreshed
                FROM column_metadata
                WHERE table_name = ?
                ORDER BY ordinal_position
            """, [table_name]).fetchall()

            columns = []
            for row in result:
                columns.append({
                    "name": row[0],
                    "adapter_type": row[1],
                    "spark_type": row[2],
                    "is_nullable": row[3],
                    "is_primary_key": row[4],
                    "ordinal_position": row[5],
                    "last_refreshed": row[6],
                })

            # Try to get row count if available
            row_count = None
            try:
                count_result = conn.execute("""
                    SELECT row_count FROM row_counts WHERE table_name = ?
                """, [table_name]).fetchone()
                if count_result:
                    row_count = count_result[0]
            except:
                pass

            self._serve_json({
                "table_name": table_name,
                "columns": columns,
                "row_count": row_count,
            })
        except Exception as e:
            self._serve_json({"error": str(e)}, 500)
        finally:
            conn.close()

    def _serve_summary(self):
        """Serve summary statistics."""
        conn = self._get_connection()
        if not conn:
            self._serve_json({"error": "Could not connect to metadata store"}, 500)
            return

        try:
            # Get summary stats
            tables = conn.execute("""
                SELECT COUNT(DISTINCT table_name) FROM column_metadata
            """).fetchone()[0]

            columns = conn.execute("""
                SELECT COUNT(*) FROM column_metadata
            """).fetchone()[0]

            sources = conn.execute("""
                SELECT COUNT(DISTINCT source_name) FROM column_metadata
            """).fetchone()[0]

            # Get unique connections/adapters
            adapters = conn.execute("""
                SELECT COUNT(DISTINCT adapter_name) FROM column_metadata
            """).fetchone()[0]

            self._serve_json({
                "total_tables": tables,
                "total_columns": columns,
                "sources": sources,
                "adapters": adapters,
            })
        except Exception as e:
            self._serve_json({"error": str(e)}, 500)
        finally:
            conn.close()

    def _generate_html(self) -> str:
        """Generate the HTML page for the profile viewer."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVT Profile Viewer</title>
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --bg: #0f172a;
            --bg-card: #1e293b;
            --text: #f1f5f9;
            --text-dim: #94a3b8;
            --border: #334155;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            padding: 2rem;
            text-align: center;
        }
        .header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .header p { color: rgba(255,255,255,0.8); }
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
        }
        .stat-card h3 { color: var(--text-dim); font-size: 0.875rem; margin-bottom: 0.5rem; }
        .stat-card .value { font-size: 2rem; font-weight: 700; color: var(--primary); }
        .tables-section { margin-top: 2rem; }
        .tables-section h2 { margin-bottom: 1rem; }
        .table-list {
            display: grid;
            gap: 1rem;
        }
        .table-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
            cursor: pointer;
            transition: all 0.2s;
        }
        .table-card:hover {
            border-color: var(--primary);
            transform: translateY(-2px);
        }
        .table-card.selected {
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3);
        }
        .table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        .table-name { font-weight: 600; font-size: 1.1rem; }
        .table-type {
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            background: var(--primary);
        }
        .table-type.source { background: var(--success); }
        .table-type.model { background: var(--warning); }
        .table-meta { color: var(--text-dim); font-size: 0.875rem; }
        .detail-panel {
            position: fixed;
            top: 0;
            right: -500px;
            width: 500px;
            height: 100vh;
            background: var(--bg-card);
            border-left: 1px solid var(--border);
            transition: right 0.3s;
            overflow-y: auto;
            z-index: 100;
        }
        .detail-panel.open { right: 0; }
        .detail-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .detail-header h2 { font-size: 1.25rem; }
        .close-btn {
            background: none;
            border: none;
            color: var(--text);
            font-size: 1.5rem;
            cursor: pointer;
        }
        .detail-content { padding: 1.5rem; }
        .column-table {
            width: 100%;
            border-collapse: collapse;
        }
        .column-table th, .column-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        .column-table th {
            color: var(--text-dim);
            font-weight: 500;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        .type-badge {
            font-family: monospace;
            font-size: 0.8rem;
            background: rgba(99, 102, 241, 0.2);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }
        .loading {
            text-align: center;
            padding: 3rem;
            color: var(--text-dim);
        }
        .error {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid var(--error);
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        @media (max-width: 768px) {
            .detail-panel { width: 100%; right: -100%; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 DVT Profile Viewer</h1>
        <p>Data profiling results from metadata_store.duckdb</p>
    </div>

    <div class="container">
        <div class="stats-grid" id="stats">
            <div class="stat-card">
                <h3>Total Tables</h3>
                <div class="value" id="stat-tables">-</div>
            </div>
            <div class="stat-card">
                <h3>Total Columns</h3>
                <div class="value" id="stat-columns">-</div>
            </div>
            <div class="stat-card">
                <h3>Sources</h3>
                <div class="value" id="stat-sources">-</div>
            </div>
            <div class="stat-card">
                <h3>Models</h3>
                <div class="value" id="stat-models">-</div>
            </div>
        </div>

        <div class="tables-section">
            <h2>Profiled Tables</h2>
            <div class="table-list" id="table-list">
                <div class="loading">Loading profiles...</div>
            </div>
        </div>
    </div>

    <div class="detail-panel" id="detail-panel">
        <div class="detail-header">
            <h2 id="detail-title">Table Details</h2>
            <button class="close-btn" onclick="closeDetail()">&times;</button>
        </div>
        <div class="detail-content" id="detail-content">
            <div class="loading">Select a table to view details</div>
        </div>
    </div>

    <script>
        async function loadSummary() {
            try {
                const resp = await fetch('/api/summary');
                const data = await resp.json();
                document.getElementById('stat-tables').textContent = data.total_tables || 0;
                document.getElementById('stat-columns').textContent = data.total_columns || 0;
                document.getElementById('stat-sources').textContent = data.sources || 0;
                document.getElementById('stat-models').textContent = data.models || 0;
            } catch (e) {
                console.error('Failed to load summary:', e);
            }
        }

        async function loadProfiles() {
            const container = document.getElementById('table-list');
            try {
                const resp = await fetch('/api/profiles');
                const data = await resp.json();

                if (data.profiles.length === 0) {
                    container.innerHTML = '<div class="loading">No profiles found. Run "dvt profile" first.</div>';
                    return;
                }

                container.innerHTML = data.profiles.map(p => `
                    <div class="table-card" onclick="showDetail('${p.table_name}')">
                        <div class="table-header">
                            <span class="table-name">${p.source_name ? p.source_name + '.' : ''}${p.table_name}</span>
                            <span class="table-type ${p.type}">${p.type}</span>
                        </div>
                        <div class="table-meta">
                            ${p.column_count} columns • Last profiled: ${new Date(p.last_profiled).toLocaleString()}
                        </div>
                    </div>
                `).join('');
            } catch (e) {
                container.innerHTML = `<div class="error">Failed to load profiles: ${e.message}</div>`;
            }
        }

        async function showDetail(tableName) {
            const panel = document.getElementById('detail-panel');
            const title = document.getElementById('detail-title');
            const content = document.getElementById('detail-content');

            panel.classList.add('open');
            title.textContent = tableName;
            content.innerHTML = '<div class="loading">Loading...</div>';

            // Highlight selected
            document.querySelectorAll('.table-card').forEach(c => c.classList.remove('selected'));
            event.currentTarget.classList.add('selected');

            try {
                const resp = await fetch(`/api/profile?table=${encodeURIComponent(tableName)}`);
                const data = await resp.json();

                if (data.error) {
                    content.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }

                let html = '';
                if (data.row_count !== null) {
                    html += `<p style="margin-bottom: 1rem;">Row count: <strong>${data.row_count.toLocaleString()}</strong></p>`;
                }

                html += `
                    <table class="column-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Column</th>
                                <th>Type</th>
                                <th>Spark Type</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.columns.map(c => `
                                <tr>
                                    <td>${c.ordinal_position}</td>
                                    <td><strong>${c.name}</strong></td>
                                    <td><span class="type-badge">${c.adapter_type || '-'}</span></td>
                                    <td><span class="type-badge">${c.spark_type || '-'}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;

                content.innerHTML = html;
            } catch (e) {
                content.innerHTML = `<div class="error">Failed to load details: ${e.message}</div>`;
            }
        }

        function closeDetail() {
            document.getElementById('detail-panel').classList.remove('open');
            document.querySelectorAll('.table-card').forEach(c => c.classList.remove('selected'));
        }

        // Initialize
        loadSummary();
        loadProfiles();
    </script>
</body>
</html>'''

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def serve_profile_ui(
    project_dir: Path,
    port: int = 8580,
    host: str = "localhost",
    open_browser: bool = True,
):
    """
    Start the profile viewer web server.

    Args:
        project_dir: Path to the DVT project
        port: Port to serve on (default: 8580)
        host: Host to bind to (default: localhost)
        open_browser: Whether to open browser automatically
    """
    # Find metadata store
    metadata_store_path = project_dir / ".dvt" / "metadata_store.duckdb"

    if not metadata_store_path.exists():
        if HAS_RICH:
            console.print(Panel(
                "[yellow]No metadata store found.[/yellow]\n\n"
                "Run [bold cyan]dvt profile[/bold cyan] first to capture profiling data.",
                title="[bold red]Error[/bold red]",
                border_style="red",
            ))
        else:
            print("Error: No metadata store found.")
            print("Run 'dvt profile' first to capture profiling data.")
        return False

    # Create handler with metadata store path
    def handler(*args, **kwargs):
        return ProfileAPIHandler(*args, metadata_store_path=metadata_store_path, **kwargs)

    # Start server
    server = HTTPServer((host, port), handler)
    url = f"http://{host}:{port}"

    if HAS_RICH:
        console.print()
        console.print(Panel(
            f"[bold green]Profile Viewer running at:[/bold green]\n\n"
            f"  [bold cyan]{url}[/bold cyan]\n\n"
            f"[dim]Press Ctrl+C to stop[/dim]",
            title="[bold magenta]🔍 DVT Profile Viewer[/bold magenta]",
            border_style="magenta",
            box=box.DOUBLE,
        ))
        console.print()
    else:
        print(f"\nDVT Profile Viewer running at: {url}")
        print("Press Ctrl+C to stop\n")

    # Open browser
    if open_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        if HAS_RICH:
            console.print("\n[yellow]Server stopped.[/yellow]")
        else:
            print("\nServer stopped.")

    return True


if __name__ == "__main__":
    # For testing
    import sys
    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    serve_profile_ui(project_dir)
