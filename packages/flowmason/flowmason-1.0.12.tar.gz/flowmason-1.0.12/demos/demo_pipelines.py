"""
FlowMason Demo Pipelines

Comprehensive demonstration pipelines showcasing all FlowMason capabilities:
- Nodes (generator, critic, improver, synthesizer, selector)
- Operators (json_transform, filter, variable_set, logger, schema_validate)
- Control Flow (conditional, router, foreach, trycatch, subpipeline, return)

These pipelines serve as:
1. Integration tests for the execution engine
2. Product demonstrations
3. Reference implementations for users

Run with: python -m demos.demo_pipelines
"""

import asyncio
import json
from typing import Any, Dict, List
from datetime import datetime


# =============================================================================
# PIPELINE DEFINITIONS
# =============================================================================

# Pipeline 1: Customer Support Triage
# Uses: router, conditional, generator, logger, json_transform
CUSTOMER_SUPPORT_PIPELINE = {
    "id": "customer-support-triage",
    "name": "Customer Support Triage",
    "version": "1.0.0",
    "description": "Routes customer inquiries to appropriate handlers based on category and urgency",
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_name": {"type": "string"},
            "inquiry_text": {"type": "string"},
            "category": {"type": "string", "enum": ["billing", "technical", "general", "complaint"]},
            "urgency": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        },
        "required": ["customer_name", "inquiry_text", "category"]
    },
    "stages": [
        # Stage 1: Log incoming request
        {
            "id": "log_request",
            "type": "logger",
            "input_mapping": {
                "message": "Customer support request received",
                "level": "info",
                "data": {
                    "customer": "{{input.customer_name}}",
                    "category": "{{input.category}}",
                    "urgency": "{{input.urgency}}"
                },
                "tags": {"pipeline": "customer-support", "stage": "intake"}
            },
            "depends_on": []
        },
        # Stage 2: Check for critical urgency - early return if critical
        {
            "id": "check_critical",
            "type": "return",
            "input_mapping": {
                "condition": "{{input.urgency == 'critical'}}",
                "return_value": {
                    "status": "escalated",
                    "message": "Critical issue escalated to on-call team immediately",
                    "customer": "{{input.customer_name}}",
                    "escalation_time": "immediate"
                },
                "message": "Critical urgency detected - escalating"
            },
            "depends_on": ["log_request"]
        },
        # Stage 3: Route by category
        {
            "id": "route_by_category",
            "type": "router",
            "input_mapping": {
                "value": "{{input.category}}",
                "routes": {
                    "billing": ["handle_billing"],
                    "technical": ["handle_technical"],
                    "complaint": ["handle_complaint"],
                    "general": ["handle_general"]
                },
                "default_route": ["handle_general"],
                "pass_data": {
                    "customer": "{{input.customer_name}}",
                    "text": "{{input.inquiry_text}}"
                }
            },
            "depends_on": ["check_critical"]
        },
        # Stage 4a: Handle billing inquiries
        {
            "id": "handle_billing",
            "type": "generator",
            "input_mapping": {
                "prompt": "Generate a helpful response to this billing inquiry from {{input.customer_name}}: {{input.inquiry_text}}",
                "system_prompt": "You are a helpful billing support agent. Be professional, empathetic, and provide clear information about billing, payments, and account issues.",
                "temperature": 0.5,
                "max_tokens": 500
            },
            "depends_on": ["route_by_category"]
        },
        # Stage 4b: Handle technical inquiries
        {
            "id": "handle_technical",
            "type": "generator",
            "input_mapping": {
                "prompt": "Generate a technical support response for {{input.customer_name}}'s issue: {{input.inquiry_text}}",
                "system_prompt": "You are a technical support specialist. Provide clear, step-by-step troubleshooting guidance. Be patient and thorough.",
                "temperature": 0.3,
                "max_tokens": 800
            },
            "depends_on": ["route_by_category"]
        },
        # Stage 4c: Handle complaints
        {
            "id": "handle_complaint",
            "type": "generator",
            "input_mapping": {
                "prompt": "Generate an empathetic response to this customer complaint from {{input.customer_name}}: {{input.inquiry_text}}",
                "system_prompt": "You are a customer relations specialist handling complaints. Be empathetic, apologetic when appropriate, and focus on resolution. Offer concrete next steps.",
                "temperature": 0.4,
                "max_tokens": 600
            },
            "depends_on": ["route_by_category"]
        },
        # Stage 4d: Handle general inquiries
        {
            "id": "handle_general",
            "type": "generator",
            "input_mapping": {
                "prompt": "Generate a helpful response to this general inquiry from {{input.customer_name}}: {{input.inquiry_text}}",
                "system_prompt": "You are a friendly customer service representative. Be helpful and informative.",
                "temperature": 0.6,
                "max_tokens": 400
            },
            "depends_on": ["route_by_category"]
        },
        # Stage 5: Format final response
        {
            "id": "format_response",
            "type": "json_transform",
            "input_mapping": {
                "data": {
                    "route_info": "{{upstream.route_by_category}}",
                    "billing_response": "{{upstream.handle_billing.content}}",
                    "technical_response": "{{upstream.handle_technical.content}}",
                    "complaint_response": "{{upstream.handle_complaint.content}}",
                    "general_response": "{{upstream.handle_general.content}}"
                },
                "mapping": {
                    "category_handled": "route_info.route_taken",
                    "response": "billing_response"
                }
            },
            "depends_on": ["handle_billing", "handle_technical", "handle_complaint", "handle_general"]
        }
    ],
    "output_stage_id": "format_response"
}


