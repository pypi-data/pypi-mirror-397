#!/usr/bin/env python3
"""
FlowMason Package Builder.

Creates .fmpkg packages from component source files.
Uses the new architecture with flowmason-package.json manifest.
"""

import json
import zipfile
import argparse
import sys
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


def load_component_module(source_path: Path):
    """Load a Python module from source path."""
    spec = importlib.util.spec_from_file_location("component_module", source_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load module from {source_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["component_module"] = module
    spec.loader.exec_module(module)
    return module


def find_component_class(module) -> Optional[type]:
    """Find the FlowMason component class in a module."""
    import inspect

    for name, obj in inspect.getmembers(module, inspect.isclass):
        if hasattr(obj, "_flowmason_metadata") and hasattr(obj, "_flowmason_type"):
            if obj.__module__ == "component_module":
                return obj

    return None


def extract_metadata(component_class) -> Dict[str, Any]:
    """Extract metadata from a component class."""
    metadata = getattr(component_class, "_flowmason_metadata", {})
    component_type = getattr(component_class, "_flowmason_type", "unknown")

    # Get Input/Output schemas
    input_schema = {}
    output_schema = {}

    if hasattr(component_class, "Input"):
        try:
            input_schema = component_class.Input.model_json_schema()
        except Exception:
            pass

    if hasattr(component_class, "Output"):
        try:
            output_schema = component_class.Output.model_json_schema()
        except Exception:
            pass

    return {
        "name": metadata.get("name", "unknown"),
        "version": metadata.get("version", "1.0.0"),
        "type": component_type,  # "node" or "operator"
        "description": metadata.get("description", ""),
        "category": metadata.get("category", "custom"),
        "icon": metadata.get("icon", "box"),
        "color": metadata.get("color", "#6B7280"),
        "author": metadata.get("author", "Unknown"),
        "tags": metadata.get("tags", []),
        "recommended_providers": metadata.get("recommended_providers", {}),
        "default_provider": metadata.get("default_provider"),
        "input_schema": input_schema,
        "output_schema": output_schema,
        "requires_llm": component_type == "node",
    }


def create_manifest(metadata: Dict[str, Any], entry_point: str = "index.py") -> Dict[str, Any]:
    """Create a flowmason-package.json manifest."""
    return {
        "name": metadata["name"],
        "version": metadata["version"],
        "description": metadata["description"],
        "type": metadata["type"],
        "author": {
            "name": metadata["author"],
        },
        "license": "MIT",
        "category": metadata["category"],
        "tags": metadata["tags"],
        "entry_point": entry_point,
        "requires_llm": metadata["requires_llm"],
        "dependencies": [],
        "recommended_providers": metadata["recommended_providers"],
        "default_provider": metadata["default_provider"],
        "input_schema": metadata["input_schema"],
        "output_schema": metadata["output_schema"],
        "is_core": True,  # Mark as core package
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


def build_package(
    source_path: Path,
    output_dir: Path,
    version_override: Optional[str] = None,
) -> Path:
    """
    Build a .fmpkg package from a component source file.

    Args:
        source_path: Path to the component Python file
        output_dir: Directory to write the package
        version_override: Optional version override

    Returns:
        Path to the created .fmpkg file
    """
    # Ensure flowmason_core is importable
    project_root = Path(__file__).parent.parent
    core_path = project_root / "core"
    if str(core_path) not in sys.path:
        sys.path.insert(0, str(core_path))

    # Load the component module
    module = load_component_module(source_path)

    # Find component class
    component_class = find_component_class(module)
    if component_class is None:
        raise ValueError(f"No FlowMason component found in {source_path}")

    # Extract metadata
    metadata = extract_metadata(component_class)

    if version_override:
        metadata["version"] = version_override

    # Create manifest
    manifest = create_manifest(metadata)

    # Read source code
    source_code = source_path.read_text()

    # Create package
    package_name = f"{metadata['name']}-{metadata['version']}.fmpkg"
    output_dir.mkdir(parents=True, exist_ok=True)
    package_path = output_dir / package_name

    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add manifest
        zf.writestr("flowmason-package.json", json.dumps(manifest, indent=2))
        # Add source code as index.py
        zf.writestr("index.py", source_code)

    print(f"Created package: {package_path}")
    print(f"  Name: {metadata['name']}")
    print(f"  Version: {metadata['version']}")
    print(f"  Type: {metadata['type']}")
    print(f"  Category: {metadata['category']}")

    return package_path


def build_all_core_packages(output_dir: Path) -> list:
    """Build all core packages."""
    project_root = Path(__file__).parent.parent
    lab_dir = project_root / "lab" / "flowmason_lab"

    packages = []

    # Core nodes
    nodes_dir = lab_dir / "nodes" / "core"
    if nodes_dir.exists():
        for py_file in nodes_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            try:
                pkg_path = build_package(py_file, output_dir)
                packages.append(pkg_path)
            except Exception as e:
                print(f"Error building {py_file}: {e}")

    # Core operators
    operators_dir = lab_dir / "operators" / "core"
    if operators_dir.exists():
        for py_file in operators_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            try:
                pkg_path = build_package(py_file, output_dir)
                packages.append(pkg_path)
            except Exception as e:
                print(f"Error building {py_file}: {e}")

    return packages


def main():
    parser = argparse.ArgumentParser(description="Build FlowMason packages")
    parser.add_argument(
        "source",
        nargs="?",
        help="Source file to package (or 'all' for all core packages)",
    )
    parser.add_argument(
        "--output", "-o",
        default="dist/packages",
        help="Output directory for packages",
    )
    parser.add_argument(
        "--version", "-v",
        help="Version override",
    )

    args = parser.parse_args()

    output_dir = Path(args.output)

    if args.source == "all" or args.source is None:
        print("Building all core packages...")
        packages = build_all_core_packages(output_dir)
        print(f"\nBuilt {len(packages)} packages")
    else:
        source_path = Path(args.source)
        if not source_path.exists():
            print(f"Error: Source file not found: {source_path}")
            sys.exit(1)
        build_package(source_path, output_dir, args.version)


if __name__ == "__main__":
    main()
