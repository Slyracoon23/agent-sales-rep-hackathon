import { DataAPIClient } from "@datastax/astra-db-ts";

export const ASTRA_DB_API_ENDPOINT = "";
export const ASTRA_DB_APPLICATION_TOKEN = "";

// Initialize the client
const client = new DataAPIClient("YOUR_TOKEN");
const db = client.db(
  "https://ebfc55cd-3c05-41c2-8432-b7fb872b46f3-us-east-2.apps.astra.datastax.com"
);

(async () => {
  const colls = await db.listCollections();
  console.log("Connected to AstraDB:", colls);
})();
