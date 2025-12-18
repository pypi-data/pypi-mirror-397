"""
Tests for the Universal Component Registry.

These tests verify that the registry can:
- Scan and load packages dynamically
- Register components without hardcoded types
- Provide lookup methods for components
- Handle errors gracefully
"""

import tempfile
import pytest
from pathlib import Path

from flowmason_core.registry.registry import ComponentRegistry
from flowmason_core.registry.types import ComponentNotFoundError, PackageLoadError


class TestComponentRegistryBasics:
    """Basic registry functionality tests."""

    def test_create_empty_registry(self):
        """Test creating an empty registry."""
        packages_dir = Path(tempfile.mkdtemp()) / "packages"
        packages_dir.mkdir()

        registry = ComponentRegistry(packages_dir, auto_scan=False)

        assert registry is not None
        assert len(registry.list_components()) == 0
        assert registry.get_stats()["total_components"] == 0

    def test_registry_auto_scan_empty_dir(self):
        """Test registry with empty packages directory."""
        packages_dir = Path(tempfile.mkdtemp()) / "packages"
        packages_dir.mkdir()

        registry = ComponentRegistry(packages_dir, auto_scan=True)

        assert len(registry.list_components()) == 0

    def test_registry_repr(self):
        """Test registry string representation."""
        packages_dir = Path(tempfile.mkdtemp()) / "packages"
        packages_dir.mkdir()

        registry = ComponentRegistry(packages_dir, auto_scan=False)
        repr_str = repr(registry)

        assert "ComponentRegistry" in repr_str
        assert "components=0" in repr_str


class TestPackageRegistration:
    """Tests for package registration."""

    def test_register_node_package(self, sample_node_package, temp_packages_dir):
        """Test registering a node package."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)

        pkg_info = registry.register_package(sample_node_package)

        assert pkg_info.name == "test-generator"
        assert pkg_info.version == "1.0.0"
        assert len(pkg_info.components) == 1
        assert "test_generator" in pkg_info.components

    def test_register_operator_package(self, sample_operator_package, temp_packages_dir):
        """Test registering an operator package."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)

        pkg_info = registry.register_package(sample_operator_package)

        assert pkg_info.name == "test-transform"
        assert len(pkg_info.components) == 1
        assert "test_transform" in pkg_info.components

    def test_scan_packages_finds_all(self, multiple_packages, temp_packages_dir):
        """Test that scan_packages finds all packages."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)

        count = registry.scan_packages()

        assert count == 2
        assert len(registry.list_components()) == 2
        assert registry.has_component("test_generator")
        assert registry.has_component("test_transform")

    def test_register_duplicate_package(self, sample_node_package, temp_packages_dir):
        """Test registering the same package twice returns cached info."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)

        pkg_info1 = registry.register_package(sample_node_package)
        pkg_info2 = registry.register_package(sample_node_package)

        assert pkg_info1.name == pkg_info2.name
        assert len(registry.list_components()) == 1

    def test_register_nonexistent_package(self, temp_packages_dir):
        """Test registering a package that doesn't exist."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)

        with pytest.raises(PackageLoadError):
            registry.register_package("/nonexistent/package.fmpkg")


class TestComponentLookup:
    """Tests for component lookup functionality."""

    def test_get_component_class(self, sample_node_package, temp_packages_dir):
        """Test getting a component class."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)
        registry.register_package(sample_node_package)

        component_class = registry.get_component_class("test_generator")

        assert component_class is not None
        assert hasattr(component_class, "_flowmason_metadata")
        assert component_class._flowmason_metadata["name"] == "test_generator"

    def test_get_component_metadata(self, sample_node_package, temp_packages_dir):
        """Test getting component metadata."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)
        registry.register_package(sample_node_package)

        metadata = registry.get_component_metadata("test_generator")

        assert metadata.component_type == "test_generator"
        assert metadata.component_kind == "node"
        assert metadata.category == "testing"
        assert metadata.description == "A test generator node"

    def test_get_nonexistent_component(self, temp_packages_dir):
        """Test getting a component that doesn't exist."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)

        with pytest.raises(ComponentNotFoundError) as exc_info:
            registry.get_component_class("nonexistent")

        assert "nonexistent" in str(exc_info.value)

    def test_has_component(self, sample_node_package, temp_packages_dir):
        """Test checking if component exists."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)
        registry.register_package(sample_node_package)

        assert registry.has_component("test_generator") is True
        assert registry.has_component("nonexistent") is False


class TestComponentListing:
    """Tests for listing components."""

    def test_list_all_components(self, multiple_packages, temp_packages_dir):
        """Test listing all components."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=True)

        components = registry.list_components()

        assert len(components) == 2

    def test_list_nodes_only(self, multiple_packages, temp_packages_dir):
        """Test listing only nodes."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=True)

        nodes = registry.list_nodes()

        assert len(nodes) == 1
        assert nodes[0].component_type == "test_generator"
        assert nodes[0].component_kind == "node"

    def test_list_operators_only(self, multiple_packages, temp_packages_dir):
        """Test listing only operators."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=True)

        operators = registry.list_operators()

        assert len(operators) == 1
        assert operators[0].component_type == "test_transform"
        assert operators[0].component_kind == "operator"

    def test_list_by_category(self, multiple_packages, temp_packages_dir):
        """Test listing components by category."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=True)

        components = registry.list_components(category="testing")

        assert len(components) == 2

    def test_get_categories(self, multiple_packages, temp_packages_dir):
        """Test getting all categories."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=True)

        categories = registry.get_categories()

        assert "testing" in categories


