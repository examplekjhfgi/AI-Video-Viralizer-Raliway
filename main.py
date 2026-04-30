import os
import requests
import re
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

# API Keys
GEMINI_API_KEY = "AIzaSyBPSzfjOouZP_nKWP65nr28hTBU329CWPs"
YT_API_KEY = "AIzaSyCa0dwxymgiP-KIRD1VJ99GGMMHqGQDycc"
SHOTSTACK_KEY = "C6CEKeobSqtR1wmGTJmhMYzdoJx2gqPhyUegts7m"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_video_id(url):
    """লিঙ্ক থেকে আইডি বের করার সবচেয়ে নিরাপদ উপায়"""
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_video_details(video_id):
    try:
        youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
        req = youtube.videos().list(part="snippet", id=video_id)
        response = req.execute()
        return response['items'][0]['snippet'] if response['items'] else None
    except Exception as e:
        print(f"YouTube Error: {e}")
        return None

@app.route('/process', methods=['GET'])
def process():
    video_url = request.args.get('url')
    task = request.args.get('task')
    
    video_id = get_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    details = get_video_details(video_id)
    if not details:
        return jsonify({"error": "Video details not found"}), 404

    if task == 'seo':
        try:
            prompt = f"Analyze this YouTube video: Title: {details['title']}, Desc: {details['description']}. Provide 5 viral titles, 20 high-ranking tags, a viral description, and 10 SEO keywords."
            response = model.generate_content(prompt)
            # Gemini response check
            if response and response.text:
                return jsonify({"type": "seo", "data": response.text})
            else:
                return jsonify({"error": "AI could not generate content"}), 500
        except Exception as e:
            print(f"Gemini Error: {e}")
            return jsonify({"error": "AI processing failed"}), 500

    elif task == 'shorts':
        try:
            shotstack_url = "https://api.shotstack.io/v1/render"
            headers = {"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"}
            
            # Shotstack-এর জন্য ভিডিও লিঙ্ক পরিষ্কার করা (শুধু আইডি ব্যবহার করা নিরাপদ)
            clean_video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            payload = {
                "timeline": {"tracks": [{"clips": [{"asset": {"type": "video", "src": clean_video_url}, "start": 0, "length": 30}]}]},
                "output": {"format": "mp4", "resolution": "hd"}
            }
            res = requests.post(shotstack_url, json=payload, headers=headers)
            return jsonify({"type": "shorts", "data": res.json()})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    render_id = request.args.get('id')
    shotstack_url = f"https://api.shotstack.io/v1/render/{render_id}"
    headers = {"x-api-key": SHOTSTACK_KEY}
    
    try:
        res = requests.get(shotstack_url, headers=headers).json()
        status = res.get('response', {}).get('status')
        video_url = res.get('response', {}).get('url')
        
        if status == 'done':
            return jsonify({"status": "done", "url": video_url})
        elif status in ['failed', 'error']:
            return jsonify({"status": "failed"})
        else:
            return jsonify({"status": "processing"})
    except:
        return jsonify({"status": "error"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
