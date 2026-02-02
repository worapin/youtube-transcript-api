from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import os

app = Flask(__name__)

# ตั้งค่า YouTube API ให้ใช้ Webshare proxy
ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username=os.getenv('WEBSHARE_USERNAME'),
        proxy_password=os.getenv('WEBSHARE_PASSWORD'),
    )
)

@app.route('/')
def home():
    return jsonify({'message': 'YouTube Transcript API is running!'})

@app.route('/transcript/<video_id>')
def get_transcript(video_id):
    try:
        transcript = ytt_api.fetch(video_id)
        return jsonify({
            'success': True,
            'data': transcript.to_raw_data()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
