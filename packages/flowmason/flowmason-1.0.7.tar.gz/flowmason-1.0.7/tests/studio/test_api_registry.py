"""
Tests for Registry API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from flowmason_core.registry import ComponentRegistry

from flowmason_studio.api.app import create_app
from flowmason_studio.api.routes.registry import set_registry
from flowmason_studio.services.storage import (
    PipelineStorage,
    RunStorage,
    set_pipeline_storage,
    set_run_storage,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def registry(multiple_packages, temp_packages_dir):
    """Create a registry with test components from packages."""
    reg = ComponentRegistry(temp_packages_dir, auto_scan=True)
    return reg


@pytest.fixture
def empty_registry(temp_packages_dir):
    """Create an empty registry."""
    return ComponentRegistry(temp_packages_dir, auto_scan=False)


@pytest.fixture
def client(registry):
    """Create a test client with components registered."""
    set_registry(registry)
    set_pipeline_storage(PipelineStorage())
    set_run_storage(RunStorage())

    app = create_app(component_registry=registry)

    # Re-set storage since create_app's lifespan may override
    set_pipeline_storage(PipelineStorage())
    set_run_storage(RunStorage())

    return TestClient(app)


@pytest.fixture
def empty_client(empty_registry):
    """Create a test client with no components."""
    set_registry(empty_registry)
    set_pipeline_storage(PipelineStorage())
    set_run_storage(RunStorage())

    app = create_app(component_registry=empty_registry)

    set_pipeline_storage(PipelineStorage())
    set_run_storage(RunStorage())

    return TestClient(app)


# =============================================================================
# Component List Tests
# =============================================================================

class TestComponentList:
    """Tests for GET /api/v1/registry/components"""

    def test_list_components(self, client):
        """Should list all registered components."""
        response = client.get("/api/v1/registry/components")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 2
        assert len(data["components"]) == 2

        # Check component types are present
        types = [c["component_type"] for c in data["components"]]
        assert "test_generator" in types
        assert "test_transform" in types

    def test_list_empty_registry(self, empty_client):
        """Should return empty list when no components registered."""
        response = empty_client.get("/api/v1/registry/components")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 0
        assert data["components"] == []


# =============================================================================
# Component Detail Tests
# =============================================================================

class TestComponentDetail:
    """Tests for GET /api/v1/registry/components/{type}"""

    def test_get_component_detail(self, client):
        """Should get component details with schema."""
        response = client.get("/api/v1/registry/components/test_generator")

        assert response.status_code == 200
        data = response.json()

        assert data["component_type"] == "test_generator"
        assert "input_schema" in data
        assert "output_schema" in data

        # Check input schema has the prompt field
        input_props = data["input_schema"].get("properties", {})
        assert "prompt" in input_props

        # Check output schema has the content field
        output_props = data["output_schema"].get("properties", {})
        assert "content" in output_props

    def test_get_component_not_found(self, client):
        """Should return 404 for unknown component."""
        response = client.get("/api/v1/registry/components/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# =============================================================================
# Registry Stats Tests
# =============================================================================

class TestRegistryStats:
    """Tests for GET /api/v1/registry/stats"""

    def test_get_stats(self, client):
        """Should return registry statistics."""
        response = client.get("/api/v1/registry/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_components"] == 2
        assert "categories" in data

    def test_get_stats_empty(self, empty_client):
        """Should return zero stats for empty registry."""
        response = empty_client.get("/api/v1/registry/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_components"] == 0


# =============================================================================
# Component Unregister Tests
# =============================================================================

class TestComponentUnregister:
    """Tests for DELETE /api/v1/registry/components/{type}"""

    def test_unregister_component(self, client):
        """Should unregister a component."""
        # Verify it exists first
        response = client.get("/api/v1/registry/components/test_generator")
        assert response.status_code == 200

        # Unregister
        response = client.delete("/api/v1/registry/components/test_generator")
        assert response.status_code == 200
        assert "message" in response.json()

        # Verify it's gone
        response = client.get("/api/v1/registry/components/test_generator")
        assert response.status_code == 404

    def test_unregister_not_found(self, client):
        """Should return 404 for unknown component."""
        response = client.delete("/api/v1/registry/components/nonexistent")
        assert response.status_code == 404


# =============================================================================
# Health Check Tests
# =============================================================================

class TestHealthCheck:
    """Tests for GET /health"""

    def test_health_check(self, client):
        """Should return healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "version" in data
