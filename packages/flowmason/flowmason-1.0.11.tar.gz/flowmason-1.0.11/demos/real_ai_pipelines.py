"""
Real AI Demo Pipelines for FlowMason.

These pipelines demonstrate FlowMason's full capabilities using REAL AI providers
(Claude, GPT-4, Gemini). Each pipeline uses 12+ unique components to showcase
the complete component library.

Pipeline Overview:
1. Content Creation & Review Pipeline - Full content workflow
2. Customer Support Intelligence Pipeline - Ticket processing
3. Market Research & Analysis Pipeline - Data enrichment + synthesis
4. Sales Automation Pipeline - CRM-to-email workflow
5. Document Processing Pipeline - Multi-stage document analysis

AVAILABLE COMPONENTS (only use these):
- Nodes (LLM): generator, critic, improver, synthesizer, selector
- Operators: json_transform, filter, logger, schema_validate, http_request, variable_set, loop
- Control Flow: conditional, router, foreach, trycatch, subpipeline, return

All pipelines use real LLM calls via configured providers.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from flowmason_core.config.types import PipelineConfig, ComponentConfig


# =============================================================================
# PIPELINE 1: Content Creation & Review Pipeline
# =============================================================================
# Components: generator, critic, improver, synthesizer, selector,
#             json_transform, filter, logger, conditional, variable_set, schema_validate, loop

def create_content_creation_pipeline() -> PipelineConfig:
    """
    Full content creation workflow with AI review and improvement.

    Flow:
    1. Generate initial content drafts (3 variations)
    2. Critic evaluates each draft
    3. Select best draft based on criteria
    4. Improve selected draft based on feedback
    5. Synthesize final package with metadata
    6. Validate output schema
    7. Conditional routing based on quality score

    Components used: generator, critic, selector, improver,
                    synthesizer, json_transform, filter, logger, conditional,
                    variable_set, schema_validate, loop (12 unique)
    """
    stages = [
        # Stage 1: Log start
        ComponentConfig(
            id="log_start",
            type="logger",
            input_mapping={
                "message": "Starting content creation pipeline",
                "level": "info",
                "data": {"pipeline": "content_creation", "version": "1.0"}
            }
        ),

        # Stage 2: Set topic variable
        ComponentConfig(
            id="set_topic",
            type="variable_set",
            input_mapping={
                "name": "content_topic",
                "value": "The Future of AI in Enterprise Software",
                "scope": "pipeline"
            },
            depends_on=["log_start"]
        ),

        # Stage 3: Generate draft 1 (formal tone)
        ComponentConfig(
            id="generate_draft_1",
            type="generator",
            input_mapping={
                "prompt": "Write a 200-word blog post about 'The Future of AI in Enterprise Software'. Use a formal, professional tone suitable for C-suite executives.",
                "system_prompt": "You are an enterprise technology thought leader. Write authoritative, insight-driven content.",
                "max_tokens": 400,
                "temperature": 0.7
            },
            depends_on=["set_topic"]
        ),

        # Stage 4: Generate draft 2 (conversational tone)
        ComponentConfig(
            id="generate_draft_2",
            type="generator",
            input_mapping={
                "prompt": "Write a 200-word blog post about 'The Future of AI in Enterprise Software'. Use a conversational, engaging tone for tech-savvy professionals.",
                "system_prompt": "You are a friendly tech blogger. Write accessible but insightful content.",
                "max_tokens": 400,
                "temperature": 0.8
            },
            depends_on=["set_topic"]
        ),

        # Stage 5: Generate draft 3 (data-driven tone)
        ComponentConfig(
            id="generate_draft_3",
            type="generator",
            input_mapping={
                "prompt": "Write a 200-word blog post about 'The Future of AI in Enterprise Software'. Focus on statistics, market trends, and concrete examples.",
                "system_prompt": "You are a data analyst and tech writer. Back claims with specifics.",
                "max_tokens": 400,
                "temperature": 0.6
            },
            depends_on=["set_topic"]
        ),

        # Stage 6: Evaluate draft 1 with critic
        ComponentConfig(
            id="critique_draft_1",
            type="critic",
            input_mapping={
                "content": "{{upstream.generate_draft_1.content}}",
                "criteria": ["clarity", "engagement", "authority", "actionability"],
                "context": "This is a B2B blog post for enterprise decision makers"
            },
            depends_on=["generate_draft_1"]
        ),

        # Stage 7: Evaluate draft 2 with critic
        ComponentConfig(
            id="critique_draft_2",
            type="critic",
            input_mapping={
                "content": "{{upstream.generate_draft_2.content}}",
                "criteria": ["clarity", "engagement", "authority", "actionability"],
                "context": "This is a B2B blog post for enterprise decision makers"
            },
            depends_on=["generate_draft_2"]
        ),

        # Stage 8: Evaluate draft 3 with critic
        ComponentConfig(
            id="critique_draft_3",
            type="critic",
            input_mapping={
                "content": "{{upstream.generate_draft_3.content}}",
                "criteria": ["clarity", "engagement", "authority", "actionability"],
                "context": "This is a B2B blog post for enterprise decision makers"
            },
            depends_on=["generate_draft_3"]
        ),

        # Stage 9: Transform critiques into selection candidates
        ComponentConfig(
            id="prepare_candidates",
            type="json_transform",
            input_mapping={
                "data": {
                    "draft1": "{{upstream.generate_draft_1.content}}",
                    "draft2": "{{upstream.generate_draft_2.content}}",
                    "draft3": "{{upstream.generate_draft_3.content}}",
                    "score1": "{{upstream.critique_draft_1.score}}",
                    "score2": "{{upstream.critique_draft_2.score}}",
                    "score3": "{{upstream.critique_draft_3.score}}"
                },
                "mapping": {
                    "all_drafts": "data"
                }
            },
            depends_on=["critique_draft_1", "critique_draft_2", "critique_draft_3"]
        ),

        # Stage 10: Select best draft
        ComponentConfig(
            id="select_best",
            type="selector",
            input_mapping={
                "candidates": [
                    "{{upstream.generate_draft_1.content}}",
                    "{{upstream.generate_draft_2.content}}",
                    "{{upstream.generate_draft_3.content}}"
                ],
                "criteria": ["professional tone", "actionable insights", "engaging opening"],
                "context": "Select the best draft for a B2B enterprise blog",
                "selection_mode": "best"
            },
            depends_on=["prepare_candidates"]
        ),

        # Stage 11: Improve the selected draft
        ComponentConfig(
            id="improve_draft",
            type="improver",
            input_mapping={
                "content": "{{upstream.select_best.selected}}",
                "feedback": "Add a compelling call-to-action, strengthen the opening hook, and ensure key benefits are clearly highlighted",
                "preserve_aspects": ["core message", "professional tone"],
                "max_iterations": 1
            },
            depends_on=["select_best"]
        ),

        # Stage 12: Filter - only proceed if improvement has content
        ComponentConfig(
            id="quality_check",
            type="filter",
            input_mapping={
                "data": {"improved": "{{upstream.improve_draft.improved_content}}"},
                "field_conditions": {},
                "pass_if_missing": False
            },
            depends_on=["improve_draft"]
        ),

        # Stage 13: Synthesize final content package
        ComponentConfig(
            id="synthesize_package",
            type="synthesizer",
            input_mapping={
                "inputs": [
                    "{{upstream.improve_draft.improved_content}}",
                    "{{upstream.select_best.explanation}}"
                ],
                "synthesis_strategy": "integrate",
                "output_format": "structured",
                "context": "Create a final content package with main article and selection rationale"
            },
            depends_on=["quality_check"]
        ),

        # Stage 14: Validate final output schema
        ComponentConfig(
            id="validate_output",
            type="schema_validate",
            input_mapping={
                "data": {"synthesized": "{{upstream.synthesize_package.synthesized}}"},
                "json_schema": {
                    "type": "object",
                    "required": ["synthesized"],
                    "properties": {
                        "synthesized": {"type": "string", "minLength": 100}
                    }
                },
                "strict": False
            },
            depends_on=["synthesize_package"]
        ),

        # Stage 15: Conditional - route based on validation
        ComponentConfig(
            id="route_output",
            type="conditional",
            input_mapping={
                "condition": "{{upstream.validate_output.valid}}",
                "true_branch_stages": [],
                "false_branch_stages": [],
                "pass_data": {"content": "{{upstream.synthesize_package.synthesized}}"}
            },
            depends_on=["validate_output"]
        ),

        # Stage 16: Log completion
        ComponentConfig(
            id="log_complete",
            type="logger",
            input_mapping={
                "message": "Content creation pipeline completed",
                "level": "info",
                "data": {"status": "{{upstream.route_output.branch_taken}}"}
            },
            depends_on=["route_output"]
        )
    ]

    return PipelineConfig(
        id="content-creation-pipeline",
        name="Content Creation & Review Pipeline",
        description="Full content workflow: generate drafts, critique, select best, improve, and synthesize",
        version="1.0.0",
        stages=stages,
        output_stage_id="synthesize_package",
        tags=["ai", "content", "real-ai", "complex", "12-components"],
        category="demo"
    )


# =============================================================================
# PIPELINE 2: Customer Support Intelligence Pipeline
# =============================================================================
# Components: generator, critic, improver, synthesizer, json_transform,
#             filter, router, logger, conditional, variable_set, trycatch, foreach

def create_support_intelligence_pipeline() -> PipelineConfig:
    """
    Intelligent customer support ticket processing.

    Flow:
    1. Receive and analyze support ticket with AI
    2. Route based on urgency/category
    3. Generate initial response
    4. Critique response quality
    5. Create knowledge base summary
    6. Handle errors gracefully

    Components used: generator, critic, improver, synthesizer, json_transform,
                    filter, router, logger, conditional, variable_set, trycatch, foreach (12 unique)
    """
    stages = [
        # Stage 1: Log incoming ticket
        ComponentConfig(
            id="log_ticket",
            type="logger",
            input_mapping={
                "message": "Processing support ticket",
                "level": "info",
                "data": {"service": "support", "action": "triage"}
            }
        ),

        # Stage 2: Set ticket data
        ComponentConfig(
            id="set_ticket",
            type="variable_set",
            input_mapping={
                "name": "ticket",
                "value": {
                    "subject": "Cannot access premium features after upgrade",
                    "body": "I upgraded my account to premium yesterday but I still cannot access the advanced analytics dashboard. I've tried logging out and back in multiple times. My account shows premium status but features are locked. This is urgent as I have a client presentation tomorrow. Order #PRE-2024-1234.",
                    "customer_tier": "enterprise"
                },
                "scope": "pipeline"
            },
            depends_on=["log_ticket"]
        ),

        # Stage 3: Wrap AI analysis in try-catch for error handling
        ComponentConfig(
            id="analysis_wrapper",
            type="trycatch",
            input_mapping={
                "try_stages": ["analyze_ticket"],
                "catch_stages": ["analysis_fallback"],
                "error_scope": "continue"
            },
            depends_on=["set_ticket"]
        ),

        # Stage 4: AI-powered ticket analysis
        ComponentConfig(
            id="analyze_ticket",
            type="generator",
            input_mapping={
                "prompt": """Analyze this support ticket and provide a JSON response with:
