#!/usr/bin/env python3
"""Test Go code generation."""

import sys
sys.path.insert(0, "core")
sys.path.insert(0, "studio")
sys.path.insert(0, "lab")

from flowmason_studio.models.codegen import CodeGenOptions, TargetPlatform, TargetLanguage, OutputFormat
from flowmason_studio.services.codegen_go import get_go_code_generator


def test_go_codegen():
    """Test Go code generation."""
    print("Testing Go Code Generation...")

    generator = get_go_code_generator()

    # Test pipeline
    pipeline = {
        "id": "go-test",
        "name": "Go AI Pipeline",
        "description": "A pipeline for testing Go code generation",
        "stages": [
            {
                "id": "generate",
                "name": "Generate Response",
                "component_type": "generator",
                "config": {"model": "gpt-4", "prompt": "{input}", "provider": "openai"},
            },
            {
                "id": "transform",
                "name": "Transform Output",
                "component_type": "json_transform",
                "config": {"mapping": {"result": "output"}},
                "depends_on": ["generate"],
            },
            {
                "id": "log",
                "name": "Log Result",
                "component_type": "logger",
                "config": {"message": "Result: {result}", "level": "info"},
                "depends_on": ["transform"],
            },
        ],
    }

    tests_passed = 0
    tests_total = 0

    # Test 1: Package generation
    tests_total += 1
    options = CodeGenOptions(
        language=TargetLanguage.GO,
        platform=TargetPlatform.STANDALONE,
        output_format=OutputFormat.PACKAGE,
    )
    result = generator.generate(pipeline, options)
    file_paths = [f.path for f in result.files]

    if "cmd/main.go" in file_paths and "go.mod" in file_paths:
        print(f"  ✓ Package structure: cmd/main.go, go.mod present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing package files: {file_paths}")

    # Test 2: Internal package structure
    tests_total += 1
    if "internal/pipeline/pipeline.go" in file_paths and "internal/stages/stages.go" in file_paths:
        print(f"  ✓ Internal packages: pipeline.go and stages.go present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing internal packages")

    # Test 3: Types and config packages
    tests_total += 1
    if "internal/types/types.go" in file_paths and "internal/config/config.go" in file_paths:
        print(f"  ✓ Support packages: types.go and config.go present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing support packages")

    # Test 4: Makefile present
    tests_total += 1
    makefile = next((f for f in result.files if f.path == "Makefile"), None)
    if makefile and "go build" in makefile.content:
        print(f"  ✓ Makefile: build target present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Makefile")

    # Test 5: Stage functions generated
    tests_total += 1
    stages_file = next((f for f in result.files if f.path == "internal/stages/stages.go"), None)
    if stages_file and "ExecuteGenerate" in stages_file.content:
        print(f"  ✓ Stage functions: ExecuteGenerate present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing stage functions")

    # Test 6: OpenAI integration
    tests_total += 1
    if stages_file and "api.openai.com" in stages_file.content:
        print(f"  ✓ OpenAI integration: API call present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing OpenAI integration")

    # Test 7: Single file output
    tests_total += 1
    single_options = CodeGenOptions(
        language=TargetLanguage.GO,
        platform=TargetPlatform.STANDALONE,
        output_format=OutputFormat.SINGLE_FILE,
    )
    single_result = generator.generate(pipeline, single_options)
    single_paths = [f.path for f in single_result.files]

    main_file = next((f for f in single_result.files if f.path == "main.go"), None)
    if main_file and "type Pipeline struct" in main_file.content:
        print(f"  ✓ Single file: Pipeline struct in main.go")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Pipeline struct in single file")

    # Test 8: AWS Lambda files
    tests_total += 1
    lambda_options = CodeGenOptions(
        language=TargetLanguage.GO,
        platform=TargetPlatform.AWS_LAMBDA,
        output_format=OutputFormat.PACKAGE,
    )
    lambda_result = generator.generate(pipeline, lambda_options)
    lambda_paths = [f.path for f in lambda_result.files]

    if "lambda/handler.go" in lambda_paths and "template.yaml" in lambda_paths:
        print(f"  ✓ AWS Lambda: handler.go and template.yaml present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Lambda files: {lambda_paths}")

    # Test 9: Docker files
    tests_total += 1
    docker_options = CodeGenOptions(
        language=TargetLanguage.GO,
        platform=TargetPlatform.DOCKER,
        output_format=OutputFormat.PACKAGE,
    )
    docker_result = generator.generate(pipeline, docker_options)
    docker_paths = [f.path for f in docker_result.files]

    if "Dockerfile" in docker_paths and "docker-compose.yml" in docker_paths:
        print(f"  ✓ Docker: Dockerfile and docker-compose.yml present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Docker files: {docker_paths}")

    # Test 10: Dockerfile with multi-stage build
    tests_total += 1
    dockerfile = next((f for f in docker_result.files if f.path == "Dockerfile"), None)
    if dockerfile and "AS builder" in dockerfile.content and "FROM alpine" in dockerfile.content:
        print(f"  ✓ Dockerfile: Multi-stage build present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing multi-stage build in Dockerfile")

    # Test 11: HTTP request component
    tests_total += 1
    http_pipeline = {
        "id": "http-test",
        "name": "HTTP Test",
        "stages": [
            {
                "id": "fetch",
                "name": "Fetch Data",
                "component_type": "http_request",
                "config": {"method": "GET", "url": "https://api.example.com/{id}"},
            },
        ],
    }
    http_result = generator.generate(http_pipeline, options)
    http_stages = next((f for f in http_result.files if f.path == "internal/stages/stages.go"), None)
    if http_stages and "httpRequest(ctx" in http_stages.content:
        print(f"  ✓ HTTP component: httpRequest call present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing httpRequest in HTTP component")

    # Test 12: Deployment config
    tests_total += 1
    if lambda_result.deployment_config and lambda_result.deployment_config.get("platform") == "aws_lambda":
        print(f"  ✓ Deployment config: aws_lambda platform")
        tests_passed += 1
    else:
        print(f"  ✗ Missing deployment config")

    print(f"\nResults: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("\n✅ Go code generation working!")
        return 0
    else:
        print(f"\n❌ {tests_total - tests_passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(test_go_codegen())
