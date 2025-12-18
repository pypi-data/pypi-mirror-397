/**
 * Node Template Generator
 *
 * Generates Python code for a new FlowMason node.
 */
interface NodeOptions {
    name: string;
    className: string;
    category: string;
    description: string;
    icon: string;
    color: string;
    requiresLlm: boolean;
}
export declare function getNodeTemplate(options: NodeOptions): string;
export {};
//# sourceMappingURL=nodeTemplate.d.ts.map