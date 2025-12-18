# Integration Patterns

Integrate Flowmason pipelines with Salesforce automation.

## Apex Trigger Integration

### Case Triage on Insert

```apex
trigger CaseTriage on Case (after insert) {
    // Load pipeline from Static Resource
    StaticResource sr = [
        SELECT Body FROM StaticResource
        WHERE Name = 'SupportTriagePipeline' LIMIT 1
    ];
    String pipelineJson = sr.Body.toString();

    List<Case> casesToUpdate = new List<Case>();

    for (Case c : Trigger.New) {
        Map<String, Object> input = new Map<String, Object>{
            'subject' => c.Subject,
            'description' => c.Description,
            'caseId' => c.Id
        };

        // Execute synchronously (for quick pipelines)
        ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

        if (result.status == 'success') {
            Map<String, Object> output = (Map<String, Object>) result.output.get('_final');
            Map<String, Object> finalResult = (Map<String, Object>) output.get('result');

            casesToUpdate.add(new Case(
                Id = c.Id,
                Category__c = (String) finalResult.get('category'),
                Priority = (String) finalResult.get('priority'),
                AI_Response__c = (String) finalResult.get('response')
            ));
        }
    }

    if (!casesToUpdate.isEmpty()) {
        update casesToUpdate;
    }
}
```

### Async Trigger Pattern (Recommended)

For longer-running pipelines, use async execution:

```apex
trigger CaseTriageAsync on Case (after insert) {
    StaticResource sr = [
        SELECT Body FROM StaticResource
        WHERE Name = 'SupportTriagePipeline' LIMIT 1
    ];
    String pipelineJson = sr.Body.toString();

    for (Case c : Trigger.New) {
        Map<String, Object> input = new Map<String, Object>{
            'subject' => c.Subject,
            'description' => c.Description,
            'caseId' => c.Id
        };

        // Execute asynchronously
        String executionId = PipelineQueueable.enqueue(pipelineJson, input);

        // Store execution ID for tracking
        System.debug('Started execution: ' + executionId);
    }
}
```

---

## Lightning Web Component Integration

### Apex Controller

```apex
public with sharing class PipelineController {
    @AuraEnabled(cacheable=false)
    public static Map<String, Object> triageTicket(String subject, String description) {
        StaticResource sr = [
            SELECT Body FROM StaticResource
            WHERE Name = 'SupportTriagePipeline' LIMIT 1
        ];

        Map<String, Object> input = new Map<String, Object>{
            'subject' => subject,
            'description' => description
        };

        ExecutionResult result = PipelineRunner.execute(sr.Body.toString(), input);

        if (result.status == 'success') {
            Map<String, Object> output = (Map<String, Object>) result.output.get('_final');
            return (Map<String, Object>) output.get('result');
        } else {
            throw new AuraHandledException(result.errorMessage);
        }
    }

    @AuraEnabled
    public static String startAsyncPipeline(String pipelineName, String inputJson) {
        StaticResource sr = [
            SELECT Body FROM StaticResource
            WHERE Name = :pipelineName LIMIT 1
        ];

        Map<String, Object> input = (Map<String, Object>) JSON.deserializeUntyped(inputJson);
        return PipelineQueueable.enqueue(sr.Body.toString(), input);
    }

    @AuraEnabled
    public static Map<String, Object> getExecutionStatus(String executionId) {
        PipelineExecution__c exec = [
            SELECT Status__c, Progress__c, Output__c, ErrorMessage__c
            FROM PipelineExecution__c
            WHERE ExecutionId__c = :executionId
            LIMIT 1
        ];

        return new Map<String, Object>{
            'status' => exec.Status__c,
            'progress' => exec.Progress__c,
            'output' => exec.Output__c != null ?
                JSON.deserializeUntyped(exec.Output__c) : null,
            'error' => exec.ErrorMessage__c
        };
    }
}
```

### LWC Component

