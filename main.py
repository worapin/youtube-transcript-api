from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import os

app = Flask(__name__)

# ตั้งค่า YouTube API ให้ใช้ Webshare proxy
proxy_config = WebshareProxyConfig(
    proxy_username=os.getenv('WEBSHARE_USERNAME'),
    proxy_password=os.getenv('WEBSHARE_PASSWORD'),
)

@app.route('/')
def home():
    return jsonify({'message': 'YouTube Transcript API is running!'})

@app.route('/transcript/<video_id>')
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxy_config.get_proxy_dict())
        return jsonify({
            'video_id': video_id,
            'transcript': transcript
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
