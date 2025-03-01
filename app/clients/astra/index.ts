import { DataAPIClient } from "@datastax/astra-db-ts";

export const ASTRA_DB_API_ENDPOINT = process.env.ASTRA_DB_API_ENDPOINT;
export const ASTRA_DB_APPLICATION_TOKEN =
  process.env.ASTRA_DB_APPLICATION_TOKEN;

// Initialize the client
const client = new DataAPIClient(ASTRA_DB_APPLICATION_TOKEN!);
const db = client.db(ASTRA_DB_API_ENDPOINT!);

(async () => {
  const colls = await db.listCollections();
  console.log("Connected to AstraDB:", colls);
})();