```javascript
// ticketTriage.js
import { LightningElement, track } from 'lwc';
import triageTicket from '@salesforce/apex/PipelineController.triageTicket';

export default class TicketTriage extends LightningElement {
    @track subject = '';
    @track description = '';
    @track result = null;
    @track loading = false;
    @track error = null;

    handleSubjectChange(event) {
        this.subject = event.target.value;
    }

    handleDescriptionChange(event) {
        this.description = event.target.value;
    }

    async handleTriage() {
        this.loading = true;
        this.error = null;

        try {
            this.result = await triageTicket({
                subject: this.subject,
                description: this.description
            });
        } catch (err) {
            this.error = err.body?.message || 'An error occurred';
        } finally {
            this.loading = false;
        }
    }
}
```

```html
<!-- ticketTriage.html -->
<template>
    <lightning-card title="AI Ticket Triage">
        <div class="slds-p-horizontal_medium">
            <lightning-input
                label="Subject"
                value={subject}
                onchange={handleSubjectChange}>
            </lightning-input>

            <lightning-textarea
                label="Description"
                value={description}
                onchange={handleDescriptionChange}>
            </lightning-textarea>

            <lightning-button
                label="Triage Ticket"
                variant="brand"
                onclick={handleTriage}
                disabled={loading}>
            </lightning-button>

            <template if:true={loading}>
                <lightning-spinner alternative-text="Processing..."></lightning-spinner>
            </template>

            <template if:true={result}>
                <div class="slds-m-top_medium">
                    <p><strong>Category:</strong> {result.category}</p>
                    <p><strong>Priority:</strong> {result.priority}</p>
                    <p><strong>Suggested Response:</strong></p>
                    <p>{result.response}</p>
                </div>
            </template>

            <template if:true={error}>
                <div class="slds-text-color_error">{error}</div>
            </template>
        </div>
    </lightning-card>
</template>
```

---

## Flow Builder Integration

### Invocable Action

```apex
public class FlowPipelineAction {
    @InvocableMethod(
        label='Run AI Pipeline'
        description='Execute a Flowmason pipeline'
        category='AI'
    )
    public static List<PipelineOutput> runPipeline(List<PipelineInput> inputs) {
        List<PipelineOutput> outputs = new List<PipelineOutput>();

        for (PipelineInput input : inputs) {
            // Load pipeline
            StaticResource sr = [
                SELECT Body FROM StaticResource
                WHERE Name = :input.pipelineName LIMIT 1
            ];

            // Build input map
            Map<String, Object> inputMap = new Map<String, Object>();
            if (String.isNotBlank(input.inputField1Name)) {
                inputMap.put(input.inputField1Name, input.inputField1Value);
            }
            if (String.isNotBlank(input.inputField2Name)) {
                inputMap.put(input.inputField2Name, input.inputField2Value);
            }

            // Execute
            ExecutionResult result = PipelineRunner.execute(
                sr.Body.toString(),
                inputMap
            );

            // Build output
            PipelineOutput output = new PipelineOutput();
            output.success = result.status == 'success';

            if (output.success) {
                Map<String, Object> finalOutput = (Map<String, Object>) result.output.get('_final');
                Map<String, Object> finalResult = (Map<String, Object>) finalOutput.get('result');
                output.outputJson = JSON.serialize(finalResult);
                output.outputField1 = (String) finalResult.get('category');
                output.outputField2 = (String) finalResult.get('priority');
            } else {
                output.errorMessage = result.errorMessage;
            }

            outputs.add(output);
        }

        return outputs;
    }

    public class PipelineInput {
        @InvocableVariable(label='Pipeline Name' required=true)
        public String pipelineName;

        @InvocableVariable(label='Input Field 1 Name')
        public String inputField1Name;

        @InvocableVariable(label='Input Field 1 Value')
        public String inputField1Value;

        @InvocableVariable(label='Input Field 2 Name')
        public String inputField2Name;

        @InvocableVariable(label='Input Field 2 Value')
        public String inputField2Value;
    }

    public class PipelineOutput {
        @InvocableVariable(label='Success')
        public Boolean success;

        @InvocableVariable(label='Output JSON')
        public String outputJson;

        @InvocableVariable(label='Output Field 1')
        public String outputField1;

        @InvocableVariable(label='Output Field 2')
        public String outputField2;

        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }
}
```

---

