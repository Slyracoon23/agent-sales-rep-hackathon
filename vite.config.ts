import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: 'esnext',
  },
  resolve: {
    // Force Vite to resolve with proper module resolution strategy
    conditions: ['node', 'import', 'module', 'default'],
  },
  ssr: {
    // Fix for rollup/parseAst module resolution issue
    noExternal: ['rollup'],
  },
}); 