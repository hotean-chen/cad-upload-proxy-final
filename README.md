# CAD Upload Proxy - Render.com 部署版本

这是一个专门为 Render.com 平台优化的 CAD 文件上传代理服务器。

## 🚀 特性

- ✅ 完整的 CORS 支持
- ✅ 详细的日志记录
- ✅ 错误处理和超时管理
- ✅ 专门为 Render.com 优化
- ✅ 支持大文件上传（最大 60 秒超时）

## 📁 文件说明

- `main.py`: 主应用文件，包含 Flask 服务器和所有路由
- `requirements.txt`: Python 依赖包列表
- `README.md`: 项目说明文档

## 🔧 部署到 Render.com

### 第一步：准备 GitHub 仓库
1. 创建新的 GitHub 仓库（必须是 Public）
2. 上传所有文件到仓库根目录

### 第二步：在 Render 创建 Web Service
1. 访问 https://render.com
2. 注册并连接 GitHub 账户
3. 创建新的 Web Service
4. 连接您的 GitHub 仓库

### 第三步：配置部署设置
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

### 第四步：添加环境变量
- **GOOGLE_SCRIPT_URL**: 您的 Google Apps Script Web App URL

## 🔍 测试端点

部署成功后，您可以测试以下端点：

- `GET /`: 基本状态检查
- `GET /api/test`: 详细状态检查
- `POST /api/cad-upload`: CAD 文件上传处理

## 📝 使用方法

部署成功后，将前端表单的 `WEB_APP_URL` 设置为：
```javascript
const WEB_APP_URL = 'https://your-service-name.onrender.com/api/cad-upload';
```

## 🐛 故障排除

如果遇到问题，请检查：
1. GitHub 仓库是否为 Public
2. 所有文件是否在根目录
3. 环境变量 `GOOGLE_SCRIPT_URL` 是否正确配置
4. Google Apps Script Web App 是否正常运行

## 📞 支持

如果部署失败，请提供：
- Render 构建日志
- Render 运行时日志
- 浏览器控制台错误信息

