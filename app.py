from concurrent.futures import ThreadPoolExecutor
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# ThreadPoolExecutor 생성 (최대 4개의 병렬 작업 허용)
executor = ThreadPoolExecutor(max_workers=4)

def analyze_sentiment(text):
    try:
        process = subprocess.Popen(
            ["python3", "index.py", text],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(timeout=20)  # 타임아웃 20초

        if process.returncode != 0:
            error_message = stderr.decode('utf-8').strip()
            raise Exception(f"Error in subprocess: {error_message}")

        return stdout.decode('utf-8').strip()
    except subprocess.TimeoutExpired:
        process.kill()
        raise Exception("Subprocess timed out")
    except Exception as e:
        raise Exception(f"Error analyzing sentiment: {e}")

@app.route('/sentiment/analysis', methods=['POST'])
def sentiment_analysis():
    try:
        data = request.get_json()
        texts = data.get('texts', [])

        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({"error": "Invalid request: texts must be a non-empty array."}), 400

        # 병렬로 텍스트 처리
        results = []
        futures = {executor.submit(analyze_sentiment, text): text for text in texts}
        for future in futures:
            try:
                result = future.result(timeout=10)  # 10초 제한
                results.append(result)
            except Exception as e:
                print(f"Error processing text: {futures[future]}, Error: {e}")
                results.append("error")

        positive_count = sum(1 for r in results if r == "positive")
        negative_count = sum(1 for r in results if r == "negative")

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
