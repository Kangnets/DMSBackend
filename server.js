const express = require("express");
const { HfInference } = require("@huggingface/inference");

// Hugging Face Inference API instance
const hf = new HfInference("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"); // Replace with your Hugging Face API Key

// Load the JSON reference file
const sentimentReference = {
  진보: {
    윤석열: "Negative",
    이명박: "Negative",
    박근혜: "Negative",
    민주당: "Positive",
    정의당: "Positive",
    김대중: "Positive",
    이재명: "Positive",
    조국: "Positive",
    문재인: "Positive",
    강경화: "Positive",
    유시민: "Positive",
    정동영: "Positive",
    노무현: "Positive",
    한명숙: "Positive",
    박원순: "Positive",
    박지현: "Positive",
    송영길: "Positive",
    이해찬: "Positive",
    이상민: "Positive",
    조희연: "Positive",
    홍익표: "Positive",
    김영진: "Positive",
    최문순: "Positive",
    김경수: "Positive",
    홍준표: "Negative",
    김기현: "Negative",
    이준석: "Negative",
    김종인: "Negative",
    박지원: "Negative",
    강효상: "Negative",
    오세훈: "Negative",
    한동훈: "Negative",
    이명박근혜: "Negative",
    한겨레: "Positive",
    KBS: "Positive",
    MBC: "Positive",
    JTBC: "Positive",
    진보적: "Positive",
    정의: "Positive",
    사회정의: "Positive",
    노동자: "Positive",
    평등: "Positive",
    환경보호: "Positive",
    성평등: "Positive",
    여성권리: "Positive",
    인권: "Positive",
    동성애: "Positive",
    사회주의: "Positive",
    연대: "Positive",
    자유민주주의: "Positive",
    국가보안법폐지: "Positive",
    통합진보당: "Positive",
    민주노총: "Positive",
    녹색당: "Positive",
    촛불혁명: "Positive",
    광화문: "Positive",
  },
  보수: {
    윤석열: "Positive",
    이명박: "Positive",
    박근혜: "Positive",
    민주당: "Negative",
    정의당: "Negative",
    김대중: "Negative",
    이재명: "Negative",
    조국: "Negative",
    문재인: "Negative",
    강경화: "Negative",
    유시민: "Negative",
    정동영: "Negative",
    노무현: "Negative",
    한명숙: "Negative",
    박원순: "Negative",
    박지현: "Negative",
    송영길: "Negative",
    이해찬: "Negative",
    이상민: "Negative",
    조희연: "Negative",
    홍익표: "Negative",
    김영진: "Negative",
    최문순: "Negative",
    김경수: "Negative",
    홍준표: "Positive",
    김기현: "Positive",
    이준석: "Positive",
    김종인: "Positive",
    박지원: "Positive",
    강효상: "Positive",
    오세훈: "Positive",
    한동훈: "Positive",
    이명박근혜: "Positive",
    조선일보: "Positive",
    동아일보: "Positive",
    서울신문: "Positive",
    한겨레: "Negative",
    KBS: "Negative",
    MBC: "Negative",
    JTBC: "Negative",
    보수적: "Positive",
    자유: "Positive",
    보수주의: "Positive",
    가족: "Positive",
    종교: "Positive",
    자유시장경제: "Positive",
    자유주의: "Positive",
    자유민주주의: "Positive",
    국가안보: "Positive",
    독립: "Positive",
    국방: "Positive",
    전통가족: "Positive",
    차별금지법: "Negative",
    국가보안법: "Positive",
    자유한국당: "Positive",
    새누리당: "Positive",
    애국자: "Positive",
    대한민국: "Positive",
    서민: "Positive",
    중산층: "Positive",
    기독교: "Positive",
    종교의자유: "Positive",
  },
};

const app = express();
const PORT = 3000;

// Middleware to parse JSON requests
app.use(express.json());

// Helper function for sentiment analysis
const analyzeSentiment = async (text) => {
  try {
    const result = await hf.textClassification({
      model: "nlptown/bert-base-multilingual-uncased-sentiment", // Updated to a Korean-compatible model
      inputs: text,
    });
    return result[0]?.label || "Neutral";
  } catch (error) {
    console.error("Error analyzing sentiment:", error);
    return "Neutral";
  }
};

// Helper function to map star ratings to sentiment
const mapStarToSentiment = (starRating) => {
  const rating = parseInt(starRating[0]); // Extract the first character as an integer
  if (rating >= 4) return "Positive";
  if (rating <= 2) return "Negative";
  return "Neutral";
};

// Endpoint to handle sentiment analysis
app.post("/sentiment/analysis", async (req, res) => {
  const videoData = req.body.data;

  if (!Array.isArray(videoData) || videoData.length === 0) {
    return res.status(400).json({
      error: "Invalid request. 'data' should be a non-empty array.",
    });
  }

  const sentimentResults = {};
  const categoryCount = { 진보: 0, 보수: 0 };

  // Process each video and its comments
  for (const video of videoData) {
    const { video: videoTitle, comments } = video;

    if (!videoTitle || !Array.isArray(comments)) {
      console.warn(`Invalid video data format for: ${videoTitle}`);
      continue;
    }

    for (const comment of comments) {
      // Perform sentiment analysis
      const sentimentResult = await analyzeSentiment(comment);
      const sentiment = mapStarToSentiment(sentimentResult);

      // Extract keywords
      const keywords = Object.keys(sentimentReference["진보"]).concat(
        Object.keys(sentimentReference["보수"])
      );

      const matchedKeywords = keywords.filter((keyword) =>
        comment.includes(keyword)
      );

      matchedKeywords.forEach((keyword) => {
        const isProgressive = sentimentReference["진보"][keyword] === sentiment;
        const sentimentType = isProgressive ? "진보" : "보수";

        sentimentResults[keyword] = sentiment;
        categoryCount[sentimentType] += 1;
      });

      // Debugging logs
      console.log("Comment:", comment);
      console.log("Sentiment Result:", sentimentResult);
      console.log("Mapped Sentiment:", sentiment);
      console.log("Matched Keywords:", matchedKeywords);
      console.log("Category Count:", categoryCount);
    }
  }

  // Calculate percentages
  const totalKeywords = categoryCount["진보"] + categoryCount["보수"];
  const percentages = totalKeywords
    ? {
        진보: ((categoryCount["진보"] / totalKeywords) * 100).toFixed(2),
        보수: ((categoryCount["보수"] / totalKeywords) * 100).toFixed(2),
      }
    : { 진보: "0.00", 보수: "0.00" };

  // Respond with results
  res.json({ percentages, sentimentResults });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
