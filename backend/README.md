# Oblivionis Backend

基于 FastAPI 的笔记应用后端服务。

## 功能特性

- 用户管理（创建、查询用户）
- 笔记管理（CRUD 操作）
- SQLite 数据库存储
- RESTful API 设计
- 自动数据库表创建
- CORS 跨域支持

## 技术栈

- **FastAPI**: 现代、高性能的 Web 框架
- **SQLAlchemy**: ORM 数据库操作
- **SQLite**: 轻量级数据库
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI 服务器

## 快速开始

### Windows

```bash
cd backend
setup_backend.bat
```

### Linux/macOS

```bash
cd backend
chmod +x setup_backend.sh
./setup_backend.sh
```

## API 端点

### 基础信息
- `GET /` - 根路径，显示 API 信息
- `GET /health` - 健康检查
- `GET /api/stats` - 系统统计信息

### 用户管理
- `POST /api/users/` - 创建用户
- `GET /api/users/` - 获取用户列表
- `GET /api/users/{user_id}` - 获取特定用户

### 笔记管理
- `POST /api/notes/` - 创建笔记
- `GET /api/notes/` - 获取笔记列表（可按用户ID筛选）
- `GET /api/notes/{note_id}` - 获取特定笔记
- `PUT /api/notes/{note_id}` - 更新笔记
- `DELETE /api/notes/{note_id}` - 删除笔记（软删除）

## 数据库

数据库文件将自动创建在 `../data/oblivionis.db`

### 数据表结构

**users 表:**
- id (主键)
- username (用户名，唯一)
- email (邮箱，唯一)
- hashed_password (密码哈希)
- is_active (是否激活)
- created_at (创建时间)
- updated_at (更新时间)

**notes 表:**
- id (主键)
- title (标题)
- content (内容)
- user_id (用户ID)
- is_deleted (是否删除)
- created_at (创建时间)
- updated_at (更新时间)

## 开发说明

- 服务运行在 `http://localhost:8000`
- API 文档访问: `http://localhost:8000/docs` (Swagger UI)
- 替代文档: `http://localhost:8000/redoc`
- 数据库文件路径: `../data/oblivionis.db`

## 注意事项

⚠️ **安全提醒**: 当前版本为开发版本，密码未进行哈希处理。生产环境请：
1. 修改 `.env` 文件中的 `SECRET_KEY`
2. 实现密码哈希功能
3. 添加 JWT 认证
4. 配置 HTTPS

## 环境变量

可以在 `.env` 文件中配置以下变量：
- `DATABASE_URL`: 数据库连接字符串
- `SECRET_KEY`: 密钥（生产环境必须修改）
- `DEBUG`: 调试模式
- `ALLOWED_ORIGINS`: 允许的跨域来源