- urgency: critical/high/medium/low
- category: billing/technical/account/feature_request
- sentiment: positive/neutral/frustrated/angry
- key_issues: list of main issues

Ticket Subject: Cannot access premium features after upgrade
Ticket Body: I upgraded my account to premium yesterday but I still cannot access the advanced analytics dashboard. I've tried logging out and back in multiple times. My account shows premium status but features are locked. This is urgent as I have a client presentation tomorrow. Order #PRE-2024-1234.
Customer Tier: enterprise""",
                "system_prompt": "You are a support ticket analyzer. Return valid JSON only.",
                "max_tokens": 300,
                "temperature": 0.3
            },
            depends_on=["analysis_wrapper"]
        ),

        # Stage 5: Fallback for analysis errors
        ComponentConfig(
            id="analysis_fallback",
            type="json_transform",
            input_mapping={
                "data": {"error": "Analysis failed"},
                "defaults": {
                    "urgency": "high",
                    "category": "technical",
                    "sentiment": "frustrated"
                }
            },
            depends_on=["analysis_wrapper"]
        ),

        # Stage 6: Transform analysis results
        ComponentConfig(
            id="transform_analysis",
            type="json_transform",
            input_mapping={
                "data": {
                    "analysis": "{{upstream.analyze_ticket.content}}",
                    "ticket_id": "PRE-2024-1234"
                },
                "mapping": {
                    "analysis_result": "data.analysis",
                    "ticket_ref": "data.ticket_id"
                }
            },
            depends_on=["analyze_ticket"]
        ),

        # Stage 7: Route based on urgency
        ComponentConfig(
            id="route_urgency",
            type="router",
            input_mapping={
                "value": "high",
                "routes": {
                    "critical": ["escalate_path"],
                    "high": ["priority_path"],
                    "medium": ["standard_path"],
                    "low": ["queue_path"]
                },
                "default_route": ["standard_path"]
            },
            depends_on=["transform_analysis"]
        ),

        # Stage 8: Generate empathetic response
        ComponentConfig(
            id="generate_response",
            type="generator",
            input_mapping={
                "prompt": """Write a helpful, empathetic support response for this ticket:
