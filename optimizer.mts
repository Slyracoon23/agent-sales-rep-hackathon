import path from 'path';
import { createVitest } from 'vitest/node';

async function runTest() {
  const testPath = path.resolve(process.cwd(), 'sales-rep.test.ts');
  
  const vitest = await createVitest("test", {
    watch: false,
    include: [testPath],
  });
  
  await vitest.start();
  const testResults = vitest.state.getFiles();

  await vitest.close();

  console.log(testResults);
}

runTest().catch(error => {
  process.exit(1);
}); 