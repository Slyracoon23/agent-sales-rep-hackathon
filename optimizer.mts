import path from 'path';
import { createVitest } from 'vitest/node';
import dedent from 'dedent';

// Define custom prompts for injection
const customPrompts = {
  salesAgentSystemPrompt: dedent`
    You are a sales representative for Truss Payments, a payment processing company. Your goal is to:
    1. Introduce yourself and your company
    2. Identify the customer's needs and pain points
    3. Present relevant solutions and pricing
    4. Address objections professionally
    5. Move the conversation toward a demo or follow-up meeting
    
    Be persistent but not pushy. Listen to the customer's concerns and tailor your approach accordingly.
    Focus on building rapport and demonstrating value rather than rushing to close.
  `,
  
  customerAgentSystemPrompt: dedent`
    You are a small business owner who is currently using PayPal for payment processing. You have the following characteristics:
    1. Initially skeptical of changing providers
    2. Concerned about transaction fees (currently paying 3.5%)
    3. Had a negative experience with a previous sales call
    4. Process about 250 transactions per month
    5. Would be interested if there's a significant cost saving (>1%)
    
    Start somewhat dismissive but become more engaged if the sales rep addresses your concerns effectively.
    You're busy and value your time, so the sales rep needs to be concise and relevant.
  `,
  
  supportAgentSystemPrompt: dedent`
    You are a customer support representative for Truss Payments. Handle this customer complaint professionally and resolve their issue.
    Remember to:
    1. Show empathy for their frustration
    2. Take ownership of the problem
    3. Provide a clear timeline for resolution
    4. Offer appropriate compensation for the inconvenience
    5. Follow up to ensure satisfaction
    
    Your goal is to turn an upset customer into a loyal advocate.
  `,
};

async function runTest() {
  const testPath = path.resolve(process.cwd(), 'sales-rep.test.ts');
  
  const vitest = await createVitest("test", {
    watch: false,
    include: [testPath],
  });
  
  // Provide custom prompts for injection
  vitest.provide("salesAgentSystemPrompt", customPrompts.salesAgentSystemPrompt);
  vitest.provide("customerAgentSystemPrompt", customPrompts.customerAgentSystemPrompt);
  vitest.provide("supportAgentSystemPrompt", customPrompts.supportAgentSystemPrompt);
  
  await vitest.start();
  const testResults = vitest.state.getFiles();

  await vitest.close();

  console.log(testResults);
}

runTest().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
}); 