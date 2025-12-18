"use strict";
/**
 * FlowMason Testing Module
 *
 * Provides VSCode Test Explorer integration for FlowMason tests.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerCoverageCommands = exports.getCoverageGuttersProvider = exports.CoverageGuttersProvider = exports.registerTestCommands = exports.FlowMasonTestController = void 0;
__exportStar(require("./types"), exports);
var testController_1 = require("./testController");
Object.defineProperty(exports, "FlowMasonTestController", { enumerable: true, get: function () { return testController_1.FlowMasonTestController; } });
Object.defineProperty(exports, "registerTestCommands", { enumerable: true, get: function () { return testController_1.registerTestCommands; } });
var coverageGutters_1 = require("./coverageGutters");
Object.defineProperty(exports, "CoverageGuttersProvider", { enumerable: true, get: function () { return coverageGutters_1.CoverageGuttersProvider; } });
Object.defineProperty(exports, "getCoverageGuttersProvider", { enumerable: true, get: function () { return coverageGutters_1.getCoverageGuttersProvider; } });
Object.defineProperty(exports, "registerCoverageCommands", { enumerable: true, get: function () { return coverageGutters_1.registerCoverageCommands; } });
//# sourceMappingURL=index.js.map