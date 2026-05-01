import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# API Key
GEMINI_KEY = "AIzaSyBgV_tGDEK-uQOFop8zdYCxMSEw9KJAzFg"
client = genai.Client(api_key=GEMINI_KEY)

@app.route('/audit', methods=['POST'])
def audit_design():
    if 'image' not in request.files:
        return jsonify({"error": "No image found"}), 400
    
    img_file = request.files['image']
    description = request.form.get('description', 'No description provided')
    
    try:
        # ইমেজ ফাইলটি রিড করা
        image_data = img_file.read()
        
        prompt = f"""
        Act as a Senior UI/UX Expert. Analyze this design thumbnail. 
        User Context: {description}
        1. Identify specific design errors (Typography, Spacing, Hierarchy, Color).
        2. Give step-by-step solutions to fix them.
        3. Provide a 'Perfection Score' out of 100.
        4. If score is 100, say 'Ready to Upload'.
        Format: Professional bullet points.
        """
        
        # জেমিনি এপিআই কল
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
            ]
        )
        
        if response and response.text:
            return jsonify({"result": response.text})
        else:
            return jsonify({"error": "AI could not generate a response"}), 500
            
    except Exception as e:
        print(f"Server Error: {str(e)}") # এটি রেলওয়ে লগে এররটি দেখাবে
        return jsonify({"error": str(e)}), 500

@app.route('/seo', methods=['POST'])
def generate_seo():
    data = request.json
    title = data.get('title', 'Design')
    platforms = data.get('platforms', [])
    
    try:
        prompt = f"Provide viral SEO titles, tags, and description for a UI/UX project titled '{title}' for {platforms}."
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        return jsonify({"seo": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
