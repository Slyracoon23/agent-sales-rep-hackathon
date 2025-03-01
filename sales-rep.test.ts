import 'dotenv/config';
import { z } from 'zod';
import { describe, it, expect, inject } from 'vitest';
import dedent from 'dedent';
import { openai } from '@ai-sdk/openai';
import { generateText, generateObject } from 'ai';

// Ensure API key is available
if (!process.env.OPENAI_API_KEY) {
  console.error('Error: OPENAI_API_KEY environment variable is not set.');
  console.error('Please set it in your .env file or environment variables.');
  process.exit(1);
}

// Define schemas based on the YAML configuration
const JudgeEvaluationSchema = z.object({
  overallScore: z.number().min(0).max(100),
  metrics: z.object({
    conversationNaturalness: z.number().min(0).max(25),
    informationExchange: z.number().min(0).max(25),
    goalProgress: z.number().min(0).max(25),
    techniqueDemonstration: z.number().min(0).max(25)
  }),
  feedback: z.string(),
  agentAnalysis: z.object({
    salesAgentStrengths: z.array(z.string()),
    salesAgentWeaknesses: z.array(z.string()),
    customerAgentStrengths: z.array(z.string()),
    customerAgentWeaknesses: z.array(z.string())
  })
});

// Store conversation results for analysis
type ConversationStep = {
  agent: string;
  message: string;
};

declare module "vitest" {
  interface ProvidedContext {
    systemMessage: string;
    salesAgentSystemPrompt: string;
    customerAgentSystemPrompt: string;
  }
}