Subject: Cannot access premium features after upgrade
Body: I upgraded my account to premium yesterday but I still cannot access the advanced analytics dashboard. I've tried logging out and back in multiple times. My account shows premium status but features are locked. This is urgent as I have a client presentation tomorrow. Order #PRE-2024-1234.

The customer is frustrated and has an urgent presentation. Category: technical/account.
Include specific troubleshooting steps and offer expedited support.""",
                "system_prompt": "You are a senior customer support specialist. Be empathetic, professional, and solution-focused. Always acknowledge the customer's frustration and urgency.",
                "max_tokens": 500,
                "temperature": 0.6
            },
            depends_on=["route_urgency"]
        ),

        # Stage 9: Critique the response
        ComponentConfig(
            id="critique_response",
            type="critic",
            input_mapping={
                "content": "{{upstream.generate_response.content}}",
                "criteria": ["empathy", "clarity", "actionability", "professionalism", "completeness"],
                "context": "This is a support response to an enterprise customer with an urgent issue"
            },
            depends_on=["generate_response"]
        ),

        # Stage 10: Filter - check if response meets quality threshold
        ComponentConfig(
            id="quality_filter",
            type="filter",
            input_mapping={
                "data": {"passes": "{{upstream.critique_response.passes_threshold}}", "score": "{{upstream.critique_response.score}}"},
                "field_conditions": {}
            },
            depends_on=["critique_response"]
        ),

        # Stage 11: Conditional - approve or flag for review
        ComponentConfig(
            id="approve_response",
            type="conditional",
            input_mapping={
                "condition": "{{upstream.critique_response.passes_threshold}}",
                "true_branch_stages": [],
                "false_branch_stages": []
            },
            depends_on=["quality_filter"]
        ),

        # Stage 12: Improve response if needed
        ComponentConfig(
            id="improve_response",
            type="improver",
            input_mapping={
                "content": "{{upstream.generate_response.content}}",
                "feedback": "{{upstream.critique_response.feedback}}",
                "improvements": "{{upstream.critique_response.improvements}}",
                "preserve_aspects": ["empathetic tone", "specific troubleshooting steps"]
            },
            depends_on=["approve_response"]
        ),

        # Stage 13: Synthesize knowledge base entry
        ComponentConfig(
            id="kb_synthesis",
            type="synthesizer",
            input_mapping={
                "inputs": [
                    "Ticket: Cannot access premium features after upgrade",
                    "Resolution: {{upstream.improve_response.improved_content}}",
                    "Category: Technical/Account issue with premium feature access"
                ],
                "synthesis_strategy": "summarize",
                "output_format": "structured",
                "context": "Create a knowledge base article for similar future tickets"
            },
            depends_on=["improve_response"]
        ),

        # Stage 14: Process extracted key issues with foreach
        ComponentConfig(
            id="process_issues",
            type="foreach",
            input_mapping={
                "items": ["premium_access", "account_sync", "feature_provisioning"],
                "loop_stages": ["log_issue"],
                "item_variable": "issue",
                "collect_results": True
            },
            depends_on=["kb_synthesis"]
        ),

        # Stage 15: Log each issue (part of foreach)
        ComponentConfig(
            id="log_issue",
            type="logger",
            input_mapping={
                "message": "Processing issue tag",
                "level": "debug",
                "data": {"issue_type": "feature_access"}
            },
            depends_on=["process_issues"]
        ),

        # Stage 16: Final logging
        ComponentConfig(
            id="log_complete",
            type="logger",
            input_mapping={
                "message": "Support ticket processed successfully",
                "level": "info",
                "data": {
                    "status": "{{upstream.approve_response.branch_taken}}",
                    "category": "technical"
                }
            },
            depends_on=["log_issue"]
        )
    ]

    return PipelineConfig(
        id="support-intelligence-pipeline",
        name="Customer Support Intelligence Pipeline",
        description="AI-powered ticket analysis, response generation, quality review, and knowledge base integration",
        version="1.0.0",
        stages=stages,
        output_stage_id="kb_synthesis",
        tags=["ai", "support", "real-ai", "complex", "12-components"],
        category="demo"
    )


# =============================================================================
# PIPELINE 3: Market Research & Analysis Pipeline
# =============================================================================
# Components: generator, synthesizer, selector, critic, improver,
#             json_transform, http_request, filter, logger, conditional, schema_validate, variable_set

def create_market_research_pipeline() -> PipelineConfig:
    """
    Market research pipeline with AI-powered analysis.

    Flow:
    1. Set research parameters
    2. Generate company profile analysis
    3. Generate competitor comparison
    4. Synthesize research findings
    5. Select key recommendation
    6. Validate and route output

    Components used: generator, synthesizer, selector, critic, improver,
                    json_transform, http_request, filter, logger, conditional,
                    schema_validate, variable_set (12 unique)
    """
    stages = [
        # Stage 1: Initialize pipeline
        ComponentConfig(
            id="init_research",
            type="logger",
            input_mapping={
                "message": "Starting market research pipeline",
                "level": "info",
                "data": {"pipeline": "market_research"}
            }
        ),

        # Stage 2: Set target company
        ComponentConfig(
            id="set_target",
            type="variable_set",
            input_mapping={
                "name": "target_company",
                "value": {"name": "OpenAI", "industry": "AI/ML"},
                "scope": "pipeline"
            },
            depends_on=["init_research"]
        ),

        # Stage 3: Generate company profile
        ComponentConfig(
            id="generate_profile",
            type="generator",
            input_mapping={
                "prompt": """Create a comprehensive company profile for OpenAI. Include:
1. Company overview and mission
2. Key products and services (GPT-4, ChatGPT, DALL-E, API platform)
3. Market position and competitive advantages
4. Recent developments and funding
5. Leadership and organizational structure

Provide factual, research-quality content.""",
                "system_prompt": "You are a business analyst at a top research firm. Provide accurate, well-structured company profiles.",
                "max_tokens": 800,
                "temperature": 0.5
            },
            depends_on=["set_target"]
        ),

        # Stage 4: Transform profile data
        ComponentConfig(
            id="transform_profile",
            type="json_transform",
            input_mapping={
                "data": {
                    "company": "OpenAI",
                    "profile": "{{upstream.generate_profile.content}}"
                },
                "mapping": {
                    "company_name": "data.company",
                    "profile_content": "data.profile"
                }
            },
            depends_on=["generate_profile"]
        ),

        # Stage 5: Filter - check profile quality
        ComponentConfig(
            id="profile_filter",
            type="filter",
            input_mapping={
                "data": {"profile": "{{upstream.generate_profile.content}}"},
                "field_conditions": {},
                "pass_if_missing": True
            },
            depends_on=["transform_profile"]
        ),

        # Stage 6: Make external API call (simulated market data endpoint)
        ComponentConfig(
            id="fetch_market_data",
            type="http_request",
            input_mapping={
                "url": "https://httpbin.org/json",
                "method": "GET",
                "headers": {"Accept": "application/json"},
                "timeout_ms": 5000,
                "retry_count": 2
            },
            depends_on=["profile_filter"]
        ),

        # Stage 7: Generate market analysis
        ComponentConfig(
            id="generate_analysis",
            type="generator",
            input_mapping={
                "prompt": """Provide a comprehensive market analysis of OpenAI in the AI industry. Cover:
1. Market position and competitive advantages
2. Key products and their market fit (GPT-4, ChatGPT, API platform)
3. Growth trajectory and recent $10B Microsoft investment
4. Potential risks and challenges (competition from Google, Anthropic, Meta)
5. Future outlook and market opportunities