class TestPackageManagement:
    """Tests for package management."""

    def test_unregister_package(self, sample_node_package, temp_packages_dir):
        """Test unregistering a package."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)
        registry.register_package(sample_node_package)

        assert registry.has_component("test_generator")

        result = registry.unregister_package("test-generator")

        assert result is True
        assert not registry.has_component("test_generator")

    def test_unregister_nonexistent_package(self, temp_packages_dir):
        """Test unregistering a package that doesn't exist."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)

        result = registry.unregister_package("nonexistent")

        assert result is False

    def test_list_packages(self, multiple_packages, temp_packages_dir):
        """Test listing all packages."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=True)

        packages = registry.list_packages()

        assert len(packages) == 2

    def test_get_package_info(self, sample_node_package, temp_packages_dir):
        """Test getting package info."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)
        registry.register_package(sample_node_package)

        pkg_info = registry.get_package_info("test-generator")

        assert pkg_info is not None
        assert pkg_info.name == "test-generator"
        assert pkg_info.version == "1.0.0"


class TestRegistryRefresh:
    """Tests for registry refresh functionality."""

    def test_refresh_clears_and_rescans(self, sample_node_package, temp_packages_dir):
        """Test that refresh clears and rescans."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=True)

        assert registry.has_component("test_generator")

        # Refresh should find the same components
        count = registry.refresh()

        assert count == 1
        assert registry.has_component("test_generator")


class TestRegistryStats:
    """Tests for registry statistics."""

    def test_get_stats(self, multiple_packages, temp_packages_dir):
        """Test getting registry stats."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=True)

        stats = registry.get_stats()

        assert stats["total_components"] == 2
        assert stats["total_nodes"] == 1
        assert stats["total_operators"] == 1
        assert stats["total_packages"] == 2
        assert "testing" in stats["categories"]


class TestComponentExecution:
    """Tests for component execution (integration)."""

    @pytest.mark.asyncio
    async def test_execute_loaded_node(self, sample_node_package, temp_packages_dir):
        """Test executing a loaded node component."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)
        registry.register_package(sample_node_package)

        # Get component class
        NodeClass = registry.get_component_class("test_generator")

        # Create input
        node_input = NodeClass.Input(prompt="Hello, world!")

        # Execute (with mock context)
        class MockContext:
            pass

        node = NodeClass()
        result = await node.execute(node_input, MockContext())

        assert result.content == "Generated from: Hello, world!"
        assert result.tokens_used == 100

    @pytest.mark.asyncio
    async def test_execute_loaded_operator(self, sample_operator_package, temp_packages_dir):
        """Test executing a loaded operator component."""
        registry = ComponentRegistry(temp_packages_dir, auto_scan=False)
        registry.register_package(sample_operator_package)

        # Get component class
        OperatorClass = registry.get_component_class("test_transform")

        # Create input
        op_input = OperatorClass.Input(data="hello", uppercase=True)

        # Execute
        class MockContext:
            pass

        op = OperatorClass()
        result = await op.execute(op_input, MockContext())

        assert result.result == "HELLO"
        assert result.transformed is True