## Batch Apex Integration

### Process Records in Batches

```apex
public class AIEnrichmentBatch implements Database.Batchable<SObject>, Database.AllowsCallouts {
    private String pipelineJson;

    public AIEnrichmentBatch() {
        StaticResource sr = [
            SELECT Body FROM StaticResource
            WHERE Name = 'EnrichmentPipeline' LIMIT 1
        ];
        this.pipelineJson = sr.Body.toString();
    }

    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator([
            SELECT Id, Name, Description, Industry
            FROM Account
            WHERE AI_Enriched__c = false
            LIMIT 1000
        ]);
    }

    public void execute(Database.BatchableContext bc, List<Account> accounts) {
        List<Account> toUpdate = new List<Account>();

        for (Account acc : accounts) {
            Map<String, Object> input = new Map<String, Object>{
                'name' => acc.Name,
                'description' => acc.Description,
                'industry' => acc.Industry
            };

            ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

            if (result.status == 'success') {
                Map<String, Object> output = (Map<String, Object>) result.output.get('_final');
                Map<String, Object> finalResult = (Map<String, Object>) output.get('result');

                toUpdate.add(new Account(
                    Id = acc.Id,
                    AI_Summary__c = (String) finalResult.get('summary'),
                    AI_Industry_Insights__c = (String) finalResult.get('insights'),
                    AI_Enriched__c = true
                ));
            }

            // Check governor limits
            if (Limits.getCallouts() >= Limits.getLimitCallouts() - 5) {
                break; // Stop processing, will continue in next batch
            }
        }

        if (!toUpdate.isEmpty()) {
            update toUpdate;
        }
    }

    public void finish(Database.BatchableContext bc) {
        System.debug('AI Enrichment Batch Complete');
    }
}

// Execute with:
// Database.executeBatch(new AIEnrichmentBatch(), 10);
```

---

## Scheduled Apex Integration

### Daily Pipeline Execution

```apex
public class DailyReportPipeline implements Schedulable {
    public void execute(SchedulableContext sc) {
        // Gather data
        AggregateResult[] results = [
            SELECT COUNT(Id) cnt, Status
            FROM Case
            WHERE CreatedDate = TODAY
            GROUP BY Status
        ];

        Map<String, Integer> caseStats = new Map<String, Integer>();
        for (AggregateResult ar : results) {
            caseStats.put((String) ar.get('Status'), (Integer) ar.get('cnt'));
        }

        // Load and run pipeline
        StaticResource sr = [
            SELECT Body FROM StaticResource
            WHERE Name = 'DailyReportPipeline' LIMIT 1
        ];

        Map<String, Object> input = new Map<String, Object>{
            'date' => Date.today().format(),
            'caseStats' => caseStats
        };

        // Use async for scheduled context
        PipelineQueueable.enqueue(sr.Body.toString(), input);
    }
}

// Schedule with:
// System.schedule('Daily Report', '0 0 8 * * ?', new DailyReportPipeline());
```

---

## Platform Event Monitoring

### Real-Time Status Updates

```apex
trigger PipelineStatusHandler on PipelineStatus__e (after insert) {
    List<PipelineExecution__c> toUpdate = new List<PipelineExecution__c>();

    for (PipelineStatus__e event : Trigger.New) {
        // Log status change
        System.debug('Pipeline ' + event.ExecutionId__c + ': ' +
            event.Status__c + ' (' + event.Progress__c + '%)');

        // Notify on completion or failure
        if (event.Status__c == 'Completed' || event.Status__c == 'Failed') {
            // Send notification
            notifyUser(event);
        }
    }
}

private static void notifyUser(PipelineStatus__e event) {
    // Send Chatter post, email, or push notification
    FeedItem post = new FeedItem(
        ParentId = UserInfo.getUserId(),
        Body = 'Pipeline ' + event.ExecutionId__c + ' ' + event.Status__c +
            (event.Status__c == 'Failed' ? ': ' + event.Message__c : '')
    );
    insert post;
}
```

## Next Steps

- [Examples](09-examples.md) - Complete pipeline examples
- [API Reference](10-api-reference.md) - Public Apex API