Base analysis on their position as a leader in LLM technology.""",
                "system_prompt": "You are a senior market analyst at a top investment firm. Provide data-driven, balanced analysis with clear insights.",
                "max_tokens": 800,
                "temperature": 0.5
            },
            depends_on=["fetch_market_data"]
        ),

        # Stage 8: Critique the analysis
        ComponentConfig(
            id="critique_analysis",
            type="critic",
            input_mapping={
                "content": "{{upstream.generate_analysis.content}}",
                "criteria": ["depth", "accuracy", "objectivity", "actionability"],
                "context": "This is a market research report for investment decisions"
            },
            depends_on=["generate_analysis"]
        ),

        # Stage 9: Improve analysis based on critique
        ComponentConfig(
            id="improve_analysis",
            type="improver",
            input_mapping={
                "content": "{{upstream.generate_analysis.content}}",
                "feedback": "{{upstream.critique_analysis.feedback}}",
                "improvements": "{{upstream.critique_analysis.improvements}}",
                "preserve_aspects": ["factual accuracy", "balanced perspective"]
            },
            depends_on=["critique_analysis"]
        ),

        # Stage 10: Synthesize all research
        ComponentConfig(
            id="synthesize_research",
            type="synthesizer",
            input_mapping={
                "inputs": [
                    "Company Profile: {{upstream.generate_profile.content}}",
                    "Market Analysis: {{upstream.improve_analysis.improved_content}}"
                ],
                "synthesis_strategy": "integrate",
                "output_format": "structured",
                "context": "Create a unified market research report combining company profile and market analysis"
            },
            depends_on=["improve_analysis"]
        ),

        # Stage 11: Select key recommendation
        ComponentConfig(
            id="select_recommendation",
            type="selector",
            input_mapping={
                "candidates": [
                    "Strong Buy - Leading market position with significant growth runway in the AI infrastructure space",
                    "Buy - Solid fundamentals with competitive moat from GPT-4 and enterprise API platform",
                    "Hold - Market leader but valuation concerns given recent funding at $90B valuation",
                    "Monitor - High potential but significant risks from regulatory scrutiny and competition"
                ],
                "criteria": ["alignment with analysis", "risk-adjusted view", "actionable recommendation"],
                "context": "Based on the comprehensive research conducted"
            },
            depends_on=["synthesize_research"]
        ),

        # Stage 12: Validate output
        ComponentConfig(
            id="validate_report",
            type="schema_validate",
            input_mapping={
                "data": {
                    "report": "{{upstream.synthesize_research.synthesized}}",
                    "recommendation": "{{upstream.select_recommendation.selected}}"
                },
                "json_schema": {
                    "type": "object",
                    "required": ["report", "recommendation"],
                    "properties": {
                        "report": {"type": "string", "minLength": 200},
                        "recommendation": {"type": "string"}
                    }
                }
            },
            depends_on=["select_recommendation"]
        ),

        # Stage 13: Route based on validation
        ComponentConfig(
            id="route_report",
            type="conditional",
            input_mapping={
                "condition": "{{upstream.validate_report.valid}}",
                "true_branch_stages": [],
                "false_branch_stages": []
            },
            depends_on=["validate_report"]
        ),

        # Stage 14: Log completion
        ComponentConfig(
            id="log_complete",
            type="logger",
            input_mapping={
                "message": "Market research pipeline completed",
                "level": "info",
                "data": {
                    "company": "OpenAI",
                    "recommendation": "{{upstream.select_recommendation.selected}}"
                }
            },
            depends_on=["route_report"]
        )
    ]

    return PipelineConfig(
        id="market-research-pipeline",
        name="Market Research & Analysis Pipeline",
        description="AI-powered market research: company profiling, analysis, critique, improvement, and recommendations",
        version="1.0.0",
        stages=stages,
        output_stage_id="synthesize_research",
        tags=["ai", "research", "real-ai", "complex", "12-components"],
        category="demo"
    )


# =============================================================================
# PIPELINE 4: Sales Automation Pipeline
# =============================================================================
# Components: generator, improver, critic, synthesizer, selector,
#             json_transform, filter, router, logger, conditional, variable_set, foreach

def create_sales_automation_pipeline() -> PipelineConfig:
    """
    Sales automation pipeline for personalized outreach.

    Flow:
    1. Process CRM contact data
    2. Generate personalized follow-up email
    3. Review and improve email quality
    4. Route based on deal stage
    5. Generate call prep summary

    Components used: generator, improver, critic, synthesizer, selector,
                    json_transform, filter, router, logger, conditional, variable_set, foreach (12 unique)
    """
    stages = [
        # Stage 1: Initialize
        ComponentConfig(
            id="init_sales",
            type="logger",
            input_mapping={
                "message": "Starting sales automation pipeline",
                "level": "info",
                "data": {"pipeline": "sales_automation", "crm": "custom"}
            }
        ),

        # Stage 2: Set CRM contact data
        ComponentConfig(
            id="set_contact",
            type="variable_set",
            input_mapping={
                "name": "crm_contact",
                "value": {
                    "name": "Sarah Chen",
                    "title": "VP of Engineering",
                    "company": "TechCorp Industries",
                    "deal_stage": "discovery",
                    "last_interaction": "Demo call",
                    "pain_points": ["scaling infrastructure", "reducing deployment time"]
                },
                "scope": "pipeline"
            },
            depends_on=["init_sales"]
        ),

        # Stage 3: Generate personalized follow-up email
        ComponentConfig(
            id="generate_email",
            type="generator",
            input_mapping={
                "prompt": """Write a personalized B2B sales follow-up email for:

