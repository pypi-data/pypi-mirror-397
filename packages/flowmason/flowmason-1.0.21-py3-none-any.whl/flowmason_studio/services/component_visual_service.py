"""
Component Visual Service.

Generates rich visual representations of pipeline components.
"""

from typing import Any, Dict, List, Optional

from flowmason_studio.models.component_visual import (
    ComponentBadge,
    ComponentCapability,
    ComponentCategory,
    ComponentGroup,
    ComponentPalette,
    ComponentPort,
    ComponentPreview,
    ComponentTheme,
    ComponentVisual,
    ConnectionStyle,
    ConnectionVisual,
    PipelineVisual,
    PortDirection,
    PortType,
    StageVisual,
)

# Theme definitions for component categories
CATEGORY_THEMES: Dict[ComponentCategory, ComponentTheme] = {
    ComponentCategory.AI: ComponentTheme(
        primary_color="#8b5cf6",
        secondary_color="#a78bfa",
        icon="sparkles",
        icon_color="#ffffff",
        gradient="linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)",
    ),
    ComponentCategory.DATA: ComponentTheme(
        primary_color="#3b82f6",
        secondary_color="#60a5fa",
        icon="database",
        icon_color="#ffffff",
        gradient="linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
    ),
    ComponentCategory.INTEGRATION: ComponentTheme(
        primary_color="#10b981",
        secondary_color="#34d399",
        icon="plug",
        icon_color="#ffffff",
        gradient="linear-gradient(135deg, #10b981 0%, #059669 100%)",
    ),
    ComponentCategory.CONTROL: ComponentTheme(
        primary_color="#f59e0b",
        secondary_color="#fbbf24",
        icon="git-branch",
        icon_color="#ffffff",
        gradient="linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
    ),
    ComponentCategory.UTILITY: ComponentTheme(
        primary_color="#6b7280",
        secondary_color="#9ca3af",
        icon="wrench",
        icon_color="#ffffff",
        gradient="linear-gradient(135deg, #6b7280 0%, #4b5563 100%)",
    ),
    ComponentCategory.CUSTOM: ComponentTheme(
        primary_color="#ec4899",
        secondary_color="#f472b6",
        icon="puzzle-piece",
        icon_color="#ffffff",
        gradient="linear-gradient(135deg, #ec4899 0%, #db2777 100%)",
    ),
}

# Component type to category mapping
COMPONENT_CATEGORIES: Dict[str, ComponentCategory] = {
    "generator": ComponentCategory.AI,
    "critic": ComponentCategory.AI,
    "improver": ComponentCategory.AI,
    "synthesizer": ComponentCategory.AI,
    "selector": ComponentCategory.AI,
    "filter": ComponentCategory.DATA,
    "json_transform": ComponentCategory.DATA,
    "schema_validate": ComponentCategory.DATA,
    "variable_set": ComponentCategory.DATA,
    "http_request": ComponentCategory.INTEGRATION,
    "webhook": ComponentCategory.INTEGRATION,
    "logger": ComponentCategory.UTILITY,
    "loop": ComponentCategory.CONTROL,
    "foreach": ComponentCategory.CONTROL,
    "conditional": ComponentCategory.CONTROL,
    "parallel": ComponentCategory.CONTROL,
    "output_router": ComponentCategory.CONTROL,
}

# Icon mapping for components
COMPONENT_ICONS: Dict[str, str] = {
    "generator": "sparkles",
    "critic": "clipboard-check",
    "improver": "arrow-trending-up",
    "synthesizer": "beaker",
    "selector": "cursor-arrow-rays",
    "filter": "funnel",
    "json_transform": "code-bracket",
    "schema_validate": "shield-check",
    "variable_set": "variable",
    "http_request": "globe-alt",
    "webhook": "bolt",
    "logger": "document-text",
    "loop": "arrow-path",
    "foreach": "queue-list",
    "conditional": "arrows-right-left",
    "parallel": "squares-plus",
    "output_router": "arrow-path-rounded-square",
}

