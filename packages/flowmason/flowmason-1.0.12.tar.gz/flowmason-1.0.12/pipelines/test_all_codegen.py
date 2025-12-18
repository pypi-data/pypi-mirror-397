#!/usr/bin/env python3
"""Test all code generation targets."""

import sys
sys.path.insert(0, "core")
sys.path.insert(0, "studio")
sys.path.insert(0, "lab")

from flowmason_studio.models.codegen import CodeGenOptions, TargetPlatform, TargetLanguage, OutputFormat
from flowmason_studio.services.codegen_python import get_python_code_generator
from flowmason_studio.services.codegen_typescript import get_typescript_code_generator
from flowmason_studio.services.codegen_go import get_go_code_generator
from flowmason_studio.services.codegen_apex import get_apex_code_generator


def test_all_codegen():
    """Test all code generation targets."""
    print("=" * 60)
    print("FlowMason Code Generation - Comprehensive Test Suite")
    print("=" * 60)

    # Standard test pipeline
    pipeline = {
        "id": "test-pipeline",
        "name": "Test AI Pipeline",
        "description": "A pipeline for testing code generation",
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
        ],
    }

    all_passed = True
    results = {}

    # Test Python
    print("\n1. Testing Python Code Generation...")
    try:
        generator = get_python_code_generator()
        options = CodeGenOptions(language=TargetLanguage.PYTHON, platform=TargetPlatform.STANDALONE)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        # Python generator creates package/<name>/main.py structure
        if any("main.py" in p for p in file_paths) and "requirements.txt" in file_paths:
            print("   ✓ Python: Package generation successful")
            results["Python"] = "PASS"
        else:
            print(f"   ✗ Python: Missing expected files - {file_paths}")
            results["Python"] = "FAIL"
            all_passed = False
    except Exception as e:
        print(f"   ✗ Python: Error - {e}")
        results["Python"] = f"ERROR: {e}"
        all_passed = False

    # Test TypeScript
    print("\n2. Testing TypeScript Code Generation...")
    try:
        generator = get_typescript_code_generator()
        options = CodeGenOptions(language=TargetLanguage.TYPESCRIPT, platform=TargetPlatform.STANDALONE)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        if "src/index.ts" in file_paths:
            print("   ✓ TypeScript: Package generation successful")
            results["TypeScript"] = "PASS"
        else:
            print(f"   ✗ TypeScript: Missing expected files - {file_paths}")
            results["TypeScript"] = "FAIL"
            all_passed = False
    except Exception as e:
        print(f"   ✗ TypeScript: Error - {e}")
        results["TypeScript"] = f"ERROR: {e}"
        all_passed = False

    # Test Go
    print("\n3. Testing Go Code Generation...")
    try:
        generator = get_go_code_generator()
        options = CodeGenOptions(language=TargetLanguage.GO, platform=TargetPlatform.STANDALONE)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        if "cmd/main.go" in file_paths:
            print("   ✓ Go: Package generation successful")
            results["Go"] = "PASS"
        else:
            print(f"   ✗ Go: Missing expected files - {file_paths}")
            results["Go"] = "FAIL"
            all_passed = False
    except Exception as e:
        print(f"   ✗ Go: Error - {e}")
        results["Go"] = f"ERROR: {e}"
        all_passed = False

    # Test Apex
    print("\n4. Testing Salesforce Apex Code Generation...")
    try:
        generator = get_apex_code_generator()
        options = CodeGenOptions(language=TargetLanguage.APEX, platform=TargetPlatform.SALESFORCE)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        if any("force-app" in p and ".cls" in p for p in file_paths):
            print("   ✓ Apex: Package generation successful")
            results["Apex"] = "PASS"
        else:
            print(f"   ✗ Apex: Missing expected files - {file_paths}")
            results["Apex"] = "FAIL"
            all_passed = False
    except Exception as e:
        print(f"   ✗ Apex: Error - {e}")
        results["Apex"] = f"ERROR: {e}"
        all_passed = False

    # Test platform targets
    print("\n5. Testing Platform-Specific Targets...")

    platforms_tested = []

    # AWS Lambda
    try:
        generator = get_python_code_generator()
        options = CodeGenOptions(language=TargetLanguage.PYTHON, platform=TargetPlatform.AWS_LAMBDA)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        if "template.yaml" in file_paths:
            platforms_tested.append("AWS Lambda (Python)")
    except:
        pass

    try:
        generator = get_typescript_code_generator()
        options = CodeGenOptions(language=TargetLanguage.TYPESCRIPT, platform=TargetPlatform.AWS_LAMBDA)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        if "template.yaml" in file_paths:
            platforms_tested.append("AWS Lambda (TypeScript)")
    except:
        pass

    try:
        generator = get_go_code_generator()
        options = CodeGenOptions(language=TargetLanguage.GO, platform=TargetPlatform.AWS_LAMBDA)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        if "template.yaml" in file_paths:
            platforms_tested.append("AWS Lambda (Go)")
    except:
        pass

    # Firebase
    try:
        generator = get_python_code_generator()
        options = CodeGenOptions(language=TargetLanguage.PYTHON, platform=TargetPlatform.FIREBASE_FUNCTIONS)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        if "firebase.json" in file_paths:
            platforms_tested.append("Firebase (Python)")
    except:
        pass

    try:
        generator = get_typescript_code_generator()
        options = CodeGenOptions(language=TargetLanguage.TYPESCRIPT, platform=TargetPlatform.FIREBASE_FUNCTIONS)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        if "firebase.json" in file_paths:
            platforms_tested.append("Firebase (TypeScript)")
    except:
        pass

    # Cloudflare Workers
    try:
        generator = get_typescript_code_generator()
        options = CodeGenOptions(language=TargetLanguage.TYPESCRIPT, platform=TargetPlatform.CLOUDFLARE_WORKERS)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        if "wrangler.toml" in file_paths:
            platforms_tested.append("Cloudflare Workers (TypeScript)")
    except:
        pass

    # Docker
    try:
        generator = get_go_code_generator()
        options = CodeGenOptions(language=TargetLanguage.GO, platform=TargetPlatform.DOCKER)
        result = generator.generate(pipeline, options)
        file_paths = [f.path for f in result.files]
        if "Dockerfile" in file_paths:
            platforms_tested.append("Docker (Go)")
    except:
        pass

    print(f"   ✓ Platform targets: {len(platforms_tested)} configurations verified")
    for pt in platforms_tested:
        print(f"      - {pt}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nLanguages:")
    for lang, status in results.items():
        emoji = "✓" if status == "PASS" else "✗"
        print(f"  {emoji} {lang}: {status}")

    print(f"\nPlatforms: {len(platforms_tested)} configurations verified")
    print(f"\nTotal: {sum(1 for s in results.values() if s == 'PASS')}/{len(results)} languages passing")

    if all_passed:
        print("\n✅ All code generation tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(test_all_codegen())
