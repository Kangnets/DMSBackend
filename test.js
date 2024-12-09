require("dotenv").config();
const readline = require("readline");
const fetch = require("node-fetch");

const OPENAI_API_KEY =
  "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";

// Function to analyze sentiment using OpenAI API
const analyzeSentiment = async (text) => {
  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system",
            content:
              "You are a sentiment analysis assistant. Analyze the sentiment of the provided text.",
          },
          {
            role: "user",
            content: `문장을 감정 분석하세요: "${text}"\n\n결과는 '긍정', '부정', 또는 '중립'으로만 응답하세요.`,
          },
        ],
        max_tokens: 10,
      }),
    });

    const data = await response.json();

    // Debug: Log the API response
    console.log("API Response:", JSON.stringify(data, null, 2));

    const sentiment =
      data.choices && data.choices[0]?.message?.content?.trim()
        ? data.choices[0].message.content.trim()
        : "분석 실패";
    return sentiment;
  } catch (error) {
    console.error("Error analyzing sentiment:", error);
    return "분석 실패";
  }
};

// Create a Readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

console.log("고급 한국어 감정 분석 콘솔");
console.log("문장을 입력하고 Enter를 누르세요.");
console.log("종료하려면 '종료'를 입력하세요.\n");

const handleInput = async (input) => {
  if (input.trim() === "종료") {
    console.log("감정 분석 콘솔을 종료합니다. 안녕히 가세요!");
    rl.close();
    return;
  }

  const sentiment = await analyzeSentiment(input);
  console.log(`감정 분석 결과: ${sentiment}\n`);

  rl.prompt();
};

// Start the input loop
rl.prompt();
rl.on("line", handleInput);
