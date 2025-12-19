# Installation

## Prerequisites

Before installing Flowmason for Salesforce, ensure you have:

1. **Salesforce Edition**: Enterprise, Unlimited, or Developer Edition
2. **API Version**: 62.0 or higher
3. **System Administrator** access to install packages
4. **LLM Provider Account**: Anthropic (Claude) or OpenAI (optional, for AI features)

## Install the Managed Package

### From AppExchange (Coming Soon)

1. Navigate to [AppExchange](https://appexchange.salesforce.com)
2. Search for "Flowmason"
3. Click **Get It Now**
4. Choose your org and click **Install**
5. Select "Install for All Users" or "Install for Admins Only"
6. Click **Install**

### Via Installation URL

For beta access, use the installation link provided by your Flowmason representative:

```
https://login.salesforce.com/packaging/installPackage.apexp?p0=04t...
```

## Post-Installation Setup

### 1. Configure Remote Site Settings

For LLM providers, add Remote Site Settings:

**Anthropic (Claude)**:
1. Go to Setup → Security → Remote Site Settings
2. Click **New Remote Site**
3. Configure:
   - Remote Site Name: `Anthropic`
   - Remote Site URL: `https://api.anthropic.com`
   - Active: ✓

**OpenAI (GPT)**:
1. Go to Setup → Security → Remote Site Settings
2. Click **New Remote Site**
3. Configure:
   - Remote Site Name: `OpenAI`
   - Remote Site URL: `https://api.openai.com`
   - Active: ✓

### 2. Configure LLM Provider

Create a Custom Metadata record for your LLM provider:

1. Go to Setup → Custom Metadata Types
2. Click **Manage Records** next to `LLMProviderConfig`
3. Click **New**
4. Configure:

```
Label: Anthropic Production
DeveloperName: Anthropic_Production
Provider: anthropic
Endpoint: https://api.anthropic.com/v1/messages
Model: claude-3-5-sonnet-20241022
API Key: [Your API Key]
Max Tokens: 4096
Temperature: 0.7
```

### 3. Assign Permissions

Ensure users have appropriate permissions:

**For Developers/Admins**:
- Assign the `Flowmason Admin` permission set

**For API Users**:
- Assign the `Flowmason User` permission set

```apex
// Assign permission set via Apex
PermissionSet ps = [SELECT Id FROM PermissionSet WHERE Name = 'Flowmason_Admin' LIMIT 1];
PermissionSetAssignment psa = new PermissionSetAssignment(
    PermissionSetId = ps.Id,
    AssigneeId = UserInfo.getUserId()
);
insert psa;
```

## Verify Installation

Run this anonymous Apex to verify the installation:

```apex
// Test basic pipeline execution
String pipelineJson = '{"name":"Test Pipeline","stages":[{"id":"test","component_type":"json_transform","config":{"data":{"message":"Hello"},"jmespath_expression":"@"},"depends_on":[]}],"output_stage_id":"test"}';

Map<String, Object> input = new Map<String, Object>();
ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

System.debug('Status: ' + result.status);
System.debug('Output: ' + result.output);
System.assert(result.status == 'success', 'Pipeline should execute successfully');
```

Expected output:
```
Status: success
Output: {_final={result={message=Hello}}}
```

## Troubleshooting

### Package Installation Fails

**Error**: "Cannot install package due to missing dependencies"

**Solution**: Ensure you're on API version 62.0+. Update your org's API version in Setup → Company Information.

### Remote Site Error

**Error**: "Unauthorized endpoint, please check Setup->Security->Remote site settings"

**Solution**: Add the LLM provider endpoint to Remote Site Settings (see step 1 above).

### Custom Metadata Not Found

**Error**: "LLMProviderConfig__mdt not found"

**Solution**: The package creates this metadata type. If missing, verify package installation completed successfully.

## Next Steps

- [Getting Started](02-getting-started.md) - Create your first pipeline
- [Development Workflow](03-development-workflow.md) - Set up local development
- [Providers](07-providers.md) - Configure additional LLM providers
