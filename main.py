import os
import requests
import io
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# রেলওয়ে ভেরিয়েবলে HF_TOKEN সেট করুন
HF_TOKEN = os.environ.get("HF_TOKEN")
# OpenAI এর Shap-E মডেল (টেক্সট থেকে ৩ডি)
API_URL = "https://api-inference.huggingface.co/models/openai/shap-e"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

@app.route('/generate-3d', methods=['POST'])
def generate_3d():
    data = request.json
    prompt = data.get("prompt", "A simple 3D chair")

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=120)
        
        if response.status_code == 200:
            # হাগিং ফেস সাধারণত জিপ ফাইল বা ডট-জিএলবি ফাইল দেয়
            return send_file(
                io.BytesIO(response.content),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name='model_3d.glb'
            )
        else:
            return jsonify({"error": "HF API error", "details": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
