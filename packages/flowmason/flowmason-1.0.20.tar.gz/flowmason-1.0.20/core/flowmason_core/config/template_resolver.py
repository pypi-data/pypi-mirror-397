"""
Template Resolver for FlowMason.

Resolves template variables in pipeline configurations.
Supports:
- {{input.field}} - Pipeline input fields
- {{upstream.stage_id.field}} - Output from previous stages
- {{env.VAR_NAME}} - Environment variables
- {{context.field}} - Execution context fields
"""

import os
import re
from typing import Any, Dict, List

from flowmason_core.config.types import TemplateError


class TemplateResolver:
    """
    Resolves template variables like {{input.field}} to actual values.

    Template Syntax:
        - {{input.field}} - Access pipeline input
        - {{input.nested.field}} - Access nested input fields
        - {{upstream.stage_id.field}} - Access output from stage 'stage_id'
        - {{env.VAR_NAME}} - Access environment variable
        - {{context.run_id}} - Access execution context

    Example:
        resolver = TemplateResolver()
        context = {
            "input": {"ticket_text": "Help me!"},
            "upstream": {"enrich": {"customer_tier": "premium"}},
            "env": {"API_KEY": "secret"},
            "context": {"run_id": "run_123"}
        }
        result = resolver.resolve("{{input.ticket_text}}", context)
        # result == "Help me!"
    """

    # Pattern for {{variable.path}} templates
    TEMPLATE_PATTERN = re.compile(r"\{\{([^}]+)\}\}")

    # Allowed template prefixes
    ALLOWED_PREFIXES = {"input", "upstream", "env", "context"}

    def __init__(self, strict_mode: bool = True):
        """
        Initialize the resolver.

        Args:
            strict_mode: If True, raise errors for unresolvable templates.
                        If False, leave unresolvable templates as-is.
        """
        self.strict_mode = strict_mode

    def resolve(self, template: Any, context: Dict[str, Any]) -> Any:
        """
        Resolve a template value.

        If the value is a string containing {{...}}, resolve the template.
        If the value is a dict or list, recursively resolve all values.
        Otherwise, return the value unchanged.

        Args:
            template: The value to resolve (may be string, dict, list, or scalar)
            context: Resolution context with 'input', 'upstream', 'env', 'context' keys

        Returns:
            Resolved value

        Raises:
            TemplateError: If template cannot be resolved (in strict mode)
        """
        if isinstance(template, str):
            return self._resolve_string(template, context)
        elif isinstance(template, dict):
            return {k: self.resolve(v, context) for k, v in template.items()}
        elif isinstance(template, list):
            return [self.resolve(item, context) for item in template]
        else:
            # Scalar value - return unchanged
            return template

    def _resolve_string(self, template: str, context: Dict[str, Any]) -> Any:
        """
        Resolve template variables in a string.

        If the entire string is a single template (e.g., "{{input.field}}"),
        return the value directly (preserving type).
        If the string contains embedded templates (e.g., "Hello {{input.name}}!"),
        return a string with templates replaced.
        """
        # Check if entire string is a single template
        if self._is_single_template(template):
            return self._resolve_single_template(template, context)

        # Multiple templates or text mixed with templates
        def replacer(match: re.Match) -> str:
            var_path = match.group(1).strip()
            try:
                value = self._get_value_at_path(var_path, context)
                return str(value) if value is not None else ""
            except TemplateError:
                if self.strict_mode:
                    raise
                return str(match.group(0))  # Return original template

        return str(self.TEMPLATE_PATTERN.sub(replacer, template))

    def _is_single_template(self, template: str) -> bool:
        """Check if the string is a single template with no other text."""
        stripped = template.strip()
        if not stripped.startswith("{{") or not stripped.endswith("}}"):
            return False

        # Count template occurrences
        matches = self.TEMPLATE_PATTERN.findall(template)
        return len(matches) == 1 and stripped == f"{{{{{matches[0]}}}}}"

    def _resolve_single_template(self, template: str, context: Dict[str, Any]) -> Any:
        """Resolve a single template and return the value with its original type."""
        match = self.TEMPLATE_PATTERN.search(template)
        if not match:
            return template

        var_path = match.group(1).strip()
        return self._get_value_at_path(var_path, context)

    def _get_value_at_path(self, var_path: str, context: Dict[str, Any]) -> Any:
        """
        Get value at a dot-separated path.

        Args:
            var_path: Path like "input.field.nested" or "upstream.stage_id.field"
            context: Resolution context

        Returns:
            Value at the path

        Raises:
            TemplateError: If path cannot be resolved
        """
        parts = var_path.split(".")
        if not parts:
            raise TemplateError(var_path, "Empty template path")

        prefix = parts[0]
        if prefix not in self.ALLOWED_PREFIXES:
            raise TemplateError(
                var_path,
                f"Invalid template prefix '{prefix}'. "
                f"Allowed prefixes: {', '.join(sorted(self.ALLOWED_PREFIXES))}"
            )

        # Special handling for env variables
        if prefix == "env":
            if len(parts) != 2:
                raise TemplateError(
                    var_path,
                    "Environment variables must be accessed as {{env.VAR_NAME}}"
                )
            var_name = parts[1]
            # First check context.env, then os.environ
            env_context = context.get("env", {})
            if var_name in env_context:
                return env_context[var_name]
            if var_name in os.environ:
                return os.environ[var_name]
            raise TemplateError(var_path, f"Environment variable '{var_name}' not found")

        # Navigate the path
        try:
            value = context
            for part in parts:
                if isinstance(value, dict):
                    if part not in value:
                        raise TemplateError(
                            var_path,
                            f"Key '{part}' not found in context"
                        )
                    value = value[part]
                elif hasattr(value, part):
                    value = getattr(value, part)
                else:
                    raise TemplateError(
                        var_path,
                        f"Cannot access '{part}' on value of type {type(value).__name__}"
                    )
            return value
        except TemplateError:
            raise
        except Exception as e:
            raise TemplateError(var_path, str(e))

    def find_templates(self, value: Any) -> List[str]:
        """
        Find all template variables in a value.

        Args:
            value: Value to search (string, dict, list, or scalar)

        Returns:
            List of template variable paths (e.g., ["input.field", "upstream.stage.result"])
        """
        templates = []

        if isinstance(value, str):
            templates.extend(self.TEMPLATE_PATTERN.findall(value))
        elif isinstance(value, dict):
            for v in value.values():
                templates.extend(self.find_templates(v))
        elif isinstance(value, list):
            for item in value:
                templates.extend(self.find_templates(item))

        return [t.strip() for t in templates]

    def validate_templates(
        self,
        value: Any,
        available_context: Dict[str, Any]
    ) -> List[str]:
        """
        Validate that all templates in a value can be resolved.

        Args:
            value: Value containing templates
            available_context: Context that will be available at runtime

        Returns:
            List of error messages (empty if all valid)
        """
        errors = []
        templates = self.find_templates(value)

        for template_path in templates:
            try:
                self._get_value_at_path(template_path, available_context)
            except TemplateError as e:
                errors.append(f"Template {{{{{{template_path}}}}}}: {e.message}")

        return errors

    def get_dependencies(self, value: Any) -> List[str]:
        """
        Get the upstream stage IDs that a value depends on.

        Args:
            value: Value containing templates

        Returns:
            List of stage IDs referenced via {{upstream.stage_id.*}}
        """
        templates = self.find_templates(value)
        dependencies = set()

        for template_path in templates:
            parts = template_path.split(".")
            if len(parts) >= 2 and parts[0] == "upstream":
                dependencies.add(parts[1])

        return list(dependencies)
