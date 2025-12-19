"""
FlowMason Snapshot Testing

Provides utilities for snapshot testing of pipeline outputs.
"""

import difflib
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class SnapshotDiff:
    """Represents a difference between actual and expected output."""
    path: str  # JSON path to the difference
    expected: Any
    actual: Any
    diff_type: str  # 'added', 'removed', 'changed', 'type_mismatch'


@dataclass
class SnapshotResult:
    """Result of a snapshot comparison."""
    matches: bool
    differences: List[SnapshotDiff]
    expected_hash: str
    actual_hash: str
    snapshot_path: Optional[str] = None


class SnapshotManager:
    """
    Manages snapshot testing for pipeline outputs.

    Usage:
        snapshots = SnapshotManager("tests/snapshots")

        # Save a new snapshot
        snapshots.save("test_name", pipeline_output)

        # Compare against existing snapshot
        result = snapshots.compare("test_name", new_output)
        if not result.matches:
            print(f"Differences: {result.differences}")

        # Update snapshot
        if update_snapshots:
            snapshots.update("test_name", new_output)
    """

    def __init__(
        self,
        snapshot_dir: str = "snapshots",
        auto_create: bool = True,
        ignore_keys: Optional[List[str]] = None,
    ):
        """
        Initialize snapshot manager.

        Args:
            snapshot_dir: Directory to store snapshots
            auto_create: Create directory if it doesn't exist
            ignore_keys: Keys to ignore in comparisons (e.g., timestamps)
        """
        self.snapshot_dir = Path(snapshot_dir)
        self.ignore_keys = set(ignore_keys or [
            "timestamp",
            "created_at",
            "updated_at",
            "run_id",
            "execution_id",
            "duration_ms",
            "started_at",
            "completed_at",
        ])

        if auto_create:
            self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _snapshot_path(self, name: str) -> Path:
        """Get the path for a snapshot file."""
        return self.snapshot_dir / f"{name}.snapshot.json"

    def _hash_data(self, data: Any) -> str:
        """Generate a hash for data."""
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    def _normalize_data(self, data: Any, path: str = "") -> Any:
        """
        Normalize data for comparison by removing ignored keys.

        Args:
            data: Data to normalize
            path: Current JSON path (for debugging)

        Returns:
            Normalized data
        """
        if isinstance(data, dict):
            return {
                k: self._normalize_data(v, f"{path}.{k}")
                for k, v in data.items()
                if k not in self.ignore_keys
            }
        elif isinstance(data, list):
            return [
                self._normalize_data(item, f"{path}[{i}]")
                for i, item in enumerate(data)
            ]
        else:
            return data

    def _find_differences(
        self,
        expected: Any,
        actual: Any,
        path: str = "$",
    ) -> List[SnapshotDiff]:
        """
        Find differences between expected and actual values.

        Args:
            expected: Expected value
            actual: Actual value
            path: Current JSON path

        Returns:
            List of differences found
        """
        differences: List[SnapshotDiff] = []

        if type(expected) != type(actual):
            differences.append(SnapshotDiff(
                path=path,
                expected=expected,
                actual=actual,
                diff_type="type_mismatch",
            ))
            return differences

        if isinstance(expected, dict):
            all_keys = set(expected.keys()) | set(actual.keys())
            for key in all_keys:
                new_path = f"{path}.{key}"

                if key not in expected:
                    differences.append(SnapshotDiff(
                        path=new_path,
                        expected=None,
                        actual=actual[key],
                        diff_type="added",
                    ))
                elif key not in actual:
                    differences.append(SnapshotDiff(
                        path=new_path,
                        expected=expected[key],
                        actual=None,
                        diff_type="removed",
                    ))
                else:
                    differences.extend(
                        self._find_differences(expected[key], actual[key], new_path)
                    )

        elif isinstance(expected, list):
            if len(expected) != len(actual):
                differences.append(SnapshotDiff(
                    path=f"{path}.length",
                    expected=len(expected),
                    actual=len(actual),
                    diff_type="changed",
                ))

            for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
                differences.extend(
                    self._find_differences(exp_item, act_item, f"{path}[{i}]")
                )

        elif expected != actual:
            differences.append(SnapshotDiff(
                path=path,
                expected=expected,
                actual=actual,
                diff_type="changed",
            ))

        return differences

    def save(self, name: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        Save a new snapshot.

        Args:
            name: Snapshot name
            data: Data to snapshot
            metadata: Optional metadata to include

        Returns:
            Path to the saved snapshot file
        """
        snapshot_path = self._snapshot_path(name)

        normalized = self._normalize_data(data)

        snapshot = {
            "version": 1,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "hash": self._hash_data(normalized),
            "data": normalized,
            "metadata": metadata or {},
        }

        with open(snapshot_path, "w") as f:
            json.dump(snapshot, f, indent=2, default=str)

        return snapshot_path

    def load(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load an existing snapshot.

        Args:
            name: Snapshot name

        Returns:
            Snapshot data or None if not found
        """
        snapshot_path = self._snapshot_path(name)

        if not snapshot_path.exists():
            return None

        with open(snapshot_path, "r") as f:
            data: Dict[str, Any] = json.load(f)
            return data

    def exists(self, name: str) -> bool:
        """Check if a snapshot exists."""
        return self._snapshot_path(name).exists()

    def compare(
        self,
        name: str,
        actual_data: Any,
    ) -> SnapshotResult:
        """
        Compare actual data against a saved snapshot.

        Args:
            name: Snapshot name
            actual_data: Data to compare

        Returns:
            SnapshotResult with match status and any differences
        """
        snapshot = self.load(name)
        normalized_actual = self._normalize_data(actual_data)
        actual_hash = self._hash_data(normalized_actual)

        if snapshot is None:
            return SnapshotResult(
                matches=False,
                differences=[SnapshotDiff(
                    path="$",
                    expected=None,
                    actual=normalized_actual,
                    diff_type="added",
                )],
                expected_hash="",
                actual_hash=actual_hash,
            )

        expected_data = snapshot["data"]
        expected_hash = snapshot["hash"]

        # Quick hash comparison
        if actual_hash == expected_hash:
            return SnapshotResult(
                matches=True,
                differences=[],
                expected_hash=expected_hash,
                actual_hash=actual_hash,
                snapshot_path=str(self._snapshot_path(name)),
            )

        # Detailed difference analysis
        differences = self._find_differences(expected_data, normalized_actual)

        return SnapshotResult(
            matches=len(differences) == 0,
            differences=differences,
            expected_hash=expected_hash,
            actual_hash=actual_hash,
            snapshot_path=str(self._snapshot_path(name)),
        )

    def update(self, name: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        Update an existing snapshot (or create if doesn't exist).

        Args:
            name: Snapshot name
            data: New data
            metadata: Optional metadata

        Returns:
            Path to the updated snapshot
        """
        return self.save(name, data, metadata)

    def delete(self, name: str) -> bool:
        """
        Delete a snapshot.

        Args:
            name: Snapshot name

        Returns:
            True if deleted, False if didn't exist
        """
        snapshot_path = self._snapshot_path(name)

        if not snapshot_path.exists():
            return False

        snapshot_path.unlink()
        return True

    def list_snapshots(self) -> List[str]:
        """List all available snapshots."""
        if not self.snapshot_dir.exists():
            return []

        snapshots = []
        for file in self.snapshot_dir.glob("*.snapshot.json"):
            name = file.name.replace(".snapshot.json", "")
            snapshots.append(name)

        return sorted(snapshots)


def assert_snapshot(
    name: str,
    actual: Any,
    snapshot_dir: str = "snapshots",
    update: bool = False,
    ignore_keys: Optional[List[str]] = None,
) -> None:
    """
    Assert that actual data matches a snapshot.

    Args:
        name: Snapshot name
        actual: Actual data to compare
        snapshot_dir: Directory for snapshots
        update: If True, update the snapshot instead of comparing
        ignore_keys: Keys to ignore in comparison

    Raises:
        AssertionError: If snapshot doesn't match
    """
    manager = SnapshotManager(snapshot_dir, ignore_keys=ignore_keys)

    if update or not manager.exists(name):
        manager.save(name, actual)
        return

    result = manager.compare(name, actual)

    if not result.matches:
        diff_message = "\n".join([
            f"  {d.path}: {d.diff_type}"
            f"\n    expected: {d.expected}"
            f"\n    actual:   {d.actual}"
            for d in result.differences
        ])
        raise AssertionError(
            f"Snapshot '{name}' doesn't match:\n{diff_message}\n\n"
            f"Run with update=True to update the snapshot."
        )


def snapshot_stage_outputs(
    stage_results: Dict[str, Any],
    snapshot_dir: str = "snapshots",
    prefix: str = "",
) -> Dict[str, SnapshotResult]:
    """
    Snapshot all stage outputs from a pipeline run.

    Args:
        stage_results: Map of stage_id to stage result
        snapshot_dir: Directory for snapshots
        prefix: Prefix for snapshot names

    Returns:
        Map of stage_id to SnapshotResult
    """
    manager = SnapshotManager(snapshot_dir)
    results: Dict[str, SnapshotResult] = {}

    for stage_id, stage_result in stage_results.items():
        name = f"{prefix}{stage_id}" if prefix else stage_id

        if not manager.exists(name):
            manager.save(name, stage_result)
            results[stage_id] = SnapshotResult(
                matches=True,
                differences=[],
                expected_hash=manager._hash_data(stage_result),
                actual_hash=manager._hash_data(stage_result),
            )
        else:
            results[stage_id] = manager.compare(name, stage_result)

    return results


def format_diff_report(result: SnapshotResult) -> str:
    """
    Format a snapshot result as a human-readable diff report.

    Args:
        result: Snapshot comparison result

    Returns:
        Formatted diff string
    """
    if result.matches:
        return "Snapshot matches (hash: {})".format(result.actual_hash)

    lines = [
        "Snapshot Mismatch",
        f"Expected hash: {result.expected_hash}",
        f"Actual hash:   {result.actual_hash}",
        "",
        "Differences:",
    ]

    for diff in result.differences:
        lines.append(f"  {diff.diff_type.upper()} at {diff.path}")
        if diff.expected is not None:
            lines.append(f"    - {json.dumps(diff.expected, default=str)}")
        if diff.actual is not None:
            lines.append(f"    + {json.dumps(diff.actual, default=str)}")

    return "\n".join(lines)


__all__ = [
    "SnapshotDiff",
    "SnapshotResult",
    "SnapshotManager",
    "assert_snapshot",
    "snapshot_stage_outputs",
    "format_diff_report",
]
