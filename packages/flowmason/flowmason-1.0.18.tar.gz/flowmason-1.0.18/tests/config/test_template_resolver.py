"""
Tests for the Template Resolver.

Tests that {{variable}} templates are correctly resolved.
"""

import pytest
import os
from flowmason_core.config.template_resolver import TemplateResolver
from flowmason_core.config.types import TemplateError


class TestTemplateResolverBasics:
    """Basic template resolution tests."""

    def test_resolve_simple_input_template(self):
        """Test resolving a simple {{input.field}} template."""
        resolver = TemplateResolver()
        context = {
            "input": {"name": "Alice"},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("{{input.name}}", context)
        assert result == "Alice"

    def test_resolve_nested_input_template(self):
        """Test resolving nested {{input.nested.field}} template."""
        resolver = TemplateResolver()
        context = {
            "input": {"customer": {"name": "Bob", "tier": "premium"}},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("{{input.customer.name}}", context)
        assert result == "Bob"

        result = resolver.resolve("{{input.customer.tier}}", context)
        assert result == "premium"

    def test_resolve_upstream_template(self):
        """Test resolving {{upstream.stage_id.field}} template."""
        resolver = TemplateResolver()
        context = {
            "input": {},
            "upstream": {
                "classify": {"category": "support", "confidence": 0.95}
            },
            "env": {},
            "context": {},
        }

        result = resolver.resolve("{{upstream.classify.category}}", context)
        assert result == "support"

        result = resolver.resolve("{{upstream.classify.confidence}}", context)
        assert result == 0.95

    def test_resolve_context_template(self):
        """Test resolving {{context.field}} template."""
        resolver = TemplateResolver()
        context = {
            "input": {},
            "upstream": {},
            "env": {},
            "context": {"run_id": "run_123", "pipeline_id": "my-pipeline"},
        }

        result = resolver.resolve("{{context.run_id}}", context)
        assert result == "run_123"

    def test_resolve_env_template(self):
        """Test resolving {{env.VAR_NAME}} template."""
        resolver = TemplateResolver()

        # Set up env in context
        context = {
            "input": {},
            "upstream": {},
            "env": {"API_KEY": "secret123"},
            "context": {},
        }

        result = resolver.resolve("{{env.API_KEY}}", context)
        assert result == "secret123"

    def test_resolve_env_from_os_environ(self):
        """Test resolving {{env.VAR}} from os.environ."""
        resolver = TemplateResolver()

        # Set environment variable
        os.environ["TEST_FLOWMASON_VAR"] = "test_value"

        context = {
            "input": {},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("{{env.TEST_FLOWMASON_VAR}}", context)
        assert result == "test_value"

        # Clean up
        del os.environ["TEST_FLOWMASON_VAR"]


class TestTemplateResolverTypePreservation:
    """Tests for preserving types during resolution."""

    def test_preserve_integer_type(self):
        """Single template should preserve integer type."""
        resolver = TemplateResolver()
        context = {
            "input": {"count": 42},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("{{input.count}}", context)
        assert result == 42
        assert isinstance(result, int)

    def test_preserve_float_type(self):
        """Single template should preserve float type."""
        resolver = TemplateResolver()
        context = {
            "input": {"score": 0.95},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("{{input.score}}", context)
        assert result == 0.95
        assert isinstance(result, float)

    def test_preserve_bool_type(self):
        """Single template should preserve boolean type."""
        resolver = TemplateResolver()
        context = {
            "input": {"active": True, "disabled": False},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("{{input.active}}", context)
        assert result is True

        result = resolver.resolve("{{input.disabled}}", context)
        assert result is False

    def test_preserve_dict_type(self):
        """Single template should preserve dict type."""
        resolver = TemplateResolver()
        context = {
            "input": {"metadata": {"key": "value", "count": 5}},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("{{input.metadata}}", context)
        assert result == {"key": "value", "count": 5}
        assert isinstance(result, dict)

    def test_preserve_list_type(self):
        """Single template should preserve list type."""
        resolver = TemplateResolver()
        context = {
            "input": {"items": ["a", "b", "c"]},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("{{input.items}}", context)
        assert result == ["a", "b", "c"]
        assert isinstance(result, list)


class TestTemplateResolverEmbedded:
    """Tests for embedded templates in strings."""

    def test_embedded_single_template(self):
        """Test template embedded in string."""
        resolver = TemplateResolver()
        context = {
            "input": {"name": "Alice"},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("Hello, {{input.name}}!", context)
        assert result == "Hello, Alice!"

    def test_embedded_multiple_templates(self):
        """Test multiple templates in one string."""
        resolver = TemplateResolver()
        context = {
            "input": {"first": "Alice", "last": "Smith"},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("Name: {{input.first}} {{input.last}}", context)
        assert result == "Name: Alice Smith"

    def test_embedded_mixed_sources(self):
        """Test templates from different sources in one string."""
        resolver = TemplateResolver()
        context = {
            "input": {"user": "Alice"},
            "context": {"run_id": "123"},
            "upstream": {},
            "env": {},
        }

        result = resolver.resolve(
            "User {{input.user}} in run {{context.run_id}}",
            context
        )
        assert result == "User Alice in run 123"


class TestTemplateResolverRecursive:
    """Tests for recursive resolution in dicts and lists."""

    def test_resolve_dict_values(self):
        """Test resolving templates in dict values."""
        resolver = TemplateResolver()
        context = {
            "input": {"name": "Alice", "age": 30},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve({
            "user_name": "{{input.name}}",
            "user_age": "{{input.age}}",
            "static": "hello",
        }, context)

        assert result["user_name"] == "Alice"
        assert result["user_age"] == 30
        assert result["static"] == "hello"

    def test_resolve_list_items(self):
        """Test resolving templates in list items."""
        resolver = TemplateResolver()
        context = {
            "input": {"a": 1, "b": 2},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve(["{{input.a}}", "{{input.b}}", "static"], context)

        assert result == [1, 2, "static"]

    def test_resolve_nested_structures(self):
        """Test resolving templates in deeply nested structures."""
        resolver = TemplateResolver()
        context = {
            "input": {"value": "test"},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve({
            "level1": {
                "level2": {
                    "value": "{{input.value}}"
                }
            }
        }, context)

        assert result["level1"]["level2"]["value"] == "test"


class TestTemplateResolverErrors:
    """Tests for error handling."""

    def test_invalid_prefix_error(self):
        """Test error on invalid template prefix."""
        resolver = TemplateResolver(strict_mode=True)
        context = {
            "input": {},
            "upstream": {},
            "env": {},
            "context": {},
        }

        with pytest.raises(TemplateError) as exc_info:
            resolver.resolve("{{invalid.field}}", context)

        assert "Invalid template prefix" in str(exc_info.value)

    def test_missing_key_error(self):
        """Test error on missing key in context."""
        resolver = TemplateResolver(strict_mode=True)
        context = {
            "input": {"a": 1},
            "upstream": {},
            "env": {},
            "context": {},
        }

        with pytest.raises(TemplateError) as exc_info:
            resolver.resolve("{{input.nonexistent}}", context)

        assert "not found" in str(exc_info.value)

    def test_missing_env_var_error(self):
        """Test error on missing environment variable."""
        resolver = TemplateResolver(strict_mode=True)
        context = {
            "input": {},
            "upstream": {},
            "env": {},
            "context": {},
        }

        with pytest.raises(TemplateError) as exc_info:
            resolver.resolve("{{env.NONEXISTENT_VAR_12345}}", context)

        assert "not found" in str(exc_info.value)

    def test_non_strict_mode_preserves_templates(self):
        """Test that non-strict mode preserves unresolvable templates."""
        resolver = TemplateResolver(strict_mode=False)
        context = {
            "input": {},
            "upstream": {},
            "env": {},
            "context": {},
        }

        result = resolver.resolve("Value: {{input.missing}}", context)
        assert result == "Value: {{input.missing}}"


class TestTemplateResolverUtilities:
    """Tests for utility methods."""

    def test_find_templates(self):
        """Test finding all templates in a value."""
        resolver = TemplateResolver()

        templates = resolver.find_templates("{{input.a}} and {{upstream.b.c}}")
        assert "input.a" in templates
        assert "upstream.b.c" in templates

    def test_find_templates_in_dict(self):
        """Test finding templates in dict."""
        resolver = TemplateResolver()

        templates = resolver.find_templates({
            "field1": "{{input.x}}",
            "field2": "{{upstream.stage.y}}",
        })

        assert "input.x" in templates
        assert "upstream.stage.y" in templates

    def test_get_dependencies(self):
        """Test extracting upstream dependencies."""
        resolver = TemplateResolver()

        deps = resolver.get_dependencies({
            "field1": "{{upstream.stage1.output}}",
            "field2": "{{upstream.stage2.result}}",
            "field3": "{{input.value}}",
        })

        assert "stage1" in deps
        assert "stage2" in deps
        assert len(deps) == 2

    def test_validate_templates_success(self):
        """Test template validation with valid context."""
        resolver = TemplateResolver()
        context = {
            "input": {"name": "test"},
            "upstream": {"prev": {"result": "ok"}},
            "env": {},
            "context": {},
        }

        errors = resolver.validate_templates(
            "{{input.name}} - {{upstream.prev.result}}",
            context
        )

        assert len(errors) == 0

    def test_validate_templates_failure(self):
        """Test template validation catches errors."""
        resolver = TemplateResolver()
        context = {
            "input": {},
            "upstream": {},
            "env": {},
            "context": {},
        }

        errors = resolver.validate_templates("{{input.missing}}", context)

        assert len(errors) > 0
        assert "missing" in errors[0].lower() or "not found" in errors[0].lower()
