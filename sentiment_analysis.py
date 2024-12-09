from transformers import pipeline
import sys

# Load a pre-trained sentiment analysis model
sentiment_pipeline = pipeline("sentiment-analysis", model="jason9693/KoBERT-sentiment")

def analyze_sentiment(text):
    result = sentiment_pipeline(text)
    return result[0]['label']

if __name__ == "__main__":
    input_text = sys.argv[1]
    sentiment = analyze_sentiment(input_text)
    print(sentiment)