# Capability definitions
COMPONENT_CAPABILITIES: Dict[str, List[Dict[str, str]]] = {
    "generator": [
        {"id": "llm", "name": "LLM Integration", "description": "Uses language model", "level": "advanced"},
        {"id": "streaming", "name": "Streaming", "description": "Supports streaming output", "level": "standard"},
    ],
    "critic": [
        {"id": "llm", "name": "LLM Integration", "description": "Uses language model", "level": "advanced"},
        {"id": "evaluation", "name": "Evaluation", "description": "Provides quality scores", "level": "standard"},
    ],
    "filter": [
        {"id": "conditional", "name": "Conditional Logic", "description": "Filters based on conditions", "level": "basic"},
    ],
    "json_transform": [
        {"id": "jmespath", "name": "JMESPath", "description": "Supports JMESPath queries", "level": "standard"},
        {"id": "jsonpath", "name": "JSONPath", "description": "Supports JSONPath queries", "level": "standard"},
    ],
    "http_request": [
        {"id": "http", "name": "HTTP Client", "description": "Makes HTTP requests", "level": "basic"},
        {"id": "auth", "name": "Authentication", "description": "Supports auth methods", "level": "standard"},
    ],
    "loop": [
        {"id": "iteration", "name": "Iteration", "description": "Loop control", "level": "standard"},
        {"id": "break", "name": "Break Conditions", "description": "Early exit support", "level": "advanced"},
    ],
}