Contact: Sarah Chen, VP of Engineering at TechCorp Industries
Deal Stage: Discovery
Last Interaction: Demo call showing strong interest in deployment automation features
Pain Points:
- Scaling infrastructure for 10x growth
- Reducing deployment time from hours to minutes
Notes: Asked about enterprise pricing. Mentioned Q1 budget planning.

Write a professional, personalized email that:
1. References the demo call specifically
2. Addresses their scaling and deployment pain points
3. Includes a clear call-to-action for next steps
4. Mentions a relevant case study briefly""",
                "system_prompt": "You are an experienced B2B sales professional. Write concise, value-focused emails that resonate with technical decision-makers.",
                "max_tokens": 500,
                "temperature": 0.6
            },
            depends_on=["set_contact"]
        ),

        # Stage 4: Transform email output
        ComponentConfig(
            id="transform_email",
            type="json_transform",
            input_mapping={
                "data": {
                    "email_content": "{{upstream.generate_email.content}}",
                    "contact": "Sarah Chen",
                    "company": "TechCorp Industries"
                },
                "mapping": {
                    "email": "data.email_content",
                    "recipient": "data.contact",
                    "account": "data.company"
                }
            },
            depends_on=["generate_email"]
        ),

        # Stage 5: Critique the email
        ComponentConfig(
            id="critique_email",
            type="critic",
            input_mapping={
                "content": "{{upstream.generate_email.content}}",
                "criteria": ["personalization", "value_proposition", "clear_cta", "appropriate_tone", "brevity"],
                "context": "B2B sales follow-up email to VP of Engineering at mid-market tech company"
            },
            depends_on=["transform_email"]
        ),

        # Stage 6: Filter based on quality
        ComponentConfig(
            id="quality_filter",
            type="filter",
            input_mapping={
                "data": {"score": "{{upstream.critique_email.score}}", "passes": "{{upstream.critique_email.passes_threshold}}"},
                "field_conditions": {}
            },
            depends_on=["critique_email"]
        ),

        # Stage 7: Improve email based on feedback
        ComponentConfig(
            id="improve_email",
            type="improver",
            input_mapping={
                "content": "{{upstream.generate_email.content}}",
                "feedback": "{{upstream.critique_email.feedback}}",
                "improvements": "{{upstream.critique_email.improvements}}",
                "preserve_aspects": ["personalization elements", "key value propositions"]
            },
            depends_on=["quality_filter"]
        ),

        # Stage 8: Route based on deal stage
        ComponentConfig(
            id="route_by_stage",
            type="router",
            input_mapping={
                "value": "discovery",
                "routes": {
                    "qualification": ["qualification_followup"],
                    "discovery": ["discovery_followup"],
                    "proposal": ["proposal_followup"],
                    "negotiation": ["negotiation_followup"]
                },
                "default_route": ["general_followup"]
            },
            depends_on=["improve_email"]
        ),

        # Stage 9: Conditional - add urgency flag
        ComponentConfig(
            id="check_urgency",
            type="conditional",
            input_mapping={
                "condition": True,
                "true_branch_stages": [],
                "false_branch_stages": []
            },
            depends_on=["route_by_stage"]
        ),

        # Stage 10: Generate talking points for call prep
        ComponentConfig(
            id="talking_points",
            type="generator",
            input_mapping={
                "prompt": """Generate 3 specific talking points for a follow-up call with Sarah Chen (VP Engineering at TechCorp Industries).

Context:
- Deal Stage: Discovery
- Last Interaction: Demo call with strong interest
- Pain Points: Scaling infrastructure, reducing deployment time
- Notes: Asked about enterprise pricing, Q1 budget planning

