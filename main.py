import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# এপিআই কী সেটআপ
API_KEY = "AIzaSyC0qxCRHpTzLPkl4jB6qlv6vd1lmnfWVZA"
genai.configure(api_key=API_KEY)

@app.route('/audit', methods=['POST'])
def audit_design():
    if 'image' not in request.files:
        return jsonify({"error": "No image found"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Audit')
    
    try:
        # লেটেস্ট মডেল ১.৫ ফ্ল্যাশ ব্যবহার করছি যা দ্রুত এবং নির্ভুল
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # ইমেজ প্রসেস করা
        image_data = img_file.read()
        contents = [
            description,
            {"mime_type": "image/jpeg", "data": image_data}
        ]
        
        # জেনারেশন শুরু
        response = model.generate_content(contents)
        
        if response.text:
            return jsonify({"result": response.text})
        else:
            return jsonify({"error": "AI could not generate feedback"}), 500
            
    except Exception as e:
        # লগ-এ পরিষ্কার মেসেজ দেখাবে
        print(f"Railway Error Logic: {str(e)}")
        return jsonify({"error": "AI Error. Please check API key permissions."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
