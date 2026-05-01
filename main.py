import os
import httpx
import base64
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app)

HF_TOKEN = os.environ.get("HF_TOKEN")
# মডেলটি পরিবর্তন করে Llava দিচ্ছি কারণ এটি Moondream এর চেয়ে দ্রুত রেসপন্স দেয়
API_URL = "https://api-inference.huggingface.co/models/llava-hf/llava-1.5-7b-hf"

@app.route('/audit', methods=['POST'])
def audit_design():
    if not HF_TOKEN:
        return jsonify({"error": "Token missing in Railway"}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image found"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Design Audit')
    
    try:
        # ইমেজ রিসাইজিং (৫০০ পিক্সেল - আরও ছোট যাতে দ্রুত আপলোড হয়)
        img = Image.open(img_file)
        img.thumbnail((500, 500))
        
        byte_arr = io.BytesIO()
        img = img.convert("RGB")
        img.save(byte_arr, format='JPEG', quality=50) 
        image_base64 = base64.b64encode(byte_arr.getvalue()).decode("utf-8")

        payload = {
            "inputs": f"USER: <image>\nAnalyze this {description} UI design. List 3 main issues and give a score out of 100.\nASSISTANT:"
        }
        # ইমেজ ডেটা আলাদাভাবে পাঠানো (Llava format)
        payload["parameters"] = {"image": image_base64}

        # HTTPX ব্যবহার করছি বড় টাইম-আউট (৯০ সেকেন্ড) সহ
        with httpx.Client(timeout=90.0) as client:
            print("DEBUG: Sending request to AI...")
            response = client.post(
                API_URL, 
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json={"inputs": f"Context: {description}. What are the UI issues?", "image": image_base64}
            )
            
            if response.status_code == 503:
                return jsonify({"error": "AI is warming up. Try again in 30s."}), 503
            
            output = response.json()
            # Llava সাধারণত লিস্ট আকারে আউটপুট দেয়
            result = output[0]['generated_text'] if isinstance(output, list) else str(output)
            return jsonify({"result": result})
            
    except Exception as e:
        print(f"Final Crash Debug: {str(e)}")
        return jsonify({"error": "Connection slow. Please try a smaller image."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