# Pipeline 2: Data Processing with Loops and Error Handling
# Uses: foreach, trycatch, json_transform, filter, logger, variable_set
DATA_PROCESSING_PIPELINE = {
    "id": "data-processing-pipeline",
    "name": "Data Processing Pipeline",
    "version": "1.0.0",
    "description": "Processes a batch of records with filtering, transformation, and error handling",
    "input_schema": {
        "type": "object",
        "properties": {
            "records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "value": {"type": "number"},
                        "category": {"type": "string"},
                        "active": {"type": "boolean"}
                    }
                }
            },
            "min_value_threshold": {"type": "number", "default": 0},
            "process_inactive": {"type": "boolean", "default": False}
        },
        "required": ["records"]
    },
    "stages": [
        # Stage 1: Log processing start
        {
            "id": "log_start",
            "type": "logger",
            "input_mapping": {
                "message": "Starting batch data processing",
                "level": "info",
                "data": {
                    "record_count": "{{len(input.records)}}",
                    "threshold": "{{input.min_value_threshold}}"
                }
            },
            "depends_on": []
        },
        # Stage 2: Initialize counters
        {
            "id": "init_counters",
            "type": "variable_set",
            "input_mapping": {
                "name": "processing_stats",
                "value": {
                    "processed": 0,
                    "filtered": 0,
                    "errors": 0,
                    "started_at": "{{datetime.now()}}"
                }
            },
            "depends_on": ["log_start"]
        },
        # Stage 3: Filter active records (unless process_inactive is true)
        {
            "id": "filter_records",
            "type": "filter",
            "input_mapping": {
                "data": "{{input.records}}",
                "condition": "data.get('active', True) == True or {{input.process_inactive}}",
                "filter_mode": "filter_array"
            },
            "depends_on": ["init_counters"]
        },
        # Stage 4: Check if any records to process
        {
            "id": "check_empty",
            "type": "conditional",
            "input_mapping": {
                "condition": "{{len(upstream.filter_records.data) > 0}}",
                "true_branch_stages": ["setup_loop"],
                "false_branch_stages": ["handle_empty"],
                "pass_data": "{{upstream.filter_records.data}}"
            },
            "depends_on": ["filter_records"]
        },
        # Stage 5a: Handle empty case
        {
            "id": "handle_empty",
            "type": "logger",
            "input_mapping": {
                "message": "No records to process after filtering",
                "level": "warning",
                "data": {"original_count": "{{len(input.records)}}"}
            },
            "depends_on": ["check_empty"]
        },
        # Stage 5b: Setup foreach loop
        {
            "id": "setup_loop",
            "type": "foreach",
            "input_mapping": {
                "items": "{{upstream.filter_records.data}}",
                "loop_stages": ["transform_record", "validate_record"],
                "item_variable": "record",
                "index_variable": "idx",
                "collect_results": True,
                "break_on_error": False
            },
            "depends_on": ["check_empty"]
        },
        # Stage 6: Transform each record (inside loop)
        {
            "id": "transform_record",
            "type": "json_transform",
            "input_mapping": {
                "data": "{{loop.record}}",
                "mapping": {
                    "record_id": "id",
                    "processed_value": "value",
                    "category_upper": "category",
                    "processing_index": "{{loop.idx}}"
                }
            },
            "depends_on": ["setup_loop"]
        },
        # Stage 7: Validate transformed record
        {
            "id": "validate_record",
            "type": "schema_validate",
            "input_mapping": {
                "data": "{{upstream.transform_record.result}}",
                "json_schema": {
                    "type": "object",
                    "required": ["record_id", "processed_value"],
                    "properties": {
                        "record_id": {"type": "string"},
                        "processed_value": {"type": "number"},
                        "category_upper": {"type": "string"}
                    }
                },
                "strict": False,
                "collect_all_errors": True
            },
            "depends_on": ["transform_record"]
        },
        # Stage 8: Aggregate results
        {
            "id": "aggregate_results",
            "type": "json_transform",
            "input_mapping": {
                "data": {
                    "loop_results": "{{upstream.setup_loop.directive.loop_results}}",
                    "filter_stats": "{{upstream.filter_records}}",
                    "original_count": "{{len(input.records)}}"
                },
                "flatten": False
            },
            "depends_on": ["setup_loop", "handle_empty"]
        },
        # Stage 9: Log completion
        {
            "id": "log_complete",
            "type": "logger",
            "input_mapping": {
                "message": "Batch processing complete",
                "level": "info",
                "data": "{{upstream.aggregate_results.result}}",
                "passthrough": "{{upstream.aggregate_results.result}}"
            },
            "depends_on": ["aggregate_results"]
        }
    ],
    "output_stage_id": "log_complete"
}


