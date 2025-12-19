# LLM Providers

Configure LLM providers for AI-powered pipeline components.

## Supported Providers

| Provider | Models | Status |
|----------|--------|--------|
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku | Supported |
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 Turbo, o1 | Supported |
| **Google** | Gemini Pro, Gemini Flash | Supported |
| **Groq** | Llama 3, Mixtral | Supported |
| **Perplexity** | Sonar, Sonar Pro, Sonar Reasoning | Supported |
| **Salesforce Einstein** | Einstein GPT | Coming Soon |

## Configuration

### Custom Metadata Setup

LLM providers are configured via the `LLMProviderConfig__mdt` Custom Metadata Type.

1. Go to **Setup → Custom Metadata Types**
2. Click **Manage Records** next to `LLMProviderConfig`
3. Click **New** to create a provider configuration

### Anthropic (Claude)

```
Label: Anthropic Production
DeveloperName: Anthropic_Production
Provider__c: anthropic
Endpoint__c: https://api.anthropic.com/v1/messages
Model__c: claude-3-5-sonnet-20241022
ApiKey__c: sk-ant-api03-...
MaxTokens__c: 4096
Temperature__c: 0.7
```

**Available Models**:
- `claude-3-5-sonnet-20241022` - Best balance of speed and intelligence
- `claude-3-opus-20240229` - Most capable, higher cost
- `claude-3-haiku-20240307` - Fastest, lowest cost

### OpenAI (GPT)

```
Label: OpenAI Production
DeveloperName: OpenAI_Production
Provider__c: openai
Endpoint__c: https://api.openai.com/v1/chat/completions
Model__c: gpt-4o
ApiKey__c: sk-...
MaxTokens__c: 4096
Temperature__c: 0.7
```

**Available Models**:
- `gpt-4o` - Most capable multimodal model
- `gpt-4-turbo` - Fast and capable
- `gpt-3.5-turbo` - Fast and economical

### Google (Gemini)

```
Label: Google Production
DeveloperName: Google_Production
Provider__c: google
Endpoint__c: https://generativelanguage.googleapis.com/v1beta
Model__c: gemini-1.5-pro
ApiKey__c: ...
MaxTokens__c: 4096
Temperature__c: 0.7
```

**Available Models**:
- `gemini-1.5-pro` - Most capable, long context
- `gemini-1.5-flash` - Fast and efficient
- `gemini-2.0-flash-exp` - Experimental flash model

### Groq

```
Label: Groq Production
DeveloperName: Groq_Production
Provider__c: groq
Endpoint__c: https://api.groq.com/openai/v1/chat/completions
Model__c: llama-3.3-70b-versatile
ApiKey__c: gsk_...
MaxTokens__c: 4096
Temperature__c: 0.7
```

**Available Models**:
- `llama-3.3-70b-versatile` - Most capable Llama model
- `llama-3.1-8b-instant` - Fast inference
- `mixtral-8x7b-32768` - Long context Mixtral

### Perplexity

```
Label: Perplexity Production
DeveloperName: Perplexity_Production
Provider__c: perplexity
Endpoint__c: https://api.perplexity.ai/chat/completions
Model__c: sonar-pro
ApiKey__c: pplx-...
MaxTokens__c: 4096
Temperature__c: 0.7
```

**Available Models**:
- `sonar-pro` - Most capable with web search (default)
- `sonar` - Standard model with web search
- `sonar-reasoning` - Enhanced reasoning with web search

**Unique Features**:
- Real-time internet search built into responses
- Citations returned in response metadata
- Best for research, fact-checking, and up-to-date information

## Remote Site Settings

Add Remote Site Settings for each provider:

### Anthropic

1. Go to **Setup → Security → Remote Site Settings**
2. Click **New Remote Site**
3. Configure:
   - **Remote Site Name**: `Anthropic`
   - **Remote Site URL**: `https://api.anthropic.com`
   - **Active**: ✓

### OpenAI

1. Go to **Setup → Security → Remote Site Settings**
2. Click **New Remote Site**
3. Configure:
   - **Remote Site Name**: `OpenAI`
   - **Remote Site URL**: `https://api.openai.com`
   - **Active**: ✓

### Google

1. Go to **Setup → Security → Remote Site Settings**
2. Click **New Remote Site**
3. Configure:
   - **Remote Site Name**: `Google`
   - **Remote Site URL**: `https://generativelanguage.googleapis.com`
   - **Active**: ✓

### Groq

1. Go to **Setup → Security → Remote Site Settings**
2. Click **New Remote Site**
3. Configure:
   - **Remote Site Name**: `Groq`
   - **Remote Site URL**: `https://api.groq.com`
   - **Active**: ✓

### Perplexity

1. Go to **Setup → Security → Remote Site Settings**
2. Click **New Remote Site**
3. Configure:
   - **Remote Site Name**: `Perplexity`
   - **Remote Site URL**: `https://api.perplexity.ai`
   - **Active**: ✓

## Using Providers in Pipelines

### Default Provider

If no provider is specified, the default provider is used:

