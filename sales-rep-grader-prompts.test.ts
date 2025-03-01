import 'dotenv/config';
import { z } from 'zod';
import { describe, it, expect, inject } from 'vitest';
import dedent from 'dedent';
import { openai } from '@ai-sdk/openai';
import { generateObject } from 'ai';
import * as fs from 'fs';
import * as path from 'path';

// Ensure API key is available
if (!process.env.OPENAI_API_KEY) {
  console.error('Error: OPENAI_API_KEY environment variable is not set.');
  console.error('Please set it in your .env file or environment variables.');
  process.exit(1);
}

// Define schemas for evaluation results
const EvaluationSchema = z.object({
  salesAgentPassed: z.boolean(),
  customerAgentPassed: z.boolean(),
  overallPassed: z.boolean(),
  salesAgentFeedback: z.string().optional(),
  customerAgentFeedback: z.string().optional(),
});

// Define schema for grader output
const GraderOutputSchema = z.object({
  evaluation: EvaluationSchema
});

// Type definitions
type Conversation = {
  agent: string;
  message: string;
}[];

type TranscriptWithEvaluation = {
  simulationNumber: number;
  startIndex: number;
  duration: number;
  conversation: { agent: string; message: string }[];
  evaluation: {
    salesAgentPassed: boolean;
    customerAgentPassed: boolean;
    overallPassed: boolean;
    salesAgentFeedback?: string;
    customerAgentFeedback?: string;
  };
};

// Helper functions for reporting
const testResultsDir = path.join(process.cwd(), 'test-results');

// Ensure the directory exists
if (!fs.existsSync(testResultsDir)) {
  fs.mkdirSync(testResultsDir, { recursive: true });
}

// Function to save detailed test results
function saveTestResults(transcriptData, testResults, testStartTime) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  
  // Calculate summary statistics
  const totalEvaluations = testResults.length;
  const accurateEvaluations = testResults.filter(result => result.accurate).length;
  const accuracyRate = totalEvaluations > 0 ? (accurateEvaluations / totalEvaluations) * 100 : 0;
  
  // Create detailed results object
  const detailedResults = {
    summary: {
      totalEvaluations,
      accurateEvaluations,
      accuracyRate: `${accuracyRate.toFixed(2)}%`,
      timestamp: new Date().toISOString(),
      duration: (Date.now() - testStartTime) / 1000,
      testRunDate: new Date().toLocaleDateString(),
      testRunTime: new Date().toLocaleTimeString()
    },
    evaluations: testResults
  };
  
  // Save detailed results
  const detailedResultsPath = path.join(testResultsDir, `grader-evaluation-results-${timestamp}.json`);
  fs.writeFileSync(detailedResultsPath, JSON.stringify(detailedResults, null, 2));
  console.log(`\n📄 Detailed evaluation results saved to: ${detailedResultsPath}`);
  
  // Save summary results
  const summaryResultsPath = path.join(testResultsDir, 'latest-grader-summary.json');
  fs.writeFileSync(summaryResultsPath, JSON.stringify(detailedResults.summary, null, 2));
  console.log(`📄 Summary saved to: ${summaryResultsPath}`);
  
  return detailedResults;
}