class ComponentVisualService:
    """Service for generating component visual representations."""

    def __init__(self):
        """Initialize the service."""
        self._favorites: List[str] = []
        self._recently_used: List[str] = []
        self._usage_counts: Dict[str, int] = {}

    def get_component_visual(
        self,
        component_type: str,
        component_info: Optional[Dict[str, Any]] = None,
        include_preview: bool = True,
        include_capabilities: bool = True,
    ) -> ComponentVisual:
        """
        Generate visual representation for a component.

        Args:
            component_type: The component type ID
            component_info: Optional component metadata from registry
            include_preview: Whether to include preview snippet
            include_capabilities: Whether to include capabilities

        Returns:
            ComponentVisual with full visual metadata
        """
        # Determine category
        category = COMPONENT_CATEGORIES.get(component_type, ComponentCategory.CUSTOM)

        # Get theme
        theme = CATEGORY_THEMES[category].model_copy()
        if component_type in COMPONENT_ICONS:
            theme.icon = COMPONENT_ICONS[component_type]

        # Build component info
        name = component_info.get("name", component_type.replace("_", " ").title()) if component_info else component_type.replace("_", " ").title()
        description = component_info.get("description", f"A {name} component") if component_info else f"A {name} component"

        # Generate ports from schema
        ports = self._generate_ports(component_type, component_info)

        # Generate badges
        badges = self._generate_badges(component_type, component_info)

        # Generate capabilities
        capabilities = []
        if include_capabilities:
            capabilities = self._generate_capabilities(component_type)

        # Generate preview
        preview = None
        if include_preview:
            preview = self._generate_preview(component_type, component_info)

        # Get usage stats
        usage_count = self._usage_counts.get(component_type, 0)
        popularity = min(1.0, usage_count / 100) if usage_count > 0 else 0.0

        return ComponentVisual(
            component_type=component_type,
            name=name,
            description=description,
            category=category,
            theme=theme,
            ports=ports,
            badges=badges,
            capabilities=capabilities,
            preview=preview,
            usage_count=usage_count,
            popularity_score=popularity,
            tags=self._get_tags(component_type, category),
        )

    def _generate_ports(
        self,
        component_type: str,
        component_info: Optional[Dict[str, Any]] = None,
    ) -> List[ComponentPort]:
        """Generate input/output ports for a component."""
        ports = []

        # Standard input port
        ports.append(
            ComponentPort(
                id="input",
                name="Input",
                direction=PortDirection.INPUT,
                type=PortType.ANY,
                description="Main input data",
                required=True,
            )
        )

        # Component-specific inputs
        if component_type == "generator":
            ports.append(
                ComponentPort(
                    id="prompt",
                    name="Prompt",
                    direction=PortDirection.INPUT,
                    type=PortType.STRING,
                    description="The prompt template",
                    required=True,
                )
            )
        elif component_type == "filter":
            ports.append(
                ComponentPort(
                    id="condition",
                    name="Condition",
                    direction=PortDirection.INPUT,
                    type=PortType.STRING,
                    description="Filter condition expression",
                    required=True,
                )
            )
        elif component_type == "http_request":
            ports.append(
                ComponentPort(
                    id="url",
                    name="URL",
                    direction=PortDirection.INPUT,
                    type=PortType.STRING,
                    description="Request URL",
                    required=True,
                )
            )
        elif component_type == "json_transform":
            ports.append(
                ComponentPort(
                    id="query",
                    name="Query",
                    direction=PortDirection.INPUT,
                    type=PortType.STRING,
                    description="JMESPath or JSONPath query",
                    required=True,
                )
            )

        # Standard output port
        ports.append(
            ComponentPort(
                id="output",
                name="Output",
                direction=PortDirection.OUTPUT,
                type=PortType.ANY,
                description="Stage output data",
            )
        )

        # Component-specific outputs
        if component_type in ["critic", "selector"]:
            ports.append(
                ComponentPort(
                    id="score",
                    name="Score",
                    direction=PortDirection.OUTPUT,
                    type=PortType.NUMBER,
                    description="Evaluation score",
                )
            )
        elif component_type == "filter":
            ports.append(
                ComponentPort(
                    id="filtered",
                    name="Filtered",
                    direction=PortDirection.OUTPUT,
                    type=PortType.ARRAY,
                    description="Filtered items",
                )
            )
            ports.append(
                ComponentPort(
                    id="excluded",
                    name="Excluded",
                    direction=PortDirection.OUTPUT,
                    type=PortType.ARRAY,
                    description="Excluded items",
                )
            )
        elif component_type == "conditional":
            ports.append(
                ComponentPort(
                    id="true_branch",
                    name="True",
                    direction=PortDirection.OUTPUT,
                    type=PortType.ANY,
                    description="Output when condition is true",
                )
            )
            ports.append(
                ComponentPort(
                    id="false_branch",
                    name="False",
                    direction=PortDirection.OUTPUT,
                    type=PortType.ANY,
                    description="Output when condition is false",
                )
            )

        return ports

    def _generate_badges(
        self,
        component_type: str,
        component_info: Optional[Dict[str, Any]] = None,
    ) -> List[ComponentBadge]:
        """Generate status badges for a component."""
        badges = []

        # LLM badge for AI components
        if component_type in ["generator", "critic", "improver", "synthesizer", "selector"]:
            badges.append(
                ComponentBadge(
                    id="llm",
                    label="LLM",
                    color="primary",
                    icon="sparkles",
                    tooltip="Uses language model",
                )
            )

        # Integration badge
        if component_type in ["http_request", "webhook"]:
            badges.append(
                ComponentBadge(
                    id="external",
                    label="External",
                    color="info",
                    icon="globe",
                    tooltip="Connects to external services",
                )
            )

        # Control flow badge
        if component_type in ["loop", "foreach", "conditional", "parallel"]:
            badges.append(
                ComponentBadge(
                    id="control",
                    label="Control",
                    color="warning",
                    icon="git-branch",
                    tooltip="Control flow component",
                )
            )

        # Add favorite badge if applicable
        if component_type in self._favorites:
            badges.append(
                ComponentBadge(
                    id="favorite",
                    label="Favorite",
                    color="danger",
                    icon="heart",
                    tooltip="Marked as favorite",
                )
            )

        return badges

    def _generate_capabilities(
        self,
        component_type: str,
    ) -> List[ComponentCapability]:
        """Generate capability list for a component."""
        cap_defs = COMPONENT_CAPABILITIES.get(component_type, [])
        return [
            ComponentCapability(**cap)
            for cap in cap_defs
        ]

    def _generate_preview(
        self,
        component_type: str,
        component_info: Optional[Dict[str, Any]] = None,
    ) -> ComponentPreview:
        """Generate preview snippet for a component."""
        previews = {
            "generator": ComponentPreview(
                type="code",
                content='prompt: "Summarize the following: {{input}}"',
                language="yaml",
            ),
            "filter": ComponentPreview(
                type="code",
                content='condition: "item.status == \'active\'"',
                language="yaml",
            ),
            "json_transform": ComponentPreview(
                type="code",
                content='query: "data[*].{name: name, value: score}"',
                language="yaml",
            ),
            "http_request": ComponentPreview(
                type="code",
                content='url: "https://api.example.com/data"\nmethod: "GET"',
                language="yaml",
            ),
            "loop": ComponentPreview(
                type="code",
                content='max_iterations: 10\nbreak_condition: "result.done"',
                language="yaml",
            ),
        }
        return previews.get(
            component_type,
            ComponentPreview(type="text", content=f"Configure {component_type} settings"),
        )

    def _get_tags(self, component_type: str, category: ComponentCategory) -> List[str]:
        """Get tags for a component."""
        tags = [category.value]

        tag_mappings = {
            "generator": ["llm", "text", "generation"],
            "critic": ["llm", "evaluation", "quality"],
            "improver": ["llm", "refinement", "iteration"],
            "filter": ["data", "filtering", "conditions"],
            "json_transform": ["data", "transformation", "query"],
            "http_request": ["api", "http", "integration"],
            "webhook": ["api", "events", "integration"],
            "loop": ["control", "iteration", "flow"],
            "foreach": ["control", "iteration", "batch"],
            "conditional": ["control", "branching", "logic"],
        }

        tags.extend(tag_mappings.get(component_type, []))
        return tags

    def get_palette(
        self,
        categories: Optional[List[ComponentCategory]] = None,
        component_registry: Optional[Any] = None,
    ) -> ComponentPalette:
        """
        Get the component palette with all available components.

        Args:
            categories: Filter to specific categories
            component_registry: Optional registry to get real components

        Returns:
            ComponentPalette with grouped components
        """
        # Define groups
        groups = [
            ComponentGroup(
                id="ai",
                name="AI Components",
                description="LLM-powered components for generation and evaluation",
                icon="sparkles",
                color="#8b5cf6",
                components=["generator", "critic", "improver", "synthesizer", "selector"],
                order=1,
            ),
            ComponentGroup(
                id="data",
                name="Data Processing",
                description="Transform and validate data",
                icon="database",
                color="#3b82f6",
                components=["filter", "json_transform", "schema_validate", "variable_set"],
                order=2,
            ),
            ComponentGroup(
                id="integration",
                name="Integrations",
                description="Connect to external services",
                icon="plug",
                color="#10b981",
                components=["http_request", "webhook"],
                order=3,
            ),
            ComponentGroup(
                id="control",
                name="Control Flow",
                description="Manage execution flow",
                icon="git-branch",
                color="#f59e0b",
                components=["loop", "foreach", "conditional", "parallel", "output_router"],
                order=4,
            ),
            ComponentGroup(
                id="utility",
                name="Utilities",
                description="Helper components",
                icon="wrench",
                color="#6b7280",
                components=["logger"],
                order=5,
            ),
        ]

        # Filter by categories if specified
        if categories:
            category_map = {
                ComponentCategory.AI: "ai",
                ComponentCategory.DATA: "data",
                ComponentCategory.INTEGRATION: "integration",
                ComponentCategory.CONTROL: "control",
                ComponentCategory.UTILITY: "utility",
            }
            allowed_ids = [category_map.get(c) for c in categories if c in category_map]
            groups = [g for g in groups if g.id in allowed_ids]

        return ComponentPalette(
            groups=groups,
            recently_used=self._recently_used[:10],
            favorites=self._favorites,
        )

    def get_pipeline_visual(
        self,
        pipeline_id: str,
        pipeline_data: Dict[str, Any],
        execution_state: Optional[Dict[str, Any]] = None,
    ) -> PipelineVisual:
        """
        Generate visual representation of a pipeline.

        Args:
            pipeline_id: The pipeline ID
            pipeline_data: Pipeline configuration data
            execution_state: Optional execution state for status

        Returns:
            PipelineVisual with complete visual data
        """
        stages = []
        connections = []

        # Layout parameters
        stage_width = 250
        stage_height = 150
        horizontal_gap = 100
        vertical_gap = 50
        start_x = 50
        start_y = 50

        # Track stage positions for connections
        stage_positions: Dict[str, Dict[str, float]] = {}

        # Generate stage visuals
        pipeline_stages = pipeline_data.get("stages", [])
        for i, stage in enumerate(pipeline_stages):
            stage_id = stage.get("id", f"stage_{i}")
            component_type = stage.get("component_type", "generator")

            # Calculate position (simple horizontal layout)
            # In real implementation, this would use dependency graph
            x = start_x + i * (stage_width + horizontal_gap)
            y = start_y

            stage_positions[stage_id] = {"x": x, "y": y}

            # Get component visual
            component_visual = self.get_component_visual(
                component_type=component_type,
                component_info=stage.get("config"),
            )

            # Get execution status if available
            status = "idle"
            progress = None
            if execution_state:
                stage_state = execution_state.get("stages", {}).get(stage_id, {})
                status = stage_state.get("status", "idle")
                progress = stage_state.get("progress")

            stages.append(
                StageVisual(
                    stage_id=stage_id,
                    component=component_visual,
                    position={"x": x, "y": y},
                    size={"width": stage_width, "height": stage_height},
                    status=status,
                    progress=progress,
                )
            )

        # Generate connections from dependencies
        for stage in pipeline_stages:
            stage_id = stage.get("id")
            depends_on = stage.get("depends_on", [])

            for dep in depends_on:
                if dep in stage_positions and stage_id in stage_positions:
                    connections.append(
                        ConnectionVisual(
                            id=f"{dep}->{stage_id}",
                            source_stage=dep,
                            source_port="output",
                            target_stage=stage_id,
                            target_port="input",
                            style=ConnectionStyle(
                                type="bezier",
                                color="#94a3b8",
                                width=2,
                                animated=execution_state is not None,
                            ),
                        )
                    )

        return PipelineVisual(
            pipeline_id=pipeline_id,
            name=pipeline_data.get("name", "Untitled Pipeline"),
            stages=stages,
            connections=connections,
        )

    def update_favorites(self, favorites: List[str]) -> None:
        """Update favorite components."""
        self._favorites = favorites

    def add_to_recently_used(self, component_type: str) -> None:
        """Add component to recently used list."""
        if component_type in self._recently_used:
            self._recently_used.remove(component_type)
        self._recently_used.insert(0, component_type)
        self._recently_used = self._recently_used[:20]  # Keep last 20

        # Update usage count
        self._usage_counts[component_type] = self._usage_counts.get(component_type, 0) + 1

    def get_connection_style(
        self,
        source_type: str,
        target_type: str,
    ) -> ConnectionStyle:
        """Get appropriate connection style for two component types."""
        # Animated for AI components
        animated = source_type in ["generator", "critic", "improver"]

        # Different colors based on category
        category = COMPONENT_CATEGORIES.get(source_type, ComponentCategory.CUSTOM)
        color = CATEGORY_THEMES[category].primary_color

        return ConnectionStyle(
            type="bezier",
            color=color,
            width=2,
            animated=animated,
        )


# Singleton instance
_service: Optional[ComponentVisualService] = None


def get_component_visual_service() -> ComponentVisualService:
    """Get the singleton ComponentVisualService instance."""
    global _service
    if _service is None:
        _service = ComponentVisualService()
    return _service
