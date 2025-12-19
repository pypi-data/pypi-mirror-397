#!/usr/bin/env python3
"""Test Firebase Functions code generation."""

import sys
sys.path.insert(0, "core")
sys.path.insert(0, "studio")
sys.path.insert(0, "lab")

from flowmason_studio.models.codegen import CodeGenOptions, TargetPlatform, OutputFormat
from flowmason_studio.services.codegen_python import get_python_code_generator


def test_firebase_codegen():
    """Test Firebase Functions code generation."""
    print("Testing Firebase Functions Code Generation...")

    generator = get_python_code_generator()

    # Test pipeline
    pipeline = {
        "id": "firebase-test",
        "name": "Firebase AI Pipeline",
        "description": "A pipeline deployed to Firebase Functions",
        "stages": [
            {
                "id": "generate",
                "name": "Generate Response",
                "component_type": "generator",
                "config": {"model": "gpt-4", "prompt": "{input}"},
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

    # Generate for Firebase
    options = CodeGenOptions(
        platform=TargetPlatform.FIREBASE_FUNCTIONS,
        output_format=OutputFormat.PACKAGE,
    )

    result = generator.generate(pipeline, options)

    # Check results
    tests_passed = 0
    tests_total = 0

    # Test 1: Firebase-specific files generated
    tests_total += 1
    file_paths = [f.path for f in result.files]
    if "main.py" in file_paths and "firebase.json" in file_paths and ".firebaserc" in file_paths:
        print(f"  ✓ Firebase files: main.py, firebase.json, .firebaserc")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Firebase files: {file_paths}")

    # Test 2: main.py contains Firebase function decorators
    tests_total += 1
    main_file = next((f for f in result.files if f.path == "main.py"), None)
    if main_file and "@https_fn.on_request()" in main_file.content:
        print(f"  ✓ Firebase decorators: @https_fn.on_request() present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Firebase decorators")

    # Test 3: Callable function generated
    tests_total += 1
    if main_file and "@https_fn.on_call()" in main_file.content:
        print(f"  ✓ Callable function: @https_fn.on_call() present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing callable function")

    # Test 4: firebase.json configuration
    tests_total += 1
    firebase_config = next((f for f in result.files if f.path == "firebase.json"), None)
    if firebase_config and '"runtime": "python311"' in firebase_config.content:
        print(f"  ✓ Firebase config: Python 3.11 runtime configured")
        tests_passed += 1
    else:
        print(f"  ✗ Invalid firebase.json")

    # Test 5: Requirements include firebase packages
    tests_total += 1
    requirements = next((f for f in result.files if f.path == "requirements.txt"), None)
    if requirements and "firebase-functions" in requirements.content and "firebase-admin" in requirements.content:
        print(f"  ✓ Requirements: firebase-functions and firebase-admin included")
        tests_passed += 1
    else:
        print(f"  ✗ Missing Firebase packages in requirements")

    # Test 6: Deployment config
    tests_total += 1
    if result.deployment_config and result.deployment_config.get("platform") == "firebase_functions":
        print(f"  ✓ Deployment config: firebase_functions platform")
        tests_passed += 1
    else:
        print(f"  ✗ Missing deployment config")

    # Test 7: Deploy instructions
    tests_total += 1
    if result.deploy_instructions and "firebase deploy" in result.deploy_instructions:
        print(f"  ✓ Deploy instructions: includes firebase deploy command")
        tests_passed += 1
    else:
        print(f"  ✗ Missing deploy instructions")

    # Test 8: CORS handling
    tests_total += 1
    if main_file and "Access-Control-Allow-Origin" in main_file.content:
        print(f"  ✓ CORS: Access-Control-Allow-Origin headers included")
        tests_passed += 1
    else:
        print(f"  ✗ Missing CORS headers")

    print(f"\nResults: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("\n✅ Firebase Functions code generation working!")
        return 0
    else:
        print(f"\n❌ {tests_total - tests_passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(test_firebase_codegen())
