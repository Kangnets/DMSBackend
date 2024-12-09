const readline = require("readline");
const { HfInference } = require("@huggingface/inference");

// Create an instance of the Hugging Face Inference API
const hf = new HfInference("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"); // Hugging Face API Key (필요 없는 경우 제거 가능)

// Function to analyze sentiment using Hugging Face
const analyzeSentiment = async (text) => {
  try {
    const result = await hf.textClassification({
      model: "distilbert-base-uncased-finetuned-sst-2-english", // Hugging Face의 감정 분석 모델
      inputs: text,
    });
    return result[0]?.label || "분석 실패";
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
