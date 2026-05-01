import os
import requests
import io
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Railway Variables থেকে টোকেন নেওয়া
HF_TOKEN = os.environ.get("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/openai/shap-e"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

@app.route('/generate-3d', methods=['POST'])
def generate_3d():
    if not HF_TOKEN:
        return jsonify({"error": "Railway Variables-এ HF_TOKEN পাওয়া যায়নি!"}), 500

    try:
        data = request.get_json()
        prompt = data.get("prompt", "A futuristic 3D icon")
        
        print(f"Requesting: {prompt}") # Railway লগে দেখা যাবে

        # Hugging Face এপিআই কল
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=180)
        
        # মডেল লোড হতে থাকলে
        if response.status_code == 503:
            return jsonify({"error": "AI Model is loading. Please wait 1 minute and try again."}), 503
            
        if response.status_code == 200:
            return send_file(
                io.BytesIO(response.content),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name='brutal_x_3d_model.glb'
            )
        else:
            print(f"HF Error: {response.status_code} - {response.text}")
            return jsonify({"error": f"HF API Error: {response.status_code}"}), response.status_code

    except Exception as e:
        print(f"Crash Log: {str(e)}")
        return jsonify({"error": "Server error, check Railway logs."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
