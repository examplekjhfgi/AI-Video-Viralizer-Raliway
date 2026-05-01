import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# একদম নতুন একটি কী এখানে বসান
GEMINI_KEY = "AIzaSyC0qxCRHpTzLPkl4jB6qlv6vd1lmnfWVZA"
genai.configure(api_key=GEMINI_KEY)

@app.route('/audit', methods=['POST'])
def audit():
    if 'image' not in request.files:
        return jsonify({"error": "No image"}), 400
    
    img = request.files['image']
    desc = request.form.get('description', '')

    try:
        # মডেলের নাম 'gemini-1.5-flash' এর বদলে শুধু 'gemini-pro-vision' ট্রাই করুন
        # অনেক পুরনো অ্যাকাউন্টে ১.৫ মডেল ডিফল্টভাবে থাকে না
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # ইমেজ প্রসেসিং
        img_data = [{'mime_type': 'image/jpeg', 'data': img.read()}]
        prompt = f"Expert UI/UX Audit for: {desc}. List issues and give a score out of 100."
        
        response = model.generate_content([prompt, img_data[0]])
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
