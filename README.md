# AI面试官系统 - 使用指南

> 🎯 一个智能化的AI面试练习系统，帮助你模拟面试、发现不足、提升表现

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [系统架构](#系统架构)
- [详细使用说明](#详细使用说明)
- [API文档](#api文档)
- [配置说明](#配置说明)
- [部署指南](#部署指南)
- [常见问题](#常见问题)
- [开发指南](#开发指南)

---

## ✨ 功能特性

### 🎭 面试模拟
- **多轮面试支持**：支持2-5轮面试，模拟真实面试流程
- **智能轮数判断**：AI根据职位信息自动推荐合适的面试轮数
- **多种面试官角色**：业务领导、部门总监、HR等不同角色
- **灵活配置**：自定义每轮的问题数量、评分权重

### 🎙️ 录音与转写
- **浏览器录音**：使用MediaRecorder API直接在浏览器中录音
- **语音转文字**：集成阿里云/腾讯云语音识别，自动转写面试内容
- **文字回答**：支持直接文字输入回答问题
- **音频管理**：自动保存和管理所有录音文件

### 🤖 AI智能评分
- **360度全方位评分**：
  - 专业能力（35%）：关键词分析、内容深度
  - 沟通表达（30%）：逻辑性、流畅度、表达清晰度
  - 面试状态（20%）：自信度、积极性、肢体语言
  - 时间控制（15%）：回答时长、节奏掌握
- **实时反馈**：每回答完一个问题立即查看评分
- **详细分析**：针对每个维度给出具体的改进建议

### 📊 面试报告
- **总体评分**：综合评分和等级评定
- **雷达图展示**：四维度能力可视化
- **面试总结**：整体表现总结
- **亮点分析**：突出你的优势
- **改进建议**：具体的提升方向
- **详细记录**：每轮面试的完整评分记录

### 🔐 安全与权限
- **邀请码机制**：Beta测试期使用邀请码注册
- **JWT认证**：Access Token + Refresh Token双Token机制
- **Token黑名单**：支持Token撤销，保护账户安全
- **请求限流**：防止API滥用
- **安全加固**：SQL注入防护、XSS攻击防护

---

## 🚀 快速开始

### 环境要求

- **后端**：Python 3.10+
- **前端**：Node.js 18+
- **数据库**：SQLite（开发）/ PostgreSQL（生产）
- **Docker**：Docker & Docker Compose（可选）

### 一键启动（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd wife_job_hunting

# 启动所有服务
./deploy.sh start

# 访问应用
# 前端：http://localhost:3000
# 后端API：http://localhost:8000
# API文档：http://localhost:8000/docs
```

### 手动启动

#### 1. 后端启动

```bash
cd ai-interviewer-backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py init

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 前端启动

```bash
cd ai-interviewer-frontend

# 安装依赖
npm install

# 启动前端
npm run dev

# 访问 http://localhost:3000
```

### 默认账户

```
管理员账户：
用户名：admin
邮箱：admin@ai-interviewer.com
密码：Admin123!

测试邀请码：
BETA-TEST-001（一次性）
BETA-TEST-002（限量10次）
```

⚠️ **重要**：生产环境请立即修改默认密码！

---

## 🏗️ 系统架构

### 技术栈

**前端**
- React 18 - UI框架
- Vite 8 - 构建工具
- Ant Design 5 - UI组件库
- React Router 7 - 路由管理
- Zustand - 状态管理
- Axios - HTTP客户端

**后端**
- FastAPI 0.104+ - Web框架
- SQLAlchemy 2.0+ - ORM
- Pydantic 2.5+ - 数据验证
- python-jose - JWT认证
- pytest - 测试框架

**数据库**
- SQLite - 开发环境
- PostgreSQL - 生产环境（推荐）

**部署**
- Docker - 容器化
- Docker Compose - 服务编排
- Nginx - 反向代理

### 项目结构

```
ai-interviewer-frontend/          # 前端项目
├── src/
│   ├── components/               # 通用组件
│   │   ├── common/              # 通用UI组件
│   │   ├── layout/              # 布局组件
│   │   └── recording/           # 录音组件
│   ├── pages/                   # 页面组件
│   │   ├── Dashboard/           # 仪表盘
│   │   ├── InterviewConfig/     # 面试配置
│   │   ├── InterviewExecution/  # 面试执行
│   │   ├── InterviewList/      # 面试列表
│   │   └── Report/             # 面试报告
│   ├── services/                # API服务
│   ├── router/                  # 路由配置
│   └── styles/                  # 样式文件

ai-interviewer-backend/           # 后端项目
├── app/
│   ├── api/                     # API路由
│   │   └── v1/                  # API v1
│   ├── core/                    # 核心功能
│   ├── models/                  # 数据模型
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # 业务逻辑
│   └── middleware/              # 中间件
├── tests/                       # 测试
├── scripts/                     # 脚本
└── migrations/                  # 数据库迁移

docker-compose.yml               # Docker编排
nginx.conf                       # Nginx配置
```

---

## 📖 详细使用说明

### 1️⃣ 用户注册与登录

#### 注册账户
1. 访问 http://localhost:3000
2. 点击"注册"按钮
3. 输入邀请码（测试码：BETA-TEST-001）
4. 填写用户信息（用户名、邮箱、密码）
5. 完成注册

#### 登录系统
1. 输入邮箱和密码
2. 点击"登录"
3. 系统自动跳转到仪表盘

### 2️⃣ 创建面试配置

#### 步骤1：填写职位信息
- **职位名称**：如"高级产品经理"
- **公司名称**：如"字节跳动"
- **职位描述**：详细描述职位要求
- **职位级别**：初级/中级/高级/专家
- **行业类型**：互联网/金融/教育等
- **薪资范围**：如"20k-35k"

#### 步骤2：AI分析轮数
- 点击"AI分析"按钮
- 系统自动分析职位信息
- 推荐合适的面试轮数（2-5轮）
- 每轮配置面试官角色和问题数量

**示例配置**：
```
第1轮：业务领导（直属） - 6个问题
第2轮：业务领导2 - 6个问题
第3轮：部门总监 - 6个问题
第4轮：HR - 6个问题
```

#### 步骤3：确认配置
- 查看完整的配置信息
- 可以调整每轮的细节
- 保存配置

### 3️⃣ 开始面试

#### 选择配置和轮次
1. 进入"面试列表"页面
2. 选择要使用的配置
3. 点击"开始面试"按钮
4. 选择要进行的轮次

#### 面试流程

**问题展示**：
- 问题内容
- 考察要点
- 建议回答时长
- 当前进度

**回答方式**：
- **文字回答**：直接在文本框输入
- **语音回答**：点击"开始录音"，完成后点击"停止"

**操作按钮**：
- **提交答案**：提交当前回答
- **跳过问题**：跳过当前问题
- **下一题**：进入下一个问题

**完成面试**：
- 回答完所有问题后
- 点击"完成面试"
- 系统自动生成评分和报告

### 4️⃣ 查看评分与报告

#### 实时评分
- 每回答完一个问题，立即查看该问题的评分
- 四维度评分：专业能力、沟通表达、面试状态、时间控制
- 总分和等级

#### 面试报告
点击"查看报告"按钮，查看：

**总体评分**：
- 综合评分（0-100分）
- 等级评定（S/A/B/C/D）

**雷达图**：
- 四维度能力可视化
- 直观展示优势和不足

**面试总结**：
- 整体表现概述
- 突出亮点
- 待改进方面

**详细建议**：
- 针对每个维度的具体建议
- 可执行的提升方向

**历史记录**：
- 每轮面试的详细评分
- 每个问题的得分和反馈

---

## 🔌 API文档

### 认证相关

#### POST `/api/v1/auth/register` - 用户注册
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Test123!",
  "invitation_code": "BETA-TEST-001"
}
```

#### POST `/api/v1/auth/login` - 用户登录
```json
{
  "email": "test@example.com",
  "password": "Test123!"
}
```

#### POST `/api/v1/auth/refresh` - 刷新Token
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 面试配置相关

#### POST `/api/v1/interviews/configs` - 创建配置
```json
{
  "position_name": "高级产品经理",
  "company_name": "字节跳动",
  "job_description": "负责抖音产品的...",
  "position_level": "高级",
  "company_type": "互联网",
  "industry": "互联网",
  "salary_range": "20k-35k"
}
```

#### GET `/api/v1/interviews/configs` - 获取配置列表
#### GET `/api/v1/interviews/configs/{id}` - 获取配置详情
#### PUT `/api/v1/interviews/configs/{id}` - 更新配置
#### DELETE `/api/v1/interviews/configs/{id}` - 删除配置

### 面试执行相关

#### POST `/api/v1/interviews/sessions` - 创建面试会话
```json
{
  "config_id": 1,
  "round_number": 1
}
```

#### GET `/api/v1/interviews/sessions/{id}` - 获取会话详情
#### GET `/api/v1/interviews/sessions/{id}/questions` - 获取所有问题
#### GET `/api/v1/interviews/sessions/{id}/current-question` - 获取当前问题
#### POST `/api/v1/interviews/sessions/{id}/answers` - 提交答案
```json
{
  "question_id": 1,
  "answer_text": "我的回答...",
  "audio_url": "/uploads/audio/xxx.mp3"
}
```

#### POST `/api/v1/interviews/sessions/{id}/complete` - 完成会话

### 评分与报告相关

#### GET `/api/v1/interviews/sessions/{id}/scores` - 获取评分
#### GET `/api/v1/interviews/sessions/{id}/report` - 获取报告

### AI分析相关

#### POST `/api/v1/ai/analyze-rounds` - AI分析轮数
```json
{
  "position_name": "高级产品经理",
  "company_type": "互联网",
  "position_level": "高级"
}
```

### 完整API文档

访问 http://localhost:8000/docs 查看完整的交互式API文档（Swagger UI）。

---

## ⚙️ 配置说明

### 环境变量配置

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=sqlite:///./data/database.db
# 生产环境使用PostgreSQL：
# DATABASE_URL=postgresql://user:password@localhost/dbname

# JWT密钥（生产环境必须修改！）
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM API配置（可选）
LLM_PROVIDER=qwen  # qwen, openai, anthropic
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# 语音识别API配置（可选）
SPEECH_PROVIDER=aliyun  # aliyun, tencent
SPEECH_API_KEY=your-api-key
SPEECH_APP_KEY=your-app-key
SPEECH_REGION=cn-beijing

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 调试模式
DEBUG=false
```

### LLM API配置

系统支持多种LLM提供商：

#### 通义千问（推荐）
```bash
LLM_PROVIDER=qwen
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus
```

#### OpenAI
```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4
```

#### Anthropic Claude
```bash
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-xxx
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL_NAME=claude-3-sonnet-20240229
```

### 语音识别API配置

#### 阿里云
```bash
SPEECH_PROVIDER=aliyun
SPEECH_API_KEY=your-access-key-id
SPEECH_APP_KEY=your-access-key-secret
SPEECH_REGION=cn-beijing
```

#### 腾讯云
```bash
SPEECH_PROVIDER=tencent
SPEECH_API_KEY=your-secret-id
SPEECH_APP_KEY=your-secret-key
SPEECH_REGION=ap-beijing
```

---

## 🐳 部署指南

### Docker部署（推荐）

#### 1. 构建镜像

```bash
# 构建所有镜像
./deploy.sh build
```

#### 2. 启动服务

```bash
# 启动所有服务
./deploy.sh start

# 查看状态
./deploy.sh status
```

#### 3. 停止服务

```bash
# 停止所有服务
./deploy.sh stop
```

#### 4. 重启服务

```bash
# 重启所有服务
./deploy.sh restart
```

### 生产环境部署

#### 1. 使用PostgreSQL

修改 `docker-compose.yml`：

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/interviewer
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: interviewer
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

#### 2. 配置SSL/HTTPS

```bash
# 使用Let's Encrypt获取免费SSL证书
certbot certonly --standalone -d yourdomain.com

# 更新nginx.conf配置SSL
```

#### 3. 数据库备份

```bash
# 创建备份
./deploy.sh backup

# 恢复备份
./deploy.sh restore backup_20260321.tar.gz
```

---

## ❓ 常见问题

### 1. 如何获取LLM API密钥？

#### 通义千问
1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 创建API Key
3. 选择模型：qwen-plus

#### OpenAI
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 创建API Key
3. 选择模型：gpt-4或gpt-3.5-turbo

### 2. 如何配置语音识别？

参考上面的"语音识别API配置"部分，配置阿里云或腾讯云的API密钥。

### 3. 测试覆盖率如何？

当前测试覆盖率：**>70%**

运行测试：
```bash
cd ai-interviewer-backend
pytest tests/ -v --cov=app --cov-report=html
```

### 4. 如何修改默认管理员密码？

```bash
cd ai-interviewer-backend
python scripts/init_db.py reset
```

或直接在代码中修改 `scripts/init_db.py` 中的密码。

### 5. 前端无法连接后端API？

检查：
1. 后端是否启动（访问 http://localhost:8000/health）
2. CORS配置是否正确
3. API代理配置是否正确（vite.config.js）

### 6. 如何查看日志？

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f frontend
docker-compose logs -f backend
```

---

## 👨‍💻 开发指南

### 本地开发环境搭建

#### 后端开发

```bash
cd ai-interviewer-backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest pytest-cov black flake8 mypy

# 运行测试
pytest tests/ -v

# 代码格式化
black app/
flake8 app/
```

#### 前端开发

```bash
cd ai-interviewer-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm run test

# 代码检查
npm run lint
```

### 数据库迁移

```bash
cd ai-interviewer-backend

# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 添加新的API端点

1. 在 `app/api/v1/` 创建新的路由文件
2. 定义路由和处理函数
3. 在 `app/api/v1/__init__.py` 注册路由
4. 在 `app/schemas/` 定义请求/响应Schema
5. 编写测试用例

### 添加新的前端页面

1. 在 `src/pages/` 创建新页面组件
2. 在 `src/router/index.jsx` 添加路由
3. 创建对应的API服务函数
4. 更新导航菜单

---

## 📊 系统监控

### 健康检查

- **前端健康检查**：http://localhost:3000
- **后端健康检查**：http://localhost:8000/health
- **API文档**：http://localhost:8000/docs

### 性能监控

- **API响应时间**：后端日志中记录
- **数据库查询**：使用SQLAlchemy logging
- **前端性能**：使用React DevTools Profiler

### 日志查看

```bash
# 查看后端日志
tail -f ai-interviewer-backend/logs/app.log

# 查看Docker日志
docker-compose logs -f backend
```

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下流程：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 代码规范

- **Python**：遵循PEP 8规范，使用black格式化
- **JavaScript**：遵循ESLint配置
- **Git提交**：使用Conventional Commits规范

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- **项目地址**：[GitHub Repository]
- **问题反馈**：[Issues]
- **邮件联系**：[project-email]

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Ant Design](https://ant.design/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

---

**祝你面试成功！🎉**
