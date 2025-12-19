# Financial Counselling for Gambling Harm

> AI-powered financial counselling workflow with zero hallucination architecture and human-centered design.

## Overview

This solution provides production-ready pipelines for financial counselling services supporting clients affected by gambling harm. It combines:

- **Claude Sonnet** for empathetic intake and document generation
- **GPT-4** for cross-validated risk assessment
- **Perplexity Sonar Pro** for real-time, cited research

**Key Principle**: AI prepares, humans deliver. All client communication goes through trained counsellors.

## Quick Start

### Prerequisites

```bash
# Install FlowMason
pip install flowmason

# Set API keys
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export PERPLEXITY_API_KEY=pplx-...
```

### Run the Pipeline

```bash
# Download the template
fm template download fc-crisis-to-action

# Create test input
cat > input.json << 'EOF'
{
  "contact_content": "Hi, I need help. I've been gambling too much and now I can't pay my rent. I owe about $15,000 on credit cards and my landlord is threatening eviction. I have two kids and I'm scared. I live in Melbourne VIC.",
  "contact_method": "email",
  "state": "VIC",
  "suburb": "Melbourne"
}
EOF

# Run
fm run fc-crisis-to-action.json --input input.json --output results.json
```

## Available Pipelines

### 1. Crisis to Action (Main Pipeline)

Complete 15-stage workflow from intake to action plan.

**Stages**:
1. `validate-input` - Schema validation
2. `parse-intake` - Empathetic intake parsing (Claude)
3. `detect-crisis` - Crisis indicator detection (Claude)
4. `crisis-gate` - Router to escalation or continue
5. `calculate-risk-score` - 0-10 risk assessment (GPT-4)
6. `research-hardship` - Utility relief, emergency funds (Perplexity)
7. `research-services` - Local support services (Perplexity)
8. `research-legal` - Consumer protections (Perplexity)
9. `research-creditors` - Bank hardship programs (Perplexity)
10. `validate-research` - Citation completeness check
11. `synthesize-action-plan` - Prioritized plan generation (Claude)
12. `generate-counsellor-briefing` - Staff preparation document
13. `generate-client-materials` - Plain language client handout
14. `route-by-severity` - Priority queue routing
15. `log-completion` - Audit trail logging

**Template**: `fc-crisis-to-action.json`

### 2. Intake & Assessment

Standalone intake with crisis detection and risk scoring.

**Use when**: You want quick triage without full research.

**Stages**: 5
**Template**: `fc-intake-assessment.json`

### 3. Verified Research

Perplexity-powered research with citation validation.

**Use when**: You need to research services for a specific client.

**Stages**: 7
**Template**: `fc-verified-research.json`

### 4. Action Plan Generator

Generate documents from research inputs.

**Use when**: You have research from another source.

**Stages**: 4
**Template**: `fc-action-plan-generator.json`

### 5. Follow-up Tracker

Progress tracking and next session planning.

**Use when**: Supporting ongoing client relationships.

**Stages**: 6
**Template**: `fc-follow-up-tracker.json`

## Architecture

### Multi-Provider Strategy

| Provider | Model | Usage | Why |
|----------|-------|-------|-----|
| Anthropic | Claude Sonnet | Intake, documents, synthesis | Best empathetic communication |
| OpenAI | GPT-4o | Risk scoring | Cross-validation with different architecture |
| Perplexity | Sonar Pro | Research | Real-time web search with citations |

### Zero Hallucination Architecture

Every factual claim requires a verifiable source:

1. **Perplexity for research** - Built-in web search with citations
2. **Mandatory citation URLs** - Every service/program needs a source
3. **Validation stage** - Items without citations flagged
4. **Explicit uncertainty** - "Unable to verify" instead of fabricated details

### Human-in-the-Loop Points

**Mandatory human intervention**:
- Crisis detection triggers immediate escalation
- High risk scores (8+) require supervisor review
- Unverified citations flagged for manual research

**Counsellor review required**:
- Intake summary before proceeding
- Action plan priorities and adjustments
- Client materials before sharing

### Data Flow

```
Input
  │
  ├─► Intake Parser ─► Structured Client Data
  │
  ├─► Crisis Detection ─┬─► [CRISIS] Human Escalation
  │                     │
  │                     └─► [SAFE] Continue
  │
  ├─► Risk Scoring ─► Score 0-10, Priority Areas
  │
  ├─► Research (4 parallel) ─► Programs, Services, Legal, Creditors
  │
  ├─► Citation Validation ─► Flag missing sources
  │
  ├─► Action Plan Synthesis ─► Prioritized actions + referrals
  │
  └─► Document Generation ─► Counsellor Briefing + Client Materials
```

## Configuration

### Input Schema

```json
{
  "contact_content": "string",     // Required: Client message/notes
  "contact_method": "email|form|phone_transcript|in_person_notes",
  "state": "VIC|NSW|QLD|SA|WA|TAS|NT|ACT",
  "suburb": "string",              // For local service search
  "creditors": ["string"],         // Banks/lenders to research
  "specific_needs": ["string"]     // Additional research topics
}
```

### Output Schema

