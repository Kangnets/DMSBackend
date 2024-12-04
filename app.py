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

        if not texts or not isinstance(texts, list):
            return jsonify({"error": "Invalid request: texts must be a non-empty array."}), 400

        results = []
        for text in texts:
            try:
                result = analyze_sentiment(text)
                results.append(result)
            except Exception as e:
                print(f"Error processing text: {text}, Error: {e}")
                results.append("error")

        # Calculate statistics
        positive_count = results.count("positive")
        negative_count = results.count("negative")
        total = len(results)

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
            ["python3", "./index.py", text],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            raise Exception("Subprocess timed out")

        if process.returncode != 0:
            error_message = stderr.decode('utf-8').strip()
            raise Exception(f"External script error: {error_message}")

        # Return the trimmed result from the script
        return stdout.decode('utf-8').strip()

    except Exception as e:
        print(f"Error analyzing sentiment for text '{text}': {e}")
        raise


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
