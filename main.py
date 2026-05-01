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
        print("CRITICAL: GEMINI_API_KEY is missing in Railway Variables!")
        return jsonify({"error": "API Key set করা হয়নি।"}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Design')
    
    try:
        # এপিআই কনফিগার করা
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        image_bytes = img_file.read()
        
        # প্রম্পট এবং ইমেজ ফরম্যাট
        contents = [
            f"Act as a Senior UI/UX Expert. Audit this {description} design. List 3 specific issues and give a score out of 100.",
            {'mime_type': 'image/jpeg', 'data': image_bytes}
        ]
        
        # জেনারেশন শুরু
        response = model.generate_content(contents)
        
        if response.text:
            return jsonify({"result": response.text})
        else:
            return jsonify({"error": "AI could not generate feedback."}), 500
            
    except Exception as e:
        # এটি আপনাকে লগে আসল এরর মেসেজটি দেখাবে
        error_msg = str(e)
        print(f"GEMINI ERROR LOG: {error_msg}")
        
        if "API_KEY_INVALID" in error_msg:
            return jsonify({"error": "আপনার এপিআই কী-টি ভুল বা ইনভ্যালিড।"}), 500
        elif "safety" in error_msg.lower():
            return jsonify({"error": "AI এই ছবিটিকে নিরাপদ মনে করছে না।"}), 500
        else:
            return jsonify({"error": f"Internal Error: {error_msg[:50]}..."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
