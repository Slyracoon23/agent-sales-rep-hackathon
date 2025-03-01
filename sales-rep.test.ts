import 'dotenv/config';
import { z } from 'zod';
import { describe, it, expect, inject } from 'vitest';
import dedent from 'dedent';
import { openai } from '@ai-sdk/openai';
import { generateText, generateObject } from 'ai';
// Import the conversation data
import { fullConversation, getInitialConversation, getConversationFromIndex, conversationStartPoint, ConversationStep } from './test/data/sales-conversation';

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

    When approached by sales representatives, be initially dismissive but willing to hear them out. Repeatedly question what benefit their service would provide that would justify changing your established processes.

    If you believe the conversation has reached a natural conclusion (e.g., you've made your final decision clear or goodbyes have been exchanged), include [END_CONVERSATION] at the end of your message.

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
    // Determine if we should use our imported conversation or start fresh
    // You can change this conversationStartIndex to start from a different point in the conversation
    const conversationStartIndex = 10; // Set to 10 as requested
    
    // Get initial conversation from the full conversation
    // Always include messages from the start up to the specified index
    const initialConversation: ConversationStep[] = 
      conversationStartIndex > 0 ? getConversationFromIndex(0, conversationStartIndex) : getInitialConversation();
    
    // Set up simulation parameters
    const maxTurns = 50;
    console.log(`\n📊 Starting Sales Call Simulation (starting from conversation index ${conversationStartIndex})`);
    
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
    
    // Continue the conversation for maxTurns - initialConversation.length turns
    for (let turn = 0; turn < maxTurns - initialConversation.length; turn++) {
      // Check if conversation has been terminated
      if (conversationTerminated) {
        console.log("\n\x1b[32m--- Conversation naturally terminated ---\x1b[0m");
        break;
      }
      
      // Determine whose turn it is - alternating turns
      const agentTurn = turn % 2 === 0 ? "sales_agent" : "customer_agent";
      const model = agentTurn === "sales_agent" ? salesAgentModel : customerAgentModel;
      const systemPrompt = agentTurn === "sales_agent" ? salesAgentSystemPrompt : customerAgentSystemPrompt;
      const agentColor = agentTurn === "sales_agent" ? "\x1b[34m" : "\x1b[31m"; // Blue for sales, Red for customer
      
      // Remove the delay between messages
      
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
    
    console.log(`\n📈 Final Verdict: ${testPassed ? '✅ PASSED' : '❌ FAILED'}`);
    console.log(`Sales Agent: ${salesAgentResult ? '✅ PASSED' : '❌ FAILED'}`);
    console.log(`Customer Agent: ${customerAgentResult ? '✅ PASSED' : '❌ FAILED'}`);
    if (evaluation.object.agentEvaluation.salesAgentFeedback) {
      console.log(`\nSales Agent Feedback: \x1b[35m${evaluation.object.agentEvaluation.salesAgentFeedback}\x1b[0m`); // Purple color for feedback
    }
    if (evaluation.object.agentEvaluation.customerAgentFeedback) {
      console.log(`\nCustomer Agent Feedback: \x1b[35m${evaluation.object.agentEvaluation.customerAgentFeedback}\x1b[0m`); // Purple color for feedback
    }

      // Set expectations based on YAML configuration
      expect(salesAgentResult).toBe(true);
      expect(customerAgentResult).toBe(true);
  });
});