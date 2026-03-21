# AI面试官系统 - 部署指南

## 系统架构

本系统采用前后端分离架构,通过Docker容器化部署:

- **前端**: React + Vite + Ant Design
- **后端**: FastAPI + SQLAlchemy + SQLite
- **反向代理**: Nginx
- **容器编排**: Docker Compose

## 快速开始

### 1. 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB可用内存
- 至少5GB可用磁盘空间

### 2. 一键部署

```bash
# 克隆项目
git clone <repository-url>
cd wife_job_hunting

# 运行部署脚本
./deploy.sh install
```

部署脚本会自动:
1. 检查Docker环境
2. 创建必要的目录
3. 生成环境配置文件
4. 构建Docker镜像
5. 启动所有服务

### 3. 访问应用

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **Nginx入口**: http://localhost
- **API文档**: http://localhost:8000/docs

## 手动部署

如果需要手动部署,请按以下步骤操作:

### 1. 准备环境变量

创建 `.env` 文件:

```bash
# 数据库配置
DATABASE_URL=sqlite:///data/database.db

# JWT密钥 (生产环境请修改)
SECRET_KEY=your-secret-key-change-this-in-production

# Token过期时间
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM配置 (可选)
LLM_PROVIDER=qwen
LLM_API_KEY=your-api-key-here
LLM_MODEL_NAME=qwen-turbo

# 语音识别配置 (可选)
SPEECH_PROVIDER=aliyun
SPEECH_API_KEY=your-speech-api-key-here
```

### 2. 构建镜像

```bash
# 构建后端镜像
cd ai-interviewer-backend
docker build -t ai-interviewer-backend .

# 构建前端镜像
cd ../ai-interviewer-frontend
docker build -t ai-interviewer-frontend .
```

### 3. 启动服务

```bash
# 返回项目根目录
cd ..

# 启动所有服务
docker-compose up -d
```

### 4. 查看服务状态

```bash
docker-compose ps

# 查看日志
docker-compose logs -f

# 检查健康状态
curl http://localhost:8000/health  # 后端
curl http://localhost:3000/health  # 前端
curl http://localhost/health       # Nginx
```

## 服务管理

### 启动服务

```bash
# 使用部署脚本
./deploy.sh start

# 或使用docker-compose
docker-compose up -d
```

### 停止服务

```bash
# 使用部署脚本
./deploy.sh stop

# 或使用docker-compose
docker-compose down
```

### 重启服务

```bash
# 使用部署脚本
./deploy.sh restart

# 或使用docker-compose
docker-compose restart
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### 更新服务

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose up -d
```

## 数据备份

### 备份数据库

```bash
# 备份SQLite数据库
cp data/database.db backups/database-$(date +%Y%m%d-%H%M%S).db
```

### 恢复数据库

```bash
# 停止服务
docker-compose down

# 恢复数据库
cp backups/database-20240321-120000.db data/database.db

# 启动服务
docker-compose up -d
```

## 性能优化

### 1. 数据库优化

```bash
# 对于生产环境,建议使用PostgreSQL替代SQLite
# 修改.env文件:
DATABASE_URL=postgresql://user:password@localhost:5432/interviewer
```

### 2. Nginx优化

编辑 `nginx.conf`:

```nginx
# 增加worker连接数
events {
    worker_connections 2048;
}

# 启用缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;
```

### 3. 后端优化

编辑 `ai-interviewer-backend/Dockerfile`:

```dockerfile
# 使用多阶段构建减小镜像大小
# 使用uvicorn多worker模式
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 安全加固

### 1. 修改默认密钥

```bash
# 生成新的SECRET_KEY
openssl rand -hex 32
```

### 2. 配置HTTPS

编辑 `nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 其他配置...
}
```

### 3. 限流配置

系统已内置限流功能,可在 `ai-interviewer-backend/app/middleware/rate_limit.py` 中调整:

```python
RATE_LIMIT_CONFIGS = {
    "POST:/api/v1/auth/login": (5, 60),  # 5次/分钟
    "default": (60, 60),                  # 60次/分钟
}
```

## 故障排查

### 1. 服务无法启动

```bash
# 查看详细日志
docker-compose logs backend

# 检查端口占用
netstat -tunlp | grep -E '3000|8000|80'
```

### 2. 数据库连接失败

```bash
# 检查数据目录权限
ls -la data/

# 重新创建数据库
docker-compose exec backend python -c "from app.database import engine; from app.models import *; Base.metadata.create_all(bind=engine)"
```

### 3. 前端无法访问后端

```bash
# 检查网络连接
docker network inspect wife_job_hunting_app-network

# 检查Nginx配置
docker-compose exec nginx nginx -t
```

## 生产环境部署

### 1. 使用PostgreSQL

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: interviewer
      POSTGRES_USER: interviewer
      POSTGRES_PASSWORD: your-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  backend:
    environment:
      - DATABASE_URL=postgresql://interviewer:your-password@postgres:5432/interviewer
    depends_on:
      - postgres
```

### 2. 使用Redis缓存

```yaml
services:
  redis:
    image: redis:alpine
    networks:
      - app-network

  backend:
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
```

### 3. 配置域名和SSL

1. 购买域名并配置DNS
2. 申请SSL证书(Let's Encrypt)
3. 更新Nginx配置
4. 配置防火墙规则

## 监控和日志

### 1. 日志收集

```bash
# 查看实时日志
docker-compose logs -f --tail=100

# 导出日志
docker-compose logs > logs-$(date +%Y%m%d).txt
```

### 2. 性能监控

建议使用以下工具:
- Prometheus + Grafana
- Docker Stats
- Nginx Log Analysis

## 升级指南

```bash
# 1. 备份数据
cp data/database.db backups/

# 2. 停止服务
docker-compose down

# 3. 拉取最新代码
git pull origin main

# 4. 重新构建
docker-compose build

# 5. 启动服务
docker-compose up -d

# 6. 验证升级
./deploy.sh status
```

## 支持

如有问题,请查看:
- 项目文档: `/docs`
- GitHub Issues: <repository-url>/issues
- API文档: http://localhost:8000/docs
