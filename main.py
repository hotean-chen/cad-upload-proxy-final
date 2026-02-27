from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# 优化 CORS 配置，减少预检请求时间
CORS(app, resources={r"/api/*": {"origins": "*"}})

GOOGLE_SCRIPT_URL = os.environ.get('GOOGLE_SCRIPT_URL')

@app.route('/')
def home():
    return "OK", 200 # 极简响应，用于快速唤醒

@app.route('/api/cad-upload', methods=['POST', 'OPTIONS'])
def cad_upload():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        # 转发到 Google，设置较短的连接超时和读取超时
        response = requests.post(
            GOOGLE_SCRIPT_URL,
            json=data,
            timeout=(5, 45) 
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"success": False, "message": "Server Busy"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
