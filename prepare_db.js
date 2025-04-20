const fs = require("fs");
const path = require("path");
const brotli = require("brotli");

let expand = () => {
  try {
    // Path to the compressed file
    const brotliFilePath = path.join("external", "snapshot.jsonl.br");
    // Path for the extracted file
    const outputFilePath = path.join("external", "snapshot.jsonl");

    console.log("Reading compressed snapshot file...");

    // Read the compressed file
    const compressedData = fs.readFileSync(brotliFilePath);

    // Decompress with Brotli
    const decompressedData = Buffer.from(brotli.decompress(compressedData));

    // Write to output file
    fs.writeFileSync(outputFilePath, decompressedData);

    console.log("Successfully extracted snapshot.jsonl.br to snapshot.jsonl");
  } catch (error) {
    console.error("Error extracting snapshot file:", error);
    throw error;
  }
};

// Function to convert JSONL to Parquet
let convertToParquet = async () => {
  try {
    const duckdb = require("duckdb");
    const db = new duckdb.Database();
    const conn = db.connect();

    // Create a temporary table from the JSONL file
    console.log("Converting snapshot.jsonl to Parquet format...");

    // Create a table to load the JSONL data
    conn.exec(`
      CREATE TABLE snapshot AS
      SELECT * FROM read_json_auto('external/snapshot.jsonl');
    `);

    // Export to Parquet format
    conn.exec(`
      COPY snapshot TO 'external/snapshot.parquet' (FORMAT PARQUET);
    `);

    // Run some example queries to show insights
    console.log("\n📊 Running some example queries on the dataset:");

    // Count total records
    const countResult = conn
      .prepare(`SELECT COUNT(*) as total_records FROM snapshot`)
      .all();
    console.log(`Total records: ${countResult[0].total_records}`);

    // View model performance statistics
    const statsQuery = conn
      .prepare(
        `
      SELECT
        ROUND(AVG(result.time)/1000, 2) as avg_response_time_seconds,
        ROUND(AVG(result.usage.totalTokens), 0) as avg_tokens_used,
        COUNT(*) as total_evaluations
      FROM snapshot
    `,
      )
      .all();

    console.log("\nModel Performance Statistics:");
    console.log(
      `Average response time: ${statsQuery[0].avg_response_time_seconds} seconds`,
    );
    console.log(`Average tokens used: ${statsQuery[0].avg_tokens_used}`);
    console.log(`Total evaluations: ${statsQuery[0].total_evaluations}`);

    // Close the connection
    conn.close();
    console.log(
      "\n✅ Successfully converted to Parquet format and ran example queries",
    );
  } catch (error) {
    console.error("Error processing data:", error);
    throw error;
  }
};

let main = async () => {
  await expand();
  await convertToParquet();
};

main();
