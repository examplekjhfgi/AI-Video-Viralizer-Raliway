import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai
from googleapiclient.discovery import build

app = Flask(__name__)

# --- API Keys Configuration ---
GEMINI_API_KEY = "AIzaSyAJOTVeo3e9lI0k1fNpOe8_3lAA1pBFp34"
YT_API_KEY = "AIzaSyCa0dwxymgiP-KIRD1VJ99GGMMHqGQDycc"
SHOTSTACK_KEY = "C6CEKeobSqtR1wmGTJmhMYzdoJx2gqPhyUegts7m"

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_video_details(video_id):
    """ইউটিউব থেকে ভিডিওর টাইটেল ও ডেসক্রিপশন নিয়ে আসবে"""
    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()
    if response['items']:
        return response['items'][0]['snippet']
    return None

@app.route('/process', methods=['GET'])
def process():
    video_url = request.args.get('url')
    task = request.args.get('task') # 'seo' অথবা 'shorts'
    
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400
    
    # ভিডিও আইডি এক্সট্র্যাক্ট করা
    video_id = video_url.split("v=")[-1].split("&")[0] if "v=" in video_url else video_url.split("/")[-1]
    
    details = get_video_details(video_id)
    if not details:
        return jsonify({"error": "Video not found"}), 404

    if task == 'seo':
        # Gemini AI দিয়ে এসইও রিসার্চ করা
        prompt = f"""
        Analyze this YouTube video as an SEO expert:
        Title: {details['title']}
        Description: {details['description']}
        
        Provide:
        1. 5 Viral Titles
        2. High-ranking Tags (comma separated)
        3. A professional SEO Description
        4. Ranking Keywords
        """
        response = model.generate_content(prompt)
        return jsonify({"type": "seo", "data": response.text})

    elif task == 'shorts':
        # Shotstack API দিয়ে শর্টস বানানোর রিকোয়েস্ট (সিম্পল এডিট)
        # এটি ভিডিওর প্রথম ৬০ সেকেন্ড কাটবে
        shotstack_url = "https://api.shotstack.io/v1/render"
        headers = {"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"}
        
        payload = {
            "timeline": {
                "tracks": [{
                    "clips": [{
                        "asset": {
                            "type": "video",
                            "src": video_url,
                            "trim": 0
                        },
                        "start": 0,
                        "length": 60
                    }]
                }]
            },
            "output": {
                "format": "mp4",
                "resolution": "hd" 
            }
        }
        
        # Shotstack এ রিকোয়েস্ট পাঠানো
        res = requests.post(shotstack_url, json=payload, headers=headers)
        return jsonify({"type": "shorts", "data": res.json()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