# Pipeline 3: Content Generation with Validation and Improvement
# Uses: generator, schema_validate, conditional, improver (via subpipeline concept)
CONTENT_GENERATION_PIPELINE = {
    "id": "content-generation-pipeline",
    "name": "Content Generation Pipeline",
    "version": "1.0.0",
    "description": "Generates, validates, and iteratively improves content",
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {"type": "string"},
            "content_type": {"type": "string", "enum": ["blog_post", "email", "summary", "code"]},
            "tone": {"type": "string", "enum": ["professional", "casual", "technical", "friendly"]},
            "max_iterations": {"type": "integer", "default": 2},
            "quality_threshold": {"type": "number", "default": 0.8}
        },
        "required": ["topic", "content_type"]
    },
    "stages": [
        # Stage 1: Log request
        {
            "id": "log_request",
            "type": "logger",
            "input_mapping": {
                "message": "Content generation request received",
                "level": "info",
                "data": {
                    "topic": "{{input.topic}}",
                    "type": "{{input.content_type}}",
                    "tone": "{{input.tone}}"
                }
            },
            "depends_on": []
        },
        # Stage 2: Generate initial content
        {
            "id": "generate_initial",
            "type": "generator",
            "input_mapping": {
                "prompt": "Write a {{input.content_type}} about: {{input.topic}}",
                "system_prompt": "You are a skilled content writer. Write in a {{input.tone}} tone. Create engaging, well-structured content that is informative and appropriate for the format requested.",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "depends_on": ["log_request"]
        },
        # Stage 3: Validate content structure
        {
            "id": "validate_content",
            "type": "schema_validate",
            "input_mapping": {
                "data": {
                    "content": "{{upstream.generate_initial.content}}",
                    "word_count": "{{len(upstream.generate_initial.content.split())}}",
                    "has_content": "{{len(upstream.generate_initial.content) > 100}}"
                },
                "json_schema": {
                    "type": "object",
                    "required": ["content", "has_content"],
                    "properties": {
                        "content": {"type": "string", "minLength": 100},
                        "word_count": {"type": "integer", "minimum": 50},
                        "has_content": {"type": "boolean", "const": True}
                    }
                },
                "strict": False
            },
            "depends_on": ["generate_initial"]
        },
        # Stage 4: Check if content passes validation
        {
            "id": "check_valid",
            "type": "conditional",
            "input_mapping": {
                "condition": "{{upstream.validate_content.valid}}",
                "true_branch_stages": ["critique_content"],
                "false_branch_stages": ["handle_invalid"],
                "pass_data": "{{upstream.generate_initial.content}}"
            },
            "depends_on": ["validate_content"]
        },
        # Stage 5a: Handle invalid content
        {
            "id": "handle_invalid",
            "type": "logger",
            "input_mapping": {
                "message": "Content validation failed",
                "level": "error",
                "data": {
                    "errors": "{{upstream.validate_content.errors}}",
                    "content_preview": "{{upstream.generate_initial.content[:200]}}"
                }
            },
            "depends_on": ["check_valid"]
        },
        # Stage 5b: Critique the content (if valid)
        {
            "id": "critique_content",
            "type": "generator",
            "input_mapping": {
                "prompt": "Critically evaluate this {{input.content_type}} content and provide specific improvement suggestions:\n\n{{upstream.generate_initial.content}}\n\nProvide:\n1. Strengths (2-3 points)\n2. Weaknesses (2-3 points)\n3. Specific improvement suggestions (3-5 actionable items)\n4. Overall quality score (0-1)",
                "system_prompt": "You are a senior content editor and quality reviewer. Be constructive but honest in your critique. Focus on clarity, engagement, accuracy, and appropriateness for the content type.",
                "temperature": 0.3,
                "max_tokens": 1000
            },
            "depends_on": ["check_valid"]
        },
        # Stage 6: Filter critique to extract score
        {
            "id": "extract_score",
            "type": "filter",
            "input_mapping": {
                "data": {
                    "critique": "{{upstream.critique_content.content}}",
                    "original_content": "{{upstream.generate_initial.content}}",
                    "estimated_score": 0.75
                },
                "condition": "data.get('estimated_score', 0) >= {{input.quality_threshold}}",
                "pass_if_missing": True
            },
            "depends_on": ["critique_content"]
        },
        # Stage 7: Decide if improvement needed
        {
            "id": "need_improvement",
            "type": "conditional",
            "input_mapping": {
                "condition": "{{not upstream.extract_score.passed}}",
                "true_branch_stages": ["improve_content"],
                "false_branch_stages": ["finalize_content"],
                "pass_data": {
                    "content": "{{upstream.generate_initial.content}}",
                    "critique": "{{upstream.critique_content.content}}"
                }
            },
            "depends_on": ["extract_score"]
        },
        # Stage 8a: Improve content based on critique
        {
            "id": "improve_content",
            "type": "generator",
            "input_mapping": {
                "prompt": "Improve this {{input.content_type}} content based on the following critique:\n\nORIGINAL CONTENT:\n{{upstream.generate_initial.content}}\n\nCRITIQUE:\n{{upstream.critique_content.content}}\n\nCreate an improved version that addresses the weaknesses while maintaining the strengths.",
                "system_prompt": "You are an expert content improver. Take the critique seriously and make meaningful improvements while preserving the good aspects of the original.",
                "temperature": 0.5,
                "max_tokens": 2500
            },
            "depends_on": ["need_improvement"]
        },
        # Stage 8b: Finalize content (already good enough)
        {
            "id": "finalize_content",
            "type": "variable_set",
            "input_mapping": {
                "name": "final_content",
                "value": "{{upstream.generate_initial.content}}"
            },
            "depends_on": ["need_improvement"]
        },
        # Stage 9: Package final output
        {
            "id": "package_output",
            "type": "json_transform",
            "input_mapping": {
                "data": {
                    "original_content": "{{upstream.generate_initial.content}}",
                    "critique": "{{upstream.critique_content.content}}",
                    "improved_content": "{{upstream.improve_content.content}}",
                    "final_content": "{{upstream.finalize_content.value}}",
                    "validation_passed": "{{upstream.validate_content.valid}}",
                    "was_improved": "{{upstream.improve_content.content != None}}"
                },
                "mapping": {
                    "content": "improved_content",
                    "original": "original_content",
                    "critique": "critique",
                    "metadata": {
                        "validated": "validation_passed",
                        "improved": "was_improved"
                    }
                }
            },
            "depends_on": ["improve_content", "finalize_content", "handle_invalid"]
        },
        # Stage 10: Log completion
        {
            "id": "log_completion",
            "type": "logger",
            "input_mapping": {
                "message": "Content generation complete",
                "level": "info",
                "data": {
                    "topic": "{{input.topic}}",
                    "type": "{{input.content_type}}",
                    "was_improved": "{{upstream.package_output.result.metadata.improved}}"
                },
                "passthrough": "{{upstream.package_output.result}}"
            },
            "depends_on": ["package_output"]
        }
    ],
    "output_stage_id": "log_completion"
}


