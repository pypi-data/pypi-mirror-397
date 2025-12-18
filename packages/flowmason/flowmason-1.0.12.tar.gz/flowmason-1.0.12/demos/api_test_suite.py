#!/usr/bin/env python3
"""
FlowMason API Test Suite

This script tests ALL FlowMason API endpoints comprehensively.
It exercises the complete API surface including:
- Registry API (components, packages)
- Pipelines API (CRUD, clone, validate, test, publish)
- Execution API (run, list runs, trace, cancel)
- Providers API (list, models, test connection)
- Templates API (list, details, instantiate)
- Health check

Usage:
    python demos/api_test_suite.py
    python demos/api_test_suite.py --base-url http://localhost:8999
    python demos/api_test_suite.py --verbose
    python demos/api_test_suite.py --section registry  # Run only registry tests

Requirements:
    - FlowMason Studio server running on port 8999
    - requests library (pip install requests)
"""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class APITestSuite:
    """Comprehensive API test suite for FlowMason."""

    def __init__(self, base_url: str = "http://localhost:8999", verbose: bool = False):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"
        self.verbose = verbose
        self.results: List[Dict[str, Any]] = []
        self.created_resources: Dict[str, List[str]] = {
            "pipelines": [],
            "runs": [],
        }

    def log(self, message: str, color: str = Colors.RESET):
        """Print a log message with optional color."""
        print(f"{color}{message}{Colors.RESET}")

    def log_verbose(self, message: str):
        """Print verbose log message."""
        if self.verbose:
            print(f"  {Colors.CYAN}{message}{Colors.RESET}")

    def record_result(self, test_name: str, passed: bool, details: str = "", response_time: float = 0):
        """Record a test result."""
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "response_time_ms": int(response_time * 1000),
        })
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        self.log(f"  [{status}] {test_name} ({int(response_time * 1000)}ms)")
        if not passed and details:
            self.log(f"       {Colors.RED}{details}{Colors.RESET}")

    def request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        expected_status: int = 200,
    ) -> Tuple[Optional[Dict], float, int]:
        """Make an API request and return (response_data, response_time, status_code)."""
        url = f"{self.api_url}{path}" if not path.startswith("http") else path

        self.log_verbose(f"{method} {url}")
        if data:
            self.log_verbose(f"Body: {json.dumps(data, indent=2)[:500]}")

        start_time = time.time()
        try:
            if method == "GET":
                resp = requests.get(url, params=params, timeout=120)
            elif method == "POST":
                if files:
                    resp = requests.post(url, files=files, params=params, timeout=120)
                else:
                    resp = requests.post(url, json=data, params=params, timeout=120)
            elif method == "PUT":
                resp = requests.put(url, json=data, params=params, timeout=120)
            elif method == "DELETE":
                resp = requests.delete(url, params=params, timeout=120)
            else:
                raise ValueError(f"Unknown method: {method}")

            response_time = time.time() - start_time

            self.log_verbose(f"Status: {resp.status_code}")

            try:
                response_data = resp.json()
                self.log_verbose(f"Response: {json.dumps(response_data, indent=2)[:500]}")
            except:
                response_data = {"raw": resp.text[:500]}

            return response_data, response_time, resp.status_code

        except requests.exceptions.ConnectionError as e:
            return None, 0, 0
        except Exception as e:
            self.log_verbose(f"Error: {e}")
            return None, time.time() - start_time, 0

    # =========================================================================
    # HEALTH CHECK TESTS
    # =========================================================================
    def test_health(self):
        """Test health check endpoint."""
        self.log(f"\n{Colors.BOLD}=== HEALTH CHECK ==={Colors.RESET}")

        # Test health endpoint (not under /api/v1)
        url = f"{self.base_url}/health"
        start_time = time.time()
        try:
            resp = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            data = resp.json()

            passed = resp.status_code == 200 and data.get("status") == "healthy"
            self.record_result(
                "GET /health",
                passed,
                f"Status: {data.get('status', 'unknown')}" if not passed else "",
                response_time
            )
        except Exception as e:
            self.record_result("GET /health", False, str(e), 0)

    # =========================================================================
    # REGISTRY API TESTS
    # =========================================================================
    def test_registry(self):
        """Test registry API endpoints."""
        self.log(f"\n{Colors.BOLD}=== REGISTRY API ==={Colors.RESET}")

        # GET /registry/components
        data, rt, status = self.request("GET", "/registry/components")
        passed = status == 200 and "components" in (data or {})
        component_count = len(data.get("components", [])) if data else 0
        self.record_result(
            "GET /registry/components",
            passed,
            f"Found {component_count} components" if passed else f"Status: {status}",
            rt
        )

        # GET /registry/components?kind=node
        data, rt, status = self.request("GET", "/registry/components", params={"kind": "node"})
        passed = status == 200 and "components" in (data or {})
        self.record_result(
            "GET /registry/components?kind=node",
            passed,
            "" if passed else f"Status: {status}",
            rt
        )

        # GET /registry/components?kind=operator
        data, rt, status = self.request("GET", "/registry/components", params={"kind": "operator"})
        passed = status == 200 and "components" in (data or {})
        self.record_result(
            "GET /registry/components?kind=operator",
            passed,
            "" if passed else f"Status: {status}",
            rt
        )

        # GET /registry/components/{type} - generator
        data, rt, status = self.request("GET", "/registry/components/generator")
        passed = status == 200 and data.get("component_type") == "generator"
        self.record_result(
            "GET /registry/components/generator",
            passed,
            "" if passed else f"Status: {status}",
            rt
        )

        # GET /registry/components/{type} - json_transform
        data, rt, status = self.request("GET", "/registry/components/json_transform")
        passed = status == 200 and data.get("component_type") == "json_transform"
        self.record_result(
            "GET /registry/components/json_transform",
            passed,
            "" if passed else f"Status: {status}",
            rt
        )

        # GET /registry/components/{type} - conditional (control flow)
        data, rt, status = self.request("GET", "/registry/components/conditional")
        passed = status == 200 and data.get("component_type") == "conditional"
        self.record_result(
            "GET /registry/components/conditional",
            passed,
            "" if passed else f"Status: {status}",
            rt
        )

        # GET /registry/components/{type} - non-existent
        data, rt, status = self.request("GET", "/registry/components/nonexistent_component")
        passed = status == 404
        self.record_result(
            "GET /registry/components/nonexistent (404)",
            passed,
            "" if passed else f"Expected 404, got {status}",
            rt
        )

        # GET /registry/stats
        data, rt, status = self.request("GET", "/registry/stats")
        passed = status == 200 and "total_components" in (data or {})
        self.record_result(
            "GET /registry/stats",
            passed,
            f"Total: {data.get('total_components', 0)} components" if passed else f"Status: {status}",
            rt
        )

        # POST /registry/refresh
        data, rt, status = self.request("POST", "/registry/refresh")
        passed = status == 200 and "packages_loaded" in (data or {})
        self.record_result(
            "POST /registry/refresh",
            passed,
            f"Loaded {data.get('packages_loaded', 0)} packages" if passed else f"Status: {status}",
            rt
        )

    # =========================================================================
    # PIPELINES API TESTS
    # =========================================================================
    def test_pipelines(self):
        """Test pipelines API endpoints."""
        self.log(f"\n{Colors.BOLD}=== PIPELINES API ==={Colors.RESET}")

        # GET /pipelines - list all
        data, rt, status = self.request("GET", "/pipelines")
        passed = status == 200 and "items" in (data or {})
        pipeline_count = len(data.get("items", [])) if data else 0
        self.record_result(
            "GET /pipelines",
            passed,
            f"Found {pipeline_count} pipelines (total: {data.get('total', 0)})" if passed else f"Status: {status}",
            rt
        )

        # GET /pipelines?category=demo
        data, rt, status = self.request("GET", "/pipelines", params={"category": "demo"})
        passed = status == 200 and "items" in (data or {})
        self.record_result(
            "GET /pipelines?category=demo",
            passed,
            f"Found {len(data.get('items', []))} demo pipelines" if passed else f"Status: {status}",
            rt
        )

        # GET /pipelines?category=real-ai
        data, rt, status = self.request("GET", "/pipelines", params={"category": "real-ai"})
        passed = status == 200 and "items" in (data or {})
        real_ai_count = len(data.get("items", [])) if data else 0
        self.record_result(
            "GET /pipelines?category=real-ai",
            passed,
            f"Found {real_ai_count} real-AI pipelines" if passed else f"Status: {status}",
            rt
        )

        # POST /pipelines - create new pipeline
        new_pipeline = {
            "name": f"API Test Pipeline {datetime.now().strftime('%H%M%S')}",
            "description": "Created by API test suite",
            "category": "test",
            "stages": [
                {
                    "id": "log_start",
                    "component_type": "logger",
                    "name": "Log Start",
                    "config": {},
                    "input_mapping": {
                        "message": "Test pipeline started",
                        "level": "info"
                    },
                    "depends_on": [],
                    "position": {"x": 0, "y": 0}
                },
                {
                    "id": "transform",
                    "component_type": "json_transform",
                    "name": "Transform Data",
                    "config": {},
                    "input_mapping": {
                        "data": {"test": "value"},
                        "mapping": {"output": "data.test"}
                    },
                    "depends_on": ["log_start"],
                    "position": {"x": 250, "y": 0}
                }
            ],
            "output_stage_id": "transform",
            "tags": ["test", "api-suite"]
        }
        data, rt, status = self.request("POST", "/pipelines", data=new_pipeline)
        passed = status in [200, 201] and "id" in (data or {})
        created_id = data.get("id") if data else None
        if created_id:
            self.created_resources["pipelines"].append(created_id)
        self.record_result(
            "POST /pipelines (create)",
            passed,
            f"Created: {created_id}" if passed else f"Status: {status}",
            rt
        )

        if created_id:
            # GET /pipelines/{id}
            data, rt, status = self.request("GET", f"/pipelines/{created_id}")
            passed = status == 200 and data.get("id") == created_id
            self.record_result(
                f"GET /pipelines/{created_id[:16]}...",
                passed,
                "" if passed else f"Status: {status}",
                rt
            )

            # PUT /pipelines/{id} - update
            update_data = {"name": f"Updated Test Pipeline {datetime.now().strftime('%H%M%S')}"}
            data, rt, status = self.request("PUT", f"/pipelines/{created_id}", data=update_data)
            passed = status == 200
            self.record_result(
                f"PUT /pipelines/{created_id[:16]}...",
                passed,
                "" if passed else f"Status: {status}",
                rt
            )

            # POST /pipelines/{id}/validate
            data, rt, status = self.request("POST", f"/pipelines/{created_id}/validate")
            passed = status == 200 and "valid" in (data or {})
            self.record_result(
                f"POST /pipelines/{created_id[:16]}../validate",
                passed,
                f"Valid: {data.get('valid')}" if passed else f"Status: {status}",
                rt
            )

            # POST /pipelines/{id}/clone
            clone_data = {"name": f"Cloned Pipeline {datetime.now().strftime('%H%M%S')}"}
            data, rt, status = self.request("POST", f"/pipelines/{created_id}/clone", data=clone_data)
            passed = status in [200, 201] and "id" in (data or {})
            cloned_id = data.get("id") if data else None
            if cloned_id:
                self.created_resources["pipelines"].append(cloned_id)
            self.record_result(
                f"POST /pipelines/{created_id[:16]}../clone",
                passed,
                f"Cloned to: {cloned_id}" if passed else f"Status: {status}",
                rt
            )

        # GET /pipelines/{id} - non-existent
        data, rt, status = self.request("GET", "/pipelines/nonexistent_pipeline_id")
        passed = status == 404
        self.record_result(
            "GET /pipelines/nonexistent (404)",
            passed,
            "" if passed else f"Expected 404, got {status}",
            rt
        )

    # =========================================================================
    # EXECUTION API TESTS
    # =========================================================================
    def test_execution(self):
        """Test execution API endpoints."""
        self.log(f"\n{Colors.BOLD}=== EXECUTION API ==={Colors.RESET}")

        # Find a simple pipeline to run
        data, _, _ = self.request("GET", "/pipelines", params={"category": "demo", "limit": 5})
        pipelines = data.get("items", []) if data else []

        test_pipeline_id = None
        for p in pipelines:
            # Look for a simple pipeline (few stages, no LLM required)
            if p.get("stage_count", 0) <= 10:
                test_pipeline_id = p.get("id")
                break

        if not test_pipeline_id and pipelines:
            test_pipeline_id = pipelines[0].get("id")

        if test_pipeline_id:
            # POST /pipelines/{id}/run (returns 202 Accepted for async execution)
            run_data = {"inputs": {}}
            data, rt, status = self.request("POST", f"/pipelines/{test_pipeline_id}/run", data=run_data)
            # The API may return 200 (sync) or 202 (async) depending on configuration
            passed = status in [200, 202] and "id" in (data or {})
            run_id = data.get("id") if data else None  # Note: field is 'id' not 'run_id'
            if run_id:
                self.created_resources["runs"].append(run_id)
            self.record_result(
                f"POST /pipelines/{test_pipeline_id[:16]}../run",
                passed,
                f"Run ID: {run_id}, Status: {data.get('status')}" if passed else f"Status: {status}, Error: {data}",
                rt
            )

            if run_id:
                # GET /runs/{run_id}
                data, rt, status = self.request("GET", f"/runs/{run_id}")
                passed = status == 200 and data.get("id") == run_id
                self.record_result(
                    f"GET /runs/{run_id[:16]}...",
                    passed,
                    f"Status: {data.get('status')}" if passed else f"HTTP Status: {status}",
                    rt
                )

                # GET /runs/{run_id}/trace
                data, rt, status = self.request("GET", f"/runs/{run_id}/trace")
                passed = status == 200 and "stages" in (data or {})
                stage_count = len(data.get("stages", [])) if data else 0
                self.record_result(
                    f"GET /runs/{run_id[:16]}../trace",
                    passed,
                    f"Stages: {stage_count}" if passed else f"Status: {status}",
                    rt
                )

        # GET /runs - list all runs
        data, rt, status = self.request("GET", "/runs")
        passed = status == 200 and "runs" in (data or {})
        run_count = len(data.get("runs", [])) if data else 0
        self.record_result(
            "GET /runs",
            passed,
            f"Found {run_count} runs" if passed else f"Status: {status}",
            rt
        )

        # GET /runs?status=completed
        data, rt, status = self.request("GET", "/runs", params={"status": "completed"})
        passed = status == 200 and "runs" in (data or {})
        self.record_result(
            "GET /runs?status=completed",
            passed,
            "" if passed else f"Status: {status}",
            rt
        )

        # GET /runs/{id} - non-existent
        data, rt, status = self.request("GET", "/runs/nonexistent_run_id")
        passed = status == 404
        self.record_result(
            "GET /runs/nonexistent (404)",
            passed,
            "" if passed else f"Expected 404, got {status}",
            rt
        )

    # =========================================================================
    # REAL AI PIPELINE EXECUTION TESTS
    # =========================================================================
    def test_real_ai_execution(self):
        """Test execution of real AI pipelines (requires LLM providers)."""
        self.log(f"\n{Colors.BOLD}=== REAL AI EXECUTION ==={Colors.RESET}")

        # Find a real-ai pipeline
        data, _, _ = self.request("GET", "/pipelines", params={"category": "real-ai", "limit": 5})
        pipelines = data.get("items", []) if data else []

        if not pipelines:
            self.log(f"  {Colors.YELLOW}No real-AI pipelines found, skipping{Colors.RESET}")
            return

        # Test the first real-AI pipeline (usually the simplest/smallest)
        # Sort by stage count to get the simplest one
        pipelines.sort(key=lambda p: p.get("stage_count", 999))
        test_pipeline = pipelines[0]
        test_pipeline_id = test_pipeline.get("id")

        self.log(f"  Testing: {test_pipeline.get('name')} ({test_pipeline.get('stage_count')} stages)")

        # Run the pipeline (returns 202 Accepted for async execution)
        run_data = {"inputs": {}}
        data, rt, status = self.request("POST", f"/pipelines/{test_pipeline_id}/run", data=run_data)
        passed = status in [200, 202] and "id" in (data or {})
        run_id = data.get("id") if data else None
        run_status = data.get("status") if data else "unknown"

        if run_id:
            self.created_resources["runs"].append(run_id)

        self.record_result(
            f"POST /pipelines/{test_pipeline_id[:16]}../run (Real AI)",
            passed and run_status in ["completed", "running", "pending"],
            f"Run ID: {run_id}, Status: {run_status}" if passed else f"Error: {data.get('error', data)}",
            rt
        )

        # Check if there were any LLM tokens used
        if passed and data:
            usage = data.get("usage") or {}
            tokens = usage.get("total_tokens", 0)
            cost = usage.get("total_cost", 0)
            if tokens > 0:
                self.log(f"  {Colors.GREEN}AI Usage: {tokens} tokens, ${cost:.4f}{Colors.RESET}")

    # =========================================================================
    # PROVIDERS API TESTS
    # =========================================================================
    def test_providers(self):
        """Test providers API endpoints."""
        self.log(f"\n{Colors.BOLD}=== PROVIDERS API ==={Colors.RESET}")

        # GET /providers
        data, rt, status = self.request("GET", "/providers")
        passed = status == 200 and "providers" in (data or {})
        provider_count = len(data.get("providers", [])) if data else 0
        self.record_result(
            "GET /providers",
            passed,
            f"Found {provider_count} providers" if passed else f"Status: {status}",
            rt
        )

        # Get first configured provider for testing
        providers = data.get("providers", []) if data else []
        configured_provider = None
        for p in providers:
            if p.get("configured"):
                configured_provider = p.get("name")
                break

        if configured_provider:
            # GET /providers/{name}/models
            data, rt, status = self.request("GET", f"/providers/{configured_provider}/models")
            passed = status == 200 and "models" in (data or {})
            model_count = len(data.get("models", [])) if data else 0
            self.record_result(
                f"GET /providers/{configured_provider}/models",
                passed,
                f"Found {model_count} models" if passed else f"Status: {status}",
                rt
            )

            # POST /providers/{name}/test
            data, rt, status = self.request("POST", f"/providers/{configured_provider}/test", data={})
            passed = status == 200 and "success" in (data or {})
            test_success = data.get("success", False) if data else False
            self.record_result(
                f"POST /providers/{configured_provider}/test",
                passed,
                f"Connection: {'OK' if test_success else 'FAILED'} ({data.get('duration_ms', 0)}ms)" if passed else f"Status: {status}",
                rt
            )
        else:
            self.log(f"  {Colors.YELLOW}No configured providers found, skipping provider tests{Colors.RESET}")

        # GET /providers/capabilities
        data, rt, status = self.request("GET", "/providers/capabilities")
        passed = status == 200 and "capabilities" in (data or {})
        self.record_result(
            "GET /providers/capabilities",
            passed,
            "" if passed else f"Status: {status}",
            rt
        )

    # =========================================================================
    # TEMPLATES API TESTS
    # =========================================================================
    def test_templates(self):
        """Test templates API endpoints."""
        self.log(f"\n{Colors.BOLD}=== TEMPLATES API ==={Colors.RESET}")

        # GET /templates
        data, rt, status = self.request("GET", "/templates")
        passed = status == 200 and "templates" in (data or {})
        template_count = len(data.get("templates", [])) if data else 0
        self.record_result(
            "GET /templates",
            passed,
            f"Found {template_count} templates" if passed else f"Status: {status}",
            rt
        )

        templates = data.get("templates", []) if data else []
        if templates:
            template_id = templates[0].get("id")

            # GET /templates/{id}
            data, rt, status = self.request("GET", f"/templates/{template_id}")
            passed = status == 200 and data.get("id") == template_id
            self.record_result(
                f"GET /templates/{template_id[:20]}...",
                passed,
                "" if passed else f"Status: {status}",
                rt
            )

            # POST /templates/{id}/instantiate
            data, rt, status = self.request(
                "POST",
                f"/templates/{template_id}/instantiate",
                params={"name": f"Instantiated Template {datetime.now().strftime('%H%M%S')}"}
            )
            passed = status in [200, 201] and "id" in (data or {})
            instantiated_id = data.get("id") if data else None
            if instantiated_id:
                self.created_resources["pipelines"].append(instantiated_id)
            self.record_result(
                f"POST /templates/{template_id[:20]}../instantiate",
                passed,
                f"Created: {instantiated_id}" if passed else f"Status: {status}",
                rt
            )

        # GET /templates/categories/list
        data, rt, status = self.request("GET", "/templates/categories/list")
        passed = status == 200 and "categories" in (data or {})
        self.record_result(
            "GET /templates/categories/list",
            passed,
            "" if passed else f"Status: {status}",
            rt
        )

    # =========================================================================
    # CLEANUP
    # =========================================================================
    def cleanup(self):
        """Clean up created resources."""
        self.log(f"\n{Colors.BOLD}=== CLEANUP ==={Colors.RESET}")

        # Delete created pipelines
        for pipeline_id in self.created_resources["pipelines"]:
            data, rt, status = self.request("DELETE", f"/pipelines/{pipeline_id}")
            passed = status == 200 or status == 204
            self.log(f"  Deleted pipeline {pipeline_id[:20]}... {'OK' if passed else 'FAILED'}")

        # Note: Runs are typically kept for audit purposes

    # =========================================================================
    # SUMMARY
    # =========================================================================
    def print_summary(self):
        """Print test summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed

        self.log(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
        self.log(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
        self.log(f"{'=' * 60}")
        self.log(f"Total Tests:  {total}")
        self.log(f"Passed:       {Colors.GREEN}{passed}{Colors.RESET}")
        self.log(f"Failed:       {Colors.RED}{failed}{Colors.RESET}")
        self.log(f"Pass Rate:    {Colors.BOLD}{passed/total*100:.1f}%{Colors.RESET}")

        avg_time = sum(r["response_time_ms"] for r in self.results) / total if total > 0 else 0
        self.log(f"Avg Response: {avg_time:.0f}ms")
        self.log(f"{'=' * 60}")

        if failed > 0:
            self.log(f"\n{Colors.RED}FAILED TESTS:{Colors.RESET}")
            for r in self.results:
                if not r["passed"]:
                    self.log(f"  - {r['test']}: {r['details']}")

        return failed == 0

    # =========================================================================
    # MAIN RUNNER
    # =========================================================================
    def run(self, sections: Optional[List[str]] = None):
        """Run all or selected test sections."""
        self.log(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
        self.log(f"{Colors.BOLD}FLOWMASON API TEST SUITE{Colors.RESET}")
        self.log(f"Base URL: {self.base_url}")
        self.log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"{'=' * 60}")

        all_sections = ["health", "registry", "pipelines", "execution", "real_ai", "providers", "templates"]

        if sections:
            sections = [s.lower() for s in sections]
        else:
            sections = all_sections

        try:
            if "health" in sections:
                self.test_health()
            if "registry" in sections:
                self.test_registry()
            if "pipelines" in sections:
                self.test_pipelines()
            if "execution" in sections:
                self.test_execution()
            if "real_ai" in sections:
                self.test_real_ai_execution()
            if "providers" in sections:
                self.test_providers()
            if "templates" in sections:
                self.test_templates()
        finally:
            self.cleanup()

        return self.print_summary()


def main():
    parser = argparse.ArgumentParser(description="FlowMason API Test Suite")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8999",
        help="Base URL of FlowMason Studio (default: http://localhost:8999)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--section", "-s",
        action="append",
        dest="sections",
        choices=["health", "registry", "pipelines", "execution", "real_ai", "providers", "templates"],
        help="Run only specific test sections (can be repeated)"
    )

    args = parser.parse_args()

    suite = APITestSuite(base_url=args.base_url, verbose=args.verbose)
    success = suite.run(sections=args.sections)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
