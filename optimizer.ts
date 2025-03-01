import { inspect } from "node:util";
import { createOpenAI } from "@ai-sdk/openai";
import { generateObject } from "ai";
import { codeBlock } from "common-tags";
import { createVitest } from "vitest/node";
import { z } from "zod";

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
    systemMessage: string;
  }> = [];

  let currentSystemMessage = codeBlock`
    You are a very good AI assistant specialized in product management...
  `;

  let iteration = 0;

  let finalTestResults = null;

  while (iteration < MAX_ITERATIONS) {
    console.log(`\nIteration ${iteration + 1}:`);

    // Create a new Vitest instance for each iteration
    const vitest = await createVitest("test", {
      watch: false,
      include: testFiles,
    });

    // Provide the current system message
    vitest.provide("systemMessage", currentSystemMessage);

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
      systemMessage: currentSystemMessage,
    });

    // Store the test results from the final iteration
    finalTestResults = testResults;

    if (passRate >= REQUIRED_PASS_RATE) {
      console.log(
        `Achieved ${REQUIRED_PASS_RATE}% or higher pass rate! Stopping iterations.`,
      );
      break;
    }

    // Generate improved system message
    const prompt = `Current system message: ${currentSystemMessage}\n\nTest results: ${inspect(
      testResults,
      { depth: null },
    )}\n\nPlease analyze the test results and provide an improved system message with explanation.`;

    const { object } = await generateObject({
      model: openai("gpt-4o", { structuredOutputs: true }),
      schema: z.object({
        improvedSystemMessage: z
          .string()
          .describe("The improved system message based on test results"),
        analysis: z.string().describe("Analysis of what was improved and why"),
      }),
      system:
        "You are an AI expert at improving system prompts based on test results.",
      prompt,
    });

    // Update the system message for the next iteration
    currentSystemMessage = object.improvedSystemMessage;

    // Clean up the current Vitest instance
    await vitest.close();

    iteration++;
  }

  return {
    finalSystemMessage: currentSystemMessage,
    iterations: iteration,
    summary: iterationSummary,
    finalResults: finalTestResults,
  };
}

// Get test files from command line arguments
const testFiles = process.argv.slice(2);

if (testFiles.length === 0) {
  console.error("Please provide at least one test file path as an argument.");
  console.error(
    "Example: pnpm loop-agent src/benchmarks/copilot/daily_task_prioritization/identify-top-priority-tasks.test.ts",
  );
  process.exit(1);
}

console.log("Running tests for files:", testFiles);

runAgentTests(testFiles)
  .then((results) => {
    console.log(inspect(results, { depth: null, colors: true }));
    process.exit(0);
  })
  .catch((error) => {
    console.error("Test failed:", error);
    process.exit(1);
  });
