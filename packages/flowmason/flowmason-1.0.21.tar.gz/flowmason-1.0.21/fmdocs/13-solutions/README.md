# FlowMason Solutions

Production-ready solutions built with FlowMason that demonstrate real-world applications and best practices.

## What is a Solution?

A FlowMason Solution is a complete, deployable package that includes:

- **Pipeline Templates**: Pre-built pipelines ready to run
- **Documentation**: Architecture, implementation, and customization guides
- **Best Practices**: Patterns for production deployment
- **Integration Points**: Clear hooks for connecting to your systems

## Available Solutions

### Financial Counselling for Gambling Harm

**Status**: Production Ready
**Category**: Human Services
**Providers**: Claude + GPT-4 + Perplexity

AI-powered workflow for financial counsellors supporting clients affected by gambling harm. Features:

- Zero hallucination architecture with verified citations
- Multi-provider AI orchestration
- Human-in-the-loop design with crisis escalation
- Trauma-informed, empathetic language throughout

[View Documentation →](./financial-counselling/README.md)

---

## Building Your Own Solutions

Solutions follow a standard structure:

```
solution-name/
├── README.md                 # Overview and quick start
├── pipelines/
│   ├── main-pipeline.json    # Primary workflow
│   └── supporting-*.json     # Modular components
├── docs/
│   ├── architecture.md       # Technical deep-dive
│   ├── implementation.md     # Deployment guide
│   └── customization.md      # Adaptation guide
└── examples/
    ├── input.json            # Sample inputs
    └── output.json           # Expected outputs
```

### Key Principles

1. **Modular Design**: Break complex workflows into reusable pipelines
2. **Human-in-the-Loop**: AI augments, humans decide
3. **Verifiable Outputs**: Citations and audit trails
4. **Production-Ready**: Error handling, retries, observability

## Contributing Solutions

We welcome solution contributions! See the [Contributing Guide](../11-contributing/README.md) for details.

To propose a new solution:
1. Open a GitHub Discussion with your use case
2. Draft architecture and pipeline designs
3. Submit a PR with templates and documentation
