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
export declare function getOperatorTemplate(options: OperatorOptions): string;
export {};
//# sourceMappingURL=operatorTemplate.d.ts.map