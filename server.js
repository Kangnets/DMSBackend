const express = require("express");
const bodyParser = require("body-parser");
const { spawn } = require("child_process");

const app = express();
const port = 3000;

// Middleware
app.use(bodyParser.json());

// Route for sentiment analysis
app.post("/sentiment/analysis", async (req, res) => {
  try {
    const { texts } = req.body; // Expecting { texts: ["text1", "text2", ...] }

    if (!Array.isArray(texts) || texts.length === 0) {
      return res
        .status(400)
        .json({ error: "Invalid request: texts must be a non-empty array." });
    }

    let positiveCount = 0;
    let negativeCount = 0;

    // Process each text
    for (const text of texts) {
      const result = await analyzeSentiment(text);

      if (result === "positive") {
        positiveCount++;
      } else {
        negativeCount++;
      }
    }

    const total = texts.length;
    const positiveRatio = ((positiveCount / total) * 100).toFixed(2);
    const negativeRatio = ((negativeCount / total) * 100).toFixed(2);

    return res.json({
      total,
      positiveCount,
      negativeCount,
      positiveRatio: `${positiveRatio}%`,
      negativeRatio: `${negativeRatio}%`,
    });
  } catch (error) {
    console.error("Error in /sentiment/analysis:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Function to call the Python script and analyze sentiment
const analyzeSentiment = (text) => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python3", ["index.py", text]);

    let output = "";
    let error = "";

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      error += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0 || error) {
        return reject(error || `Process exited with code ${code}`);
      }

      // Process Python script output
      const sentiment = output.trim(); // Expected output: "positive" or "negative"
      resolve(sentiment);
    });
  });
};

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
