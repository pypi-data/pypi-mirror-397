"""
Tests for the Package Loader.

Tests the extraction and loading of .fmpkg packages.
"""

import json
import zipfile
import pytest
from pathlib import Path

from flowmason_core.registry.loader import PackageLoader
from flowmason_core.registry.types import PackageLoadError

from tests.conftest import SAMPLE_NODE_SOURCE, create_sample_manifest


class TestPackageExtraction:
    """Tests for package extraction."""

    def test_extract_valid_package(self, temp_packages_dir, sample_node_package):
        """Test extracting a valid package."""
        loader = PackageLoader()

        extract_dir, manifest = loader.extract_package(sample_node_package)

        assert extract_dir.exists()
        assert (extract_dir / "flowmason-package.json").exists()
        assert (extract_dir / "index.py").exists()
        assert manifest["name"] == "test-generator"

    def test_extract_nonexistent_file(self, temp_packages_dir):
        """Test extracting a file that doesn't exist."""
        loader = PackageLoader()

        with pytest.raises(PackageLoadError) as exc_info:
            loader.extract_package("/nonexistent/file.fmpkg")

        assert "not found" in str(exc_info.value)

    def test_extract_non_fmpkg_file(self, temp_packages_dir):
        """Test extracting a non-.fmpkg file."""
        loader = PackageLoader()
        fake_file = temp_packages_dir / "fake.txt"
        fake_file.write_text("not a package")

        with pytest.raises(PackageLoadError) as exc_info:
            loader.extract_package(fake_file)

        assert "Not a .fmpkg file" in str(exc_info.value)

    def test_extract_invalid_zip(self, temp_packages_dir):
        """Test extracting an invalid zip file."""
        loader = PackageLoader()
        bad_pkg = temp_packages_dir / "bad.fmpkg"
        bad_pkg.write_text("not a valid zip file")

        with pytest.raises(PackageLoadError) as exc_info:
            loader.extract_package(bad_pkg)

        assert "Invalid zip file" in str(exc_info.value)

    def test_extract_missing_manifest(self, temp_packages_dir):
        """Test extracting a package without manifest."""
        loader = PackageLoader()
        bad_pkg = temp_packages_dir / "no-manifest.fmpkg"

        with zipfile.ZipFile(bad_pkg, "w") as zf:
            zf.writestr("index.py", "# no manifest")

        with pytest.raises(PackageLoadError) as exc_info:
            loader.extract_package(bad_pkg)

        assert "Missing flowmason-package.json" in str(exc_info.value)


class TestManifestReading:
    """Tests for reading package manifests."""

    def test_read_manifest(self, sample_node_package):
        """Test reading manifest from package."""
        loader = PackageLoader()

        manifest = loader.read_manifest(sample_node_package)

        assert manifest["name"] == "test-generator"
        assert manifest["version"] == "1.0.0"
        assert manifest["type"] == "node"

    def test_read_manifest_invalid_json(self, temp_packages_dir):
        """Test reading manifest with invalid JSON."""
        loader = PackageLoader()
        bad_pkg = temp_packages_dir / "bad-json.fmpkg"

        with zipfile.ZipFile(bad_pkg, "w") as zf:
            zf.writestr("flowmason-package.json", "{ invalid json }")

        with pytest.raises(PackageLoadError) as exc_info:
            loader.read_manifest(bad_pkg)

        assert "Invalid manifest JSON" in str(exc_info.value)


class TestComponentLoading:
    """Tests for loading component classes."""

    def test_load_node_class(self, temp_packages_dir, sample_node_package):
        """Test loading a node class from package."""
        loader = PackageLoader()
        extract_dir, manifest = loader.extract_package(sample_node_package)

        component_class = loader.load_component_class(extract_dir, "index.py")

        assert component_class is not None
        assert component_class.__name__ == "TestGeneratorNode"
        assert hasattr(component_class, "_flowmason_metadata")
        assert component_class._flowmason_type == "node"

    def test_load_operator_class(self, temp_packages_dir, sample_operator_package):
        """Test loading an operator class from package."""
        loader = PackageLoader()
        extract_dir, manifest = loader.extract_package(sample_operator_package)

        component_class = loader.load_component_class(extract_dir, "index.py")

        assert component_class is not None
        assert component_class.__name__ == "TestTransformOperator"
        assert component_class._flowmason_type == "operator"

    def test_load_missing_entry_point(self, temp_packages_dir, sample_node_package):
        """Test loading with missing entry point."""
        loader = PackageLoader()
        extract_dir, _ = loader.extract_package(sample_node_package)

        with pytest.raises(PackageLoadError) as exc_info:
            loader.load_component_class(extract_dir, "nonexistent.py")

        assert "not found" in str(exc_info.value)

    def test_load_specific_class(self, temp_packages_dir, sample_node_package):
        """Test loading a specific class by name."""
        loader = PackageLoader()
        extract_dir, _ = loader.extract_package(sample_node_package)

        component_class = loader.load_component_class(
            extract_dir,
            "index.py",
            class_name="TestGeneratorNode"
        )

        assert component_class.__name__ == "TestGeneratorNode"

    def test_load_wrong_class_name(self, temp_packages_dir, sample_node_package):
        """Test loading a non-existent class name."""
        loader = PackageLoader()
        extract_dir, _ = loader.extract_package(sample_node_package)

        with pytest.raises(PackageLoadError) as exc_info:
            loader.load_component_class(
                extract_dir,
                "index.py",
                class_name="NonExistentClass"
            )

        assert "not found" in str(exc_info.value)


class TestPackageUnloading:
    """Tests for package unloading."""

    def test_unload_package(self, temp_packages_dir, sample_node_package):
        """Test unloading a package."""
        loader = PackageLoader()
        extract_dir, _ = loader.extract_package(sample_node_package)
        loader.load_component_class(extract_dir, "index.py")

        # Should not raise
        loader.unload_package(extract_dir)

    def test_cleanup(self, temp_packages_dir, sample_node_package):
        """Test cleanup clears all loaded modules."""
        loader = PackageLoader()
        extract_dir, _ = loader.extract_package(sample_node_package)
        loader.load_component_class(extract_dir, "index.py")

        loader.cleanup()

        assert len(loader._loaded_modules) == 0


class TestPackageInfo:
    """Tests for package info creation."""

    def test_get_package_info(self, sample_node_package):
        """Test creating PackageInfo from manifest."""
        loader = PackageLoader()
        manifest = loader.read_manifest(sample_node_package)

        pkg_info = loader.get_package_info(manifest, str(sample_node_package))

        assert pkg_info.name == "test-generator"
        assert pkg_info.version == "1.0.0"
        assert pkg_info.author == "Test Author"
        assert pkg_info.package_path == str(sample_node_package)

    def test_get_package_info_minimal_manifest(self, temp_packages_dir):
        """Test PackageInfo with minimal manifest."""
        loader = PackageLoader()

        minimal_manifest = {
            "name": "minimal",
            "version": "0.1.0",
            "description": "Minimal package"
        }

        pkg_info = loader.get_package_info(minimal_manifest, "/path/to/pkg.fmpkg")

        assert pkg_info.name == "minimal"
        assert pkg_info.version == "0.1.0"
        assert pkg_info.author is None
