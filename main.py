import os
import requests
import base64
import io
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app)

HF_TOKEN = os.environ.get("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/vikhyatk/moondream2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

@app.route('/audit', methods=['POST'])
def audit_design():
    if not HF_TOKEN:
        return jsonify({"error": "Missing HF_TOKEN"}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Design')
    
    try:
        # ইমেজ রিসাইজিং এবং কমপ্রেশন (৫০০ কিলোবাইট এর আশেপাশে রাখা ভালো)
        img = Image.open(img_file)
        img.thumbnail((800, 800)) # আরও ছোট করা হলো দ্রুত রেসপন্স পাওয়ার জন্য
        
        byte_arr = io.BytesIO()
        img = img.convert("RGB")
        img.save(byte_arr, format='JPEG', quality=60) 
        image_bytes = byte_arr.getvalue()

        payload = {
            "inputs": {
                "image": base64.b64encode(image_bytes).decode("utf-8"),
                "question": f"Analyze this UI/UX design: {description}. List 3 issues and a score out of 100."
            }
        }
        
        # এপিআই রিকোয়েস্ট (আমরা ২ বার ট্রাই করার অপশন রাখছি)
        for i in range(2):
            response = requests.post(API_URL, headers=headers, json=payload)
            
            # যদি খালি রেসপন্স আসে (আপনার আগের এররটি এখানে হ্যান্ডেল হবে)
            if not response.content:
                print(f"Empty response, retrying... ({i+1}/2)")
                time.sleep(2)
                continue
                
            try:
                output = response.json()
            except:
                print("Failed to parse JSON, retrying...")
                time.sleep(2)
                continue

            if isinstance(output, dict) and "error" in output:
                # মডেল লোড হতে থাকলে ২০ সেকেন্ড সময় নেয়
                if "loading" in output["error"]:
                    return jsonify({"error": "Model is starting up. Wait 20 seconds and try again."}), 503
                return jsonify({"error": output["error"]}), 500
                
            return jsonify({"result": output.get("answer", "AI could not process this image.")})

        return jsonify({"error": "Server is too busy or model is offline. Please try again in a minute."}), 504
            
    except Exception as e:
        print(f"Final Debug Error: {str(e)}")
        return jsonify({"error": "Something went wrong. Please try again."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
