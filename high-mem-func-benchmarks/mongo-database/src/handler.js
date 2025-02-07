const { MongoClient } = require("mongodb");

// Replace with your MongoDB Atlas connection string
const uri = "paste your creds here"

async function getDatabaseStats() {
    const client = new MongoClient(uri);

    try {
        // Connect to MongoDB
        await client.connect();

        // Specify the database name
        const databaseName = "<dbname>"; // Replace with your database name
        const database = client.db(databaseName);

        // Get all collections
        const collections = await database.listCollections().toArray();

        const stats = [];
        for (const collection of collections) {
            const collectionName = collection.name;

            // Get the document count for each collection
            const documentCount = await database.collection(collectionName).countDocuments();

            stats.push({
                collection: collectionName,
                documentCount,
            });
        }

        // Return stats
        return {
            statusCode: 200,
            body: {
                databaseName,
                collections: stats,
            },
        };
    } catch (error) {
        console.error("Error connecting to MongoDB:", error);
        return {
            statusCode: 500,
            body: `Error: ${error.message}`,
        };
    } finally {
        // Close the connection
        await client.close();
    }
}

module.exports = async function (event, context = null) {
    return await getDatabaseStats();
};
