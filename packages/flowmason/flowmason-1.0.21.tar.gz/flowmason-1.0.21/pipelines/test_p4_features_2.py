#!/usr/bin/env python3
"""
Test script for P4 features (Part 2):
- Visual Pipeline Diff & Merge
- Kubernetes Operator for Pipeline CRDs
"""

import sys
sys.path.insert(0, "core")
sys.path.insert(0, "studio")
sys.path.insert(0, "lab")

from flowmason_studio.models.diff import (
    ChangeType,
    ConflictResolution,
    DiffPipelinesRequest,
    MergePipelinesRequest,
    PipelineDiff,
)
from flowmason_studio.services.diff_service import get_diff_service
from flowmason_studio.models.kubernetes import (
    FlowMasonPipeline,
    FlowMasonPipelineRun,
    ScheduleSpec,
    ScheduleType,
    ResourceSpec,
    CRDGenerationOptions,
)
from flowmason_studio.services.kubernetes_service import get_kubernetes_service


def test_diff_service():
    """Test pipeline diff service."""
    print("\n[1/2] Testing Visual Pipeline Diff & Merge...")

    diff_service = get_diff_service()
    tests_passed = 0
    tests_total = 0

    # Test basic diff
    tests_total += 1
    base_pipeline = {
        "id": "pipe-1",
        "name": "Test Pipeline",
        "description": "Original description",
        "stages": [
            {"id": "stage1", "name": "Stage 1", "component_type": "generator", "config": {"model": "gpt-4"}},
            {"id": "stage2", "name": "Stage 2", "component_type": "filter", "depends_on": ["stage1"]},
        ],
        "variables": {"input": "test"},
        "settings": {"timeout": 300},
    }

    compare_pipeline = {
        "id": "pipe-1",
        "name": "Test Pipeline Updated",  # Changed
        "description": "Original description",
        "stages": [
            {"id": "stage1", "name": "Stage 1", "component_type": "generator", "config": {"model": "gpt-4-turbo"}},  # Modified
            # stage2 removed
            {"id": "stage3", "name": "Stage 3", "component_type": "logger", "depends_on": ["stage1"]},  # Added
        ],
        "variables": {"input": "test", "output": "result"},  # Added variable
        "settings": {"timeout": 600},  # Modified
    }

    diff = diff_service.compute_diff(base_pipeline, compare_pipeline)

    if diff.has_changes and diff.total_changes > 0:
        print(f"  ✓ Basic diff: {diff.total_changes} changes detected")
        tests_passed += 1
    else:
        print(f"  ✗ Basic diff failed")

    # Test stage changes detection
    tests_total += 1
    added = [c for c in diff.stage_changes if c.change_type == ChangeType.ADDED]
    removed = [c for c in diff.stage_changes if c.change_type == ChangeType.REMOVED]
    modified = [c for c in diff.stage_changes if c.change_type == ChangeType.MODIFIED]

    if len(added) == 1 and len(removed) == 1 and len(modified) == 1:
        print(f"  ✓ Stage changes: +1 added, -1 removed, ~1 modified")
        tests_passed += 1
    else:
        print(f"  ✗ Stage changes: expected 1/1/1, got {len(added)}/{len(removed)}/{len(modified)}")

    # Test variable changes
    tests_total += 1
    var_added = [c for c in diff.variable_changes if c.change_type == ChangeType.ADDED]
    if len(var_added) == 1 and var_added[0].variable_name == "output":
        print(f"  ✓ Variable changes: output added")
        tests_passed += 1
    else:
        print(f"  ✗ Variable changes detection failed")

    # Test visual diff generation
    tests_total += 1
    visual = diff_service.generate_visual_diff(diff)
    if "summary" in visual and "sections" in visual:
        print(f"  ✓ Visual diff: {len(visual['sections'])} sections")
        tests_passed += 1
    else:
        print(f"  ✗ Visual diff generation failed")

    # Test three-way merge
    tests_total += 1
    base = {
        "id": "merge-test",
        "name": "Merge Test",
        "stages": [
            {"id": "s1", "name": "S1", "component_type": "generator", "config": {"model": "gpt-4"}},
        ],
        "variables": {"x": 1},
        "settings": {},
    }

    ours = {
        "id": "merge-test",
        "name": "Merge Test - Ours",  # We changed name
        "stages": [
            {"id": "s1", "name": "S1", "component_type": "generator", "config": {"model": "gpt-4"}},
            {"id": "s2", "name": "S2", "component_type": "logger"},  # We added stage
        ],
        "variables": {"x": 5, "y": 2},  # We changed x to 5 and added y
        "settings": {},
    }

    theirs = {
        "id": "merge-test",
        "name": "Merge Test",  # They didn't change name
        "stages": [
            {"id": "s1", "name": "S1", "component_type": "generator", "config": {"model": "gpt-4-turbo"}},  # They changed config
        ],
        "variables": {"x": 10},  # They changed x to 10
        "settings": {"timeout": 100},  # They added setting
    }

    merge_result = diff_service.three_way_merge(base, ours, theirs)

    # Should have conflict on variable x (both modified differently)
    if merge_result.has_conflicts:
        print(f"  ✓ Three-way merge: {len(merge_result.conflicts)} conflicts detected")
        tests_passed += 1
    else:
        print(f"  ✗ Three-way merge should detect conflicts")

    # Test merge with resolution
    tests_total += 1
    resolutions = {c.id: ConflictResolution.USE_OURS for c in merge_result.conflicts}
    resolved_result = diff_service.three_way_merge(base, ours, theirs, resolutions=resolutions)

    if resolved_result.success and resolved_result.merged_pipeline:
        merged = resolved_result.merged_pipeline
        # Should have: ours name, both our and their stages, both variables with ours value
        print(f"  ✓ Merge with resolution: success, {len(merged.get('stages', []))} stages")
        tests_passed += 1
    else:
        print(f"  ✗ Merge with resolution failed")

    # Test apply diff
    tests_total += 1
    applied = diff_service.apply_diff(base_pipeline, diff)
    if applied.get("name") == "Test Pipeline Updated":
        print(f"  ✓ Apply diff: name updated correctly")
        tests_passed += 1
    else:
        print(f"  ✗ Apply diff failed")

    return tests_passed, tests_total