```json
{
  "id": "generate",
  "component_type": "generator",
  "config": {
    "prompt": "Write a summary...",
    "max_tokens": 500
  }
}
```

### Specific Provider

Specify a provider by its DeveloperName:

```json
{
  "id": "generate",
  "component_type": "generator",
  "config": {
    "provider": "OpenAI_Production",
    "prompt": "Write a summary...",
    "max_tokens": 500
  }
}
```

### Override Settings

Override provider settings per-stage:

```json
{
  "id": "generate",
  "component_type": "generator",
  "config": {
    "provider": "Anthropic_Production",
    "model": "claude-3-haiku-20240307",
    "temperature": 0.3,
    "max_tokens": 100,
    "prompt": "Classify this: {{input.text}}"
  }
}
```

## Cost Tracking

### Token Usage

Access token usage from execution results:

```apex
ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

if (result.trace != null && result.trace.usage != null) {
    Integer inputTokens = result.trace.usage.totalInputTokens;
    Integer outputTokens = result.trace.usage.totalOutputTokens;
    Decimal cost = result.trace.usage.totalCostUsd;

    System.debug('Input Tokens: ' + inputTokens);
    System.debug('Output Tokens: ' + outputTokens);
    System.debug('Estimated Cost: $' + cost);
}
```

### Pricing Reference

| Provider | Model | Input (per 1M) | Output (per 1M) |
|----------|-------|----------------|-----------------|
| Anthropic | Claude 3.5 Sonnet | $3.00 | $15.00 |
| Anthropic | Claude 3 Opus | $15.00 | $75.00 |
| Anthropic | Claude 3 Haiku | $0.25 | $1.25 |
| OpenAI | GPT-4o | $2.50 | $10.00 |
| OpenAI | GPT-4 Turbo | $10.00 | $30.00 |
| OpenAI | GPT-3.5 Turbo | $0.50 | $1.50 |
| Google | Gemini 1.5 Pro | $1.25 | $5.00 |
| Google | Gemini 1.5 Flash | $0.075 | $0.30 |
| Groq | Llama 3.3 70B | $0.59 | $0.79 |
| Groq | Llama 3.1 8B | $0.05 | $0.08 |
| Perplexity | Sonar Pro | $3.00 | $15.00 |
| Perplexity | Sonar | $1.00 | $1.00 |
| Perplexity | Sonar Reasoning | $1.00 | $5.00 |

*Prices as of December 2024. Check provider websites for current pricing.*

## Security Best Practices

### Named Credentials (Recommended for Production)

For production deployments, use Named Credentials instead of storing API keys in Custom Metadata:

1. Create an External Credential:
   - Go to **Setup → Named Credentials → External Credentials**
   - Create new with Authentication Protocol: Custom
   - Add a Principal with your API key as a header

2. Create a Named Credential:
   - Go to **Setup → Named Credentials → Named Credentials**
   - Point to your External Credential
   - URL: `https://api.anthropic.com`

3. Update provider configuration:
   ```
   UseNamedCredential__c: true
   NamedCredential__c: Anthropic_Named_Credential
   ```

### API Key Rotation

Regularly rotate API keys:

1. Generate new API key from provider dashboard
2. Update `LLMProviderConfig__mdt` record
3. Invalidate old key

### Rate Limiting

Implement rate limiting for production use:

```apex
// Check daily usage before execution
Integer dailyTokens = getDailyTokenUsage();
if (dailyTokens > MAX_DAILY_TOKENS) {
    throw new RateLimitException('Daily token limit exceeded');
}

ExecutionResult result = PipelineRunner.execute(pipelineJson, input);
```

## Multiple Providers

Use different providers for different use cases:

```json
{
  "stages": [
    {
      "id": "classify",
      "component_type": "generator",
      "config": {
        "provider": "Anthropic_Haiku",
        "prompt": "Classify: {{input.text}}",
        "max_tokens": 50,
        "temperature": 0.1
      }
    },
    {
      "id": "generate-response",
      "component_type": "generator",
      "config": {
        "provider": "Anthropic_Sonnet",
        "prompt": "Write a detailed response...",
        "max_tokens": 500,
        "temperature": 0.7
      }
    }
  ]
}
```

**Strategy**:
- Use fast/cheap models (Haiku, GPT-3.5) for classification
- Use capable models (Sonnet, GPT-4) for generation
- Use most capable (Opus, GPT-4) for complex reasoning

## Troubleshooting

### Authentication Errors

**Error**: `401 Unauthorized`

**Solution**:
- Verify API key is correct in Custom Metadata
- Check key hasn't expired
- Ensure account has sufficient credits

### Rate Limit Errors

**Error**: `429 Too Many Requests`

**Solution**:
- Implement retry with exponential backoff
- Use async execution to spread load
- Upgrade provider plan for higher limits

### Model Not Found

**Error**: `Model xyz not found`

**Solution**:
- Verify model name is correct
- Check model is available in your region
- Ensure account has access to the model

## Next Steps

- [Integration Patterns](08-integration-patterns.md) - Triggers, LWC, Flows
- [Examples](09-examples.md) - Complete pipeline examples
