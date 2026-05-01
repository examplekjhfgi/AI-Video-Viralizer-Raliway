import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# এখানে আপনার এপিআই কী-টি সরাসরি দিন
API_KEY = "AIzaSyC0qxCRHpTzLPkl4jB6qlv6vd1lmnfWVZA"
genai.configure(api_key=API_KEY)

@app.route('/audit', methods=['POST'])
def audit_design():
    if 'image' not in request.files:
        return jsonify({"error": "No image found"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'Professional UI/UX Audit')
    
    try:
        # পুরনো এবং স্ট্যাবল মডেল যা সহজে ক্র্যাশ করে না
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # ইমেজ ডেটা ফরম্যাট করা
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": img_file.read()
            }
        ]
        
        prompt = f"""
        Act as a Senior UI/UX Expert. Analyze this design.
        Context: {description}
        1. List design issues (Spacing, Hierarchy, Colors).
        2. Give step-by-step solutions.
        3. Score it out of 100.
        """
        
        response = model.generate_content([prompt, image_parts[0]])
        
        if response.text:
            return jsonify({"result": response.text})
        else:
            return jsonify({"error": "AI could not read the image"}), 500
            
    except Exception as e:
        print(f"Railway Crash Logic: {str(e)}")
        return jsonify({"error": "Server is busy, try again!"}), 500

if __name__ == '__main__':
    # রেলওয়ের জন্য পোর্ট সেটআপ
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
