// Declare global __vitest_meta__ to fix TypeScript errors
declare global {
  // eslint-disable-next-line no-var
  var __vitest_meta__: {
    simulationResults?: {
      conversation: any;
      evaluation: any;
    };
    supportSimulationResults?: {
      conversation: any;
      evaluation: any;
    };
  };
}

// Initialize the global if it doesn't exist
globalThis.__vitest_meta__ = globalThis.__vitest_meta__ || {};

export {}; 