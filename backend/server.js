const app = require('./app');

// Hardcoded port with fallback for robustness
const PORT = process.env.PORT || 3000;

app.listen(PORT, (err) => {
  if (err) {
    console.error(`Error starting server on port ${PORT}:`, err);
    process.exit(1); // Exit process if there's an error in starting the server
  } else {
    console.log(`Server running successfully on port ${PORT}`);
  }
});
