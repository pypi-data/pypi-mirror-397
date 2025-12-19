# Examples

Complete pipeline examples demonstrating various capabilities.

## Customer Support Triage

AI-powered classification and response generation.

```json
{
  "name": "Customer Support Triage",
  "version": "1.0.0",
  "stages": [
    {
      "id": "classify",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are a support ticket classifier. Analyze the ticket and output JSON with: category (billing/technical/account/other), priority (low/medium/high/critical), sentiment (positive/neutral/negative).",
        "prompt": "Classify this support ticket:\n\nSubject: {{input.subject}}\n\nDescription: {{input.description}}",
        "max_tokens": 100,
        "temperature": 0.1
      },
      "depends_on": []
    },
    {
      "id": "parse-classification",
      "component_type": "json_transform",
      "config": {
        "data": "{{upstream.classify.content}}",
        "jmespath_expression": "@"
      },
      "depends_on": ["classify"]
    },
    {
      "id": "generate-response",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are a professional support agent. Write helpful, empathetic responses.",
        "prompt": "Write a response for this {{upstream.parse-classification.result.category}} ticket:\n\nSubject: {{input.subject}}\nDescription: {{input.description}}\nPriority: {{upstream.parse-classification.result.priority}}\n\nProvide a helpful response addressing their concern.",
        "max_tokens": 300,
        "temperature": 0.7
      },
      "depends_on": ["parse-classification"]
    },
    {
      "id": "output",
      "component_type": "json_transform",
      "config": {
        "data": {
          "category": "{{upstream.parse-classification.result.category}}",
          "priority": "{{upstream.parse-classification.result.priority}}",
          "sentiment": "{{upstream.parse-classification.result.sentiment}}",
          "response": "{{upstream.generate-response.content}}"
        },
        "jmespath_expression": "@"
      },
      "depends_on": ["generate-response"]
    }
  ],
  "output_stage_id": "output"
}
```

**Usage**:
```apex
Map<String, Object> input = new Map<String, Object>{
    'subject' => 'Cannot access my account',
    'description' => 'I have been trying to login for 2 hours. Need urgent help!'
};

ExecutionResult result = PipelineRunner.execute(pipelineJson, input);
// Output: { category: "account", priority: "high", sentiment: "negative", response: "..." }
```

---

## Data Validation ETL

Validate, transform, and filter data without AI.

```json
{
  "name": "Data Validation ETL",
  "version": "1.0.0",
  "stages": [
    {
      "id": "validate",
      "component_type": "schema_validate",
      "config": {
        "data": "{{input.records}}",
        "schema": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "email": { "type": "string", "format": "email" },
              "name": { "type": "string", "minLength": 1 },
              "amount": { "type": "number", "minimum": 0 }
            },
            "required": ["email", "name"]
          }
        }
      },
      "depends_on": []
    },
    {
      "id": "filter-valid",
      "component_type": "filter",
      "config": {
        "data": "{{input.records}}",
        "condition": "item.amount > 0"
      },
      "depends_on": ["validate"]
    },
    {
      "id": "transform",
      "component_type": "json_transform",
      "config": {
        "data": "{{upstream.filter-valid.result}}",
        "jmespath_expression": "[*].{ email: email, name: name, amount: amount, tier: amount >= `1000` && 'gold' || amount >= `500` && 'silver' || 'bronze' }"
      },
      "depends_on": ["filter-valid"]
    },
    {
      "id": "set-stats",
      "component_type": "variable_set",
      "config": {
        "variables": {
          "total_records": "{{upstream.transform.result | length(@)}}",
          "total_amount": "{{upstream.transform.result | sum([*].amount)}}"
        }
      },
      "depends_on": ["transform"]
    },
    {
      "id": "output",
      "component_type": "json_transform",
      "config": {
        "data": {
          "records": "{{upstream.transform.result}}",
          "stats": {
            "count": "{{context.total_records}}",
            "total": "{{context.total_amount}}"
          }
        },
        "jmespath_expression": "@"
      },
      "depends_on": ["set-stats"]
    }
  ],
  "output_stage_id": "output"
}
```

