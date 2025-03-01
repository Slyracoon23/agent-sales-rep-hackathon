// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    testTimeout: 300000,
    globals: true,
    environment: 'node',
    setupFiles: ['./vitest.setup.ts'],
    outputFile: {
      json: './test-results/vitest-results.json'
    },
    reporters: ['default', 'json']
  }
});