import os
import requests
import base64
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app)

HF_TOKEN = os.environ.get("HF_TOKEN")
# দ্রুত রেসপন্সের জন্য মডেলটি আপডেট করা হলো
API_URL = "https://api-inference.huggingface.co/models/llava-hf/llava-1.5-7b-hf"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

@app.route('/audit', methods=['POST'])
def audit_design():
    if not HF_TOKEN:
        return jsonify({"error": "Railway HF_TOKEN is missing!"}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Design')
    
    try:
        # ইমেজটি ৪৫০ পিক্সেল করা হয়েছে যাতে খুব দ্রুত আপলোড হয়
        img = Image.open(img_file)
        img.thumbnail((450, 450))
        
        byte_arr = io.BytesIO()
        img = img.convert("RGB")
        img.save(byte_arr, format='JPEG', quality=40) 
        img_b64 = base64.b64encode(byte_arr.getvalue()).decode("utf-8")

        # হাগিং ফেসের জন্য একদম পারফেক্ট পেলোড
        payload = {
            "inputs": f"Describe the UI/UX issues in this {description} design and give a score out of 100.",
            "image": img_b64
        }
        
        # Requests দিয়ে টাইমআউট বাড়িয়ে দেওয়া হলো
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 503:
            return jsonify({"error": "AI Model is starting up. Try again in 30 seconds."}), 503
            
        output = response.json()
        
        # আউটপুট থেকে টেক্সট বের করা
        if isinstance(output, list) and len(output) > 0:
            result = output[0].get('generated_text', 'No feedback generated.')
        else:
            result = str(output)

        return jsonify({"result": result})
            
    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": "Connection timed out. Please try again."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
