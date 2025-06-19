from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"])

# 从环境变量获取 Google Apps Script URL
GOOGLE_SCRIPT_URL = os.environ.get('GOOGLE_SCRIPT_URL')

@app.route('/')
def home():
    """主页端点 - 服务状态检查"""
    return jsonify({
        "status": "ok",
        "message": "CAD Upload Proxy is running",
        "service": "Hotean CAD Upload Proxy",
        "version": "1.0",
        "platform": "Render.com"
    })

@app.route('/api/test')
def test():
    """测试端点 - 详细状态检查"""
    return jsonify({
        "status": "ok",
        "message": "CAD Upload Proxy is running",
        "google_script_configured": bool(GOOGLE_SCRIPT_URL),
        "google_script_url_length": len(GOOGLE_SCRIPT_URL) if GOOGLE_SCRIPT_URL else 0,
        "platform": "Render.com"
    })

@app.route('/api/cad-upload', methods=['POST', 'OPTIONS'])
def cad_upload():
    """CAD 文件上传处理端点"""
    
    # 处理 CORS 预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response
    
    try:
        # 检查 Google Script URL 是否配置
        if not GOOGLE_SCRIPT_URL:
            logger.error("GOOGLE_SCRIPT_URL environment variable not configured")
            response = jsonify({
                "success": False,
                "message": "Server configuration error: Google Script URL not set"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            logger.warning("No JSON data received in request")
            response = jsonify({
                "success": False,
                "message": "No data received"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        logger.info(f"Received upload request for: {data.get('name', 'Unknown user')}")
        logger.info(f"Service type: {data.get('serviceType', 'Unknown')}")
        logger.info(f"File name: {data.get('fileName', 'Unknown file')}")
        
        # 转发请求到 Google Apps Script
        logger.info(f"Forwarding request to Google Apps Script: {GOOGLE_SCRIPT_URL[:50]}...")
        
        response = requests.post(
            GOOGLE_SCRIPT_URL,
            json=data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Hotean-CAD-Proxy/1.0'
            },
            timeout=60  # 增加超时时间到60秒
        )
        
        logger.info(f"Google Apps Script response status: {response.status_code}")
        
        # 检查响应状态
        if response.status_code != 200:
            logger.error(f"Google Apps Script returned status {response.status_code}")
            flask_response = jsonify({
                "success": False,
                "message": f"Google Apps Script error (status {response.status_code})"
            })
            flask_response.headers.add('Access-Control-Allow-Origin', '*')
            return flask_response, 502
        
        # 解析 Google Apps Script 的响应
        try:
            result = response.json()
        except ValueError as e:
            logger.error(f"Failed to parse Google Apps Script response as JSON: {e}")
            logger.error(f"Response content: {response.text[:500]}")
            flask_response = jsonify({
                "success": False,
                "message": "Invalid response from Google Apps Script"
            })
            flask_response.headers.add('Access-Control-Allow-Origin', '*')
            return flask_response, 502
        
        # 添加 CORS 头并返回结果
        flask_response = jsonify(result)
        flask_response.headers.add('Access-Control-Allow-Origin', '*')
        flask_response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        
        success = result.get('success', False)
        logger.info(f"Request processed. Success: {success}")
        
        if success:
            logger.info("File upload completed successfully")
        else:
            logger.warning(f"File upload failed: {result.get('message', 'Unknown error')}")
        
        return flask_response
        
    except requests.exceptions.Timeout:
        logger.error("Request to Google Apps Script timed out")
        response = jsonify({
            "success": False,
            "message": "Request timeout. Please try again with a smaller file."
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 504
        
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Google Apps Script")
        response = jsonify({
            "success": False,
            "message": "Unable to connect to Google Apps Script. Please check the configuration."
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 502
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Google Apps Script failed: {str(e)}")
        response = jsonify({
            "success": False,
            "message": "Failed to process request. Please try again."
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 502
        
    except Exception as e:
        logger.error(f"Unexpected error in cad_upload: {str(e)}", exc_info=True)
        response = jsonify({
            "success": False,
            "message": "Internal server error. Please try again."
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    response = jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": ["/", "/api/test", "/api/cad-upload"]
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 404

@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    response = jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 500

if __name__ == '__main__':
    # 获取端口号（Render 会设置 PORT 环境变量）
    port = int(os.environ.get('PORT', 5000))
    
    # 记录启动信息
    logger.info(f"Starting CAD Upload Proxy on port {port}")
    logger.info(f"Google Script URL configured: {bool(GOOGLE_SCRIPT_URL)}")
    if GOOGLE_SCRIPT_URL:
        logger.info(f"Google Script URL: {GOOGLE_SCRIPT_URL[:50]}...")
    
    # 启动 Flask 应用
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )

