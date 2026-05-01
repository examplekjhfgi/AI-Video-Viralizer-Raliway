import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# এপিআই সেটআপ
GEMINI_KEY = "AIzaSyBgV_tGDEK-uQOFop8zdYCxMSEw9KJAzFg"
genai.configure(api_key=GEMINI_KEY)
# Gemini 1.5 Flash ব্যবহার করা হয়েছে যা ছবি বুঝতে পারদর্শী
model = genai.GenerativeModel('gemini-1.5-flash')

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

@app.route('/audit', methods=['POST'])
def audit_design():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', '')
    
    prompt = f"""
    Act as a Senior UI/UX Expert. Analyze this design. 
    Context: {description}
    1. Identify specific issues (Spacing, Visual Hierarchy, Typography, Color Contrast).
    2. Provide actionable fixes for each issue.
    3. Give a 'Perfection Score' out of 100.
    4. If score is 100, suggest uploading to professional platforms.
    Tone: Professional and constructive.
    """
    
    img_data = encode_image(img_file)
    response = model.generate_content([
        prompt,
        {'mime_type': 'image/jpeg', 'data': img_data}
    ])
    
    return jsonify({"result": response.text})

@app.route('/seo', methods=['POST'])
def generate_seo():
    data = request.json
    title = data.get('title', 'UI/UX Design')
    platforms = data.get('platforms', [])
    
    prompt = f"""
    Create a viral SEO package for a design titled '{title}'.
    Target Platforms: {', '.join(platforms)}.
    Provide:
    - Image Metadata: Title, Subject, Tags (semicolon separated), and Comments.
    - Captions: Platform-specific hooks and hashtags for Dribbble, Behance, and LinkedIn.
    """
    response = model.generate_content(prompt)
    return jsonify({"seo": response.text})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
