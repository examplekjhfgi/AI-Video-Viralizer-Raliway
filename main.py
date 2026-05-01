import os
import requests
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# রেলওয়ে ভ্যারিয়েবল থেকে টোকেন সংগ্রহ
HF_TOKEN = os.environ.get("HF_TOKEN")

# Moondream মডেল ইউআরএল
API_URL = "https://api-inference.huggingface.co/models/vikhyatk/moondream2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

@app.route('/audit', methods=['POST'])
def audit_design():
    # ডিবাগ: টোকেন ঠিকমতো পেয়েছে কি না চেক (সুরক্ষার জন্য প্রথম ৩টি অক্ষর দেখাবে)
    if not HF_TOKEN:
        print("DEBUG ERROR: HF_TOKEN is missing in Railway Variables!")
        return jsonify({"error": "Server setup incomplete (Missing Token)"}), 500
    else:
        print(f"DEBUG: Token found. Starts with: {HF_TOKEN[:3]}")

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Design Audit')
    
    try:
        # ইমেজ প্রসেসিং
        image_bytes = img_file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        
        payload = {
            "inputs": {
                "image": image_base64,
                "question": f"Analyze this {description}. List 3 specific UI/UX issues and give a score out of 100."
            }
        }
        
        print("DEBUG: Sending request to Hugging Face...")
        response = requests.post(API_URL, headers=headers, json=payload)
        output = response.json()
        print(f"DEBUG HF Response: {output}") # হাগিং ফেস কী বলছে তা লগে দেখাবে
        
        if isinstance(output, dict) and "error" in output:
            return jsonify({"error": output["error"]}), 500
            
        result_text = output.get("answer", "AI could not generate a response.")
        return jsonify({"result": result_text})
            
    except Exception as e:
        print(f"DEBUG CRASH: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
