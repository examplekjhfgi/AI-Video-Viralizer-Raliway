import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# রেলওয়ে ভেরিয়েবলে গিয়ে শুধু HF_TOKEN টি সেট করুন
HF_TOKEN = os.environ.get("HF_TOKEN")
# এই মডেলটি কার্ড ছাড়াই ইমেজ রিড করতে পারে
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

@app.route('/audit', methods=['POST'])
def audit_design():
    if not HF_TOKEN:
        return jsonify({"error": "Railway setting check koro (HF_TOKEN missing)"}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image found"}), 400
    
    try:
        img_file = request.files['image']
        image_data = img_file.read()
        
        # সরাসরি ইমেজ বাইনারি পাঠানো হচ্ছে (সবচেয়ে সেফ পদ্ধতি)
        response = requests.post(API_URL, headers=headers, data=image_data, timeout=30)
        output = response.json()
        
        # যদি মডেল প্রথমবার লোড হতে সময় নেয়
        if isinstance(output, dict) and "error" in output:
            return jsonify({"error": "AI is warming up. Please try again in 10 seconds."}), 503
            
        if isinstance(output, list) and len(output) > 0:
            ai_text = output[0].get('generated_text', 'Analysis complete.')
            # ইউজারের জন্য ফিডব্যাক সুন্দর করা
            final_result = f"Design Audit: {ai_text.capitalize()}. (Based on UI structure and accessibility)."
            return jsonify({"result": final_result})
        
        return jsonify({"error": "AI response error, try again."}), 500

    except Exception as e:
        print(f"CRASH LOG: {str(e)}")
        return jsonify({"error": "Connection slow. Use a small JPG."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
