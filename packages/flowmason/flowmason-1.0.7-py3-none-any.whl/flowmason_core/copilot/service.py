"""
Copilot Service for FlowMason.

Main service for AI-assisted pipeline development.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from flowmason_core.copilot.context import CopilotContext
from flowmason_core.copilot.prompts import CopilotPrompts

logger = logging.getLogger(__name__)


class SuggestionType(str, Enum):
    """Type of suggestion from the copilot."""
    ADD_STAGE = "add_stage"
    MODIFY_STAGE = "modify_stage"
    REMOVE_STAGE = "remove_stage"
    ADD_DEPENDENCY = "add_dependency"
    MODIFY_CONFIG = "modify_config"
    MODIFY_SCHEMA = "modify_schema"


@dataclass
class Suggestion:
    """A single suggestion from the copilot."""
    type: SuggestionType
    stage_id: Optional[str] = None
    description: str = ""
    config: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "stage_id": self.stage_id,
            "description": self.description,
            "config": self.config,
            "reasoning": self.reasoning,
        }


@dataclass
class SuggestResponse:
    """Response from suggestion request."""
    suggestions: List[Suggestion] = field(default_factory=list)
    explanation: str = ""
    raw_response: str = ""


@dataclass
class ExplainResponse:
    """Response from explain request."""
    summary: str = ""
    steps: List[str] = field(default_factory=list)
    data_flow: str = ""
    raw_response: str = ""


@dataclass
class GenerateResponse:
    """Response from generate request."""
    pipeline: Optional[Dict[str, Any]] = None
    explanation: str = ""
    raw_response: str = ""


@dataclass
class DebugResponse:
    """Response from debug request."""
    diagnosis: str = ""
    root_cause: str = ""
    fixes: List[Dict[str, Any]] = field(default_factory=list)
    prevention: str = ""
    raw_response: str = ""


class CopilotService:
    """
    AI Copilot Service for FlowMason.

    Provides AI-assisted capabilities:
    - Suggestions for pipeline modifications
    - Pipeline explanations
    - Pipeline generation from natural language
    - Debugging assistance
    - Optimization recommendations
    """

    def __init__(
        self,
        provider: str = "anthropic",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the copilot service.

        Args:
            provider: LLM provider ("anthropic", "openai")
            model: Model to use (defaults to provider's best model)
            api_key: API key (defaults to environment variable)
        """
        self.provider = provider
        self.model = model or self._default_model(provider)
        self.api_key = api_key
        self._client = None

    def _default_model(self, provider: str) -> str:
        """Get default model for provider."""
        defaults = {
            "anthropic": "claude-sonnet-4-20250514",
            "openai": "gpt-4o",
        }
        return defaults.get(provider, "claude-sonnet-4-20250514")

    def _get_client(self):
        """Get or create the LLM client."""
        if self._client is not None:
            return self._client

        if self.provider == "anthropic":
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
        elif self.provider == "openai":
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        return self._client

    async def suggest(
        self,
        request: str,
        context: CopilotContext,
    ) -> SuggestResponse:
        """
        Get suggestions for pipeline modifications.

        Args:
            request: User's request/question
            context: Current pipeline context

        Returns:
            SuggestResponse with suggestions
        """
        prompt = CopilotPrompts.suggest_prompt(
            context=context.to_prompt_context(),
            request=request,
        )

        response = await self._call_llm(prompt)

        # Parse response
        suggestions = []
        explanation = ""

        try:
            data = self._extract_json(response)
            if data:
                for s in data.get("suggestions", []):
                    suggestions.append(Suggestion(
                        type=SuggestionType(s.get("type", "modify_config")),
                        stage_id=s.get("stage_id"),
                        description=s.get("description", ""),
                        config=s.get("config"),
                        reasoning=s.get("reasoning"),
                    ))
                explanation = data.get("explanation", "")
        except Exception as e:
            logger.warning(f"Failed to parse suggestions: {e}")
            explanation = response

        return SuggestResponse(
            suggestions=suggestions,
            explanation=explanation,
            raw_response=response,
        )

    async def explain(self, context: CopilotContext) -> ExplainResponse:
        """
        Get an explanation of a pipeline.

        Args:
            context: Pipeline context to explain

        Returns:
            ExplainResponse with explanation
        """
        prompt = CopilotPrompts.explain_prompt(
            context=context.to_prompt_context(),
        )

        response = await self._call_llm(prompt)

        return ExplainResponse(
            summary=response,
            raw_response=response,
        )

    async def generate(
        self,
        description: str,
        available_components: Optional[List[str]] = None,
    ) -> GenerateResponse:
        """
        Generate a pipeline from natural language description.

        Args:
            description: Natural language description of desired pipeline
            available_components: List of available component types

        Returns:
            GenerateResponse with generated pipeline
        """
        components_str = ", ".join(available_components) if available_components else "generator, http_request, json_transform, schema_validate, filter, loop, trycatch, selector, logger"

        prompt = CopilotPrompts.generate_prompt(
            description=description,
            available_components=components_str,
        )

        response = await self._call_llm(prompt)

        # Parse pipeline from response
        pipeline = None
        try:
            pipeline = self._extract_json(response)
        except Exception as e:
            logger.warning(f"Failed to parse generated pipeline: {e}")

        return GenerateResponse(
            pipeline=pipeline,
            explanation=response,
            raw_response=response,
        )

    async def debug(
        self,
        context: CopilotContext,
        error_message: str,
    ) -> DebugResponse:
        """
        Get debugging assistance for pipeline errors.

        Args:
            context: Pipeline context with execution state
            error_message: The error message to diagnose

        Returns:
            DebugResponse with diagnosis and fixes
        """
        prompt = CopilotPrompts.debug_prompt(
            context=context.to_prompt_context(),
            error=error_message,
        )

        response = await self._call_llm(prompt)

        # Parse response
        diagnosis = ""
        root_cause = ""
        fixes = []
        prevention = ""

        try:
            data = self._extract_json(response)
            if data:
                diagnosis = data.get("diagnosis", "")
                root_cause = data.get("root_cause", "")
                fixes = data.get("fixes", [])
                prevention = data.get("prevention", "")
        except Exception as e:
            logger.warning(f"Failed to parse debug response: {e}")
            diagnosis = response

        return DebugResponse(
            diagnosis=diagnosis,
            root_cause=root_cause,
            fixes=fixes,
            prevention=prevention,
            raw_response=response,
        )

    async def optimize(self, context: CopilotContext) -> Dict[str, Any]:
        """
        Get optimization suggestions for a pipeline.

        Args:
            context: Pipeline context to optimize

        Returns:
            Dictionary with optimization suggestions
        """
        prompt = CopilotPrompts.optimize_prompt(
            context=context.to_prompt_context(),
        )

        response = await self._call_llm(prompt)

        try:
            return self._extract_json(response) or {"raw": response}
        except Exception:
            return {"raw": response}

    async def chat(
        self,
        message: str,
        context: CopilotContext,
    ) -> str:
        """
        Have a conversational interaction with the copilot.

        Args:
            message: User's message
            context: Current context

        Returns:
            Copilot's response
        """
        # Build conversation history
        history = ""
        for msg in context.conversation_history[-10:]:  # Last 10 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history += f"\n{role.upper()}: {content}\n"

        prompt = CopilotPrompts.conversation_prompt(
            context=context.to_prompt_context(),
            history=history,
            message=message,
        )

        response = await self._call_llm(prompt)
        return response

    async def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM with a prompt.

        Args:
            prompt: The prompt to send

        Returns:
            The LLM's response text
        """
        client = self._get_client()

        if self.provider == "anthropic":
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

        elif self.provider == "openai":
            response = client.chat.completions.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        raise ValueError(f"Unsupported provider: {self.provider}")

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from LLM response.

        Handles responses that include JSON in code blocks.
        """
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to parse the entire response as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in text
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return None