describe('Sales Conversation Grader Evaluation Test', () => {
  // Load transcript data from file
  const transcriptsPath = path.join(process.cwd(), 'test', 'data', 'paste.txt');
  let transcripts: TranscriptWithEvaluation[] = [];
  
  try {
    // Parse the transcript data
    const fileContent = fs.readFileSync(transcriptsPath, 'utf8');
    transcripts = JSON.parse(fileContent);
    console.log(`📋 Loaded ${transcripts.length} transcripts for evaluation`);
  } catch (error) {
    console.error(`Error loading transcript data: ${error.message}`);
    process.exit(1);
  }
  
  // Get the grader system prompt from inject
  const graderSystemPrompt = inject("graderPrompt") ?? dedent`
    You are an expert conversation analyst tasked with evaluating a simulated conversation between a sales agent and a potential customer.
    
    Your goal is to evaluate this conversation and provide a boolean assessment for both the sales agent and customer agent.
    
    For the sales agent, evaluate:
    1. Did they effectively introduce themselves and Truss Payments?
    2. Did they attempt to identify the customer's payment challenges?
    3. Did they present the solution clearly?
    4. Did they emphasize key benefits relevant to the customer?
    5. Did they handle objections professionally?
    
    For the customer agent, evaluate:
    1. Did they maintain their established character traits (resistant to change, values relationships, etc.)?
    2. Did they communicate in a direct, sometimes blunt style?
    3. Did they question the benefits of changing their established processes?
    4. Did they respond realistically to the sales pitch?
    
    Provide a boolean value (true for pass, false for fail) for each agent, along with brief feedback explaining your decision.
    
    The overall evaluation should pass only if both the sales agent and customer agent pass.
  `;

  // Model for grader evaluation
  const graderModel = openai('gpt-4o');
  
  // Array to store test results
  const testResults = [];
  // Track test start time
  const testStartTime = Date.now();

  console.log('\n🔍 Grader Evaluation Test Starting...\n');

  // Run tests for each transcript
  transcripts.forEach((transcript, index) => {
    it(`Evaluates Transcript #${transcript.simulationNumber} correctly`, async () => {
      // Format conversation for grader evaluation
      const conversationText = transcript.conversation
        .map(step => `${step.agent}: ${step.message}`)
        .join("\n\n");
      
      // Prepare grader evaluation prompt
      const evaluationPrompt = dedent`
        Here is a conversation between a sales agent for Truss Payments and a potential customer:
        
        ${conversationText}
        
        Evaluate this conversation based on the specified criteria.
      `;
      
      console.log(`\n📊 Evaluating Transcript #${transcript.simulationNumber}`);
      
      // Generate grader evaluation
      const graderResult = await generateObject({
        model: graderModel,
        systemPrompt: graderSystemPrompt,
        prompt: evaluationPrompt,
        schema: GraderOutputSchema
      });
      
      // Extract the evaluation from the result
      const evaluation = graderResult.object.evaluation;
      
      // Compare with expected evaluation from transcript
      const expectedEvaluation = transcript.evaluation;
      
      // Check if the evaluation matches the expected results
      const salesAgentMatch = evaluation.salesAgentPassed === expectedEvaluation.salesAgentPassed;
      const customerAgentMatch = evaluation.customerAgentPassed === expectedEvaluation.customerAgentPassed;
      const overallMatch = evaluation.overallPassed === expectedEvaluation.overallPassed;
      const evaluationAccurate = salesAgentMatch && customerAgentMatch && overallMatch;
      
      console.log(`\n📈 Transcript #${transcript.simulationNumber} Grader Accuracy: ${evaluationAccurate ? '✅ ACCURATE' : '❌ INACCURATE'}`);
      console.log(`Sales Agent Evaluation: ${salesAgentMatch ? '✅ MATCH' : '❌ MISMATCH'} (Expected: ${expectedEvaluation.salesAgentPassed}, Got: ${evaluation.salesAgentPassed})`);
      console.log(`Customer Agent Evaluation: ${customerAgentMatch ? '✅ MATCH' : '❌ MISMATCH'} (Expected: ${expectedEvaluation.customerAgentPassed}, Got: ${evaluation.customerAgentPassed})`);
      console.log(`Overall Evaluation: ${overallMatch ? '✅ MATCH' : '❌ MISMATCH'} (Expected: ${expectedEvaluation.overallPassed}, Got: ${evaluation.overallPassed})`);
      
      if (!evaluationAccurate) {
        console.log("\n📝 Grader Feedback:");
        console.log(`Sales Agent Feedback: ${evaluation.salesAgentFeedback}`);
        console.log(`Customer Agent Feedback: ${evaluation.customerAgentFeedback}`);
        
        console.log("\n📝 Expected Feedback:");
        console.log(`Sales Agent Feedback: ${expectedEvaluation.salesAgentFeedback}`);
        console.log(`Customer Agent Feedback: ${expectedEvaluation.customerAgentFeedback}`);
      }
      
      // Store the results for summary analysis
      testResults.push({
        transcriptNumber: transcript.simulationNumber,
        accurate: evaluationAccurate,
        salesAgentMatch,
        customerAgentMatch,
        overallMatch,
        expected: {
          salesAgentPassed: expectedEvaluation.salesAgentPassed,
          customerAgentPassed: expectedEvaluation.customerAgentPassed,
          overallPassed: expectedEvaluation.overallPassed
        },
        actual: {
          salesAgentPassed: evaluation.salesAgentPassed,
          customerAgentPassed: evaluation.customerAgentPassed,
          overallPassed: evaluation.overallPassed,
          salesAgentFeedback: evaluation.salesAgentFeedback,
          customerAgentFeedback: evaluation.customerAgentFeedback
        }
      });
      
      // Set expectation for test
      expect(evaluationAccurate).toBe(true);
    });
  });

  // Add a summary test that runs after all evaluations
  it('Grader Evaluation Summary', () => {
    console.log('\n📊 EVALUATION SUMMARY 📊');
    console.log(`Total Transcripts Evaluated: ${testResults.length}`);
    
    const accurateEvaluations = testResults.filter(result => result.accurate).length;
    const accuracyRate = (accurateEvaluations / testResults.length * 100).toFixed(2);
    console.log(`Accurate Evaluations: ${accurateEvaluations} (${accuracyRate}%)`);
    
    // Output detailed results
    console.log('\nDetailed Results:');
    testResults.forEach(result => {
      console.log(`\nTranscript #${result.transcriptNumber}:`);
      console.log(`  Overall Accuracy: ${result.accurate ? '✅ ACCURATE' : '❌ INACCURATE'}`);
      console.log(`  Sales Agent Evaluation: ${result.salesAgentMatch ? '✅ MATCH' : '❌ MISMATCH'}`);
      console.log(`  Customer Agent Evaluation: ${result.customerAgentMatch ? '✅ MATCH' : '❌ MISMATCH'}`);
      console.log(`  Overall Evaluation: ${result.overallMatch ? '✅ MATCH' : '❌ MISMATCH'}`);
    });
    
    // Save all results to files
    saveTestResults(transcripts, testResults, testStartTime);
    
    // Calculate total test duration
    const totalDuration = (Date.now() - testStartTime) / 1000;
    console.log(`\n⏱️ Total Test Duration: ${totalDuration.toFixed(2)}s`);
    console.log(`\n📊 Final Result: ${accurateEvaluations}/${testResults.length} evaluations accurate (${accuracyRate}%)`);
    
    // This test is just for reporting, always passes
    expect(true).toBe(true);
  });
});