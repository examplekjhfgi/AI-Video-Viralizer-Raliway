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
        # --- ইমেজ রিসাইজিং পার্ট (যাতে 'entity too large' এরর না আসে) ---
        img = Image.open(img_file)
        # যদি ইমেজটি ১০০০ পিক্সেলের বেশি চওড়া হয়, তবে ছোট করা হবে
        if img.width > 1000:
            ratio = 1000 / float(img.width)
            height = int((float(img.height) * float(ratio)))
            img = img.resize((1000, height), Image.LANCZOS)
        
        # ছবিকে কম্প্রেস করে বাইনারিতে রূপান্তর
        byte_arr = io.BytesIO()
        img = img.convert("RGB") # PNG থাকলেও JPG ফরম্যাটে কনভার্ট হবে
        img.save(byte_arr, format='JPEG', quality=70) # ৭০% কোয়ালিটি যাতে সাইজ ছোট হয়
        image_bytes = byte_arr.getvalue()
        # ---------------------------------------------------------

        payload = {
            "inputs": {
                "image": base64.b64encode(image_bytes).decode("utf-8"),
                "question": f"Analyze this UI/UX design: {description}. List 3 issues and a score out of 100."
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        output = response.json()
        
        if isinstance(output, dict) and "error" in output:
            return jsonify({"error": output["error"]}), 500
            
        return jsonify({"result": output.get("answer", "No response from AI.")})
            
    except Exception as e:
        print(f"DEBUG CRASH: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
