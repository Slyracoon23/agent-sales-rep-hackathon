import { inspect } from "node:util";
import { createOpenAI } from "@ai-sdk/openai";
import { generateObject } from "ai";
import { codeBlock } from "common-tags";
import { createVitest } from "vitest/node";
import { z } from "zod";

// Module augmentation for Vitest
declare module "vitest" {
  interface ProvidedContext {
    systemMessage: string;
  }
}

// Initialize AI client
const openai = createOpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  baseURL: process.env.OPENAI_API_BASE ?? "https://api.openai.com/v1",
  compatibility: "strict",
});

// Configuration constants
const MAX_ITERATIONS = 5;
const REQUIRED_PASS_RATE = 80;

export async function runAgentTests(testFiles: string[]) {
  const iterationSummary: Array<{
    iteration: number;
    passRate: number;
    salesAgentSystemPrompt?: string;
    customerAgentSystemPrompt?: string;
    supportAgentSystemPrompt?: string;
  }> = [];

  // Initial system prompts
  let salesAgentSystemPrompt = codeBlock`
    You are a sales representative for Truss Payments, a payment processing company. Your goal is to:
    1. Introduce yourself and your company
    2. Identify the customer's needs and pain points
    3. Present relevant solutions and pricing
    4. Address objections professionally
    5. Move the conversation toward a demo or follow-up meeting
    
    Be persistent but not pushy. Listen to the customer's concerns and tailor your approach accordingly.
  `;
  
  let customerAgentSystemPrompt = codeBlock`
    You are a small business owner who is currently using PayPal for payment processing. You have the following characteristics:
    1. Initially skeptical of changing providers
    2. Concerned about transaction fees (currently paying 3.5%)
    3. Had a negative experience with a previous sales call
    4. Process about 250 transactions per month
    5. Would be interested if there's a significant cost saving (>1%)
    
    Start somewhat dismissive but become more engaged if the sales rep addresses your concerns effectively.
  `;
  
  let supportAgentSystemPrompt = codeBlock`
    You are a customer support representative for Truss Payments. Handle this customer complaint professionally and resolve their issue.
  `;

  let iteration = 0;

  // Using a more generic type
  let finalTestResults: any[] | null = null;

  while (iteration < MAX_ITERATIONS) {
    console.log(`\nIteration ${iteration + 1}:`);

    // Create a new Vitest instance for each iteration
    const vitest = await createVitest("test", {
      watch: false,
      include: testFiles,
    });

    // Provide the current system prompts
    vitest.provide("systemMessage", "You are a helpful assistant.");
    // vitest.provide("salesAgentSystemPrompt", salesAgentSystemPrompt);
    // vitest.provide("customerAgentSystemPrompt", customerAgentSystemPrompt);
    // vitest.provide("supportAgentSystemPrompt", supportAgentSystemPrompt);

    // Run the tests
    await vitest.start();
    const testResults = vitest.state.getFiles();
    await vitest.close();

    const totalTests = testResults.length;
    const passedTests = testResults.filter(
      (result) => result.result?.state === "pass",
    ).length;
    const passRate = (passedTests / totalTests) * 100;

    console.log(`Pass rate: ${passRate.toFixed(2)}%`);

    iterationSummary.push({
      iteration: iteration + 1,
      passRate,
      salesAgentSystemPrompt,
      customerAgentSystemPrompt,
      supportAgentSystemPrompt,
    });

    // Store the test results from the final iteration
    finalTestResults = testResults;

    if (passRate >= REQUIRED_PASS_RATE) {
      console.log(
        `Achieved ${REQUIRED_PASS_RATE}% or higher pass rate! Stopping iterations.`,
      );
      break;
    }

    // Generate improved system prompts
    const prompt = `
Current prompts:

SALES AGENT:
${salesAgentSystemPrompt}

CUSTOMER AGENT:
${customerAgentSystemPrompt}

SUPPORT AGENT:
${supportAgentSystemPrompt}

Test results: ${inspect(testResults, { depth: null })}

Please analyze the test results and provide improved system prompts for the agents.
The sales agent should be more persuasive and address customer objections better.
The customer agent should be realistic in responses.
The support agent should be more empathetic and solutions-oriented.
`;

    const { object } = await generateObject({
      model: openai("gpt-4o", { structuredOutputs: true }),
      schema: z.object({
        salesAgentSystemPrompt: z
          .string()
          .describe("The improved sales agent system prompt based on test results"),
        customerAgentSystemPrompt: z
          .string()
          .describe("The improved customer agent system prompt based on test results"),
        supportAgentSystemPrompt: z
          .string()
          .describe("The improved support agent system prompt based on test results"),
        analysis: z.string().describe("Analysis of what was improved and why"),
      }),
      system:
        "You are an AI expert at improving system prompts based on test results.",
      prompt,
    });

    // Update the system prompts for the next iteration
    salesAgentSystemPrompt = object.salesAgentSystemPrompt;
    customerAgentSystemPrompt = object.customerAgentSystemPrompt;
    supportAgentSystemPrompt = object.supportAgentSystemPrompt;

    console.log("\nANALYSIS:");
    console.log(object.analysis);

    // Clean up the current Vitest instance
    await vitest.close();

    iteration++;
  }

  return {
    finalSalesAgentSystemPrompt: salesAgentSystemPrompt,
    finalCustomerAgentSystemPrompt: customerAgentSystemPrompt,
    finalSupportAgentSystemPrompt: supportAgentSystemPrompt,
    iterations: iteration,
    summary: iterationSummary,
    finalResults: finalTestResults,
  };
}

// Hardcode the test file to sales-rep.test.ts instead of using command line arguments
const testFiles = ["sales-rep.test.ts"];

console.log("Running tests for files:", testFiles);

runAgentTests(testFiles)
  .then((results) => {
    console.log("\n===== OPTIMIZATION RESULTS =====");
    console.log(`Total iterations: ${results.iterations}`);
    console.log("\nFinal Sales Agent System Prompt:");
    console.log(results.finalSalesAgentSystemPrompt);
    console.log("\nFinal Customer Agent System Prompt:");
    console.log(results.finalCustomerAgentSystemPrompt);
    console.log("\nFinal Support Agent System Prompt:");
    console.log(results.finalSupportAgentSystemPrompt);
    
    console.log("\nIteration Summary:");
    results.summary.forEach(iteration => {
      console.log(`Iteration ${iteration.iteration}: ${iteration.passRate.toFixed(2)}%`);
    });
    
    process.exit(0);
  })
  .catch((error) => {
    console.error("Test failed:", error);
    process.exit(1);
  });
