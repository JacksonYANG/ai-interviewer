# 前端Dockerfile - 多阶段构建优化版本

# 构建阶段
FROM node:20-alpine as build

WORKDIR /app

# 设置npm镜像源(可选,加速国内构建)
# RUN npm config set registry https://registry.npmmirror.com

# 复制package文件
COPY package*.json ./

# 安装所有依赖(包括devDependencies,构建需要)
RUN npm install

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
