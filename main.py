import os
import requests
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# রেলওয়ে ভ্যারিয়েবল থেকে টোকেন সংগ্রহ
HF_TOKEN = os.environ.get("HF_TOKEN")

# Hugging Face মডেল ইউআরএল (Moondream2)
API_URL = "https://api-inference.huggingface.co/models/vikhyatk/moondream2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

@app.route('/audit', methods=['POST'])
def audit_design():
    # টোকেন চেক করা (নিরাপত্তার জন্য)
    if not HF_TOKEN:
        return jsonify({"error": "HF_TOKEN not found in Railway Variables"}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Design')
    
    try:
        # ইমেজ প্রসেসিং
        image_bytes = img_file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        
        # AI কে পাঠানোর জন্য ডেটা ফরম্যাট
        payload = {
            "inputs": {
                "image": image_base64,
                "question": f"Analyze this {description}. List 3 specific UI/UX issues and give a score out of 100."
            }
        }
        
        # হাগিং ফেস এপিআই কল
        response = requests.post(API_URL, headers=headers, json=payload)
        output = response.json()
        
        # মডেল লোড হওয়ার এরর হ্যান্ডেল করা
        if isinstance(output, dict) and "error" in output:
            if "loading" in output["error"]:
                return jsonify({"error": "Model is waking up. Please try again in 20 seconds."}), 503
            return jsonify({"error": output["error"]}), 500
            
        # রেজাল্ট পাঠানো
        result_text = output.get("answer", "AI could not generate a response.")
        return jsonify({"result": result_text})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # রেলওয়ে অটোমেটিক পোর্ট সেট করে দেয়
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