---

## Content Generation

Generate multi-format marketing content from a product description.

```json
{
  "name": "Content Generation Pipeline",
  "version": "1.0.0",
  "stages": [
    {
      "id": "product-description",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are a marketing copywriter. Write compelling product descriptions.",
        "prompt": "Write a 2-3 sentence product description for:\n\nProduct: {{input.product_name}}\nFeatures: {{input.features}}\nTarget Audience: {{input.target_audience}}",
        "max_tokens": 150,
        "temperature": 0.7
      },
      "depends_on": []
    },
    {
      "id": "tagline",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are an advertising creative. Write catchy taglines.",
        "prompt": "Create a memorable tagline (max 10 words) for {{input.product_name}}",
        "max_tokens": 30,
        "temperature": 0.8
      },
      "depends_on": []
    },
    {
      "id": "social-post",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are a social media manager. Write engaging posts.",
        "prompt": "Write a LinkedIn post (max 200 words) announcing {{input.product_name}}. Include relevant hashtags.",
        "max_tokens": 200,
        "temperature": 0.7
      },
      "depends_on": []
    },
    {
      "id": "email-campaign",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are an email marketing specialist.",
        "prompt": "Write a promotional email for {{input.product_name}}. Include subject line, body, and CTA.",
        "max_tokens": 300,
        "temperature": 0.6
      },
      "depends_on": []
    },
    {
      "id": "output",
      "component_type": "json_transform",
      "config": {
        "data": {
          "product": "{{input.product_name}}",
          "description": "{{upstream.product-description.content}}",
          "tagline": "{{upstream.tagline.content}}",
          "social_post": "{{upstream.social-post.content}}",
          "email": "{{upstream.email-campaign.content}}"
        },
        "jmespath_expression": "@"
      },
      "depends_on": ["product-description", "tagline", "social-post", "email-campaign"]
    }
  ],
  "output_stage_id": "output"
}
```

**Note**: All 4 generator stages run in parallel for efficiency.

---

## Conditional Workflow

VIP routing with dynamic branching.

```json
{
  "name": "VIP Conditional Workflow",
  "version": "1.0.0",
  "stages": [
    {
      "id": "check-vip",
      "component_type": "conditional",
      "config": {
        "condition": "{{input.customer.lifetime_value}}",
        "condition_expression": "value >= 1000",
        "true_branch_stages": ["vip-treatment"],
        "false_branch_stages": ["standard-treatment"]
      },
      "depends_on": []
    },
    {
      "id": "vip-treatment",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are a premium concierge. Provide exceptional, personalized service.",
        "prompt": "Write a VIP response for {{input.customer.name}} (lifetime value: ${{input.customer.lifetime_value}}):\n\nRequest: {{input.request}}",
        "max_tokens": 400,
        "temperature": 0.7
      },
      "depends_on": ["check-vip"]
    },
    {
      "id": "standard-treatment",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are a helpful customer service agent.",
        "prompt": "Respond to this request from {{input.customer.name}}:\n\n{{input.request}}",
        "max_tokens": 300,
        "temperature": 0.7
      },
      "depends_on": ["check-vip"]
    },
    {
      "id": "route-request",
      "component_type": "router",
      "config": {
        "value": "{{input.request_type}}",
        "routes": {
          "order": ["process-order"],
          "refund": ["process-refund"],
          "complaint": ["process-complaint"]
        },
        "default_route": ["process-inquiry"]
      },
      "depends_on": ["check-vip"]
    }
  ]
}
```

---

## Error Handling with TryCatch

Graceful error recovery with fallback.

