from concurrent.futures import ThreadPoolExecutor
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# ThreadPoolExecutor 생성 (최대 4개의 병렬 작업 허용)
executor = ThreadPoolExecutor(max_workers=4)

# 최대 텍스트 수 및 텍스트 길이 제한
MAX_TEXT_COUNT = 100
MAX_TEXT_LENGTH = 500  # 텍스트 길이 제한 (500자)

def analyze_sentiment(text):
    """
    Subprocess를 통해 텍스트의 감정을 분석하는 함수.
    """
    try:
        process = subprocess.Popen(
            ["python3", "index.py", text],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(timeout=30)  # 타임아웃 증가 (30초)

        if process.returncode != 0:
            error_message = stderr.decode('utf-8').strip()
            raise Exception(f"Error in subprocess: {error_message}")

        return stdout.decode('utf-8').strip()
    except subprocess.TimeoutExpired:
        process.kill()
        raise Exception(f"Subprocess timed out for input: {text}")
    except Exception as e:
        raise Exception(f"Error analyzing sentiment for input: {text}, Error: {e}")

@app.route('/sentiment/analysis', methods=['POST'])
def sentiment_analysis():
    """
    POST 요청을 받아 텍스트 감정 분석을 수행하는 API 엔드포인트.
    """
    try:
        data = request.get_json()
        texts = data.get('texts', [])

        # 요청 검증: 텍스트 배열이 올바른지 확인
        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({"error": "Invalid request: texts must be a non-empty array."}), 400

        # 최대 텍스트 수 제한
        if len(texts) > MAX_TEXT_COUNT:
            return jsonify({"error": f"Too many texts. The maximum allowed is {MAX_TEXT_COUNT}."}), 400

        # 텍스트 길이 제한 검증
        if any(len(text) > MAX_TEXT_LENGTH for text in texts):
            return jsonify({"error": f"One or more texts exceed the maximum allowed length of {MAX_TEXT_LENGTH} characters."}), 400

        # 병렬로 텍스트 처리
        results = []
        futures = {executor.submit(analyze_sentiment, text): text for text in texts}
        for future in futures:
            text = futures[future]
            try:
                result = future.result(timeout=30)  # 타임아웃 증가 (30초)
                results.append(result)
            except Exception as e:
                print(f"Error processing text: {text}, Error: {e}")
                results.append("error")

        positive_count = sum(1 for r in results if r == "positive")
        negative_count = sum(1 for r in results if r == "negative")
        error_count = sum(1 for r in results if r == "error")

        total = len(texts)
        positive_ratio = round((positive_count / total) * 100, 2)
        negative_ratio = round((negative_count / total) * 100, 2)

        return jsonify({
            "total": total,
            "positiveCount": positive_count,
            "negativeCount": negative_count,
            "errorCount": error_count,
            "positiveRatio": f"{positive_ratio}%",
            "negativeRatio": f"{negative_ratio}%"
        })

    except Exception as e:
        print(f"Error in /sentiment/analysis: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
