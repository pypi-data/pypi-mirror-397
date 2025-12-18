"""
Tests for Pipeline API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from flowmason_core.registry import ComponentRegistry

from flowmason_studio.api.app import create_app
from flowmason_studio.api.routes.registry import set_registry
from flowmason_studio.services.storage import (
    PipelineStorage,
    set_pipeline_storage,
    set_run_storage,
    RunStorage,
)
from flowmason_studio.services.database import (
    setup_test_database,
    teardown_test_database,
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
def client(registry):
    """Create a test client with the app."""
    # Set up fresh in-memory database for each test
    setup_test_database()

    # Create fresh storage (uses the in-memory database)
    pipeline_storage = PipelineStorage()
    run_storage = RunStorage()

    # Set global state
    set_registry(registry)
    set_pipeline_storage(pipeline_storage)
    set_run_storage(run_storage)

    # Create app
    app = create_app(component_registry=registry)

    # Re-set storage since create_app's lifespan may override
    set_pipeline_storage(pipeline_storage)
    set_run_storage(run_storage)

    yield TestClient(app)

    # Cleanup
    teardown_test_database()


# =============================================================================
# Pipeline CRUD Tests
# =============================================================================

class TestPipelineCreate:
    """Tests for POST /api/v1/pipelines"""

    def test_create_simple_pipeline(self, client):
        """Should create a pipeline with a single stage."""
        response = client.post("/api/v1/pipelines", json={
            "name": "Test Pipeline",
            "description": "A test pipeline",
            "stages": [
                {
                    "id": "gen_stage",
                    "component_type": "test_generator",
                    "input_mapping": {"prompt": "{{input.text}}"},
                }
            ],
            "output_stage_id": "gen_stage",
        })

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "Test Pipeline"
        assert data["description"] == "A test pipeline"
        assert len(data["stages"]) == 1
        assert data["stages"][0]["id"] == "gen_stage"
        assert data["output_stage_id"] == "gen_stage"
        assert data["id"].startswith("pipe_")
        assert data["version"] == "1.0.0"

    def test_create_multi_stage_pipeline(self, client):
        """Should create a pipeline with multiple stages."""
        response = client.post("/api/v1/pipelines", json={
            "name": "Multi-Stage Pipeline",
            "stages": [
                {
                    "id": "gen_stage",
                    "component_type": "test_generator",
                    "input_mapping": {"prompt": "{{input.text}}"},
                },
                {
                    "id": "transform_stage",
                    "component_type": "test_transform",
                    "input_mapping": {"data": "{{stages.gen_stage.content}}", "uppercase": True},
                    "depends_on": ["gen_stage"],
                }
            ],
            "output_stage_id": "transform_stage",
        })

        assert response.status_code == 201
        data = response.json()

        assert len(data["stages"]) == 2
        assert data["stages"][1]["depends_on"] == ["gen_stage"]

    def test_create_pipeline_unknown_component(self, client):
        """Should reject pipeline with unknown component type."""
        response = client.post("/api/v1/pipelines", json={
            "name": "Bad Pipeline",
            "stages": [
                {
                    "id": "bad_stage",
                    "component_type": "nonexistent_component",
                    "input_mapping": {},
                }
            ],
        })

        assert response.status_code == 400
        assert "Unknown component type" in response.json()["detail"]

    def test_create_pipeline_invalid_dependency(self, client):
        """Should reject pipeline with invalid stage dependency."""
        response = client.post("/api/v1/pipelines", json={
            "name": "Bad Pipeline",
            "stages": [
                {
                    "id": "stage1",
                    "component_type": "test_generator",
                    "input_mapping": {"prompt": "test"},
                    "depends_on": ["nonexistent_stage"],
                }
            ],
        })

        assert response.status_code == 400
        assert "depends on unknown stage" in response.json()["detail"]

    def test_create_pipeline_invalid_output_stage(self, client):
        """Should reject pipeline with invalid output_stage_id."""
        response = client.post("/api/v1/pipelines", json={
            "name": "Bad Pipeline",
            "stages": [
                {
                    "id": "stage1",
                    "component_type": "test_generator",
                    "input_mapping": {"prompt": "test"},
                }
            ],
            "output_stage_id": "nonexistent",
        })

        assert response.status_code == 400
        assert "output_stage_id" in response.json()["detail"]

    def test_create_pipeline_duplicate_stage_ids(self, client):
        """Should reject pipeline with duplicate stage IDs."""
        response = client.post("/api/v1/pipelines", json={
            "name": "Bad Pipeline",
            "stages": [
                {"id": "dupe", "component_type": "test_generator", "input_mapping": {"prompt": "a"}},
                {"id": "dupe", "component_type": "test_generator", "input_mapping": {"prompt": "b"}},
            ],
        })

        assert response.status_code == 400
        assert "Duplicate" in response.json()["detail"]


class TestPipelineGet:
    """Tests for GET /api/v1/pipelines/{id}"""

    def test_get_pipeline(self, client):
        """Should get a pipeline by ID."""
        # Create first
        create_resp = client.post("/api/v1/pipelines", json={
            "name": "Test Pipeline",
            "stages": [
                {"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "test"}}
            ],
        })
        pipeline_id = create_resp.json()["id"]

        # Get
        response = client.get(f"/api/v1/pipelines/{pipeline_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pipeline_id
        assert data["name"] == "Test Pipeline"

    def test_get_pipeline_not_found(self, client):
        """Should return 404 for unknown pipeline."""
        response = client.get("/api/v1/pipelines/pipe_nonexistent")

        assert response.status_code == 404


class TestPipelineList:
    """Tests for GET /api/v1/pipelines"""

    def test_list_empty(self, client):
        """Should return empty list when no pipelines."""
        response = client.get("/api/v1/pipelines")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_pipelines(self, client):
        """Should list all pipelines."""
        # Create some pipelines
        for i in range(3):
            client.post("/api/v1/pipelines", json={
                "name": f"Pipeline {i}",
                "stages": [
                    {"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "test"}}
                ],
            })

        response = client.get("/api/v1/pipelines")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_list_with_category_filter(self, client):
        """Should filter pipelines by category."""
        # Create pipelines with different categories
        client.post("/api/v1/pipelines", json={
            "name": "Pipeline A",
            "category": "nlp",
            "stages": [{"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "a"}}],
        })
        client.post("/api/v1/pipelines", json={
            "name": "Pipeline B",
            "category": "vision",
            "stages": [{"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "b"}}],
        })

        response = client.get("/api/v1/pipelines?category=nlp")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Pipeline A"

    def test_list_with_pagination(self, client):
        """Should paginate results."""
        # Create 5 pipelines
        for i in range(5):
            client.post("/api/v1/pipelines", json={
                "name": f"Pipeline {i}",
                "stages": [{"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "test"}}],
            })

        # Get first page
        response = client.get("/api/v1/pipelines?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

        # Get second page
        response = client.get("/api/v1/pipelines?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5


class TestPipelineUpdate:
    """Tests for PUT /api/v1/pipelines/{id}"""

    def test_update_pipeline_name(self, client):
        """Should update pipeline name."""
        # Create
        create_resp = client.post("/api/v1/pipelines", json={
            "name": "Original Name",
            "stages": [{"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "test"}}],
        })
        pipeline_id = create_resp.json()["id"]

        # Update
        response = client.put(f"/api/v1/pipelines/{pipeline_id}", json={
            "name": "New Name",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["version"] == "1.0.1"  # Version incremented

    def test_update_pipeline_stages(self, client):
        """Should update pipeline stages."""
        # Create
        create_resp = client.post("/api/v1/pipelines", json={
            "name": "Test Pipeline",
            "stages": [{"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "test"}}],
        })
        pipeline_id = create_resp.json()["id"]

        # Update stages
        response = client.put(f"/api/v1/pipelines/{pipeline_id}", json={
            "stages": [
                {"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "new"}},
                {"id": "s2", "component_type": "test_transform", "input_mapping": {"data": "{{stages.s1.content}}"}, "depends_on": ["s1"]},
            ],
            "output_stage_id": "s2",
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data["stages"]) == 2

    def test_update_pipeline_not_found(self, client):
        """Should return 404 for unknown pipeline."""
        response = client.put("/api/v1/pipelines/pipe_nonexistent", json={
            "name": "New Name",
        })

        assert response.status_code == 404


class TestPipelineDelete:
    """Tests for DELETE /api/v1/pipelines/{id}"""

    def test_delete_pipeline(self, client):
        """Should delete a pipeline."""
        # Create
        create_resp = client.post("/api/v1/pipelines", json={
            "name": "To Delete",
            "stages": [{"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "test"}}],
        })
        pipeline_id = create_resp.json()["id"]

        # Delete
        response = client.delete(f"/api/v1/pipelines/{pipeline_id}")
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/v1/pipelines/{pipeline_id}")
        assert response.status_code == 404

    def test_delete_pipeline_not_found(self, client):
        """Should return 404 for unknown pipeline."""
        response = client.delete("/api/v1/pipelines/pipe_nonexistent")
        assert response.status_code == 404


class TestPipelineClone:
    """Tests for POST /api/v1/pipelines/{id}/clone"""

    def test_clone_pipeline(self, client):
        """Should clone a pipeline."""
        # Create original
        create_resp = client.post("/api/v1/pipelines", json={
            "name": "Original",
            "description": "Original description",
            "stages": [{"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "test"}}],
            "tags": ["test"],
        })
        original_id = create_resp.json()["id"]

        # Clone
        response = client.post(f"/api/v1/pipelines/{original_id}/clone")

        assert response.status_code == 201
        data = response.json()
        assert data["id"] != original_id
        assert data["name"] == "Original (Copy)"
        assert data["description"] == "Original description"
        assert len(data["stages"]) == 1
        assert data["tags"] == ["test"]

    def test_clone_with_new_name(self, client):
        """Should clone with custom name."""
        # Create original
        create_resp = client.post("/api/v1/pipelines", json={
            "name": "Original",
            "stages": [{"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "test"}}],
        })
        original_id = create_resp.json()["id"]

        # Clone with new name
        response = client.post(f"/api/v1/pipelines/{original_id}/clone?new_name=Custom Clone")

        assert response.status_code == 201
        assert response.json()["name"] == "Custom Clone"

    def test_clone_not_found(self, client):
        """Should return 404 for unknown pipeline."""
        response = client.post("/api/v1/pipelines/pipe_nonexistent/clone")
        assert response.status_code == 404


class TestPipelineValidate:
    """Tests for POST /api/v1/pipelines/{id}/validate"""

    def test_validate_valid_pipeline(self, client):
        """Should validate a valid pipeline."""
        # Create
        create_resp = client.post("/api/v1/pipelines", json={
            "name": "Valid Pipeline",
            "stages": [
                {"id": "s1", "component_type": "test_generator", "input_mapping": {"prompt": "test"}},
            ],
            "output_stage_id": "s1",
        })
        pipeline_id = create_resp.json()["id"]

        # Validate
        response = client.post(f"/api/v1/pipelines/{pipeline_id}/validate")

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["errors"] == []

    def test_validate_not_found(self, client):
        """Should return 404 for unknown pipeline."""
        response = client.post("/api/v1/pipelines/pipe_nonexistent/validate")
        assert response.status_code == 404
