const duckdb = require('duckdb');
const fs = require('fs');

// Create database connection
const db = new duckdb.Database('external/snapshot.duckdb');

// Query the database
db.all('SELECT * FROM question LIMIT 10', (err, data) => {
  if (err) {
    console.error('Error querying database:', err);
    process.exit(1);
  }
  
  // Create public directory if it doesn't exist
  if (!fs.existsSync('./public')) {
    fs.mkdirSync('./public');
  }
  
  // Write data to a JSON file
  fs.writeFileSync('./public/questions.json', JSON.stringify(data, null, 2));
  
  console.log('✅ Successfully generated questions.json with', data.length, 'records');
  
  // Close the database connection
  db.close();
});
