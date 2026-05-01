import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# সিকিউরিটি টিপস: সরাসরি কী না লিখে এনভায়রনমেন্ট ভ্যারিয়েবল ব্যবহার করুন
# রেলওয়েতে ভ্যারিয়েবল সেট করলে এটি অটোমেটিক কাজ করবে
API_KEY = os.environ.get("GEMINI_KEY", "AIzaSyC0qxCRHpTzLPkl4jB6qlv6vd1lmnfWVZA")

client = genai.Client(
    api_key=API_KEY,
    http_options={'api_version': 'v1'} # এরর এড়াতে ভv1 ফোর্স করা হয়েছে
)

@app.route('/audit', methods=['POST'])
def audit_design():
    if 'image' not in request.files:
        return jsonify({"error": "No image found"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'UI/UX Design Audit')
    
    try:
        image_data = img_file.read()
        
        prompt = f"""
        Act as a Senior UI/UX Expert. Analyze this design thumbnail. 
        User Context: {description}
        1. Identify specific design errors (Typography, Spacing, Hierarchy, Color).
        2. Give step-by-step solutions to fix them.
        3. Provide a 'Perfection Score' out of 100.
        4. If score is 100, say 'Ready to Upload'.
        """
        
        # মডেল নেম আপডেট করা হয়েছে
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
            ]
        )
        
        return jsonify({"result": response.text})
            
    except Exception as e:
        print(f"Final Debug Error: {str(e)}")
        return jsonify({"error": "Server is busy. Try again with a new API key."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
