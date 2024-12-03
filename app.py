from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Route for sentiment analysis
@app.route('/sentiment/analysis', methods=['POST'])
def sentiment_analysis():
    try:
        # Get JSON body
        data = request.get_json()
        texts = data.get('texts', [])

        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({"error": "Invalid request: texts must be a non-empty array."}), 400

        positive_count = 0
        negative_count = 0

        # Analyze each text
        for text in texts:
            result = analyze_sentiment(text)
            if result == "positive":
                positive_count += 1
            else:
                negative_count += 1

        total = len(texts)
        positive_ratio = round((positive_count / total) * 100, 2)
        negative_ratio = round((negative_count / total) * 100, 2)

        return jsonify({
            "total": total,
            "positiveCount": positive_count,
            "negativeCount": negative_count,
            "positiveRatio": f"{positive_ratio}%",
            "negativeRatio": f"{negative_ratio}%"
        })

    except Exception as e:
        print(f"Error in /sentiment/analysis: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Function to call the Python script and analyze sentiment
def analyze_sentiment(text):
    try:
        # Execute the external Python script
        process = subprocess.Popen(
            ["python3", "ai/index.py", text],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise Exception(stderr.decode('utf-8'))

        # Return the trimmed result from the script
        return stdout.decode('utf-8').strip()

    except Exception as e:
        raise Exception(f"Error analyzing sentiment: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
