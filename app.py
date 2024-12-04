from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import subprocess
from keras.models import Sequential
from keras.layers import Dense

# Flask 앱 초기화
app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=2)

# 모델 초기화 및 가중치 로드
def load_model():
    print("Loading model...")
    model = Sequential([
        Dense(64, activation='relu', input_shape=(100,)),  # 예시 input_shape
        Dense(1, activation='sigmoid')
    ])
    model.load_weights('./ai/DATA_OUT/cnn_classifier_kr/weights.weights.h5')
    print("Model loaded successfully.")
    return model

# 글로벌 모델 객체
model = load_model()

def analyze_sentiment(text):
    try:
        # 입력 검증
        if not text or not isinstance(text, str) or len(text.strip()) == 0:
            raise ValueError("Invalid text input.")

        print(f"Analyzing text: {text}")
        process = subprocess.Popen(
            ["python3", "index.py", text],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(timeout=120)  # 타임아웃 증가

        if process.returncode != 0:
            error_message = stderr.decode('utf-8').strip()
            raise Exception(f"Subprocess error: {error_message}")

        return stdout.decode('utf-8').strip()

    except subprocess.TimeoutExpired:
        process.kill()
        raise Exception(f"Subprocess timed out for input: {text}")
    except Exception as e:
        raise Exception(f"Error analyzing sentiment for text: {text}, Error: {e}")

@app.route('/sentiment/analysis', methods=['POST'])
def sentiment_analysis():
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({"error": "Invalid request: texts must be a non-empty array."}), 400

        results = []
        futures = {executor.submit(analyze_sentiment, text): text for text in texts}
        for future in futures:
            try:
                results.append(future.result(timeout=120))
            except Exception as e:
                results.append("error")

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
