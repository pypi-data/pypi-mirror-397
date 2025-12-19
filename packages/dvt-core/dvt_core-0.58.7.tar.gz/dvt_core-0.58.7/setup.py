"""
DVT-Core Setup with Cython Compilation

This setup.py integrates with pyproject.toml to compile DVT-specific
modules to binary extensions during wheel building.

The pyproject.toml handles metadata and dependencies.
This setup.py handles Cython extension compilation.
"""

import os
import sys
from pathlib import Path

from setuptools import setup

# DVT-specific modules to compile to binary (IP protection)
# v0.56.0: Expanded to ALL 35 proprietary DVT modules
# v0.57.0: CRITICAL FIX - Do NOT compile __init__.py files of packages with submodules!
#          Compiling __init__.py creates a .so FILE at the same level as the package
#          DIRECTORY, causing Python import ambiguity on Linux (manylinux).
#          Package __init__.py files MUST remain as .py for Python to recognize
#          the directory as a package with __path__ attribute.
COMPILABLE_MODULES = [
    # --- Core Query Analysis ---
    ("dbt.query_analyzer", "dbt/query_analyzer.py"),

    # --- Configuration ---
    ("dbt.config.dvt_profile", "dbt/config/dvt_profile.py"),
    ("dbt.config.compute", "dbt/config/compute.py"),

    # --- Task Commands (DVT-specific CLI) ---
    ("dbt.task.metadata", "dbt/task/metadata.py"),  # v0.57.0: Replaces snap.py
    ("dbt.task.target_sync", "dbt/task/target_sync.py"),
    ("dbt.task.compute", "dbt/task/compute.py"),
    ("dbt.task.profile", "dbt/task/profile.py"),
    ("dbt.task.java", "dbt/task/java.py"),
    ("dbt.task.spark", "dbt/task/spark.py"),
    ("dbt.task.init", "dbt/task/init.py"),  # Enhanced multi-connection wizard
    ("dbt.task.docs.serve", "dbt/task/docs/serve.py"),

    # --- REST API Endpoints ---
    # NOTE: dbt.task.docs.api/__init__.py NOT compiled (package with submodules)
    ("dbt.task.docs.api.catalog", "dbt/task/docs/api/catalog.py"),
    ("dbt.task.docs.api.lineage", "dbt/task/docs/api/lineage.py"),
    ("dbt.task.docs.api.profile", "dbt/task/docs/api/profile.py"),
    ("dbt.task.docs.api.spark", "dbt/task/docs/api/spark.py"),

    # --- Compute Layer (Base) ---
    # NOTE: dbt.compute/__init__.py NOT compiled (package with submodules)
    ("dbt.compute.federated_executor", "dbt/compute/federated_executor.py"),
    ("dbt.compute.smart_selector", "dbt/compute/smart_selector.py"),
    ("dbt.compute.filter_pushdown", "dbt/compute/filter_pushdown.py"),
    ("dbt.compute.jdbc_utils", "dbt/compute/jdbc_utils.py"),
    ("dbt.compute.jar_provisioning", "dbt/compute/jar_provisioning.py"),
    ("dbt.compute.java_compat", "dbt/compute/java_compat.py"),

    # --- Compute Engines ---
    # NOTE: dbt.compute.engines/__init__.py NOT compiled (package with submodules)
    ("dbt.compute.engines.spark_engine", "dbt/compute/engines/spark_engine.py"),

    # --- Compute Strategies (Platform-Specific) ---
    # NOTE: dbt.compute.strategies/__init__.py NOT compiled (package with submodules)
    ("dbt.compute.strategies.base", "dbt/compute/strategies/base.py"),
    ("dbt.compute.strategies.local", "dbt/compute/strategies/local.py"),
    ("dbt.compute.strategies.standalone", "dbt/compute/strategies/standalone.py"),
    ("dbt.compute.strategies.emr", "dbt/compute/strategies/emr.py"),
    ("dbt.compute.strategies.dataproc", "dbt/compute/strategies/dataproc.py"),

    # --- Metadata Architecture ---
    # NOTE: dbt.compute.metadata/__init__.py NOT compiled (package with submodules)
    ("dbt.compute.metadata.adapters_registry", "dbt/compute/metadata/adapters_registry.py"),
    ("dbt.compute.metadata.registry", "dbt/compute/metadata/registry.py"),
    ("dbt.compute.metadata.store", "dbt/compute/metadata/store.py"),
]


def get_ext_modules():
    """Build Cython extensions if Cython is available."""
    try:
        from Cython.Build import cythonize
        from setuptools import Extension
    except ImportError:
        print("Cython not available - building pure Python wheel")
        return []

    extensions = []
    base_dir = Path(__file__).parent

    for module_name, source_path in COMPILABLE_MODULES:
        full_path = base_dir / source_path
        if not full_path.exists():
            print(f"WARNING: Source not found: {source_path}")
            continue

        ext = Extension(
            name=module_name,
            sources=[str(source_path)],
        )
        extensions.append(ext)

    if not extensions:
        print("No modules to compile")
        return []

    print(f"Compiling {len(extensions)} DVT modules to binary...")
    for ext in extensions:
        print(f"  - {ext.name}")

    return cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
        },
    )


# Only define ext_modules - everything else comes from pyproject.toml
setup(
    ext_modules=get_ext_modules(),
)
