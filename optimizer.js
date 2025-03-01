"use strict";
var __makeTemplateObject = (this && this.__makeTemplateObject) || function (cooked, raw) {
    if (Object.defineProperty) { Object.defineProperty(cooked, "raw", { value: raw }); } else { cooked.raw = raw; }
    return cooked;
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var _a;
Object.defineProperty(exports, "__esModule", { value: true });
exports.runAgentTests = runAgentTests;
var node_util_1 = require("node:util");
var openai_1 = require("@ai-sdk/openai");
var ai_1 = require("ai");
var common_tags_1 = require("common-tags");
var node_1 = require("vitest/node");
var zod_1 = require("zod");
// Initialize AI client
var openai = (0, openai_1.createOpenAI)({
    apiKey: process.env.OPENAI_API_KEY,
    baseURL: (_a = process.env.OPENAI_API_BASE) !== null && _a !== void 0 ? _a : "https://api.openai.com/v1",
    compatibility: "strict",
});
// Configuration constants
var MAX_ITERATIONS = 5;
var REQUIRED_PASS_RATE = 80;
function runAgentTests(testFiles) {
    return __awaiter(this, void 0, void 0, function () {
        var iterationSummary, salesAgentSystemPrompt, customerAgentSystemPrompt, supportAgentSystemPrompt, iteration, finalTestResults, vitest, testResults, totalTests, passedTests, passRate, prompt_1, object;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    iterationSummary = [];
                    salesAgentSystemPrompt = (0, common_tags_1.codeBlock)(templateObject_1 || (templateObject_1 = __makeTemplateObject(["\n    You are a sales representative for Truss Payments, a payment processing company. Your goal is to:\n    1. Introduce yourself and your company\n    2. Identify the customer's needs and pain points\n    3. Present relevant solutions and pricing\n    4. Address objections professionally\n    5. Move the conversation toward a demo or follow-up meeting\n    \n    Be persistent but not pushy. Listen to the customer's concerns and tailor your approach accordingly.\n  "], ["\n    You are a sales representative for Truss Payments, a payment processing company. Your goal is to:\n    1. Introduce yourself and your company\n    2. Identify the customer's needs and pain points\n    3. Present relevant solutions and pricing\n    4. Address objections professionally\n    5. Move the conversation toward a demo or follow-up meeting\n    \n    Be persistent but not pushy. Listen to the customer's concerns and tailor your approach accordingly.\n  "])));
                    customerAgentSystemPrompt = (0, common_tags_1.codeBlock)(templateObject_2 || (templateObject_2 = __makeTemplateObject(["\n    You are a small business owner who is currently using PayPal for payment processing. You have the following characteristics:\n    1. Initially skeptical of changing providers\n    2. Concerned about transaction fees (currently paying 3.5%)\n    3. Had a negative experience with a previous sales call\n    4. Process about 250 transactions per month\n    5. Would be interested if there's a significant cost saving (>1%)\n    \n    Start somewhat dismissive but become more engaged if the sales rep addresses your concerns effectively.\n  "], ["\n    You are a small business owner who is currently using PayPal for payment processing. You have the following characteristics:\n    1. Initially skeptical of changing providers\n    2. Concerned about transaction fees (currently paying 3.5%)\n    3. Had a negative experience with a previous sales call\n    4. Process about 250 transactions per month\n    5. Would be interested if there's a significant cost saving (>1%)\n    \n    Start somewhat dismissive but become more engaged if the sales rep addresses your concerns effectively.\n  "])));
                    supportAgentSystemPrompt = (0, common_tags_1.codeBlock)(templateObject_3 || (templateObject_3 = __makeTemplateObject(["\n    You are a customer support representative for Truss Payments. Handle this customer complaint professionally and resolve their issue.\n  "], ["\n    You are a customer support representative for Truss Payments. Handle this customer complaint professionally and resolve their issue.\n  "])));
                    iteration = 0;
                    finalTestResults = null;
                    _a.label = 1;
                case 1:
                    if (!(iteration < MAX_ITERATIONS)) return [3 /*break*/, 7];
                    console.log("\nIteration ".concat(iteration + 1, ":"));
                    return [4 /*yield*/, (0, node_1.createVitest)("test", {
                            watch: false,
                            include: testFiles,
                        })];
                case 2:
                    vitest = _a.sent();
                    // Provide the current system prompts
                    vitest.provide("systemMessage", "You are a helpful assistant.");
                    // vitest.provide("salesAgentSystemPrompt", salesAgentSystemPrompt);
                    // vitest.provide("customerAgentSystemPrompt", customerAgentSystemPrompt);
                    // vitest.provide("supportAgentSystemPrompt", supportAgentSystemPrompt);
                    // Run the tests
                    return [4 /*yield*/, vitest.start()];
                case 3:
                    // vitest.provide("salesAgentSystemPrompt", salesAgentSystemPrompt);
                    // vitest.provide("customerAgentSystemPrompt", customerAgentSystemPrompt);
                    // vitest.provide("supportAgentSystemPrompt", supportAgentSystemPrompt);
                    // Run the tests
                    _a.sent();
                    testResults = vitest.state.getFiles();
                    return [4 /*yield*/, vitest.close()];
                case 4:
                    _a.sent();
                    totalTests = testResults.length;
                    passedTests = testResults.filter(function (result) { var _a; return ((_a = result.result) === null || _a === void 0 ? void 0 : _a.state) === "pass"; }).length;
                    passRate = (passedTests / totalTests) * 100;
                    console.log("Pass rate: ".concat(passRate.toFixed(2), "%"));
                    iterationSummary.push({
                        iteration: iteration + 1,
                        passRate: passRate,
                        salesAgentSystemPrompt: salesAgentSystemPrompt,
                        customerAgentSystemPrompt: customerAgentSystemPrompt,
                        supportAgentSystemPrompt: supportAgentSystemPrompt,
                    });
                    // Store the test results from the final iteration
                    finalTestResults = testResults;
                    if (passRate >= REQUIRED_PASS_RATE) {
                        console.log("Achieved ".concat(REQUIRED_PASS_RATE, "% or higher pass rate! Stopping iterations."));
                        return [3 /*break*/, 7];
                    }
                    prompt_1 = "\nCurrent prompts:\n\nSALES AGENT:\n".concat(salesAgentSystemPrompt, "\n\nCUSTOMER AGENT:\n").concat(customerAgentSystemPrompt, "\n\nSUPPORT AGENT:\n").concat(supportAgentSystemPrompt, "\n\nTest results: ").concat((0, node_util_1.inspect)(testResults, { depth: null }), "\n\nPlease analyze the test results and provide improved system prompts for the agents.\nThe sales agent should be more persuasive and address customer objections better.\nThe customer agent should be realistic in responses.\nThe support agent should be more empathetic and solutions-oriented.\n");
                    return [4 /*yield*/, (0, ai_1.generateObject)({
                            model: openai("gpt-4o", { structuredOutputs: true }),
                            schema: zod_1.z.object({
                                salesAgentSystemPrompt: zod_1.z
                                    .string()
                                    .describe("The improved sales agent system prompt based on test results"),
                                customerAgentSystemPrompt: zod_1.z
                                    .string()
                                    .describe("The improved customer agent system prompt based on test results"),
                                supportAgentSystemPrompt: zod_1.z
                                    .string()
                                    .describe("The improved support agent system prompt based on test results"),
                                analysis: zod_1.z.string().describe("Analysis of what was improved and why"),
                            }),
                            system: "You are an AI expert at improving system prompts based on test results.",
                            prompt: prompt_1,
                        })];
                case 5:
                    object = (_a.sent()).object;
                    // Update the system prompts for the next iteration
                    salesAgentSystemPrompt = object.salesAgentSystemPrompt;
                    customerAgentSystemPrompt = object.customerAgentSystemPrompt;
                    supportAgentSystemPrompt = object.supportAgentSystemPrompt;
                    console.log("\nANALYSIS:");
                    console.log(object.analysis);
                    // Clean up the current Vitest instance
                    return [4 /*yield*/, vitest.close()];
                case 6:
                    // Clean up the current Vitest instance
                    _a.sent();
                    iteration++;
                    return [3 /*break*/, 1];
                case 7: return [2 /*return*/, {
                        finalSalesAgentSystemPrompt: salesAgentSystemPrompt,
                        finalCustomerAgentSystemPrompt: customerAgentSystemPrompt,
                        finalSupportAgentSystemPrompt: supportAgentSystemPrompt,
                        iterations: iteration,
                        summary: iterationSummary,
                        finalResults: finalTestResults,
                    }];
            }
        });
    });
}
// Hardcode the test file to sales-rep.test.ts instead of using command line arguments
var testFiles = ["sales-rep.test.ts"];
console.log("Running tests for files:", testFiles);
runAgentTests(testFiles)
    .then(function (results) {
    console.log("\n===== OPTIMIZATION RESULTS =====");
    console.log("Total iterations: ".concat(results.iterations));
    console.log("\nFinal Sales Agent System Prompt:");
    console.log(results.finalSalesAgentSystemPrompt);
    console.log("\nFinal Customer Agent System Prompt:");
    console.log(results.finalCustomerAgentSystemPrompt);
    console.log("\nFinal Support Agent System Prompt:");
    console.log(results.finalSupportAgentSystemPrompt);
    console.log("\nIteration Summary:");
    results.summary.forEach(function (iteration) {
        console.log("Iteration ".concat(iteration.iteration, ": ").concat(iteration.passRate.toFixed(2), "%"));
    });
    process.exit(0);
})
    .catch(function (error) {
    console.error("Test failed:", error);
    process.exit(1);
});
var templateObject_1, templateObject_2, templateObject_3;
