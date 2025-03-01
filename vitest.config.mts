// vitest.config.ts
import { defineConfig } from 'vitest/config';
import DetailedReporter from './reporters/DetailedReporter.mts';

export default defineConfig({
  test: {
    testTimeout: 300000,
    globals: true,
    environment: 'node',
    setupFiles: ['./vitest.setup.ts'],
    outputFile: {
      json: './test-results/vitest-results.json'
    },
    reporters: ['default', 'json', new DetailedReporter()]
  }
});