import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# রেলওয়ে ভেরিয়েবল থেকে কী নেওয়া
API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/audit', methods=['POST'])
def audit_design():
    if not API_KEY:
        return jsonify({"error": "API Key missing in Railway!"}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Design')
    
    try:
        # এপিআই কনফিগার করা
        genai.configure(api_key=API_KEY)
        
        # সবথেকে স্ট্যাবল ইমেজ মডেল (gemini-pro-vision)
        model = genai.GenerativeModel('gemini-pro-vision')
        
        image_bytes = img_file.read()
        
        # প্রম্পট এবং ইমেজ
        contents = [
            f"As a Senior UI/UX Designer, analyze this {description}. Provide 3 critical issues and a design score out of 100.",
            {'mime_type': 'image/jpeg', 'data': image_bytes}
        ]
        
        # জেনারেশন শুরু
        response = model.generate_content(contents)
        
        # জেমিনি প্রো-ভিশনে টেক্সট পাওয়ার সঠিক পদ্ধতি
        if response and response.text:
            return jsonify({"result": response.text})
        else:
            return jsonify({"error": "AI response was empty."}), 500
            
    except Exception as e:
        error_msg = str(e)
        print(f"GEMINI ERROR LOG: {error_msg}")
        return jsonify({"error": "Service is temporarily busy. Please retry in 30 seconds."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
