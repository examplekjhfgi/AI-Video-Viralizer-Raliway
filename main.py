import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient
import io

app = Flask(__name__)
CORS(app)

# Railway Variables থেকে টোকেন নেওয়া
HF_TOKEN = os.environ.get("HF_TOKEN")

# ক্লায়েন্ট সেটআপ
client = InferenceClient(token=HF_TOKEN)

@app.route('/generate-3d', methods=['POST'])
def generate_3d():
    if not HF_TOKEN:
        return jsonify({"error": "HF_TOKEN missing in Railway"}), 500

    try:
        data = request.get_json()
        prompt = data.get("prompt", "A simple 3D cube")
        
        print(f"Generating 3D for: {prompt}")

        # নতুন মেথডে মডেল কল (Shap-E)
        # এখানে সরাসরি মডেল আইডি ব্যবহার করা হচ্ছে
        image_data = client.post(
            json={"inputs": prompt},
            model="openai/shap-e",
        )
        
        if image_data:
            return send_file(
                io.BytesIO(image_data),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name='model_3d.glb'
            )
        else:
            return jsonify({"error": "No data received from HF"}), 500

    except Exception as e:
        error_msg = str(e)
        print(f"HF Error: {error_msg}")
        
        # যদি মডেলটি এখন এপিআই হিসেবে কাজ না করে তবে বিকল্প মেসেজ
        if "404" in error_msg:
            return jsonify({"error": "This specific model is currently unavailable as a free API."}), 404
        return jsonify({"error": "Processing error, try again later."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
