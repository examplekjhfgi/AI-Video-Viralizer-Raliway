import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# এখানে আপনার Hugging Face Access Token টি দিন
HF_TOKEN = "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"
# আমরা Moondream বা Llava মডেল ব্যবহার করব যা ছবি বুঝতে পারে
API_URL = "https://api-inference.huggingface.co/models/vikhyatk/moondream2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query(image_data, prompt):
    # Hugging Face এ ইমেজ এবং প্রম্পট পাঠানোর ফরম্যাট
    payload = {
        "inputs": {
            "image": image_data,
            "question": prompt
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@app.route('/audit', methods=['POST'])
def audit_design():
    if 'image' not in request.files:
        return jsonify({"error": "No image found"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Design')
    
    try:
        import base64
        image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        
        # প্রম্পটটি Hugging Face মডেলের জন্য ছোট এবং সহজ রাখা ভালো
        prompt = f"Act as a UI/UX expert. Audit this {description}. List 3 main design issues and give a score out of 100."
        
        output = query(image_base64, prompt)
        
        # Hugging Face মডেল সাধারণত সরাসরি টেক্সট দেয়
        result_text = output.get("answer", "AI could not analyze the image.")
        
        return jsonify({"result": result_text})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
