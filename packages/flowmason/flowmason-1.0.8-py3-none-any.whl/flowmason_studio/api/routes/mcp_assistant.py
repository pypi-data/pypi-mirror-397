"""
MCP AI Assistant API Routes.

Provides HTTP API for AI-assisted MCP tool discovery and usage.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from flowmason_studio.models.mcp_assistant import (
    AnalyzeTaskRequest,
    AnalyzeTaskResponse,
    AutocompleteRequest,
    AutocompleteResult,
    ConversationContext,
    CreateChainRequest,
    EnhancedTool,
    ExplainToolRequest,
    SmartInvokeRequest,
    SmartInvokeResponse,
    TaskAnalysis,
    ToolCategory,
    ToolChain,
    ToolExplanation,
    ToolRecommendation,
)
from flowmason_studio.services.mcp_assistant_service import get_mcp_assistant_service

router = APIRouter(prefix="/mcp-assistant", tags=["mcp-assistant"])


# =============================================================================
# Tool Discovery
# =============================================================================


@router.get("/tools", response_model=List[EnhancedTool])
async def list_enhanced_tools(
    category: Optional[ToolCategory] = Query(None, description="Filter by category"),
) -> List[EnhancedTool]:
    """
    List all available MCP tools with enhanced AI-generated metadata.

    Each tool includes:
    - Categorization and capabilities
    - When to use hints
    - Prerequisites and related tools
    - Usage examples
    """
    service = get_mcp_assistant_service()
    tools = service.get_enhanced_tools()

    if category:
        tools = [t for t in tools if t.category == category]

    return tools


@router.get("/tools/{tool_name}", response_model=EnhancedTool)
async def get_enhanced_tool(tool_name: str) -> EnhancedTool:
    """
    Get enhanced information about a specific tool.
    """
    service = get_mcp_assistant_service()
    tools = service.get_enhanced_tools()

    tool = next((t for t in tools if t.name == tool_name), None)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    return tool


@router.get("/tools/search", response_model=List[EnhancedTool])
async def search_tools(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
) -> List[EnhancedTool]:
    """
    Search for tools by keyword.

    Searches tool names, descriptions, and capabilities.
    """
    service = get_mcp_assistant_service()
    tools = service.get_enhanced_tools()
    query_lower = q.lower()

    # Score and filter tools
    scored_tools = []
    for tool in tools:
        score = 0
        if query_lower in tool.name.lower():
            score += 3
        if query_lower in tool.description.lower():
            score += 2
        for cap in tool.capabilities:
            if query_lower in cap.name.lower() or query_lower in cap.description.lower():
                score += 1

        if score > 0:
            scored_tools.append((score, tool))

    # Sort by score and return
    scored_tools.sort(key=lambda x: x[0], reverse=True)
    return [tool for _, tool in scored_tools[:limit]]


# =============================================================================
# Task Analysis
# =============================================================================


@router.post("/analyze", response_model=AnalyzeTaskResponse)
async def analyze_task(request: AnalyzeTaskRequest) -> AnalyzeTaskResponse:
    """
    Analyze a task and get tool recommendations.

    The AI analyzes your task description and recommends the best tools
    to accomplish it, along with suggested parameters and workflow.

    **Example:**
    ```json
    {
      "task": "I need to create a new pipeline that summarizes news articles",
      "available_data": {"source": "rss_feed"},
      "constraints": ["must be fast", "output in JSON"]
    }
    ```
    """
    service = get_mcp_assistant_service()

    analysis = await service.analyze_task(
        task=request.task,
        available_data=request.available_data,
        constraints=request.constraints,
    )

    return AnalyzeTaskResponse(
        analysis=analysis,
        success=True,
        message="Task analyzed successfully",
    )


class QuickRecommendResponse(BaseModel):
    """Quick recommendation response."""

    task: str
    recommendations: List[ToolRecommendation]


@router.get("/recommend", response_model=QuickRecommendResponse)
async def quick_recommend(
    task: str = Query(..., min_length=5, description="Task description"),
    limit: int = Query(3, ge=1, le=10, description="Maximum recommendations"),
) -> QuickRecommendResponse:
    """
    Get quick tool recommendations for a task.

    A convenience endpoint for fast recommendations without full analysis.
    """
    service = get_mcp_assistant_service()

    analysis = await service.analyze_task(task=task)
    recommendations = analysis.tool_recommendations[:limit]

    return QuickRecommendResponse(
        task=task,
        recommendations=recommendations,
    )


# =============================================================================
# Tool Explanation
# =============================================================================


@router.post("/explain", response_model=ToolExplanation)
async def explain_tool(request: ExplainToolRequest) -> ToolExplanation:
    """
    Get a detailed explanation of a tool.

    Returns comprehensive information about the tool including
    parameter explanations, use cases, tips, and warnings.

    **Example:**
    ```json
    {
      "tool_name": "create_pipeline",
      "context": "I'm building a content moderation system",
      "detail_level": "detailed"
    }
    ```
    """
    service = get_mcp_assistant_service()

    try:
        explanation = await service.explain_tool(
            tool_name=request.tool_name,
            context=request.context,
            detail_level=request.detail_level,
        )
        return explanation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/explain/{tool_name}", response_model=ToolExplanation)
async def get_tool_explanation(
    tool_name: str,
    detail_level: str = Query("normal", description="brief, normal, or detailed"),
) -> ToolExplanation:
    """
    Get explanation for a tool by name.

    A convenience endpoint for quick tool lookups.
    """
    service = get_mcp_assistant_service()

    try:
        return await service.explain_tool(
            tool_name=tool_name,
            detail_level=detail_level,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =============================================================================
# Tool Chains
# =============================================================================


@router.post("/chains", response_model=ToolChain)
async def create_tool_chain(request: CreateChainRequest) -> ToolChain:
    """
    Create a tool chain for a complex task.

    The AI designs a sequence of tool calls that work together
    to accomplish your goal.

    **Example:**
    ```json
    {
      "goal": "Create a pipeline that monitors an API and sends alerts on errors",
      "available_tools": null,
      "max_steps": 5
    }
    ```
    """
    service = get_mcp_assistant_service()

    chain = await service.create_tool_chain(
        goal=request.goal,
        available_tools=request.available_tools,
        max_steps=request.max_steps,
    )

    return chain


class ChainListResponse(BaseModel):
    """List of tool chains."""

    chains: List[ToolChain]
    total: int


@router.get("/chains", response_model=ChainListResponse)
async def list_chains() -> ChainListResponse:
    """
    List previously created tool chains.

    Returns all chains created in the current session.
    """
    service = get_mcp_assistant_service()
    chains = list(service._chains.values())

    return ChainListResponse(
        chains=chains,
        total=len(chains),
    )


@router.get("/chains/{chain_id}", response_model=ToolChain)
async def get_chain(chain_id: str) -> ToolChain:
    """
    Get a specific tool chain by ID.
    """
    service = get_mcp_assistant_service()

    if chain_id not in service._chains:
        raise HTTPException(status_code=404, detail="Chain not found")

    return service._chains[chain_id]


# =============================================================================
# Smart Invocation
# =============================================================================


@router.post("/invoke", response_model=SmartInvokeResponse)
async def smart_invoke(request: SmartInvokeRequest) -> SmartInvokeResponse:
    """
    Invoke a tool with AI-assisted parameter resolution.

    You can provide parameters in natural language, partial parameters,
    or context data, and the AI will resolve the actual parameter values.

    **Example:**
    ```json
    {
      "tool_name": "create_pipeline",
      "natural_language_params": "create a pipeline called 'news-summarizer' that processes RSS feeds",
      "partial_params": {"version": "1.0.0"},
      "context": {"available_components": ["generator", "filter"]}
    }
    ```
    """
    service = get_mcp_assistant_service()

    try:
        response = await service.smart_invoke(
            tool_name=request.tool_name,
            natural_language_params=request.natural_language_params,
            partial_params=request.partial_params,
            context=request.context,
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =============================================================================
# Autocomplete
# =============================================================================


@router.post("/autocomplete", response_model=AutocompleteResult)
async def get_autocomplete(request: AutocompleteRequest) -> AutocompleteResult:
    """
    Get autocomplete suggestions for a tool parameter.

    Returns intelligent suggestions based on the tool's schema,
    current context, and previous usage.

    **Example:**
    ```json
    {
      "tool_name": "run_pipeline",
      "parameter": "pipeline_id",
      "partial_value": "news",
      "context": {"recent_pipelines": ["news-summarizer", "news-classifier"]}
    }
    ```
    """
    service = get_mcp_assistant_service()

    try:
        result = await service.get_autocomplete(
            tool_name=request.tool_name,
            parameter=request.parameter,
            partial_value=request.partial_value,
            context=request.context,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =============================================================================
# Conversations
# =============================================================================


class StartConversationRequest(BaseModel):
    """Request to start an AI-assisted conversation."""

    initial_task: Optional[str] = Field(
        default=None,
        description="Initial task to work on"
    )


class ConversationMessageRequest(BaseModel):
    """Send a message in a conversation."""

    message: str = Field(..., min_length=1)


class ConversationResponse(BaseModel):
    """Response with conversation state."""

    context: ConversationContext
    assistant_response: str


@router.post("/conversations", response_model=ConversationResponse)
async def start_conversation(
    request: StartConversationRequest,
) -> ConversationResponse:
    """
    Start a new AI-assisted MCP conversation.

    Creates a conversation context that maintains state across
    multiple interactions for complex multi-step tasks.
    """
    service = get_mcp_assistant_service()

    context = service.start_conversation(initial_task=request.initial_task)

    # Generate initial response
    if request.initial_task:
        response = f"I'll help you with: {request.initial_task}. Let me analyze what tools we'll need."
    else:
        response = "Hello! I'm your MCP assistant. What would you like to accomplish today?"

    return ConversationResponse(
        context=context,
        assistant_response=response,
    )


@router.post("/conversations/{conversation_id}/messages", response_model=ConversationResponse)
async def send_message(
    conversation_id: str,
    request: ConversationMessageRequest,
) -> ConversationResponse:
    """
    Send a message in an ongoing conversation.

    The AI maintains context from previous messages and can
    execute tool chains based on the conversation flow.
    """
    service = get_mcp_assistant_service()

    try:
        context, response = await service.continue_conversation(
            conversation_id=conversation_id,
            message=request.message,
        )
        return ConversationResponse(
            context=context,
            assistant_response=response,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=ConversationContext)
async def get_conversation(conversation_id: str) -> ConversationContext:
    """
    Get the current state of a conversation.
    """
    service = get_mcp_assistant_service()

    if conversation_id not in service._conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return service._conversations[conversation_id]


@router.delete("/conversations/{conversation_id}")
async def end_conversation(conversation_id: str) -> dict:
    """
    End a conversation and cleanup resources.
    """
    service = get_mcp_assistant_service()

    if conversation_id not in service._conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    del service._conversations[conversation_id]
    return {"success": True, "message": "Conversation ended"}


# =============================================================================
# Categories
# =============================================================================


class CategoryInfo(BaseModel):
    """Information about a tool category."""

    category: ToolCategory
    description: str
    tool_count: int
    example_tools: List[str]


@router.get("/categories", response_model=List[CategoryInfo])
async def list_categories() -> List[CategoryInfo]:
    """
    List all tool categories with descriptions.
    """
    service = get_mcp_assistant_service()
    tools = service.get_enhanced_tools()

    # Group tools by category
    category_tools: dict[ToolCategory, list[str]] = {}
    for tool in tools:
        if tool.category not in category_tools:
            category_tools[tool.category] = []
        category_tools[tool.category].append(tool.name)

    # Category descriptions
    category_descriptions = {
        ToolCategory.PIPELINE: "Tools for creating and managing pipelines",
        ToolCategory.COMPONENT: "Tools for working with components",
        ToolCategory.DATA: "Tools for data manipulation and analysis",
        ToolCategory.INTEGRATION: "Tools for external integrations",
        ToolCategory.UTILITY: "General utility tools",
    }

    categories = []
    for cat, tool_names in category_tools.items():
        categories.append(
            CategoryInfo(
                category=cat,
                description=category_descriptions.get(cat, ""),
                tool_count=len(tool_names),
                example_tools=tool_names[:3],
            )
        )

    return categories