```json
{
  "structured_intake": {
    "client_situation": {...},
    "financial_snapshot": {...},
    "gambling_context": {...},
    "immediate_concerns": {...}
  },
  "crisis_assessment": {
    "crisis_detected": false,
    "severity": "standard|elevated|urgent|immediate",
    "safe_to_proceed": true
  },
  "risk_score": {
    "score": 0-10,
    "level": "stable|moderate|elevated|high|critical",
    "primary_concerns": [...],
    "protective_factors": [...]
  },
  "research": {
    "hardship_programs": [...],
    "local_services": [...],
    "legal_protections": [...],
    "creditor_policies": [...]
  },
  "action_plan": {
    "immediate_actions": [...],
    "urgent_actions": [...],
    "important_actions": [...],
    "referrals": [...]
  },
  "counsellor_briefing": {...},
  "client_materials": {...},
  "all_citations": [...]
}
```

## Customization

### Modifying Prompts

Each generator stage has a `system_prompt` and `prompt` that can be customized:

```json
{
  "id": "parse-intake",
  "config": {
    "system_prompt": "You are supporting a financial counsellor at [YOUR ORG]...",
    "prompt": "..."
  }
}
```

**Maintain trauma-informed language**:
- Always: Person-first language, strengths identification, hope-focused framing
- Never: Shame-based language, character judgments, minimizing language

### Model Selection

Swap models based on your requirements:

```json
// For cost optimization:
"model": "claude-3-haiku-20240307"

// For maximum quality:
"model": "claude-opus-4-20250514"

// For different research provider:
"provider": "perplexity",
"model": "sonar"  // vs "sonar-pro"
```

### Regional Adaptation

Default configuration is Australia-focused. To adapt:

1. **Update research prompts**: Replace "Australia" with your region
2. **Update state/region enums**: Match your jurisdiction structure
3. **Update service references**: Local helplines, programs, legislation
4. **Test with regional scenarios**: Ensure citations resolve correctly

**Example services by region**:

| Australia | UK | US |
|-----------|----|----|
| Gambler's Help | GambleAware | NCPG |
| NILS | StepChange | NFCC |
| ACCC protections | FCA regulations | FDCPA |

## Integration

### REST API

```bash
# Start server
fm serve --port 8080

# Execute pipeline
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline": "fc-crisis-to-action",
    "input": {"contact_content": "...", "state": "VIC"}
  }'
```

### Python SDK

```python
from flowmason import Pipeline

pipeline = Pipeline.from_file("fc-crisis-to-action.json")
result = pipeline.run({
    "contact_content": client_message,
    "state": "VIC"
})

action_plan = result["action_plan"]
briefing = result["counsellor_briefing"]
```

### Webhook Integration

```bash
# Configure webhook endpoint
fm webhook create \
  --pipeline fc-crisis-to-action \
  --path /intake \
  --secret YOUR_WEBHOOK_SECRET
```

## Testing

### Required Test Scenarios

1. **Standard intake** - Basic debt and housing concerns
2. **Crisis scenario** - Self-harm indicators (verify escalation)
3. **High risk** - Imminent eviction, dependents present
4. **Low information** - Minimal details provided
5. **Follow-up** - Progress tracking with partial completion

### Critical: Crisis Escalation Test

Before production deployment, verify crisis detection:

```bash
cat > crisis-test.json << 'EOF'
{
  "contact_content": "I don't know what to do anymore. I've lost everything to gambling and I'm thinking about ending it all.",
  "contact_method": "email"
}
EOF

fm run fc-crisis-to-action.json --input crisis-test.json

# Expected: Pipeline halts at crisis-gate
# Expected: crisis_detected = true
# Expected: escalation_required = true
```

## Production Deployment

### Checklist

- [ ] API keys stored in secure secret manager
- [ ] Crisis escalation contacts configured
- [ ] Logging level set appropriately (no PII)
- [ ] Rate limiting configured
- [ ] CMS integration tested end-to-end
- [ ] Staff trained on reviewing AI outputs

### Estimated Costs

Per full Crisis-to-Action pipeline execution:

| Provider | Model | Est. Tokens | Est. Cost |
|----------|-------|-------------|-----------|
| Anthropic | Claude Sonnet | ~15,000 | ~$0.10 |
| OpenAI | GPT-4o | ~3,000 | ~$0.03 |
| Perplexity | Sonar Pro | ~8,000 | ~$0.04 |
| **Total** | | | **~$0.17** |

*Estimates based on typical input sizes. Check provider pricing for current rates.*

## Security & Compliance

### Data Security

- Client data processed, not stored permanently by AI providers
- API keys via environment variables
- No PII in logs (configurable)
- Supports self-hosted LLM deployment for sensitive environments

### Audit Trail

- Complete execution trace with timestamps
- All AI reasoning captured for review
- Citation sources documented
- Human intervention points logged

### Compliance Considerations

- Designed for human oversight (not autonomous advice)
- No financial advice provided directly to clients
- All recommendations reviewed by qualified counsellors
- Supports organization's existing compliance framework

## Support

- [GitHub Discussions](https://github.com/flowmason/flowmason/discussions) - Community support
- [Documentation](/docs) - Full FlowMason documentation
- [Website](https://flowmason.com/solutions/financial-counselling) - Solution showcase