describe('Sales Call Simulation', () => {
  // Context fields for additional information
  const salesAgentContext = `
    <context>
      <company_details>
        <rates>Starting at 2.3% for qualified merchants</rates>
        <promotion>First month free for new customers</promotion>
        <integrations>All major e-commerce systems</integrations>
        <support>24/7 customer support</support>
      </company_details>
    </context>
  `;
  
  const customerAgentContext = `
    <context>
      <business_type>Online craft supply store</business_type>
      <current_provider>PayPal for 3 years</current_provider>
      <pain_point>Lack of responsive customer service</pain_point>
      <openness>Open to better options but needs convincing</openness>
    </context>
  `;

  // Initial system prompts from the YAML
  const salesAgentSystemPrompt = inject("salesAgentSystemPrompt") ?? dedent`
    You are a sales representative for Truss Payments, a payment processing company. Your goal is to:
    1. Introduce yourself and your company
    2. Identify the customer's needs and pain points
    3. Present relevant solutions and pricing
    4. Address objections professionally
    5. Move the conversation toward a demo or follow-up meeting
    
    Be persistent but not pushy. Listen to the customer's concerns and tailor your approach accordingly.

    <context>
      ${salesAgentContext}
    </context>
  `;
  
  const customerAgentSystemPrompt = inject("customerAgentSystemPrompt") ?? dedent`
    You are a small business owner who is currently using PayPal for payment processing. You have the following characteristics:
    1. Initially skeptical of changing providers
    2. Concerned about transaction fees (currently paying 3.5%)
    3. Had a negative experience with a previous sales call
    4. Process about 250 transactions per month
    5. Would be interested if there's a significant cost saving (>1%)
    
    Start somewhat dismissive but become more engaged if the sales rep addresses your concerns effectively.

    <context>
      ${customerAgentContext}
    </context>
  `;

  // Models defined in the configuration
  const salesAgentModel = openai('gpt-4o');
  const customerAgentModel = openai('gpt-4o'); // Using gpt-4-turbo as a stand-in for claude-3-sonnet
  const judgeModel = openai('gpt-4o');

  // Test a single iteration of the sales conversation
  it('Sales Call Simulation', async () => {
    // Initial conversation steps from the YAML
    const initialConversation: ConversationStep[] = [
      {
        agent: "sales_agent",
        message: "Hello, this is Alex from Truss Payments. We help small businesses reduce their payment processing fees while providing better support. Do you have a moment to chat about your current payment solution?"
      },
      {
        agent: "customer_agent",
        message: "I'm really not interested in changing payment providers right now. PayPal works fine for us."
      },
      {
        agent: "sales_agent",
        message: "I understand your hesitation. Many of our current clients felt the same way before they learned how much they could save. Would you mind sharing what your current transaction fees are with PayPal?"
      },
      {
        agent: "customer_agent",
        message: "We're paying around 3.5% plus a small fixed fee per transaction. I've heard sales pitches before and they always sound good until you read the fine print."
      }
    ];

    // Set up simulation parameters
    const maxTurns = 8;
    console.log(`\n📊 Starting Sales Call Simulation`);
    
    // Log the initial conversation first with colors
    console.log('\n--- Initial Conversation ---');
    initialConversation.forEach(step => {
      const agentColor = step.agent === "sales_agent" ? "\x1b[34m" : "\x1b[31m"; // Blue for sales, Red for customer
      console.log(`\n${agentColor}${step.agent === "sales_agent" ? "Sales Agent" : "Customer"}: ${step.message}\x1b[0m`);
    });
    console.log('\n--- Continuing Conversation ---');
    
    // Start with the initial conversation
    let conversation: ConversationStep[] = [...initialConversation];
    
    // Continue the conversation for maxTurns - initialConversation.length turns
    for (let turn = 0; turn < maxTurns - initialConversation.length; turn++) {
      // Determine whose turn it is - alternating turns
      const agentTurn = turn % 2 === 0 ? "sales_agent" : "customer_agent";
      const model = agentTurn === "sales_agent" ? salesAgentModel : customerAgentModel;
      const systemPrompt = agentTurn === "sales_agent" ? salesAgentSystemPrompt : customerAgentSystemPrompt;
      const agentColor = agentTurn === "sales_agent" ? "\x1b[34m" : "\x1b[31m"; // Blue for sales, Red for customer
      
      // Add a small delay between messages
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
      
      // Generate the next message
      const result = await generateText({
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          ...conversation.map(step => ({
            role: step.agent === agentTurn ? "assistant" as const : "user" as const,
            content: step.message
          }))
        ]
      });
      
      // Add to conversation
      conversation.push({
        agent: agentTurn,
        message: result.text
      });

      console.log(`\n${agentColor}${agentTurn === "sales_agent" ? "Sales Agent" : "Customer"}: ${result.text}\x1b[0m`);
    }
    
    // // Format conversation for judge evaluation
    // const conversationText = conversation
    //   .map(step => `${step.agent === "sales_agent" ? "Sales Agent" : "Customer"}: ${step.message}`)
    //   .join("\n\n");
    
    // // Generate judge evaluation
    // const evaluationPrompt = dedent`
    //   You are an expert conversation analyst tasked with evaluating a simulated conversation between a sales agent and a potential customer.
      
    //   Here is the conversation:
    //   ${conversationText}
      
    //   Your goal is to evaluate this conversation and provide detailed scoring and feedback.
      
    //   Score the conversation on these metrics (0-25 points each):
    //   1. Conversation Naturalness: How realistic and natural is the flow?
    //   2. Information Exchange: How effectively do agents share and request relevant information?
    //   3. Goal Progress: How much progress is made toward the sales agent's goal of moving toward a demo/meeting?
    //   4. Technique Demonstration: How well does the sales agent demonstrate effective techniques, and how realistically does the customer respond?
      
    //   In your feedback, provide:
    //   1. A summary of the overall conversation quality
    //   2. Specific strengths and weaknesses for each agent
    //   3. Examples from the conversation that illustrate your points
    //   4. Areas where the conversation could be improved
    // `;
    
    // console.log('\n📝 Judge Evaluation Prompt:');
    // console.log(evaluationPrompt);
    
    // const evaluation = await generateObject({
    //   model: judgeModel,
    //   prompt: evaluationPrompt,
    //   schema: JudgeEvaluationSchema
    // });
    
    // console.log('\n🤖 Judge Evaluation Result:');
    // console.log(JSON.stringify(evaluation.object, null, 2));
    
    
    // // Check if expectations are met
    // const finalScore = evaluation.object.overallScore;
    // const conversationNaturalness = evaluation.object.metrics.conversationNaturalness;
    // const informationExchange = evaluation.object.metrics.informationExchange;
    // const goalProgress = evaluation.object.metrics.goalProgress;
    // const techniqueDemonstration = evaluation.object.metrics.techniqueDemonstration;
    
    // // Set expectations based on YAML configuration
    // expect(finalScore).toBeGreaterThanOrEqual(70);
    // expect(conversationNaturalness).toBeGreaterThanOrEqual(17);
    // expect(informationExchange).toBeGreaterThanOrEqual(18);
    // expect(goalProgress).toBeGreaterThanOrEqual(18);
    // expect(techniqueDemonstration).toBeGreaterThanOrEqual(17);
    
    // console.log(`\n📈 Final Verdict: ${finalScore >= 70 ? '✅ PASSED' : '❌ FAILED'}`);
  });
});