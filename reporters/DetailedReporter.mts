import { Reporter } from 'vitest/reporters';
import type { 
  RunnerTestFile as File,
  RunnerTask as Task,
  RunnerTaskResult as TaskResult,
  TaskMeta
} from 'vitest';
import fs from 'fs';
import path from 'path';

// Add custom interface to extend TaskMeta
interface ExtendedTaskMeta extends TaskMeta {
  simulationId?: string;
}

/**
 * A custom Vitest reporter that provides detailed output for sales call simulations
 * including conversation logs, agent evaluations, and performance metrics
 */
export default class DetailedReporter implements Reporter {
  private startTime: number = 0;
  private testResults: Record<string, any> = {};
  private consoleLogs: Record<string, string[]> = {};
  private salesSimulations: Record<string, {
    conversation: any[];
    evaluation: any;
    startIndex: number;
    duration: number;
  }> = {};
  private outputDir: string = path.join(process.cwd(), 'test-results');
  
  onInit() {
    console.log('\n🔍 Sales Call Simulation Reporter Starting...\n');
    this.startTime = Date.now();
    
    // Create output directory if it doesn't exist
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  onFinished(files: File[] = [], errors: unknown[] = []) {
    // Don't call super.onFinished as this class doesn't extend another class
    this.saveSalesSimulationResults();
    
    // Print summary of test results
    console.log('\n📊 Sales Call Simulation Summary:');
    console.log(`Total simulations: ${Object.keys(this.salesSimulations).length}`);
    console.log(`Total duration: ${((Date.now() - this.startTime) / 1000).toFixed(2)}s`);
  }
  
  // Called when a test file starts running
  onTestFileStart(file: File) {
    console.log(`\n🔄 Running test file: ${path.relative(process.cwd(), file.filepath)}`);
  }
  
  // Called when a test file finishes running
  onTestFileSuccess(file: File) {
    console.log(`✅ Test file completed: ${path.relative(process.cwd(), file.filepath)}`);
  }
  
  // Called when a test starts running
  onTestStart(task: Task) {
    console.log(`  ▶️ ${task.name}`);
  }
  
  // Called when a test finishes running
  onTestEnd(task: Task) {
    const status = task.result?.state === 'pass' ? '✅' : task.result?.state === 'fail' ? '❌' : '⚠️';
    console.log(`  ${status} ${task.name} (${task.result?.duration || 0}ms)`);
    
    // Only process simulation tests
    if (task.name.includes('Sales Call Simulation') && (task.result?.state === 'pass' || task.result?.state === 'fail')) {
      console.log(`  🔍 Processing results for ${task.name}...`);
      this.processTaskOutput(task);
    }
  }
  
  // Process task output to extract simulation data
  private processTaskOutput(task: Task): void {
    // Extract simulation ID from task name or metadata
    const simulationId = this.extractSimulationId(task);
    if (!simulationId) return;
    
    // Initialize simulation record if it doesn't exist
    if (!this.salesSimulations[simulationId]) {
      this.salesSimulations[simulationId] = {
        conversation: [],
        evaluation: null,
        startIndex: 0,
        duration: 0
      };
    }
    
    // Extract conversation and evaluation data from console logs
    this.extractSimulationData(task, simulationId);
  }
  
  // Extract simulation data from task output
  private extractSimulationData(task: Task, simulationId: string): void {
    // Get console logs for this task
    const logs = (task.result as any)?.output || [];
    
    // Process each log line
    for (const log of logs) {
      // Extract conversation data
      const conversationMatch = log.match(/CONVERSATION_DATA:(.*)/);
      if (conversationMatch) {
        try {
          const conversationData = JSON.parse(conversationMatch[1]);
          this.salesSimulations[simulationId].conversation = conversationData;
          console.log(`✅ Captured conversation data for simulation ${simulationId}`);
        } catch (e) {
          console.error(`Error parsing conversation data for simulation ${simulationId}:`, e);
        }
      }
      
      // Extract evaluation data
      const evaluationMatch = log.match(/EVALUATION_DATA:(.*)/);
      if (evaluationMatch) {
        try {
          const evaluationData = JSON.parse(evaluationMatch[1]);
          this.salesSimulations[simulationId].evaluation = evaluationData;
          console.log(`✅ Captured evaluation data for simulation ${simulationId}`);
        } catch (e) {
          console.error(`Error parsing evaluation data for simulation ${simulationId}:`, e);
        }
      }
      
      // Extract duration information
      const durationMatch = log.match(/SIMULATION_DURATION:(\d+\.?\d*)/);
      if (durationMatch) {
        this.salesSimulations[simulationId].duration = parseFloat(durationMatch[1]);
      }
      
      // Extract start index information
      const startIndexMatch = log.match(/SIMULATION_START_INDEX:(\d+)/);
      if (startIndexMatch) {
        this.salesSimulations[simulationId].startIndex = parseInt(startIndexMatch[1], 10);
      }
    }
  }
  
  // Extract simulation ID from task
  private extractSimulationId(task: Task): string | null {
    // Try to extract from task name
    const nameMatch = task.name.match(/Sales Call Simulation #(\d+)/i);
    if (nameMatch) return nameMatch[1];
    
    // Try to extract from console logs
    const logs = (task.result as any)?.output || [];
    for (const log of logs) {
      const idMatch = log.match(/SIMULATION_ID:(\w+)/);
      if (idMatch) return idMatch[1];
    }
    
    // Try to extract from task metadata
    const meta = task.meta as ExtendedTaskMeta;
    if (meta?.simulationId) return meta.simulationId;
    
    return null;
  }
  
  // Save detailed simulation results to file
  private saveSalesSimulationResults() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filePath = path.join(this.outputDir, `sales-simulation-results-${timestamp}.json`);
    
    try {
      // Count passed simulations
      const passedSimulations = Object.values(this.salesSimulations)
        .filter(sim => sim.evaluation?.agentEvaluation?.salesAgent && sim.evaluation?.agentEvaluation?.customerAgent)
        .length;
      
      // Calculate pass rate
      const totalSimulations = Object.keys(this.salesSimulations).length;
      const passRate = totalSimulations > 0 ? (passedSimulations / totalSimulations) * 100 : 0;
      
      // Prepare detailed results
      const detailedResults = {
        summary: {
          totalSimulations,
          passedSimulations,
          passRate: `${passRate.toFixed(2)}%`,
          timestamp: new Date().toISOString(),
          duration: (Date.now() - this.startTime) / 1000,
          testRunDate: new Date().toLocaleDateString(),
          testRunTime: new Date().toLocaleTimeString()
        },
        simulations: {}
      };
      
      // Process each simulation to create a cleaner output
      Object.entries(this.salesSimulations).forEach(([id, simulation]) => {
        detailedResults.simulations[id] = {
          id,
          startIndex: simulation.startIndex,
          duration: simulation.duration,
          passed: simulation.evaluation?.agentEvaluation?.salesAgent && 
                 simulation.evaluation?.agentEvaluation?.customerAgent,
          salesAgentPassed: simulation.evaluation?.agentEvaluation?.salesAgent || false,
          customerAgentPassed: simulation.evaluation?.agentEvaluation?.customerAgent || false,
          salesAgentFeedback: simulation.evaluation?.agentEvaluation?.salesAgentFeedback || '',
          customerAgentFeedback: simulation.evaluation?.agentEvaluation?.customerAgentFeedback || '',
          conversation: simulation.conversation.map(step => ({
            role: step.agent === 'sales_agent' ? 'Sales Agent' : 'Customer',
            message: step.message
          }))
        };
      });
      
      // Write to file
      fs.writeFileSync(filePath, JSON.stringify(detailedResults, null, 2));
      
      console.log(`\n📄 Detailed simulation results saved to: ${filePath}`);
      console.log(`\n📊 Summary: ${passedSimulations}/${totalSimulations} simulations passed (${passRate.toFixed(2)}%)`);
      
      // Also create a summary file that's always at the same location
      const summaryFilePath = path.join(this.outputDir, 'latest-simulation-summary.json');
      fs.writeFileSync(summaryFilePath, JSON.stringify(detailedResults.summary, null, 2));
      console.log(`📄 Summary saved to: ${summaryFilePath}`);
    } catch (e) {
      console.error('Error saving simulation results:', e);
    }
  }

  // Process console output from Vitest
  onConsoleLog(log: string, taskId?: string) {
    if (!taskId) return;
    
    // Store console logs by task ID
    if (!this.consoleLogs[taskId]) {
      this.consoleLogs[taskId] = [];
    }
    this.consoleLogs[taskId].push(log);
    
    // Check if this is a simulation data log
    if (log.includes('CONVERSATION_DATA:') || 
        log.includes('EVALUATION_DATA:') || 
        log.includes('SIMULATION_ID:')) {
      console.log(`  📊 Captured simulation data for task ${taskId}`);
    }
  }
}