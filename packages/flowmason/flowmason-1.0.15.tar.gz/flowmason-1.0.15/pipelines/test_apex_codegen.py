#!/usr/bin/env python3
"""Test Salesforce Apex code generation."""

import sys
sys.path.insert(0, "core")
sys.path.insert(0, "studio")
sys.path.insert(0, "lab")

from flowmason_studio.models.codegen import CodeGenOptions, TargetPlatform, TargetLanguage, OutputFormat
from flowmason_studio.services.codegen_apex import get_apex_code_generator


def test_apex_codegen():
    """Test Salesforce Apex code generation."""
    print("Testing Salesforce Apex Code Generation...")

    generator = get_apex_code_generator()

    # Test pipeline
    pipeline = {
        "id": "apex-test",
        "name": "Apex AI Pipeline",
        "description": "A pipeline for testing Salesforce Apex code generation",
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

    # Test 1: Package generation with SFDX structure
    tests_total += 1
    options = CodeGenOptions(
        language=TargetLanguage.APEX,
        platform=TargetPlatform.SALESFORCE,
        output_format=OutputFormat.PACKAGE,
    )
    result = generator.generate(pipeline, options)
    file_paths = [f.path for f in result.files]

    if "force-app/main/default/classes/ApexAiPipeline.cls" in file_paths:
        print(f"  ✓ SFDX structure: Main class in force-app directory")
        tests_passed += 1
    else:
        print(f"  ✗ Missing SFDX structure: {file_paths}")

    # Test 2: Class metadata file
    tests_total += 1
    if "force-app/main/default/classes/ApexAiPipeline.cls-meta.xml" in file_paths:
        print(f"  ✓ Class metadata: cls-meta.xml present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing class metadata")

    # Test 3: Service class for callouts
    tests_total += 1
    if "force-app/main/default/classes/ApexAiPipelineService.cls" in file_paths:
        print(f"  ✓ Service class: ApexAiPipelineService.cls present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing service class")

    # Test 4: Test class generated
    tests_total += 1
    if "force-app/main/default/classes/ApexAiPipelineTest.cls" in file_paths:
        print(f"  ✓ Test class: ApexAiPipelineTest.cls present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing test class")

    # Test 5: Invocable action for Flow
    tests_total += 1
    if "force-app/main/default/classes/ApexAiPipelineInvocable.cls" in file_paths:
        print(f"  ✓ Invocable class: ApexAiPipelineInvocable.cls present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing invocable class")

    # Test 6: Named Credentials
    tests_total += 1
    if "force-app/main/default/namedCredentials/OpenAI.namedCredential-meta.xml" in file_paths:
        print(f"  ✓ Named Credentials: OpenAI credential present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing named credentials")

    # Test 7: Remote Site Settings
    tests_total += 1
    if "force-app/main/default/remoteSiteSettings/OpenAI_API.remoteSite-meta.xml" in file_paths:
        print(f"  ✓ Remote Site Settings: OpenAI_API present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing remote site settings")

    # Test 8: sfdx-project.json
    tests_total += 1
    sfdx_project = next((f for f in result.files if f.path == "sfdx-project.json"), None)
    if sfdx_project and "packageDirectories" in sfdx_project.content:
        print(f"  ✓ SFDX project: sfdx-project.json present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing sfdx-project.json")

    # Test 9: Main class has PipelineResult inner class
    tests_total += 1
    main_class = next((f for f in result.files if f.path == "force-app/main/default/classes/ApexAiPipeline.cls"), None)
    if main_class and "public class PipelineResult" in main_class.content:
        print(f"  ✓ PipelineResult: Inner class present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing PipelineResult inner class")

    # Test 10: OpenAI callout in main class
    tests_total += 1
    if main_class and "callout:OpenAI" in main_class.content:
        print(f"  ✓ OpenAI callout: Named credential callout present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing OpenAI callout")

    # Test 11: Invocable method annotation
    tests_total += 1
    invocable_class = next((f for f in result.files if f.path == "force-app/main/default/classes/ApexAiPipelineInvocable.cls"), None)
    if invocable_class and "@InvocableMethod" in invocable_class.content:
        print(f"  ✓ Flow integration: @InvocableMethod annotation present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing @InvocableMethod annotation")

    # Test 12: Test class has mock callout
    tests_total += 1
    test_class = next((f for f in result.files if f.path == "force-app/main/default/classes/ApexAiPipelineTest.cls"), None)
    if test_class and "HttpCalloutMock" in test_class.content:
        print(f"  ✓ Test mock: HttpCalloutMock present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing HttpCalloutMock in test")

    # Test 13: Single file output
    tests_total += 1
    single_options = CodeGenOptions(
        language=TargetLanguage.APEX,
        platform=TargetPlatform.SALESFORCE,
        output_format=OutputFormat.SINGLE_FILE,
    )
    single_result = generator.generate(pipeline, single_options)
    single_paths = [f.path for f in single_result.files]

    if "ApexAiPipeline.cls" in single_paths:
        print(f"  ✓ Single file: ApexAiPipeline.cls present")
        tests_passed += 1
    else:
        print(f"  ✗ Missing single file class")

    # Test 14: Deployment config
    tests_total += 1
    if result.deployment_config and result.deployment_config.get("platform") == "salesforce":
        print(f"  ✓ Deployment config: salesforce platform")
        tests_passed += 1
    else:
        print(f"  ✗ Missing deployment config")

    print(f"\nResults: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("\n✅ Salesforce Apex code generation working!")
        return 0
    else:
        print(f"\n❌ {tests_total - tests_passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(test_apex_codegen())