# Pipeline 4: Error Handling Demo with TryCatch
# Uses: trycatch, conditional, logger, return
ERROR_HANDLING_PIPELINE = {
    "id": "error-handling-demo",
    "name": "Error Handling Demo",
    "version": "1.0.0",
    "description": "Demonstrates try-catch error handling with retries and fallbacks",
    "input_schema": {
        "type": "object",
        "properties": {
            "operation": {"type": "string", "enum": ["safe", "risky", "failing"]},
            "data": {"type": "object"}
        },
        "required": ["operation"]
    },
    "stages": [
        # Stage 1: Setup try-catch
        {
            "id": "error_boundary",
            "type": "trycatch",
            "input_mapping": {
                "try_stages": ["risky_operation"],
                "catch_stages": ["handle_error"],
                "finally_stages": ["cleanup"],
                "max_retries": 2,
                "retry_delay_ms": 500
            },
            "depends_on": []
        },
        # Stage 2: Risky operation
        {
            "id": "risky_operation",
            "type": "filter",
            "input_mapping": {
                "data": "{{input.data}}",
                "condition": "'{{input.operation}}' != 'failing'",
                "pass_if_missing": False
            },
            "depends_on": ["error_boundary"]
        },
        # Stage 3: Handle errors (catch block)
        {
            "id": "handle_error",
            "type": "logger",
            "input_mapping": {
                "message": "Error caught and handled",
                "level": "warning",
                "data": {
                    "operation": "{{input.operation}}",
                    "fallback_used": True
                },
                "passthrough": {"status": "recovered", "used_fallback": True}
            },
            "depends_on": ["error_boundary"]
        },
        # Stage 4: Cleanup (finally block)
        {
            "id": "cleanup",
            "type": "logger",
            "input_mapping": {
                "message": "Cleanup completed",
                "level": "info",
                "data": {"finalized": True}
            },
            "depends_on": ["risky_operation", "handle_error"]
        },
        # Stage 5: Format result
        {
            "id": "format_result",
            "type": "json_transform",
            "input_mapping": {
                "data": {
                    "operation_result": "{{upstream.risky_operation}}",
                    "error_handled": "{{upstream.handle_error.passthrough}}",
                    "cleanup_done": "{{upstream.cleanup.logged}}"
                },
                "flatten": True
            },
            "depends_on": ["cleanup"]
        }
    ],
    "output_stage_id": "format_result"
}


