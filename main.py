import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# এপিআই কী সেটআপ
GEMINI_KEY = "AIzaSyBgV_tGDEK-uQOFop8zdYCxMSEw9KJAzFg"
client = genai.Client(api_key=GEMINI_KEY)

@app.route('/audit', methods=['POST'])
def audit_design():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', '')
    
    # ইমেজ কনভার্ট করা
    image_bytes = img_file.read()
    
    prompt = f"""
    Act as a Senior UI/UX Expert. Analyze this design. 
    Context: {description}
    1. Identify specific issues (Spacing, Visual Hierarchy, Typography, Color Contrast).
    2. Provide actionable fixes for each issue.
    3. Give a 'Perfection Score' out of 100.
    4. If score is 100, suggest uploading to professional platforms.
    Tone: Professional and constructive.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            ]
        )
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/seo', methods=['POST'])
def generate_seo():
    data = request.json
    title = data.get('title', 'UI/UX Design')
    platforms = data.get('platforms', [])
    
    prompt = f"Create a viral SEO package for a design titled '{title}' for platforms: {', '.join(platforms)}."
    
    try:
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        return jsonify({"seo": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