```json
{
  "name": "Safe Data Processing",
  "version": "1.0.0",
  "stages": [
    {
      "id": "safe-process",
      "component_type": "trycatch",
      "config": {
        "try_stages": ["risky-transform"],
        "catch_stages": ["fallback-transform"],
        "error_variable": "last_error"
      },
      "depends_on": []
    },
    {
      "id": "risky-transform",
      "component_type": "json_transform",
      "config": {
        "data": "{{input.data}}",
        "jmespath_expression": "complex.nested.path.that.might.fail"
      },
      "depends_on": []
    },
    {
      "id": "fallback-transform",
      "component_type": "json_transform",
      "config": {
        "data": {
          "error": "{{context.last_error}}",
          "fallback_result": "default_value"
        },
        "jmespath_expression": "@"
      },
      "depends_on": []
    },
    {
      "id": "log-result",
      "component_type": "logger",
      "config": {
        "message": "Processing complete",
        "level": "info",
        "data": "{{upstream.safe-process.result}}"
      },
      "depends_on": ["safe-process"]
    }
  ],
  "output_stage_id": "safe-process"
}
```

---

## Batch Processing with ForEach

Process arrays with iteration.

```json
{
  "name": "Batch Item Processor",
  "version": "1.0.0",
  "stages": [
    {
      "id": "process-items",
      "component_type": "foreach",
      "config": {
        "items": "{{input.items}}",
        "item_variable": "current_item",
        "loop_stages": ["transform-item"],
        "collect_results": true
      },
      "depends_on": []
    },
    {
      "id": "transform-item",
      "component_type": "json_transform",
      "config": {
        "data": {
          "original": "{{context.current_item}}",
          "index": "{{context.item_index}}",
          "processed": true
        },
        "jmespath_expression": "@"
      },
      "depends_on": []
    },
    {
      "id": "filter-valid",
      "component_type": "filter",
      "config": {
        "data": "{{upstream.process-items.results}}",
        "condition": "item.processed == true"
      },
      "depends_on": ["process-items"]
    },
    {
      "id": "output",
      "component_type": "json_transform",
      "config": {
        "data": {
          "items": "{{upstream.filter-valid.result}}",
          "count": "{{upstream.filter-valid.result | length(@)}}"
        },
        "jmespath_expression": "@"
      },
      "depends_on": ["filter-valid"]
    }
  ],
  "output_stage_id": "output"
}
```

---

## Book Chapter Editor

AI-powered editorial pipeline.

```json
{
  "name": "Book Chapter Editor",
  "version": "1.0.0",
  "stages": [
    {
      "id": "analyze",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are a text analyst. Output JSON with word_count, themes, tone, and literary_devices.",
        "prompt": "Analyze this chapter:\n\n{{input.content}}",
        "max_tokens": 300,
        "temperature": 0.1
      },
      "depends_on": []
    },
    {
      "id": "critique",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are a senior book editor. Provide constructive feedback.",
        "prompt": "Critique this {{input.genre}} chapter:\n\n{{input.content}}\n\nProvide detailed editorial feedback.",
        "max_tokens": 500,
        "temperature": 0.4
      },
      "depends_on": []
    },
    {
      "id": "version-refined",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are an expert editor. Make surgical improvements.",
        "prompt": "Refine this chapter based on the critique:\n\nOriginal:\n{{input.content}}\n\nCritique:\n{{upstream.critique.content}}\n\nOutput the refined version:",
        "max_tokens": 1000,
        "temperature": 0.6
      },
      "depends_on": ["critique"]
    },
    {
      "id": "version-humanized",
      "component_type": "generator",
      "config": {
        "system_prompt": "Make prose feel natural and authentic.",
        "prompt": "Humanize this chapter. Make it feel emotionally resonant:\n\n{{input.content}}",
        "max_tokens": 1000,
        "temperature": 0.75
      },
      "depends_on": []
    },
    {
      "id": "output",
      "component_type": "json_transform",
      "config": {
        "data": {
          "title": "{{input.title}}",
          "analysis": "{{upstream.analyze.content}}",
          "critique": "{{upstream.critique.content}}",
          "versions": [
            {"name": "Refined", "content": "{{upstream.version-refined.content}}"},
            {"name": "Humanized", "content": "{{upstream.version-humanized.content}}"}
          ]
        },
        "jmespath_expression": "@"
      },
      "depends_on": ["analyze", "version-refined", "version-humanized"]
    }
  ],
  "output_stage_id": "output"
}
```

## Next Steps

- [API Reference](10-api-reference.md) - Public Apex API
