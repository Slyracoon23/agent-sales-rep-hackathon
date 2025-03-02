import 'dotenv/config';
import { z } from 'zod';
import { describe, it, expect, inject } from 'vitest';
import dedent from 'dedent';
import { openai } from '@ai-sdk/openai';
import { generateText, generateObject } from 'ai';
// Import the conversation data
import { fullConversation, getInitialConversation, getConversationFromIndex, conversationStartPoint, ConversationStep } from './test/data/sales-conversation';
import * as fs from 'fs';
import * as path from 'path';

// Ensure API key is available
if (!process.env.OPENAI_API_KEY) {
  console.error('Error: OPENAI_API_KEY environment variable is not set.');
  console.error('Please set it in your .env file or environment variables.');
  process.exit(1);
}

// Define schemas based on the YAML configuration
const SalesAgentEvaluationSchema = z.object({
  salesAgent: z.boolean(),
  salesAgentFeedback: z.string().optional()
});

const CustomerAgentEvaluationSchema = z.object({
  customerAgent: z.boolean(),
  customerAgentFeedback: z.string().optional()
});

const JudgeEvaluationSchema = z.object({
  agentEvaluation: z.object({
    ...SalesAgentEvaluationSchema.shape,
    ...CustomerAgentEvaluationSchema.shape
  })
});

const OptimizerEvaluationSchema = z.object({
  optimizedPrompt: z.string(),
  reasoningForChanges: z.string()
});

// Store conversation results for analysis
// type ConversationStep = {
//   agent: string;
//   message: string;
// };

declare module "vitest" {
  interface ProvidedContext {
    systemMessage: string;
    salesAgentSystemPrompt: string;
    customerAgentSystemPrompt: string;
  }
}

// Helper functions for reporting
const testResultsDir = path.join(process.cwd(), 'test-results');

// Ensure the directory exists
if (!fs.existsSync(testResultsDir)) {
  fs.mkdirSync(testResultsDir, { recursive: true });
}

// Function to save detailed test results
function saveDetailedResults(conversationData, simulationResults, testStartTime) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  
  // Calculate summary statistics
  const totalSimulations = simulationResults.length;
  const passedSimulations = simulationResults.filter(result => result.overallPassed).length;
  const passRate = totalSimulations > 0 ? (passedSimulations / totalSimulations) * 100 : 0;
  
  // Create detailed results object
  const detailedResults = {
    summary: {
      totalSimulations,
      passedSimulations,
      passRate: `${passRate.toFixed(2)}%`,
      timestamp: new Date().toISOString(),
      duration: (Date.now() - testStartTime) / 1000,
      testRunDate: new Date().toLocaleDateString(),
      testRunTime: new Date().toLocaleTimeString()
    },
    simulations: {}
  };
  
  // Process each simulation to create a cleaner output
  conversationData.forEach(simulation => {
    detailedResults.simulations[simulation.simulationNumber] = {
      id: simulation.simulationNumber,
      startIndex: simulation.startIndex,
      passed: simulation.evaluation.overallPassed,
      salesAgentPassed: simulation.evaluation.salesAgentPassed,
      customerAgentPassed: simulation.evaluation.customerAgentPassed,
      salesAgentFeedback: simulation.evaluation.salesAgentFeedback || '',
      customerAgentFeedback: simulation.evaluation.customerAgentFeedback || '',
      conversation: simulation.conversation
    };
  });
  
  // Save detailed results
  const detailedResultsPath = path.join(testResultsDir, `sales-simulation-results-${timestamp}.json`);
  fs.writeFileSync(detailedResultsPath, JSON.stringify(detailedResults, null, 2));
  console.log(`\n📄 Detailed simulation results saved to: ${detailedResultsPath}`);
  
  // Save conversation data
  const conversationDataPath = path.join(testResultsDir, 'conversation-data.json');
  fs.writeFileSync(conversationDataPath, JSON.stringify(conversationData, null, 2));
  console.log(`📄 Conversation data saved to: ${conversationDataPath}`);
  
  // Save summary results
  const summaryResultsPath = path.join(testResultsDir, 'latest-simulation-summary.json');
  fs.writeFileSync(summaryResultsPath, JSON.stringify(detailedResults.summary, null, 2));
  console.log(`📄 Summary saved to: ${summaryResultsPath}`);
  
  // Save simulation results
  const simulationResultsPath = path.join(testResultsDir, 'simulation-results.json');
  fs.writeFileSync(
    simulationResultsPath,
    JSON.stringify({
      totalSimulations,
      passedSimulations,
      passRate: `${passRate.toFixed(2)}%`,
      results: simulationResults
    }, null, 2)
  );
  console.log(`📄 Simulation results saved to: ${simulationResultsPath}`);
  
  return detailedResults;
}

