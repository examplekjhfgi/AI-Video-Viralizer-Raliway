import os
import requests
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# রেলওয়ে ভ্যারিয়েবল থেকে টোকেন
HF_TOKEN = os.environ.get("HF_TOKEN")
# তুলনামূলক ছোট এবং স্থিতিশীল মডেল
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

@app.route('/audit', methods=['POST'])
def audit_design():
    if not HF_TOKEN:
        return jsonify({"error": "HF_TOKEN missing"}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image"}), 400
    
    try:
        img_file = request.files['image']
        image_bytes = img_file.read()
        
        # ডিবাগ: ফাইল সাইজ চেক
        file_size_mb = len(image_bytes) / (1024 * 1024)
        print(f"DEBUG: Processing image of size {file_size_mb:.2f} MB")

        # হাগিং ফেস এপিআই কল (সরাসরি বাইনারি ডেটা পাঠিয়ে)
        response = requests.post(API_URL, headers=headers, data=image_bytes, timeout=60)
        
        if response.status_code == 503:
            return jsonify({"error": "AI is loading. Wait 20s."}), 503
            
        output = response.json()
        
        # BLIP মডেল সাধারণত ডেসক্রিপশন দেয়
        if isinstance(output, list) and len(output) > 0:
            result = output[0].get('generated_text', 'No feedback.')
            # যেহেতু এটি ছোট মডেল, আমরা অডিট টেক্সট কিছুটা ম্যানুয়ালি যোগ করতে পারি
            final_feedback = f"Design Observation: {result}. (Note: Please use a smaller JPG for detailed UI audit score)."
            return jsonify({"result": final_feedback})
        
        return jsonify({"error": "AI response error"}), 500

    except Exception as e:
        print(f"CRASH LOG: {str(e)}")
        return jsonify({"error": "Railway Memory Full. Use smaller image."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
