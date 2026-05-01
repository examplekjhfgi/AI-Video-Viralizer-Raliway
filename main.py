import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# এখানে আপনার একদম নতুন এপিআই কী-টি দিন
API_KEY = "AIzaSyC0qxCRHpTzLPkl4jB6qlv6vd1lmnfWVZA"

# ক্লায়েন্ট কনফিগারেশন - আমরা সরাসরি মডেল স্ট্রিং ব্যবহার করব
client = genai.Client(api_key=API_KEY)

@app.route('/audit', methods=['POST'])
def audit_design():
    if 'image' not in request.files:
        return jsonify({"error": "No image found"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Design Audit')
    
    try:
        image_data = img_file.read()
        
        prompt = f"""
        Act as a Senior UI/UX Expert. Analyze this design. 
        Context: {description}
        1. Identify specific issues.
        2. Provide actionable fixes.
        3. Give a 'Perfection Score' out of 100.
        """
        
        # মডেলের নাম 'models/gemini-1.5-flash' এর বদলে শুধু 'gemini-1.5-flash' ব্যবহার করুন
        # যদি flash কাজ না করে, তবে 'gemini-1.5-pro' ট্রাই করতে পারেন
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[
                prompt,
                types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
            ]
        )
        
        return jsonify({"result": response.text})
            
    except Exception as e:
        # এরর মেসেজটি পরিষ্কারভাবে দেখার জন্য
        error_msg = str(e)
        print(f"Final Debug Error: {error_msg}")
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