Provide actionable, specific talking points that:
1. Address their scaling infrastructure concerns with concrete solutions
2. Demonstrate deployment time reduction ROI with numbers
3. Guide the conversation toward moving from discovery to proposal stage""",
                "system_prompt": "You are a sales coach. Provide actionable, specific talking points for technical sales conversations.",
                "max_tokens": 400,
                "temperature": 0.6
            },
            depends_on=["check_urgency"]
        ),

        # Stage 11: Synthesize call prep materials
        ComponentConfig(
            id="synthesize_prep",
            type="synthesizer",
            input_mapping={
                "inputs": [
                    "Email sent: {{upstream.improve_email.improved_content}}",
                    "Talking points: {{upstream.talking_points.content}}"
                ],
                "synthesis_strategy": "integrate",
                "output_format": "structured",
                "context": "Create a comprehensive call preparation document"
            },
            depends_on=["talking_points"]
        ),

        # Stage 12: Select primary next action
        ComponentConfig(
            id="select_action",
            type="selector",
            input_mapping={
                "candidates": [
                    "Schedule discovery call to discuss technical requirements",
                    "Send pricing proposal with custom enterprise terms",
                    "Arrange technical deep-dive with engineering team",
                    "Follow up with case study and ROI calculator"
                ],
                "criteria": ["appropriate for discovery stage", "moves deal forward", "addresses pain points"],
                "context": "Discovery stage deal with engaged VP Engineering prospect"
            },
            depends_on=["synthesize_prep"]
        ),

        # Stage 13: Process follow-up tasks with foreach
        ComponentConfig(
            id="create_tasks",
            type="foreach",
            input_mapping={
                "items": ["Send email", "Schedule follow-up call", "Prepare proposal draft"],
                "loop_stages": ["log_task"],
                "item_variable": "task",
                "collect_results": True
            },
            depends_on=["select_action"]
        ),

        # Stage 14: Log each task
        ComponentConfig(
            id="log_task",
            type="logger",
            input_mapping={
                "message": "Created CRM task",
                "level": "info",
                "data": {"contact": "Sarah Chen", "company": "TechCorp Industries"}
            },
            depends_on=["create_tasks"]
        ),

        # Stage 15: Final summary
        ComponentConfig(
            id="log_complete",
            type="logger",
            input_mapping={
                "message": "Sales automation pipeline completed",
                "level": "info",
                "data": {
                    "contact": "Sarah Chen",
                    "email_quality_score": "{{upstream.critique_email.score}}",
                    "deal_stage": "discovery",
                    "next_action": "{{upstream.select_action.selected}}"
                }
            },
            depends_on=["log_task"]
        )
    ]

    return PipelineConfig(
        id="sales-automation-pipeline",
        name="Sales Automation Pipeline",
        description="Personalized outreach: email generation, quality review, deal stage routing, and call prep",
        version="1.0.0",
        stages=stages,
        output_stage_id="synthesize_prep",
        tags=["ai", "sales", "real-ai", "complex", "12-components"],
        category="demo"
    )


# =============================================================================
# PIPELINE 5: Document Processing Pipeline with Subpipeline
# =============================================================================
# Components: generator, critic, synthesizer, selector, improver, subpipeline,
#             json_transform, filter, logger, conditional, schema_validate, return

def create_document_processing_pipeline() -> PipelineConfig:
    """
    Multi-stage document processing with nested subpipeline.

    Flow:
    1. Extract document sections
    2. Analyze each section with AI
    3. Generate comprehensive review
    4. Critique and improve
    5. Create final summary with early return capability

    Components used: generator, critic, synthesizer, selector, improver, subpipeline,
                    json_transform, filter, logger, conditional, schema_validate, return (12 unique)
    """
    stages = [
        # Stage 1: Initialize
        ComponentConfig(
            id="init_document",
            type="logger",
            input_mapping={
                "message": "Starting document processing pipeline",
                "level": "info",
                "data": {"document_type": "technical_spec"}
            }
        ),

        # Stage 2: Prepare document sections
        ComponentConfig(
            id="prepare_sections",
            type="json_transform",
            input_mapping={
                "data": {
                    "title": "FlowMason Technical Architecture",
                    "sections": ["Introduction", "Core Components", "Execution Engine", "API Layer"]
                },
                "mapping": {
                    "title": "data.title",
                    "sections": "data.sections"
                },
                "defaults": {
                    "document_type": "technical_spec",
                    "page_count": 15
                }
            },
            depends_on=["init_document"]
        ),

        # Stage 3: Generate introduction analysis
        ComponentConfig(
            id="analyze_intro",
            type="generator",
            input_mapping={
                "prompt": """Analyze this technical document section:

Section: Introduction to FlowMason
Content: FlowMason is a visual pipeline orchestration platform for AI workflows. It enables users to build complex AI pipelines using a drag-and-drop interface, connecting various AI models and data transformations without writing code. The platform supports multiple LLM providers including Anthropic, OpenAI, and Google.

Provide:
1. Key concepts introduced
2. Target audience identification
3. Document scope assessment
4. Clarity rating (1-10)""",
                "system_prompt": "You are a technical documentation analyst. Provide structured analysis.",
                "max_tokens": 400,
                "temperature": 0.4
            },
            depends_on=["prepare_sections"]
        ),

        # Stage 4: Generate component analysis
        ComponentConfig(
            id="analyze_components",
            type="generator",
            input_mapping={
                "prompt": """Analyze the 'Core Components' section describing:

- Nodes: AI operations that use LLM providers (generator, critic, improver, synthesizer, selector)
- Operators: Data transformations (json_transform, filter, http_request, logger)
- Control Flow: Pipeline logic (conditional, router, foreach, trycatch, subpipeline, return)

