import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Increase timeout to 5 minutes (300000ms) for all tests
    testTimeout: 300000,
    // Add globals type declaration for __vitest_meta__
    globals: true,
    environment: 'node',
    setupFiles: ['./vitest.setup.ts'],
  },
}); 