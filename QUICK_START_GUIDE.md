# AI面试官系统 - 快速使用指南

## 快速开始(Docker部署 - 推荐)

### 1. 一键启动

```bash
# 进入项目目录
cd /Users/jackson/Documents/wife/wife_job_hunting

# 启动系统
./deploy.sh start
```

### 2. 访问应用

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 3. 核心功能使用

#### 3.1 创建面试配置

1. 登录系统
2. 进入"面试配置"页面
3. 填写职位信息
4. AI自动分析需要几轮面试
5. 保存配置

#### 3.2 开始面试

1. 在"面试列表"中选择配置
2. 选择面试轮次
3. 点击"开始面试"
4. 逐个回答问题
5. 支持文字或语音回答

#### 3.3 查看评分和报告

1. 完成面试后自动显示评分
2. 查看各维度得分:
   - 专业能力 (35%)
   - 沟通表达 (30%)
   - 面试状态 (20%)
   - 时间控制 (15%)
3. 查看AI反馈
4. 查看改进建议
5. 查看完整面试报告

## 评分说明

### 评分维度

**专业能力** (35%)
- 技术关键词使用
- 答案完整度
- 结构化表达
- 经验匹配度

**沟通表达** (30%)
- 逻辑性
- 表达清晰度
- 语言流畅度
- 完整性

**面试状态** (20%)
- 自信度
- 积极性
- 专业态度
- 表现力

**时间控制** (15%)
- 时间合理性
- 节奏掌握
- 简洁性

### 评分等级

- **90-100分**: 优秀
- **80-89分**: 良好
- **70-79分**: 中等
- **60-69分**: 及格
- **60分以下**: 需要提升

## 管理命令

### 启动服务

```bash
./deploy.sh start
```

### 停止服务

```bash
./deploy.sh stop
```

### 重启服务

```bash
./deploy.sh restart
```

### 查看状态

```bash
./deploy.sh status
```

### 查看日志

```bash
./deploy.sh logs
```

### 清理资源

```bash
./deploy.sh cleanup
```

## 常见问题

### Q1: 端口被占用怎么办?

修改`docker-compose.yml`中的端口映射:

```yaml
services:
  frontend:
    ports:
      - "3001:80"  # 修改前端端口
  backend:
    ports:
      - "8001:8000"  # 修改后端端口
```

### Q2: 如何修改JWT密钥?

编辑`.env`文件:

```bash
SECRET_KEY=your-new-secret-key
```

然后重启服务:

```bash
./deploy.sh restart
```

### Q3: 如何备份数据?

```bash
# 备份数据库
cp data/database.db backups/database-$(date +%Y%m%d).db
```

### Q4: 如何配置LLM API?

编辑`.env`文件:

```bash
LLM_PROVIDER=qwen  # 或 openai, anthropic
LLM_API_KEY=your-api-key
LLM_MODEL_NAME=qwen-turbo
```

### Q5: 如何配置语音识别?

编辑`.env`文件:

```bash
SPEECH_PROVIDER=aliyun  # 或 tencent
SPEECH_API_KEY=your-api-key
```

## 技术支持

- **完整文档**: 查看 `/DEPLOYMENT.md`
- **实施报告**: 查看 `/TASK_7-12_COMPLETION_REPORT.md`
- **API文档**: http://localhost:8000/docs
- **健康检查**:
  - 后端: http://localhost:8000/health
  - 前端: http://localhost:3000/health
  - Nginx: http://localhost/health

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ 内存
- 5GB+ 磁盘空间

## 下一步

1. **配置API密钥**: 编辑`.env`文件,添加LLM和语音识别API密钥
2. **创建面试配置**: 登录系统创建第一个面试配置
3. **开始练习**: 进行模拟面试练习
4. **查看报告**: 分析评分和改进建议
5. **持续提升**: 根据建议改进面试技巧

祝你面试成功! 🎉
