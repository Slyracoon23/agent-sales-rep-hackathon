import { connectToDatabase, Book } from "../app/clients/astra/connect";

(async function () {
  const database = connectToDatabase();

  const collection = database.collection<Book>("quickstart_collection2");

  const singleVectorMatch = await collection.findOne(
    {},
    { sort: { $vectorize: "Electrical" } }
  );
  console.log("singleVectorMatch", JSON.stringify(singleVectorMatch));
})();