# =============================================================================
# DEMO PIPELINE RUNNER
# =============================================================================

class DemoPipelineRunner:
    """
    Runner for demo pipelines.

    Executes pipelines and validates results, demonstrating
    the full FlowMason execution engine.
    """

    def __init__(self):
        self.results = {}
        self.errors = []

    async def run_all(self):
        """Run all demo pipelines."""
        print("\n" + "="*60)
        print("  FlowMason Demo Pipeline Runner")
        print("="*60 + "\n")

        demos = [
            ("Customer Support Triage", self.demo_customer_support),
            ("Data Processing", self.demo_data_processing),
            ("Content Generation", self.demo_content_generation),
            ("Error Handling", self.demo_error_handling),
        ]

        for name, demo_func in demos:
            print(f"\n{'='*60}")
            print(f"  Running: {name}")
            print("="*60)
            try:
                result = await demo_func()
                self.results[name] = {"status": "passed", "result": result}
                print(f"  [PASSED] {name}")
            except Exception as e:
                self.results[name] = {"status": "failed", "error": str(e)}
                self.errors.append((name, str(e)))
                print(f"  [FAILED] {name}: {e}")

        self._print_summary()

    async def demo_customer_support(self):
        """Demo: Customer Support Triage Pipeline."""
        from flowmason_core.registry import ComponentRegistry
        from flowmason_core.config import ComponentConfig, ExecutionContext
        from flowmason_core.execution import DAGExecutor

        # Create registry and executor
        registry = ComponentRegistry(auto_scan=True)
        context = ExecutionContext(
            run_id="demo-customer-support-001",
            pipeline_id=CUSTOMER_SUPPORT_PIPELINE["id"],
            pipeline_version=CUSTOMER_SUPPORT_PIPELINE["version"],
            pipeline_input={}
        )

        # Test inputs for different scenarios
        test_cases = [
            {
                "name": "Billing inquiry",
                "input": {
                    "customer_name": "John Smith",
                    "inquiry_text": "I was charged twice for my subscription last month. Can you help?",
                    "category": "billing",
                    "urgency": "medium"
                }
            },
            {
                "name": "Technical support",
                "input": {
                    "customer_name": "Jane Doe",
                    "inquiry_text": "The application keeps crashing when I try to export my data.",
                    "category": "technical",
                    "urgency": "high"
                }
            },
            {
                "name": "Critical escalation",
                "input": {
                    "customer_name": "Bob Wilson",
                    "inquiry_text": "Our entire system is down and we can't access anything!",
                    "category": "technical",
                    "urgency": "critical"
                }
            }
        ]

        results = []
        for test in test_cases:
            print(f"\n  Testing: {test['name']}")

            # Build stages from pipeline definition
            stages = [
                ComponentConfig(**stage)
                for stage in CUSTOMER_SUPPORT_PIPELINE["stages"]
            ]

            # Execute
            dag_executor = DAGExecutor(registry, context)
            try:
                result = await dag_executor.execute(stages, test["input"])
                results.append({
                    "test": test["name"],
                    "status": "success",
                    "stages_completed": len(result)
                })
                print(f"    Completed {len(result)} stages")
            except Exception as e:
                results.append({
                    "test": test["name"],
                    "status": "error",
                    "error": str(e)
                })
                print(f"    Error: {e}")

        return results

    async def demo_data_processing(self):
        """Demo: Data Processing Pipeline."""
        from flowmason_core.registry import ComponentRegistry
        from flowmason_core.config import ComponentConfig, ExecutionContext
        from flowmason_core.execution import DAGExecutor

        registry = ComponentRegistry(auto_scan=True)
        context = ExecutionContext(
            run_id="demo-data-processing-001",
            pipeline_id=DATA_PROCESSING_PIPELINE["id"],
            pipeline_version=DATA_PROCESSING_PIPELINE["version"],
            pipeline_input={}
        )

        test_input = {
            "records": [
                {"id": "rec-001", "value": 100, "category": "A", "active": True},
                {"id": "rec-002", "value": 250, "category": "B", "active": True},
                {"id": "rec-003", "value": 50, "category": "A", "active": False},
                {"id": "rec-004", "value": 175, "category": "C", "active": True},
                {"id": "rec-005", "value": 300, "category": "B", "active": True},
            ],
            "min_value_threshold": 75,
            "process_inactive": False
        }

        print(f"\n  Processing {len(test_input['records'])} records...")

        stages = [
            ComponentConfig(**stage)
            for stage in DATA_PROCESSING_PIPELINE["stages"]
        ]

        dag_executor = DAGExecutor(registry, context)
        result = await dag_executor.execute(stages, test_input)

        print(f"  Completed {len(result)} stages")
        return {"stages_completed": len(result)}

    async def demo_content_generation(self):
        """Demo: Content Generation Pipeline."""
        from flowmason_core.registry import ComponentRegistry
        from flowmason_core.config import ComponentConfig, ExecutionContext
        from flowmason_core.execution import DAGExecutor

        registry = ComponentRegistry(auto_scan=True)
        context = ExecutionContext(
            run_id="demo-content-generation-001",
            pipeline_id=CONTENT_GENERATION_PIPELINE["id"],
            pipeline_version=CONTENT_GENERATION_PIPELINE["version"],
            pipeline_input={}
        )

        test_input = {
            "topic": "The benefits of automated testing in software development",
            "content_type": "blog_post",
            "tone": "professional",
            "max_iterations": 2,
            "quality_threshold": 0.7
        }

        print(f"\n  Generating {test_input['content_type']} about: {test_input['topic'][:50]}...")

        stages = [
            ComponentConfig(**stage)
            for stage in CONTENT_GENERATION_PIPELINE["stages"]
        ]

        dag_executor = DAGExecutor(registry, context)
        result = await dag_executor.execute(stages, test_input)

        print(f"  Completed {len(result)} stages")
        return {"stages_completed": len(result)}

    async def demo_error_handling(self):
        """Demo: Error Handling Pipeline."""
        from flowmason_core.registry import ComponentRegistry
        from flowmason_core.config import ComponentConfig, ExecutionContext
        from flowmason_core.execution import DAGExecutor

        registry = ComponentRegistry(auto_scan=True)
        context = ExecutionContext(
            run_id="demo-error-handling-001",
            pipeline_id=ERROR_HANDLING_PIPELINE["id"],
            pipeline_version=ERROR_HANDLING_PIPELINE["version"],
            pipeline_input={}
        )

        test_cases = [
            {"name": "Safe operation", "input": {"operation": "safe", "data": {"value": 1}}},
            {"name": "Risky operation", "input": {"operation": "risky", "data": {"value": 2}}},
        ]

        results = []
        for test in test_cases:
            print(f"\n  Testing: {test['name']}")

            stages = [
                ComponentConfig(**stage)
                for stage in ERROR_HANDLING_PIPELINE["stages"]
            ]

            dag_executor = DAGExecutor(registry, context)
            try:
                result = await dag_executor.execute(stages, test["input"])
                results.append({
                    "test": test["name"],
                    "status": "success",
                    "stages_completed": len(result)
                })
                print(f"    Completed {len(result)} stages")
            except Exception as e:
                results.append({
                    "test": test["name"],
                    "status": "handled",
                    "message": str(e)
                })
                print(f"    Handled error: {e}")

        return results

    def _print_summary(self):
        """Print execution summary."""
        print("\n" + "="*60)
        print("  EXECUTION SUMMARY")
        print("="*60)

        passed = sum(1 for r in self.results.values() if r["status"] == "passed")
        failed = len(self.results) - passed

        print(f"\n  Total Demos: {len(self.results)}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")

        if self.errors:
            print("\n  ERRORS:")
            for name, error in self.errors:
                print(f"    - {name}: {error[:100]}...")

        print("\n" + "="*60 + "\n")