def test_kubernetes_service():
    """Test Kubernetes CRD generation."""
    print("\n[2/2] Testing Kubernetes Operator for Pipeline CRDs...")

    k8s_service = get_kubernetes_service()
    tests_passed = 0
    tests_total = 0

    # Test pipeline to CRD conversion
    tests_total += 1
    pipeline = {
        "id": "test-pipeline",
        "name": "Test AI Pipeline",
        "description": "A test pipeline for Kubernetes",
        "stages": [
            {
                "id": "generate",
                "name": "Generate",
                "component_type": "generator",
                "config": {"model": "gpt-4", "prompt": "Hello"},
                "depends_on": [],
            },
            {
                "id": "filter",
                "name": "Filter",
                "component_type": "filter",
                "config": {"condition": "len(input) > 0"},
                "depends_on": ["generate"],
            },
        ],
        "variables": {"api_key": "{{secrets.openai_key}}"},
        "settings": {"timeout": 300, "parallelism": 2},
        "providers": {
            "openai": {"type": "openai", "model": "gpt-4"},
        },
    }

    crd = k8s_service.pipeline_to_crd(
        pipeline=pipeline,
        name="test-ai-pipeline",
        namespace="default",
        labels={"env": "test"},
    )

    if crd.metadata.name == "test-ai-pipeline" and len(crd.spec.stages) == 2:
        print(f"  ✓ Pipeline to CRD: {crd.metadata.name} with {len(crd.spec.stages)} stages")
        tests_passed += 1
    else:
        print(f"  ✗ Pipeline to CRD conversion failed")

    # Test YAML generation
    tests_total += 1
    yaml_content = k8s_service.crd_to_yaml(crd)
    if "apiVersion: flowmason.io/v1alpha1" in yaml_content and "kind: Pipeline" in yaml_content:
        print(f"  ✓ YAML generation: {len(yaml_content)} chars")
        tests_passed += 1
    else:
        print(f"  ✗ YAML generation failed")

    # Test with schedule
    tests_total += 1
    schedule = ScheduleSpec(
        type=ScheduleType.CRON,
        cron="0 * * * *",
        timezone="UTC",
    )

    scheduled_crd = k8s_service.pipeline_to_crd(
        pipeline=pipeline,
        name="scheduled-pipeline",
        namespace="production",
        schedule=schedule,
    )

    if scheduled_crd.spec.schedule and scheduled_crd.spec.schedule.cron == "0 * * * *":
        print(f"  ✓ Scheduled CRD: cron={scheduled_crd.spec.schedule.cron}")
        tests_passed += 1
    else:
        print(f"  ✗ Scheduled CRD failed")

    # Test resource requirements
    tests_total += 1
    resources = ResourceSpec(
        requests={"cpu": "100m", "memory": "128Mi"},
        limits={"cpu": "500m", "memory": "512Mi"},
    )

    resourced_crd = k8s_service.pipeline_to_crd(
        pipeline=pipeline,
        name="resourced-pipeline",
        namespace="default",
        resources=resources,
    )

    if resourced_crd.spec.resources and resourced_crd.spec.resources.requests.get("cpu") == "100m":
        print(f"  ✓ Resource CRD: cpu={resourced_crd.spec.resources.requests.get('cpu')}")
        tests_passed += 1
    else:
        print(f"  ✗ Resource CRD failed")

    # Test PipelineRun creation
    tests_total += 1
    run = k8s_service.create_pipeline_run(
        pipeline_name="test-ai-pipeline",
        namespace="default",
        inputs={"prompt": "Hello World"},
    )

    if run.spec.pipelineRef == "test-ai-pipeline" and run.spec.inputs.get("prompt") == "Hello World":
        print(f"  ✓ PipelineRun: {run.metadata.name}")
        tests_passed += 1
    else:
        print(f"  ✗ PipelineRun creation failed")

    # Test operator manifests generation
    tests_total += 1
    manifests = k8s_service.generate_operator_manifests()
    expected_files = ["crds.yaml", "rbac.yaml", "operator.yaml", "configmap.yaml"]
    if all(f in manifests for f in expected_files):
        print(f"  ✓ Operator manifests: {list(manifests.keys())}")
        tests_passed += 1
    else:
        print(f"  ✗ Operator manifests missing files")

    # Test CRD definitions content
    tests_total += 1
    crds_yaml = manifests["crds.yaml"]
    if "pipelines.flowmason.io" in crds_yaml and "pipelineruns.flowmason.io" in crds_yaml:
        print(f"  ✓ CRD definitions: Pipeline and PipelineRun")
        tests_passed += 1
    else:
        print(f"  ✗ CRD definitions incomplete")

    # Test name sanitization
    tests_total += 1
    sanitized = k8s_service._sanitize_name("My Test Pipeline!!!")
    if sanitized == "my-test-pipeline" and sanitized.islower():
        print(f"  ✓ Name sanitization: '{sanitized}'")
        tests_passed += 1
    else:
        print(f"  ✗ Name sanitization failed: '{sanitized}'")

    # Test list pipelines
    tests_total += 1
    pipelines = k8s_service.list_pipelines()
    if len(pipelines) >= 1:
        print(f"  ✓ List pipelines: {len(pipelines)} stored")
        tests_passed += 1
    else:
        print(f"  ✗ List pipelines failed")

    return tests_passed, tests_total


def main():
    print("=" * 60)
    print("P4 FEATURE TESTS - Part 2")
    print("=" * 60)

    total_passed = 0
    total_tests = 0

    # Test Diff & Merge
    passed, total = test_diff_service()
    total_passed += passed
    total_tests += total

    # Test Kubernetes
    passed, total = test_kubernetes_service()
    total_passed += passed
    total_tests += total

    print("\n" + "=" * 60)
    print(f"RESULTS: {total_passed}/{total_tests} tests passed")
    print("=" * 60)

    if total_passed == total_tests:
        print("\n✅ ALL P4 FEATURES (Part 2) WORKING!")
        return 0
    else:
        print(f"\n❌ {total_tests - total_passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
