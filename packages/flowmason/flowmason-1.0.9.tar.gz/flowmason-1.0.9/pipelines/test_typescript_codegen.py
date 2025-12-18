#!/usr/bin/env python3
"""Test TypeScript/Node.js code generation."""

import sys
sys.path.insert(0, "core")
sys.path.insert(0, "studio")
sys.path.insert(0, "lab")

from flowmason_studio.models.codegen import CodeGenOptions, TargetPlatform, TargetLanguage, OutputFormat
from flowmason_studio.services.codegen_typescript import get_typescript_code_generator


def test_typescript_codegen():
    """Test TypeScript/Node.js code generation."""
    print("Testing TypeScript/Node.js Code Generation...")

    generator = get_typescript_code_generator()

    # Test pipeline
    pipeline = {
        "id": "typescript-test",
        "name": "TypeScript AI Pipeline",
        "description": "A pipeline for testing TypeScript code generation",
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
        language=TargetLanguage.TYPESCRIPT,
        platform=TargetPlatform.STANDALONE,
        output_format=OutputFormat.PACKAGE,
    )
    result = generator.generate(pipeline, options)
    file_paths = [f.path for f in result.files]

    if "src/index.ts" in file_paths and "src/pipeline.ts" in file_paths and "package.json" in file_paths:
        print(f"  ✓ Package structure: src/index.ts, src/pipeline.ts, package.json")
        tests_passed += 1
    else:
        print(f"  ✗ Missing package files: {file_paths}")

    # Test 2: TypeScript types file generated
    tests_total += 1
    types_file = next((f for f in result.files if f.path == "src/types.ts"), None)
    if types_file and "StageInput" in types_file.content and "StageOutput" in types_file.content:
        print(f"  ✓ Types file: StageInput and StageOutput defined")
        tests_passed += 1
    else:
        print(f"  ✗ Missing type definitions")

    # Test 3: tsconfig.json present
    tests_total += 1
    tsconfig = next((f for f in result.files if f.path == "tsconfig.json"), None)
    if tsconfig and '"compilerOptions"' in tsconfig.content:
        print(f"  ✓ TypeScript config: tsconfig.json present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing tsconfig.json")

    # Test 4: Stage functions generated
    tests_total += 1
    stages_file = next((f for f in result.files if f.path == "src/stages.ts"), None)
    if stages_file and "executeGenerate" in stages_file.content:
        print(f"  ✓ Stage functions: executeGenerate present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing stage functions")

    # Test 5: OpenAI integration in generator
    tests_total += 1
    if stages_file and "new OpenAI" in stages_file.content:
        print(f"  ✓ OpenAI integration: OpenAI client present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing OpenAI integration")

    # Test 6: AWS Lambda files
    tests_total += 1
    lambda_options = CodeGenOptions(
        language=TargetLanguage.TYPESCRIPT,
        platform=TargetPlatform.AWS_LAMBDA,
        output_format=OutputFormat.PACKAGE,
    )
    lambda_result = generator.generate(pipeline, lambda_options)
    lambda_paths = [f.path for f in lambda_result.files]

    if "src/handler.ts" in lambda_paths and "template.yaml" in lambda_paths:
        print(f"  ✓ AWS Lambda: handler.ts and template.yaml present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Lambda files: {lambda_paths}")

    # Test 7: Cloudflare Workers files
    tests_total += 1
    workers_options = CodeGenOptions(
        language=TargetLanguage.TYPESCRIPT,
        platform=TargetPlatform.CLOUDFLARE_WORKERS,
        output_format=OutputFormat.PACKAGE,
    )
    workers_result = generator.generate(pipeline, workers_options)
    workers_paths = [f.path for f in workers_result.files]

    if "src/worker.ts" in workers_paths and "wrangler.toml" in workers_paths:
        print(f"  ✓ Cloudflare Workers: worker.ts and wrangler.toml present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Workers files: {workers_paths}")

    # Test 8: Firebase Functions files
    tests_total += 1
    firebase_options = CodeGenOptions(
        language=TargetLanguage.TYPESCRIPT,
        platform=TargetPlatform.FIREBASE_FUNCTIONS,
        output_format=OutputFormat.PACKAGE,
    )
    firebase_result = generator.generate(pipeline, firebase_options)
    firebase_paths = [f.path for f in firebase_result.files]

    if "src/functions.ts" in firebase_paths and "firebase.json" in firebase_paths:
        print(f"  ✓ Firebase Functions: functions.ts and firebase.json present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Firebase files: {firebase_paths}")

    # Test 9: Single file output
    tests_total += 1
    single_options = CodeGenOptions(
        language=TargetLanguage.TYPESCRIPT,
        platform=TargetPlatform.STANDALONE,
        output_format=OutputFormat.SINGLE_FILE,
    )
    single_result = generator.generate(pipeline, single_options)
    single_paths = [f.path for f in single_result.files]

    main_file = next((f for f in single_result.files if f.path.endswith(".ts") and "package" not in f.path), None)
    if main_file and "class Pipeline" in main_file.content:
        print(f"  ✓ Single file: Pipeline class in single file")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Pipeline class in single file")

    # Test 10: HTTP request component
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
    http_stages = next((f for f in http_result.files if f.path == "src/stages.ts"), None)
    if http_stages and "fetch(url" in http_stages.content:
        print(f"  ✓ HTTP component: fetch() call present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing fetch() in HTTP component")

    # Test 11: Filter component
    tests_total += 1
    filter_pipeline = {
        "id": "filter-test",
        "name": "Filter Test",
        "stages": [
            {
                "id": "filter",
                "name": "Filter Items",
                "component_type": "filter",
                "config": {"condition": "score > 0.5 and active"},
            },
        ],
    }
    filter_result = generator.generate(filter_pipeline, options)
    filter_stages = next((f for f in filter_result.files if f.path == "src/stages.ts"), None)
    if filter_stages and "&&" in filter_stages.content:  # Python 'and' converted to JS '&&'
        print(f"  ✓ Filter component: condition converted to JS")
        tests_passed += 1
    else:
        print(f"  ✗ Filter condition not converted")

    # Test 12: Deployment config
    tests_total += 1
    if lambda_result.deployment_config and lambda_result.deployment_config.get("platform") == "aws_lambda":
        print(f"  ✓ Deployment config: aws_lambda platform")
        tests_passed += 1
    else:
        print(f"  ✗ Missing deployment config")

    print(f"\nResults: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("\n✅ TypeScript/Node.js code generation working!")
        return 0
    else:
        print(f"\n❌ {tests_total - tests_passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(test_typescript_codegen())