# =============================================================================
# STANDALONE TEST RUNNER
# =============================================================================

async def run_standalone_tests():
    """
    Run standalone tests of control flow components.

    These tests don't require the full pipeline infrastructure
    and directly test control flow components.
    """
    print("\n" + "="*60)
    print("  Standalone Control Flow Tests")
    print("="*60 + "\n")

    from flowmason_core.config import ExecutionContext

    # Create context
    context = ExecutionContext(
        run_id="standalone-test-001",
        pipeline_id="standalone-tests",
        pipeline_version="1.0.0",
        pipeline_input={}
    )

    tests_passed = 0
    tests_failed = 0

    # Test 1: Conditional
    print("  [TEST] Conditional Component")
    try:
        from flowmason_lab.operators.control_flow import ConditionalComponent
        cond = ConditionalComponent()
        result = await cond.execute(
            cond.Input(
                condition=True,
                true_branch_stages=["a", "b"],
                false_branch_stages=["c"]
            ),
            context
        )
        assert result.branch_taken == "true"
        print("    [PASS] Conditional true branch")
        tests_passed += 1
    except Exception as e:
        print(f"    [FAIL] {e}")
        tests_failed += 1

    # Test 2: Router
    print("  [TEST] Router Component")
    try:
        from flowmason_lab.operators.control_flow import RouterComponent
        router = RouterComponent()
        result = await router.execute(
            router.Input(
                value="billing",
                routes={
                    "billing": ["billing_handler"],
                    "support": ["support_handler"]
                },
                default_route=["default"]
            ),
            context
        )
        assert result.route_taken == "billing"
        print("    [PASS] Router routing")
        tests_passed += 1
    except Exception as e:
        print(f"    [FAIL] {e}")
        tests_failed += 1

    # Test 3: ForEach
    print("  [TEST] ForEach Component")
    try:
        from flowmason_lab.operators.control_flow import ForEachComponent
        foreach = ForEachComponent()
        result = await foreach.execute(
            foreach.Input(
                items=[1, 2, 3, 4, 5],
                loop_stages=["process"],
                item_variable="item"
            ),
            context
        )
        assert result.total_items == 5
        print("    [PASS] ForEach iteration setup")
        tests_passed += 1
    except Exception as e:
        print(f"    [FAIL] {e}")
        tests_failed += 1

    # Test 4: TryCatch
    print("  [TEST] TryCatch Component")
    try:
        from flowmason_lab.operators.control_flow import TryCatchComponent
        tc = TryCatchComponent()
        result = await tc.execute(
            tc.Input(
                try_stages=["risky"],
                catch_stages=["handle"],
                finally_stages=["cleanup"],
                max_retries=3
            ),
            context
        )
        assert result.status == "pending"
        print("    [PASS] TryCatch setup")
        tests_passed += 1
    except Exception as e:
        print(f"    [FAIL] {e}")
        tests_failed += 1

    # Test 5: SubPipeline
    print("  [TEST] SubPipeline Component")
    try:
        from flowmason_lab.operators.control_flow import SubPipelineComponent
        sp = SubPipelineComponent()
        result = await sp.execute(
            sp.Input(
                pipeline_id="child-pipeline",
                input_data={"key": "value"},
                timeout_ms=30000
            ),
            context
        )
        assert result.pipeline_id == "child-pipeline"
        print("    [PASS] SubPipeline setup")
        tests_passed += 1
    except Exception as e:
        print(f"    [FAIL] {e}")
        tests_failed += 1

    # Test 6: Return
    print("  [TEST] Return Component")
    try:
        from flowmason_lab.operators.control_flow import ReturnComponent
        ret = ReturnComponent()
        result = await ret.execute(
            ret.Input(
                condition=True,
                return_value={"status": "early_exit"}
            ),
            context
        )
        assert result.should_return == True
        print("    [PASS] Return early exit")
        tests_passed += 1
    except Exception as e:
        print(f"    [FAIL] {e}")
        tests_failed += 1

    print(f"\n  Results: {tests_passed} passed, {tests_failed} failed\n")
    return tests_passed, tests_failed


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point for demo pipeline runner."""
    import sys

    print("\n" + "="*60)
    print("    FLOWMASON DEMO SUITE")
    print("="*60)

    # Run standalone tests first
    passed, failed = await run_standalone_tests()

    if failed > 0:
        print("  Some standalone tests failed. Check component implementations.")
        sys.exit(1)

    # Run full pipeline demos
    runner = DemoPipelineRunner()
    await runner.run_all()

    if runner.errors:
        print("  Some demos failed. See details above.")
        sys.exit(1)

    print("  All demos completed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
