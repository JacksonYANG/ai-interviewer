# 数据库迁移和模型文档

## 概述

本项目使用SQLAlchemy ORM和Alembic进行数据库管理。所有数据模型都已实现，并配置了完整的迁移系统。

## 数据库表

### 用户认证相关表

1. **users** - 用户表
   - 用户基本信息、认证信息
   - 支持邀请码关联和推荐关系

2. **invitation_codes** - 邀请码表
   - 支持一次性、限量、无限三种类型
   - 可设置过期时间和使用次数限制

3. **email_verifications** - 邮箱验证表
   - 存储邮箱验证令牌

4. **login_logs** - 登录日志表
   - 记录用户登录历史和安全信息

5. **refresh_tokens** - 刷新令牌表
   - JWT刷新令牌管理
   - 支持设备信息记录

### 用户资料相关表

6. **user_profiles** - 用户画像表
   - 用户求职信息和偏好设置

7. **resumes** - 简历表
   - 用户上传的简历文件

### 面试配置相关表

8. **interview_configs** - 面试配置表
   - 职位信息、公司信息
   - AI建议轮数和实际轮数

9. **interview_rounds** - 面试轮次配置表
   - 每轮的面试官角色和问题数量

### 面试数据相关表

10. **interview_sessions** - 面试会话表
    - 面试进行状态和总体评分

11. **questions** - 问题表
    - 每轮的面试问题

12. **answers** - 回答表
    - 用户的回答文本和音频

13. **scores** - 评分表
    - 每个问题的多维度评分

14. **round_summaries** - 轮次总结表
    - 每轮面试的总结和反馈

### 文件和报告相关表

15. **audio_files** - 音频文件表
    - 面试录音文件记录

16. **reports** - 面试报告表
    - 完整的面试分析报告

## 使用方法

### 1. 初始化数据库

使用初始化脚本创建所有表并插入初始数据：

```bash
# 创建数据库表和初始数据
python scripts/init_db.py init

# 重置数据库（删除所有表并重新创建）
python scripts/init_db.py reset

# 删除所有表（危险操作）
python scripts/init_db.py drop
```

### 2. 使用Alembic迁移

```bash
# 查看当前迁移状态
python -m alembic current

# 查看迁移历史
python -m alembic history

# 升级到最新版本
python -m alembic upgrade head

# 降级一个版本
python -m alembic downgrade -1

# 创建新的迁移
python -m alembic revision --autogenerate -m "迁移描述"
```

### 3. 测试模型

运行测试脚本验证所有模型是否正常工作：

```bash
python scripts/test_models.py
```

## 默认数据

### 管理员账户

- 用户名: `admin`
- 密码: `Admin123!`
- 邮箱: `admin@ai-interviewer.com`
- 角色: `admin`

### 测试邀请码

1. **BETA-TEST-001**
   - 类型: limited（限量）
   - 最大使用次数: 10
   - 说明: 内测阶段邀请码

2. **BETA-TEST-002**
   - 类型: unlimited（无限）
   - 最大使用次数: 999
   - 说明: 内测阶段无限使用邀请码

## 模型关系

### 用户认证关系

```
users → user_profiles (1:1)
users → resumes (1:N)
users → invitation_codes (N:1, 通过invitation_code_id)
users → users (自关联, 通过referred_by)
```

### 面试配置关系

```
users → interview_configs (1:N)
interview_configs → interview_rounds (1:N)
```

### 面试执行关系

```
interview_configs → interview_sessions (1:N)
interview_sessions → questions (1:N)
questions → answers (1:1)
questions → scores (1:1)
interview_sessions → round_summaries (1:N)
interview_sessions → audio_files (1:N)
interview_sessions → reports (1:1)
```

## 注意事项

### 循环依赖问题

User和InvitationCode之间存在外键相互引用，已通过以下方式解决：

1. 所有外键字段设置为`nullable=True`
2. 使用`foreign_keys`参数明确指定外键字段
3. 避免在relationship中使用`back_populates`导致的循环引用

### 级联删除

以下表配置了CASCADE删除：

- `interview_sessions` 删除时会级联删除：
  - `questions`
  - `answers`
  - `scores`
  - `round_summaries`
  - `audio_files`
  - `reports`

- `questions` 删除时会级联删除：
  - `answers`
  - `scores`

## 数据库迁移最佳实践

1. **修改模型后**：运行`alembic revision --autogenerate -m "描述"`
2. **检查迁移文件**：确保生成的迁移文件正确
3. **测试迁移**：在开发环境先测试升级和降级
4. **版本控制**：将迁移文件提交到Git
5. **团队协作**：确保所有成员保持迁移同步

## 故障排除

### 问题：迁移时出现循环依赖警告

```bash
# 解决方案：这是正常的，只要迁移成功即可忽略
# 或者修改模型关系，避免循环依赖
```

### 问题：数据库文件被锁定

```bash
# 解决方案：确保没有其他进程正在使用数据库
# 或者使用不同的数据库文件名
```

### 问题：迁移失败

```bash
# 解决方案：检查当前迁移状态
python -m alembic current

# 降级到上一个版本
python -m alembic downgrade -1

# 修复问题后重新升级
python -m alembic upgrade head
```

## 后续工作

1. 根据实际需求调整模型字段
2. 添加更多的索引以优化查询性能
3. 实现数据验证和业务逻辑
4. 添加数据库备份策略
5. 准备从SQLite迁移到PostgreSQL的方案
