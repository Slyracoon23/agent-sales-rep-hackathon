import path from "path";
import dotenv from "dotenv";
import { defineConfig } from "vitest/config";

/**
 * Load environment variables from .env.local.test file.
 * This is necessary because t3 env doesn't work with Vitest.
 * We need to manually load the environment variables for our tests.
 */
dotenv.config({ path: ".env" });

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./apps/agent-bench/src"),
    },
  },
  test: {
    globals: true,
    testTimeout: 30000,
    environment: "node",
    // include: ["src/**/*.{test,bench}.{js,ts}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
    },
    // reporters: ["default", "json"],
  },
});
