"use strict";
/**
 * Node Template Generator
 *
 * Generates Python code for a new FlowMason node.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.getNodeTemplate = getNodeTemplate;
function getNodeTemplate(options) {
    const { name, className, category, description, icon, color, requiresLlm } = options;
    const llmImport = requiresLlm ? '' : '';
    const llmUsage = requiresLlm ? `
        # Use the LLM to process the input
        response = await context.llm.generate(
            prompt=f"Process this text: {input.text}",
            system_prompt="You are a helpful assistant.",
            max_tokens=1000,
        )

        return self.Output(
            result=response.content,
            metadata={
                "model": response.model,
                "tokens_used": response.usage.get("total_tokens", 0) if response.usage else 0,
            }
        )` : `
        # Process the input (no LLM required)
        result = input.text.upper()  # Example transformation

        return self.Output(
            result=result,
            metadata={}
        )`;
    return `"""
${className}

${description}
"""

from typing import Any, Dict, Optional
from pydantic import Field

from flowmason_core.components import node, NodeInput, NodeOutput, ExecutionContext


@node(
    name="${name}",
    category="${category}",
    description="${description}",
    icon="${icon}",
    color="${color}",
    version="1.0.0",
    requires_llm=${requiresLlm ? 'True' : 'False'},
)
class ${className}:
    """${description}"""

    class Input(NodeInput):
        """Input schema for ${className}."""

        text: str = Field(
            ...,
            description="The input text to process",
            min_length=1,
        )

        # Add more input fields as needed
        # temperature: float = Field(
        #     default=0.7,
        #     description="Temperature for generation",
        #     ge=0.0,
        #     le=2.0,
        # )

    class Output(NodeOutput):
        """Output schema for ${className}."""

        result: str = Field(
            ...,
            description="The processed result",
        )

        metadata: Dict[str, Any] = Field(
            default_factory=dict,
            description="Additional metadata about the processing",
        )

    async def execute(self, input: Input, context: ExecutionContext) -> Output:
        """
        Execute the node.

        Args:
            input: The validated input data
            context: Execution context with LLM access and utilities

        Returns:
            Output: The processed result
        """${llmUsage}


# For testing
if __name__ == "__main__":
    import asyncio
    from flowmason_core.testing import MockContext, MockLLM

    async def test():
        node = ${className}()

        # Create mock context${requiresLlm ? `
        mock_llm = MockLLM(responses=["This is a test response."])
        context = MockContext(llm=mock_llm)` : `
        context = MockContext()`}

        # Test input
        input_data = ${className}.Input(text="Hello, world!")

        # Execute
        output = await node.execute(input_data, context)

        print(f"Result: {output.result}")
        print(f"Metadata: {output.metadata}")

    asyncio.run(test())
`;
}
//# sourceMappingURL=nodeTemplate.js.map