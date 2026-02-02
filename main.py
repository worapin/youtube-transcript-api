from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import os
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# ตั้งค่า Rate Limiter - จำกัด 10 requests ต่อนาที
limiter = Limiter(    get_remote_address,
    app=app,
    default_limits=["10000 per day", "1000 per hour"],    storage_uri="memory://",
)

# ตั้งค่า API key จาก environment variable
API_KEY = os.getenv('API_KEY', 'your-secret-api-key-here')

# ตั้งค่า YouTube API ให้ใช้ Webshare proxy
proxy_config = WebshareProxyConfig(
    proxy_username=os.getenv('WEBSHARE_USERNAME'),
    proxy_password=os.getenv('WEBSHARE_PASSWORD'),
)

# สร้าง YouTubeTranscriptApi instance ด้วย proxy config
ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)

# Decorator สำหรับตรวจสอบ API key
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ตรวจสอบ API key จาก header
        api_key = request.headers.get('X-API-Key')
        
        # ถ้าไม่มี API key ใน header ให้ลองดูจาก query parameter
        if not api_key:
            api_key = request.args.get('api_key')
        
        # ตรวจสอบว่า API key ถูกต้องหรือไม่
        if not api_key or api_key != API_KEY:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Valid API key required. Please provide API key in X-API-Key header or api_key query parameter.'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@limiter.limit("30 per minute")
def home():
    return jsonify({
        'message': 'YouTube Transcript API is running!',
        'version': '1.1.0',
        'endpoints': {
            '/transcript/<video_id>': 'Get transcript for a YouTube video (requires API key)'
        },
        'authentication': {
            'method': 'API Key',
            'header': 'X-API-Key: your-api-key',
            'query_param': '?api_key=your-api-key'
        },
        'rate_limits': {
            'default': '10000 requests per day, 1000 per hour',            'transcript_endpoint': '10 requests per minute'
        },
        'security': {
            'default': '10000 requests per day, 1000 per hour',            'rate_limiting': 'Enabled to prevent abuse'
        }
    })

@app.route('/transcript/<video_id>')
@limiter.limit("10 per minute")
@require_api_key
def get_transcript(video_id):
    try:
        # ใช้ ytt_api.fetch() แทน YouTubeTranscriptApi.get_transcript()
        transcript = ytt_api.fetch(video_id)
        return jsonify({
            'video_id': video_id,
            'transcript': [{'text': entry.text, 'start': entry.start, 'duration': entry.duration} for entry in transcript]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
