/**
 * Operator Template Generator
 *
 * Generates Python code for a new FlowMason operator.
 */

interface OperatorOptions {
    name: string;
    className: string;
    category: string;
    description: string;
    icon: string;
    color: string;
}

export function getOperatorTemplate(options: OperatorOptions): string {
    const { name, className, category, description, icon, color } = options;

    return `"""
${className}

${description}
"""

from typing import Any, Dict, List, Optional
from pydantic import Field

from flowmason_core.components import operator, OperatorInput, OperatorOutput, ExecutionContext


@operator(
    name="${name}",
    category="${category}",
    description="${description}",
    icon="${icon}",
    color="${color}",
    version="1.0.0",
)
class ${className}:
    """${description}"""

    class Input(OperatorInput):
        """Input schema for ${className}."""

        data: str = Field(
            ...,
            description="The input data to process",
        )

        # Add more input fields as needed
        # options: Dict[str, Any] = Field(
        #     default_factory=dict,
        #     description="Processing options",
        # )

    class Output(OperatorOutput):
        """Output schema for ${className}."""

        result: Any = Field(
            ...,
            description="The processed result",
        )

        success: bool = Field(
            default=True,
            description="Whether the operation was successful",
        )

        errors: List[str] = Field(
            default_factory=list,
            description="Any errors that occurred during processing",
        )

    async def execute(self, input: Input, context: ExecutionContext) -> Output:
        """
        Execute the operator.

        Args:
            input: The validated input data
            context: Execution context with utilities

        Returns:
            Output: The processed result
        """
        try:
            # Process the input data
            # This is a placeholder - implement your logic here
            result = input.data

            return self.Output(
                result=result,
                success=True,
                errors=[],
            )

        except Exception as e:
            return self.Output(
                result=None,
                success=False,
                errors=[str(e)],
            )


# For testing
if __name__ == "__main__":
    import asyncio
    from flowmason_core.testing import MockContext

    async def test():
        op = ${className}()

        # Create mock context
        context = MockContext()

        # Test input
        input_data = ${className}.Input(data="test data")

        # Execute
        output = await op.execute(input_data, context)

        print(f"Result: {output.result}")
        print(f"Success: {output.success}")
        print(f"Errors: {output.errors}")

    asyncio.run(test())
`;
}