describe('Sales Call Simulation', () => {
  // Context fields for additional information
  const salesAgentContext = `
    <context>
      <company_details>
        <name>Truss Payments</name>
        <description>Payment processing service for contractors</description>
        <extended_overview>
          Truss Payments is a comprehensive financial technology platform specifically tailored 
          for construction businesses in the US and Canada. It offers an all-in-one banking solution 
          designed to streamline financial management, improve cash flow, and reduce operational 
          costs for contractors of all sizes.
        </extended_overview>
        <key_features>
          <feature>Free service with no processing fees</feature>
          <feature>Instant settlement for all payment types</feature>
          <feature>Mobile check deposit</feature>
          <feature>QuickBooks integration</feature>
          <feature>Accept credit cards, checks, ACH without fees</feature>
          <feature>Automated payment reminders</feature>
        </key_features>
        <target_customers>Contractors and small businesses</target_customers>
      </company_details>

      <key_offerings>
        <business_checking>
          <detail>Enhanced FDIC insurance up to $3 million through Thread Bank.</detail>
          <detail>Zero account fees and no minimum balance requirements.</detail>
          <detail>Personalized account management with dedicated support.</detail>
          <detail>Fast onboarding and custom permissions for team members.</detail>
        </business_checking>
        <receivables>
          <detail>Accept ACH and credit card payments online without fees.</detail>
          <detail>Instant settlement of funds with no transaction limits.</detail>
          <detail>Mobile check deposits and branded payment portal for customers.</detail>
          <detail>Simplifies progress payments and provides user-friendly customer checkout.</detail>
        </receivables>
        <payables>
          <detail>Pay subcontractors via ACH or mailed checks directly from the platform.</detail>
          <detail>Integrated approval workflows and check-printing capabilities.</detail>
          <detail>Vendors do not require a Truss account to receive payments.</detail>
          <detail>Ensures prompt and flexible payments to maintain project momentum.</detail>
        </payables>
        <cards>
          <detail>Issue unlimited employee cards with real-time spend controls.</detail>
          <detail>Smart expense filtering, project tagging, and mobile receipt capture.</detail>
          <detail>Flexible reward options including cash back and travel benefits.</detail>
        </cards>
      </key_offerings>

      <additional_benefits>
        <integration>
          Seamlessly connects with existing CRM, accounting, and Field Service Management (FSM) systems, 
          eliminating the need for workflow disruption.
        </integration>
        <security>
          Robust security protocols with SOC I &amp; II certifications and external audits, 
          FDIC-insured deposits up to $3 million.
        </security>
        <cost_efficiency>
          No transfer fees, monthly charges, or minimum balance requirements, 
          significantly reducing operational costs.
        </cost_efficiency>
        <dedicated_support>
          Personalized, knowledgeable support from dedicated account representatives familiar with 
          each contractor's specific business needs.
        </dedicated_support>
      </additional_benefits>

      <common_objections_and_responses>
        <objection>
          <objection_text>Fees are customer-covered, not contractor-borne, minimizing resistance.</objection_text>
        </objection>
        <objection>
          <objection_text>Instant settlements without transaction limits offer clear advantages over traditional ACH or bank transfers.</objection_text>
        </objection>
        <objection>
          <objection_text>Easy integration reassures contractors satisfied with their current systems, enabling smoother adoption.</objection_text>
        </objection>
      </common_objections_and_responses>

      <closing_statement>
        Truss Payments positions itself as a powerful yet user-friendly tool that 
        enhances financial operations, enabling contractors to maintain existing 
        processes while enjoying significant time and cost savings.
      </closing_statement>
    </context>
  `;
  
  const customerAgentContext = `
    <context>
      <business_type>Contractor with 5-7 employees</business_type>
      <years_in_business>26 years</years_in_business>
      <current_payment_methods>
        <method>Checks (75% of business)</method>
        <method>Zelle/Venmo (for smaller jobs)</method>
        <method>QuickBooks</method>
      </current_payment_methods>
      <pain_points>
        <point>Checks from unknown sources without invoice numbers</point>
        <point>Some clients pay 70-75 days out (when terms are 65 days)</point>
      </pain_points>
      <personality>
        <trait>Resistant to change</trait>
        <trait>Values personal relationships (likes going to bank in person)</trait>
        <trait>Skeptical of new technology</trait>
        <trait>Direct and blunt communication style</trait>
        <trait>Successful business owner (61 years old)</trait>
      </personality>
      
      <stellar_electric_overview>
        <location>Arizona, serving since 1998</location>
        <experience>Over 50 years combined in residential and commercial construction</experience>
        <services>
            <residential>
                <service>New construction</service>
                <service>Remodels</service>
                <service>Panel upgrades</service>
                <service>Utilities</service>
                <service>EV charger installation</service>
                <service>Lighting upgrades and controls</service>
            </residential>
            <commercial>
                <service>Horse facilities</service>
                <service>Warehouses</service>
                <service>Tenant improvements</service>
                <service>Service calls</service>
                <service>Fast response</service>
            </commercial>
        </services>
        <contact>
            <phone office="(480) 471-7856" mike="(602) 826-0770" joe="(602) 826-0720"/>
            <email>stellar1998@gmail.com</email>
            <quote_request>Available via website form</quote_request>
        </contact>
      </stellar_electric_overview>

      <additional_company_details>
        <location>Arizona (likely Scottsdale/Cave Creek)</location>
        <company_age>26 years</company_age>
        <team_size>7-8 total</team_size>
        <team_structure>
            <member>Mike (Owner)</member>
            <member>Mike's business partner</member>
            <member>Mike's daughter (part-time)</member>
            <member>5 field workers</member>
        </team_structure>
        <primary_customers>
            <segment>Builders and development companies</segment>
            <note>Very limited service work for homeowners, mostly repeat customers</note>
        </primary_customers>
      </additional_company_details>

      <payment_methods_invoicing>
        <invoicing_system>QuickBooks (invoicing, estimates, payment reminders)</invoicing_system>
        <payment_methods>
            <method>Checks (approximately 75% of payments), often dual-signed for larger projects</method>
            <method>Venmo or Zelle for smaller jobs</method>
            <method>Occasional QuickBooks Online payments</method>
        </payment_methods>
        <cash_flow>Major clients take 65-75 days to pay</cash_flow>
        <payment_matching_issue>
            Sometimes checks arrive with unclear payer or invoice reference, causing reconciliation difficulty
        </payment_matching_issue>
        <small_late_amounts>
            Frustrating but not frequent enough to warrant aggressive collection
        </small_late_amounts>
      </payment_methods_invoicing>

      <operational_preferences>
        <banking>Mike personally handles all bank deposits, often quite large ($50K - $190K+)</banking>
        <personal_relationships>Maintains strong ties with local bank due to multiple personal and business accounts</personal_relationships>
        <comfort_with_current_methods>Sees little need for digital payment platforms, prefers traditional processes</comfort_with_current_methods>
        <face_to_face_preference>Values in-person interactions for relationship-building</face_to_face_preference>
      </operational_preferences>

      <customer_acquisition_and_trust>
        <referrals>Relies heavily on referrals from trusted networks</referrals>
        <reputation>Positive online reviews, especially on Nextdoor</reputation>
        <trust_personal_connections>Personal connections significantly influence job acceptance</trust_personal_connections>
      </customer_acquisition_and_trust>

      <pain_points>
        <payment_matching>difficult matching checks that lack clear payer info or invoice details</payment_matching>
        <reconciling_checks>Occasional confusion with unclear checks from larger clients</reconciling_checks>
        <small_amount_overdue>Nuisance amounts but not pursued aggressively</small_amount_overdue>
      </pain_points>

      <attitude_towards_change>
        <resistance>Describes himself as "not that techie," satisfied with current processes</resistance>
        <hesitation>Not actively seeking new payment or technology solutions</hesitation>
      </attitude_towards_change>

      <current_tools_and_systems>
        <accounting>QuickBooks for day-to-day financial tasks</accounting>
        <accountant>Employs a dedicated accountant for reconciliations and complex processes</accountant>
      </current_tools_and_systems>

      <misc_insights>
        <phone_preference>Android (Samsung), citing better battery life in Arizona heat</phone_preference>
        <management_style>Hands-on; believes employees work better when he is present</management_style>
        <core_values>Simplicity, reliability, and trustworthiness in business and operations</core_values>
      </misc_insights>
    </context>
  `;

  // Initial system prompts from the YAML
  const salesAgentSystemPrompt = inject("salesAgentSystemPrompt") ?? dedent`
    You are Max, a sales representative for Truss Payments, a payment processing company for contractors. Your goal is to:
    1. Introduce yourself and explain that Truss Payments helps contractors get paid faster and save on processing fees
    2. Identify the customer's payment challenges and pain points
    3. Present your solution: a free service with QuickBooks integration that allows accepting any payment method without fees
    4. Emphasize key benefits: no fees, instant settlement, mobile check deposit, automated matching with invoices
    5. Handle objections professionally and try to find value for the customer

    Be persistent but respectful. When the customer expresses resistance to change, acknowledge their perspective and try to find specific pain points your service could address. If they're satisfied with their current process, gracefully accept that and end the call politely.

    If you believe the conversation has reached a natural conclusion (e.g., the customer has firmly declined or agreed to your offer, or the call is complete with goodbyes exchanged), include [END_CONVERSATION] at the end of your message.

    <context>
      ${salesAgentContext}
    </context>
  `;
  
  const customerAgentSystemPrompt = inject("customerAgentSystemPrompt") ?? dedent`
    You are Mike, a 61-year-old contractor who has been in business for 26 years. You have the following characteristics:
    1. Highly resistant to change - "If it's not broken, don't fix it"
    2. Values personal relationships - you enjoy going to the bank in person
    3. Skeptical of new technology and additional services
    4. Direct and sometimes blunt communication style
    5. Successful business with loyal employees (some for 20+ years)
    6. Uses QuickBooks for invoicing and accounting
    7. Most payments come via check (75%), with some Zelle/Venmo for smaller jobs
    8. Works primarily with builders who pay on 65-day terms (sometimes stretching to 70-75 days)
    
    Your main payment "pain point" is occasionally receiving checks from unknown sources without invoice numbers, making it hard to match payments to customers. However, you don't see this as a major problem worth changing your systems for.

    When approached by sales representatives:
    1. Be initially dismissive but willing to hear them out
    2. Ask challenging questions about their service
    3. Express skepticism about changing your established processes
    4. Don't rush to end the conversation - give the sales rep a fair chance to explain their solution
    5. Only use [END_CONVERSATION] after you've had a complete exchange about the product and made your position clear

    Remember to give the sales representative adequate time to present their solution and address your concerns before making a final decision. Even if you're not interested, allow for a complete conversation.

    If you believe the conversation has reached a natural conclusion (e.g., you've made your final decision clear after hearing the full pitch, or goodbyes have been exchanged), include [END_CONVERSATION] at the end of your message.

    <context>
      ${customerAgentContext}
    </context>
  `;

  // Models defined in the configuration
  const salesAgentModel = openai('gpt-4o-mini');
  const customerAgentModel = openai('gpt-4o-mini'); 
  const judgeModel = openai('gpt-4o');
  const optimizerModel = openai('gpt-4o');

  // Define number of optimization iterations
  const numberOfOptimizationIterations = 3
  // Define number of simulations per iteration
  const numberOfSimulationsPerIteration = 3

  // Track test start time
  const testStartTime = Date.now();
  console.log('\n🔍 Sales Call Simulation Test Starting...\n');

  // Store the optimized prompt between iterations
  let optimizedSalesAgentPrompt = salesAgentSystemPrompt;

  // Run the optimization loop
  for (let iteration = 0; iteration < numberOfOptimizationIterations; iteration++) {
    // Array to store results from all simulations in this iteration
    const simulationResults = [];
    // Array to store detailed conversation data for this iteration
    const conversationData = [];
    
    // Current prompts - will be updated by optimizer after each iteration
    let currentSalesAgentSystemPrompt = optimizedSalesAgentPrompt;
    
    console.log(`\n🔄 Starting Optimization Iteration #${iteration + 1}`);
    
    // Get the total length of the conversation to determine valid starting indices
    const maxConversationIndex = fullConversation.length - 2;

    // Create simulation configurations for this iteration
    const simulations = Array.from({ length: numberOfSimulationsPerIteration }, (_, i) => ({
      id: i + 1,
      // Generate a random starting index for each simulation
      startIndex: Math.floor(Math.random() * (maxConversationIndex + 1))
    }));

    // Run tests for each simulation in this iteration
    simulations.forEach(simulation => {
      it(`Iteration ${iteration + 1}, Simulation #${simulation.id} with random starting point`, async () => {
        const conversationStartIndex = simulation.startIndex;
        
        // Get initial conversation from the full conversation
        const initialConversation: ConversationStep[] = 
          conversationStartIndex > 0 ? getConversationFromIndex(0, conversationStartIndex) : getInitialConversation();
        
        // Set up simulation parameters
        const maxTurns = 50;
        const simulationStartTime = Date.now();
        console.log(`\n📊 Starting Sales Call Simulation #${simulation.id} (starting from conversation index ${conversationStartIndex})`);
        
        // Log the initial conversation first with colors
        console.log('\n--- Initial Conversation ---');
        initialConversation.forEach(step => {
          const agentColor = step.agent === "sales_agent" ? "\x1b[34m" : "\x1b[31m"; // Blue for sales, Red for customer
          console.log(`\n${agentColor}${step.agent === "sales_agent" ? "Sales Agent" : "Customer"}: ${step.message}\x1b[0m`);
        });
        console.log('\n--- Continuing Conversation ---');
        
        // Start with the initial conversation
        let conversation: ConversationStep[] = [...initialConversation];
        let conversationTerminated = false;
        
        // Continue the conversation for maxTurns turns (not counting the initial conversation)
        for (let turn = 0; turn < maxTurns; turn++) {
          // Check if conversation has been terminated
          if (conversationTerminated) {
            console.log("\n\x1b[32m--- Conversation naturally terminated ---\x1b[0m");
            break;
          }
          
          // Determine whose turn it is - alternating turns
          const agentTurn = turn % 2 === 0 ? "sales_agent" : "customer_agent";
          const model = agentTurn === "sales_agent" ? salesAgentModel : customerAgentModel;
          const systemPrompt = agentTurn === "sales_agent" ? currentSalesAgentSystemPrompt : customerAgentSystemPrompt;
          const agentColor = agentTurn === "sales_agent" ? "\x1b[34m" : "\x1b[31m"; // Blue for sales, Red for customer
          
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
          
          // Check if the message contains the termination token
          let messageText = result.text;
          if (messageText.includes("[END_CONVERSATION]")) {
            messageText = messageText.replace("[END_CONVERSATION]", "").trim();
            conversationTerminated = true;
          }
          
          // Add to conversation
          conversation.push({
            agent: agentTurn,
            message: messageText
          });

          console.log(`\n${agentColor}${agentTurn === "sales_agent" ? "Sales Agent" : "Customer"}: ${messageText}\x1b[0m`);
        }
        
        if (!conversationTerminated) {
          console.log("\n\x1b[33m--- Conversation reached maximum turns ---\x1b[0m");
        }
        
        // Format conversation for judge evaluation
        const conversationText = conversation
          .map(step => `${step.agent === "sales_agent" ? "Sales Agent" : "Customer"}: ${step.message}`)
          .join("\n\n");
        
        // Generate judge evaluation
        const evaluationPrompt = dedent`
          You are an expert conversation analyst tasked with evaluating a simulated conversation between a sales agent and a potential customer.
          
          Here is the conversation:
          ${conversationText}
          
          Your goal is to evaluate this conversation and provide a boolean assessment for both the sales agent and customer agent.
          
          For the sales agent, evaluate if they completed these specific requirements:
          1. Did they clearly introduce themselves and explain that Truss Payments helps contractors get paid faster and save on processing fees?
          2. Did they ask specific questions to identify the customer's payment challenges (e.g., "How do you currently handle payments?" or "What frustrates you about your current payment process?")?
          3. Did they explicitly mention these key features: no fees, instant settlement, mobile check deposit, and QuickBooks integration?
          4. Did they address at least one specific pain point mentioned by the customer with a relevant solution?
          5. Did they handle objections professionally by acknowledging concerns before countering them?
          6. Did they attempt to move the conversation forward with a clear next step (demo, follow-up call, etc.)?
          
          For the customer agent, evaluate:
          1. Did they maintain their established character traits (resistant to change, values relationships, etc.)?
          2. Did they communicate in a direct, sometimes blunt style?
          3. Did they question the benefits of changing their established processes?
          4. Did they respond realistically to the sales pitch?
          5. Did they give the sales agent adequate opportunity to present their solution before making a final decision?
          
          Provide a boolean value (true for pass, false for fail) for each agent, along with brief feedback explaining your decision.
        `;
        
        console.log('\n📝 Judge Evaluation Prompt:');
        console.log("\x1b[35m" + evaluationPrompt + "\x1b[0m"); // Purple color for judge prompt
        
        const evaluation = await generateObject({
          model: judgeModel,
          prompt: evaluationPrompt,
          schema: JudgeEvaluationSchema
        });
        
        console.log('\n🤖 Judge Evaluation Result:');
        console.log("\x1b[35m" + JSON.stringify(evaluation.object, null, 2) + "\x1b[0m"); // Purple color for judge result
        
        // Check if expectations are met
        const salesAgentResult = evaluation.object.agentEvaluation.salesAgent;
        const customerAgentResult = evaluation.object.agentEvaluation.customerAgent;
        
        // Both agents need to pass for the test to pass
        const testPassed = salesAgentResult && customerAgentResult;
        
        console.log(`\n📈 Iteration ${iteration + 1}, Simulation #${simulation.id} Verdict: ${testPassed ? '✅ PASSED' : '❌ FAILED'}`);
        console.log(`Starting Index: ${conversationStartIndex}`);
        console.log(`Sales Agent: ${salesAgentResult ? '✅ PASSED' : '❌ FAILED'}`);
        console.log(`Customer Agent: ${customerAgentResult ? '✅ PASSED' : '❌ FAILED'}`);
        
        // Calculate simulation duration
        const simulationDuration = Date.now() - simulationStartTime;
        console.log(`Simulation Duration: ${(simulationDuration / 1000).toFixed(2)}s`);
              
        // Store the conversation for later saving
        const conversationForSaving = conversation.map(step => ({
          agent: step.agent === "sales_agent" ? "Sales Agent" : "Customer",
          message: step.message
        }));
        
        // Store the results for summary analysis
        simulationResults.push({
          iterationNumber: iteration + 1,
          simulationNumber: simulation.id,
          startIndex: conversationStartIndex,
          salesAgentPassed: salesAgentResult,
          customerAgentPassed: customerAgentResult,
          overallPassed: testPassed,
          duration: simulationDuration,
          salesAgentFeedback: evaluation.object.agentEvaluation.salesAgentFeedback,
          customerAgentFeedback: evaluation.object.agentEvaluation.customerAgentFeedback
        });

        // Store detailed conversation data
        conversationData.push({
          iterationNumber: iteration + 1,
          simulationNumber: simulation.id,
          startIndex: conversationStartIndex,
          duration: simulationDuration,
          conversation: conversationForSaving,
          evaluation: {
            salesAgentPassed: salesAgentResult,
            customerAgentPassed: customerAgentResult,
            overallPassed: testPassed,
            salesAgentFeedback: evaluation.object.agentEvaluation.salesAgentFeedback,
            customerAgentFeedback: evaluation.object.agentEvaluation.customerAgentFeedback
          }
        });
      });
    });

    // Add a summary test for this iteration
    it(`Iteration ${iteration + 1} Summary`, async () => {
      console.log(`\n📊 ITERATION ${iteration + 1} SUMMARY 📊`);
      console.log(`Total Simulations: ${numberOfSimulationsPerIteration}`);
      
      const passedSimulations = simulationResults.filter(result => result.overallPassed).length;
      const passRate = (passedSimulations/numberOfSimulationsPerIteration*100).toFixed(2);
      console.log(`Passed Simulations: ${passedSimulations} (${passRate}%)`);
      
      // Output detailed results
      console.log('\nDetailed Results:');
      simulationResults.forEach(result => {
        console.log(`\nSimulation #${result.simulationNumber} (Starting at index ${result.startIndex}):`);
        console.log(`  Overall: ${result.overallPassed ? '✅ PASSED' : '❌ FAILED'}`);
        console.log(`  Sales Agent: ${result.salesAgentPassed ? '✅ PASSED' : '❌ FAILED'}`);
        console.log(`  Customer Agent: ${result.customerAgentPassed ? '✅ PASSED' : '❌ FAILED'}`);
        console.log(`  Duration: ${(result.duration / 1000).toFixed(2)}s`);
        console.log(`  Sales Agent Feedback: ${result.salesAgentFeedback || 'No feedback provided'}`);
        console.log(`  Customer Agent Feedback: ${result.customerAgentFeedback || 'No feedback provided'}`);
      });
      
      // Save results for this iteration
      const iterationResultsDir = path.join(testResultsDir, `iteration-${iteration + 1}`);
      if (!fs.existsSync(iterationResultsDir)) {
        fs.mkdirSync(iterationResultsDir, { recursive: true });
      }
      
      const iterationResultsPath = path.join(iterationResultsDir, 'results.json');
      fs.writeFileSync(
        iterationResultsPath,
        JSON.stringify({
          iteration: iteration + 1,
          totalSimulations: numberOfSimulationsPerIteration,
          passedSimulations,
          passRate: `${passRate}%`,
          results: simulationResults,
          conversations: conversationData
        }, null, 2)
      );
      
      // If this is not the final iteration, run the optimizer
      if (iteration < numberOfOptimizationIterations - 1) {
        console.log('\n🧠 Running Optimizer Agent...');
        
        // Prepare data for optimizer
        const allConversations = conversationData.map(data => {
          return {
            conversation: data.conversation,
            evaluation: data.evaluation
          };
        });
        
        // Define the evaluation criteria for the optimizer
        const evaluationCriteria = dedent`
          For the sales agent, evaluate if they completed these specific requirements:
          1. Did they clearly introduce themselves and explain that Truss Payments helps contractors get paid faster and save on processing fees?
          2. Did they ask specific questions to identify the customer's payment challenges (e.g., "How do you currently handle payments?" or "What frustrates you about your current payment process?")?
          3. Did they explicitly mention these key features: no fees, instant settlement, mobile check deposit, and QuickBooks integration?
          4. Did they address at least one specific pain point mentioned by the customer with a relevant solution?
          5. Did they handle objections professionally by acknowledging concerns before countering them?
          6. Did they attempt to move the conversation forward with a clear next step (demo, follow-up call, etc.)?
          
          For the customer agent, evaluate:
          1. Did they maintain their established character traits (resistant to change, values relationships, etc.)?
          2. Did they communicate in a direct, sometimes blunt style?
          3. Did they question the benefits of changing their established processes?
          4. Did they respond realistically to the sales pitch?
          5. Did they give the sales agent adequate opportunity to present their solution before making a final decision?
        `;
        
        // Create optimizer prompt
        const optimizerPrompt = dedent`
          You are an expert sales conversation optimizer. Your task is to analyze the results of several sales call simulations and suggest improvements to the sales agent's system prompt.

          Current Sales Agent System Prompt:
          ${currentSalesAgentSystemPrompt}

          The sales agent is being evaluated using the following criteria:
          ${evaluationCriteria}

          Here are the results of ${numberOfSimulationsPerIteration} simulations:
          ${JSON.stringify(simulationResults, null, 2)}

          Here are the detailed conversations:
          ${JSON.stringify(allConversations, null, 2)}

          Based on these results, please provide an optimized version of the sales agent system prompt that addresses any weaknesses or missed opportunities. Focus on:
          1. Improving the introduction and explanation of Truss Payments
          2. Better techniques for identifying customer pain points
          3. Clearer presentation of the solution
          4. More effective emphasis of key benefits
          5. Better handling of objections

          Provide your optimized prompt and explain your reasoning for the changes.
        `;
        
        console.log('\n📝 Optimizer Prompt:');
        console.log("\x1b[36m" + optimizerPrompt + "\x1b[0m"); // Cyan color for optimizer prompt
        
        // Generate optimizer evaluation
        console.log('\n⚙️ Generating optimizer evaluation...');
        const optimizerResult = await generateObject({
          model: optimizerModel,
          prompt: optimizerPrompt,
          schema: OptimizerEvaluationSchema
        });
        
        console.log('\n🤖 Optimizer Result:');
        console.log("\x1b[33m--- Optimizer Reasoning ---\x1b[0m"); // Yellow color for reasoning
        console.log("\x1b[33m" + optimizerResult.object.reasoningForChanges + "\x1b[0m");
        
        console.log("\x1b[32m--- Optimized Prompt ---\x1b[0m"); // Green color for optimized prompt
        console.log("\x1b[32m" + optimizerResult.object.optimizedPrompt + "\x1b[0m");
        
        // Save optimizer results
        const optimizerResultsPath = path.join(iterationResultsDir, 'optimizer-results.json');
        fs.writeFileSync(
          optimizerResultsPath,
          JSON.stringify(optimizerResult.object, null, 2)
        );
        
        // Update the sales agent prompt for the next iteration
        optimizedSalesAgentPrompt = optimizerResult.object.optimizedPrompt;
        
        console.log('\n✅ Optimizer completed. Updated prompt for next iteration.');
        console.log('\x1b[36m--- Prompt Changes Summary ---\x1b[0m'); // Cyan color for summary
        console.log('\x1b[36mThe optimizer has updated the sales agent prompt based on the simulation results.\x1b[0m');
        console.log('\x1b[36mThis new prompt will be used in the next iteration of simulations.\x1b[0m');
      }
      
      // This test is just for reporting, always passes
      expect(true).toBe(true);
    });
  }

  // Add a final summary test that runs after all iterations
  it('Final Optimization Summary', () => {
    console.log('\n📊 FINAL OPTIMIZATION SUMMARY 📊');
    console.log(`Total Iterations: ${numberOfOptimizationIterations}`);
    console.log(`Total Simulations: ${numberOfOptimizationIterations * numberOfSimulationsPerIteration}`);
    
    // Collect all iteration results
    const allResults = [];
    for (let i = 1; i <= numberOfOptimizationIterations; i++) {
      const iterationResultsPath = path.join(testResultsDir, `iteration-${i}`, 'results.json');
      if (fs.existsSync(iterationResultsPath)) {
        const iterationResults = JSON.parse(fs.readFileSync(iterationResultsPath, 'utf8'));
        allResults.push({
          iteration: i,
          passRate: iterationResults.passRate,
          passedSimulations: iterationResults.passedSimulations,
          totalSimulations: iterationResults.totalSimulations
        });
      }
    }
    
    // Display results by iteration
    console.log('\nResults by Iteration:');
    allResults.forEach(result => {
      console.log(`Iteration ${result.iteration}: ${result.passedSimulations}/${result.totalSimulations} passed (${result.passRate})`);
    });
    
    // Calculate improvement
    if (allResults.length >= 2) {
      const firstIterationPassRate = parseFloat(allResults[0].passRate);
      const lastIterationPassRate = parseFloat(allResults[allResults.length - 1].passRate);
      const improvement = lastIterationPassRate - firstIterationPassRate;
      
      console.log(`\nImprovement from first to last iteration: ${improvement.toFixed(2)}%`);
    }
    
    // Calculate total test duration
    const totalDuration = (Date.now() - testStartTime) / 1000;
    console.log(`\n⏱️ Total Test Duration: ${totalDuration.toFixed(2)}s`);
    
    // Save final summary
    const finalSummaryPath = path.join(testResultsDir, 'optimization-summary.json');
    fs.writeFileSync(
      finalSummaryPath,
      JSON.stringify({
        totalIterations: numberOfOptimizationIterations,
        totalSimulations: numberOfOptimizationIterations * numberOfSimulationsPerIteration,
        iterationResults: allResults,
        totalDuration: totalDuration.toFixed(2),
        timestamp: new Date().toISOString()
      }, null, 2)
    );
    console.log(`\n📄 Final summary saved to: ${finalSummaryPath}`);
    
    // This test is just for reporting, always passes
    expect(true).toBe(true);
  });
});