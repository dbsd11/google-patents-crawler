# Google Patents MCP Server 部署指南

## GitHub Actions 自动化部署

本项目使用 GitHub Actions 进行自动化 Docker 镜像构建和部署。

### 必需的 Secrets 配置

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加以下 secrets：

#### Docker Registry 配置
- `DOCKER_USER`: 阿里云容器镜像服务的用户名
- `DOCKER_PASSWORD`: 阿里云容器镜像服务的密码

### Workflow 触发方式

#### 1. 手动触发 (workflow_dispatch)
- 在 GitHub Actions 页面点击 "Run workflow"
- 可选择参数：
  - **Log Level**: 日志级别 (info/warning/debug)
  - **Tags**: 镜像标签 (默认: latest)
  - **Environment**: 目标环境 (dev/staging/prod)

#### 2. 自动触发
- **Push 到 main 分支**: 构建并推送 latest 标签
- **Push 到 develop 分支**: 构建并部署到开发环境
- **Push 标签 (v*)**: 构建并部署到生产环境

### 构建流程

1. **代码检出**: 获取最新代码
2. **环境准备**: 设置 Python 3.11 环境
3. **依赖安装**: 安装项目依赖包
4. **测试运行**: 执行单元测试 (可选)
5. **Docker 构建**: 构建多架构镜像 (linux/amd64, linux/arm64)
6. **镜像测试**: 启动容器进行健康检查
7. **镜像推送**: 推送到阿里云容器镜像服务
8. **环境部署**: 根据分支/标签部署到对应环境

### 镜像标签策略

- `latest`: main 分支的最新构建
- `develop`: develop 分支的最新构建
- `v1.0.0`: 版本标签构建
- `pr-123`: Pull Request 构建
- 自定义标签: 手动触发时指定

### 部署环境

#### 开发环境 (Development)
- 触发条件: develop 分支推送或手动选择 dev 环境
- 镜像标签: `latest` 或 `develop`

#### 生产环境 (Production)
- 触发条件: 版本标签推送 (v*) 或手动选择 prod 环境
- 镜像标签: 对应的版本号

### 本地测试

在推送代码前，建议先在本地测试：

```bash
# 构建镜像
docker build -t google-patents-mcp:local .

# 测试 SSE 服务
docker run -d -p 18080:18080 --name test-sse google-patents-mcp:local

# 测试 WebSocket 服务
docker run -d -p 28080:28080 --name test-ws google-patents-mcp:local \
  python start_mcp_server.py --transport websocket --host 0.0.0.0 --port 28080

# 健康检查
curl -f http://localhost:18080/sse

# 清理
docker stop test-sse test-ws
docker rm test-sse test-ws
```

### 使用 docker-compose 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 故障排除

#### 1. Docker 登录失败
- 检查 `DOCKER_USER` 和 `DOCKER_PASSWORD` secrets 是否正确配置
- 确认阿里云容器镜像服务账号权限

#### 2. 镜像构建失败
- 检查 Dockerfile 语法
- 确认依赖包版本兼容性
- 查看构建日志中的错误信息

#### 3. 健康检查失败
- 确认应用启动时间是否足够
- 检查端口映射是否正确
- 验证健康检查端点是否可访问

#### 4. 部署失败
- 检查目标环境的网络连接
- 确认部署脚本权限
- 验证环境变量配置

### 监控和日志

- GitHub Actions 提供详细的构建日志
- 可以在 Actions 页面查看每个步骤的执行情况
- 失败时会收到邮件通知 (如果启用)

### 安全注意事项

- 不要在代码中硬编码敏感信息
- 使用 GitHub Secrets 管理凭据
- 定期更新依赖包版本
- 启用 Dependabot 安全更新