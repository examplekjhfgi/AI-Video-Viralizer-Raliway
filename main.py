import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# রেলওয়ে ভেরিয়েবল থেকে এপিআই কী নেওয়া
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
        # গুগলের লেটেস্ট ক্লায়েন্ট সেটআপ
        client = genai.Client(api_key=API_KEY)
        
        image_bytes = img_file.read()
        
        # নতুন লাইব্রেরিতে ইমেজ এবং প্রম্পট পাঠানোর নিয়ম
        prompt = f"Act as a Senior UI/UX Expert. Audit this {description} design. List 3 specific issues and give a score out of 100."
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
            ]
        )
        
        if response.text:
            return jsonify({"result": response.text})
        else:
            return jsonify({"error": "AI response was empty."}), 500
            
    except Exception as e:
        error_msg = str(e)
        print(f"GEMINI ERROR LOG: {error_msg}")
        return jsonify({"error": "AI is busy. Please try again in 10 seconds."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