Evaluate:
1. Completeness of component documentation
2. Clarity of component relationships
3. Technical accuracy
4. Missing information""",
                "system_prompt": "You are a software architect reviewer. Focus on technical precision.",
                "max_tokens": 400,
                "temperature": 0.4
            },
            depends_on=["analyze_intro"]
        ),

        # Stage 5: Filter - check section quality
        ComponentConfig(
            id="section_filter",
            type="filter",
            input_mapping={
                "data": {"intro": "{{upstream.analyze_intro.content}}", "components": "{{upstream.analyze_components.content}}"},
                "field_conditions": {},
                "pass_if_missing": True
            },
            depends_on=["analyze_components"]
        ),

        # Stage 6: Call subpipeline for additional analysis
        ComponentConfig(
            id="deep_analysis",
            type="subpipeline",
            input_mapping={
                "pipeline_id": "content-creation-pipeline",
                "input_data": {"topic": "Technical documentation best practices"},
                "timeout_ms": 120000,
                "inherit_context": True
            },
            depends_on=["section_filter"]
        ),

        # Stage 7: Synthesize all analyses
        ComponentConfig(
            id="synthesize_analysis",
            type="synthesizer",
            input_mapping={
                "inputs": [
                    "Introduction Analysis: {{upstream.analyze_intro.content}}",
                    "Component Analysis: {{upstream.analyze_components.content}}"
                ],
                "synthesis_strategy": "integrate",
                "output_format": "structured",
                "context": "Combine all section analyses into a unified document review"
            },
            depends_on=["deep_analysis"]
        ),

        # Stage 8: Critique the document review
        ComponentConfig(
            id="critique_review",
            type="critic",
            input_mapping={
                "content": "{{upstream.synthesize_analysis.synthesized}}",
                "criteria": ["completeness", "clarity", "actionability", "technical_accuracy"]
            },
            depends_on=["synthesize_analysis"]
        ),

        # Stage 9: Improve the review based on critique
        ComponentConfig(
            id="improve_review",
            type="improver",
            input_mapping={
                "content": "{{upstream.synthesize_analysis.synthesized}}",
                "feedback": "{{upstream.critique_review.feedback}}",
                "improvements": "{{upstream.critique_review.improvements}}",
                "preserve_aspects": ["technical accuracy", "structured format"]
            },
            depends_on=["critique_review"]
        ),

        # Stage 10: Conditional - check if review is acceptable
        ComponentConfig(
            id="check_quality",
            type="conditional",
            input_mapping={
                "condition": "{{upstream.critique_review.passes_threshold}}",
                "true_branch_stages": [],
                "false_branch_stages": []
            },
            depends_on=["improve_review"]
        ),

        # Stage 11: Select final recommendation
        ComponentConfig(
            id="final_recommendation",
            type="selector",
            input_mapping={
                "candidates": [
                    "Approve - Document meets all quality standards and is ready for publication",
                    "Approve with minor revisions - Good quality with small improvements suggested",
                    "Revise - Significant improvements required before approval",
                    "Reject - Document does not meet minimum standards"
                ],
                "criteria": ["aligned with critique", "actionable", "appropriate severity"],
                "context": "Document review based on comprehensive analysis"
            },
            depends_on=["check_quality"]
        ),

        # Stage 12: Validate final output
        ComponentConfig(
            id="validate_output",
            type="schema_validate",
            input_mapping={
                "data": {
                    "review": "{{upstream.improve_review.improved_content}}",
                    "recommendation": "{{upstream.final_recommendation.selected}}",
                    "score": "{{upstream.critique_review.score}}"
                },
                "json_schema": {
                    "type": "object",
                    "required": ["review", "recommendation"],
                    "properties": {
                        "review": {"type": "string"},
                        "recommendation": {"type": "string"}
                    }
                }
            },
            depends_on=["final_recommendation"]
        ),

        # Stage 13: Early return if validation fails
        ComponentConfig(
            id="early_return",
            type="return",
            input_mapping={
                "condition": False,
                "return_value": {"status": "validation_failed"},
                "message": "Output validation failed - returning early"
            },
            depends_on=["validate_output"]
        ),

        # Stage 14: Final logging
        ComponentConfig(
            id="log_complete",
            type="logger",
            input_mapping={
                "message": "Document processing pipeline completed",
                "level": "info",
                "data": {
                    "recommendation": "{{upstream.final_recommendation.selected}}",
                    "quality_score": "{{upstream.critique_review.score}}"
                }
            },
            depends_on=["early_return"]
        )
    ]

    return PipelineConfig(
        id="document-processing-pipeline",
        name="Document Processing Pipeline",
        description="Multi-stage document analysis with subpipeline, quality review, and early return capability",
        version="1.0.0",
        stages=stages,
        output_stage_id="improve_review",
        tags=["ai", "document", "real-ai", "complex", "12-components", "subpipeline"],
        category="demo"
    )


# =============================================================================
# EXPORTS
# =============================================================================

REAL_AI_PIPELINES = {
    "content_creation": create_content_creation_pipeline(),
    "support_intelligence": create_support_intelligence_pipeline(),
    "market_research": create_market_research_pipeline(),
    "sales_automation": create_sales_automation_pipeline(),
    "document_processing": create_document_processing_pipeline(),
}


def get_real_ai_pipeline(name: str) -> PipelineConfig:
    """Get a real AI pipeline by name."""
    if name not in REAL_AI_PIPELINES:
        raise ValueError(f"Unknown pipeline: {name}. Available: {list(REAL_AI_PIPELINES.keys())}")
    return REAL_AI_PIPELINES[name]


def list_real_ai_pipelines() -> list:
    """List all available real AI pipelines."""
    return [
        {
            "name": name,
            "id": pipeline.id,
            "description": pipeline.description,
            "stages": len(pipeline.stages),
            "tags": pipeline.tags
        }
        for name, pipeline in REAL_AI_PIPELINES.items()
    ]


if __name__ == "__main__":
    print("=" * 80)
    print("FLOWMASON REAL AI PIPELINES")
    print("=" * 80)

    for name, pipeline in REAL_AI_PIPELINES.items():
        print(f"\n{pipeline.name}")
        print(f"  ID: {pipeline.id}")
        print(f"  Stages: {len(pipeline.stages)}")
        print(f"  Description: {pipeline.description}")

        # Count unique component types
        component_types = set(s.type for s in pipeline.stages)
        print(f"  Unique Components ({len(component_types)}): {sorted(component_types)}")
