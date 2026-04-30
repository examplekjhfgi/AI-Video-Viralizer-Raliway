import os
import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

# API Keys
GEMINI_API_KEY = "AIzaSyAJOTVeo3e9lI0k1fNpOe8_3lAA1pBFp34"
YT_API_KEY = "AIzaSyCa0dwxymgiP-KIRD1VJ99GGMMHqGQDycc"
SHOTSTACK_KEY = "C6CEKeobSqtR1wmGTJmhMYzdoJx2gqPhyUegts7m"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_video_id(url):
    """লিঙ্ক থেকে সঠিক ভিডিও আইডি বের করার উন্নত ফাংশন"""
    reg_exp = r'^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*'
    match = re.search(reg_exp, url)
    return match.group(7) if match and len(match.group(7)) == 11 else None

def get_video_details(video_id):
    try:
        youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
        request = youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()
        return response['items'][0]['snippet'] if response['items'] else None
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return None

@app.route('/process', methods=['GET'])
def process():
    video_url = request.args.get('url')
    task = request.args.get('task')
    
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    video_id = get_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL format"}), 400

    details = get_video_details(video_id)
    if not details:
        return jsonify({"error": f"Video with ID {video_id} not found"}), 404

    if task == 'seo':
        prompt = f"Analyze this YouTube video: Title: {details['title']}, Desc: {details['description']}. Provide 5 viral titles, 20 high-ranking tags, a viral description, and 10 SEO keywords."
        response = model.generate_content(prompt)
        return jsonify({"type": "seo", "data": response.text})

    elif task == 'shorts':
        shotstack_url = "https://api.shotstack.io/v1/render"
        headers = {"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"}
        payload = {
            "timeline": {"tracks": [{"clips": [{"asset": {"type": "video", "src": video_url}, "start": 0, "length": 59}]}]},
            "output": {"format": "mp4", "resolution": "hd"}
        }
        res = requests.post(shotstack_url, json=payload, headers=headers)
        return jsonify({"type": "shorts", "data": res.json()})

if __name__ == '__main__':
    # Railway-এর জন্য পোর্ট সেটআপ
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
