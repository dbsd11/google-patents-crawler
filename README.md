# Google Patents Crawler MCP Server

一个基于 MCP (Model Context Protocol) 的 Google 专利搜索服务器，支持通过关键字搜索专利信息并返回结构化数据。

## 功能特性

- 🔍 **智能搜索**: 支持关键字搜索 Google Patents
- 📄 **分页支持**: 可配置每页结果数量和页码
- 🔄 **排序选项**: 支持按相关性或时间排序
- 🌐 **多传输方式**: 支持 stdio、SSE、WebSocket 三种传输方式
- 📊 **结构化数据**: 返回标题、专利号、发明人、申请人等完整信息
- 🚀 **异步处理**: 基于异步架构，性能优异

## MCP 配置方式

### 1. Claude Desktop 配置

在 Claude Desktop 的配置文件中添加以下配置：

**位置**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "google-patents-crawler": {
      "command": "python",
      "args": ["/Users/lvzhongqin/src/google-patents-crawler/start_mcp_server.py", "--transport", "stdio"],
      "env": {
        "PYTHONPATH": "/Users/lvzhongqin/src/google-patents-crawler"
      }
    }
  }
}
```

### 2. 通用 MCP 配置格式

```json
{
  "mcpServers": {
    "server_name": {
      "url": "server_url",
      "transport": "sse" | "stdio" | "websocket"
    }
  }
}
```

### 3. 不同传输方式的配置示例

#### stdio 传输 (推荐)
```json
{
  "mcpServers": {
    "google-patents-crawler": {
      "command": "python",
      "args": ["/path/to/start_mcp_server.py", "--transport", "stdio"],
      "transport": "stdio"
    }
  }
}
```

#### SSE 传输
```json
{
  "mcpServers": {
    "google-patents-crawler-sse": {
      "url": "http://localhost:8080",
      "transport": "sse"
    }
  }
}
```

#### WebSocket 传输
```json
{
  "mcpServers": {
    "google-patents-crawler-websocket": {
      "url": "ws://localhost:8081", 
      "transport": "websocket"
    }
  }
}
```

## 安装依赖

```bash
pip install -r requirements.txt
```

### 环境要求

1. **Python 3.8+**
2. **ChromeDriver**: 用于浏览器自动化
   ```bash
   # macOS (使用 Homebrew)
   brew install chromedriver
   
   # 或者手动下载并配置 PATH
   # https://chromedriver.chromium.org/
   ```

## 启动服务器

### 使用启动脚本 (推荐)

```bash
# stdio 传输 (默认)
python start_mcp_server.py

# SSE 传输
python start_mcp_server.py --transport sse --port 8080

# WebSocket 传输  
python start_mcp_server.py --transport websocket --port 8081

# 调试模式
python start_mcp_server.py --debug
```

### 直接运行服务器

```bash
python mcp_server.py
```

## 使用方法

### search_patents 工具

搜索 Google Patents 并返回专利信息。

**参数**:
- `query` (必需): 搜索关键字
- `page_size` (可选): 每页结果数量，默认 10，范围 1-100
- `page` (可选): 页码，默认 0 (第一页)
- `sort` (可选): 排序方式
  - `"relevance"`: 按相关性排序 (默认)
  - `"new"`: 按时间排序 (最新优先)

**返回结构**:
```json
[
  {
    "title": "专利标题",
    "patent_number": "专利号",
    "inventor": "发明人",
    "assignee": "申请人/受让人", 
    "dates": "相关日期信息",
    "abstract": "专利摘要",
    "pdf_link": "PDF链接 (如果有)"
  }
]
```

### 使用示例

```python
# 基本搜索
result = await search_patents("人工智能")

# 分页搜索
result = await search_patents("机器学习", page_size=20, page=1)

# 按时间排序
result = await search_patents("深度学习", sort="new")

# 复合参数
result = await search_patents("智能制造", page_size=15, page=2, sort="new")
```

## 项目结构

```
google-patents-crawler/
├── mcp_server.py                 # MCP 服务器主文件
├── start_mcp_server.py          # 服务器启动脚本
├── requirements.txt             # Python 依赖
├── README.md                   # 项目文档
├── mcp_config.json             # MCP 配置示例
├── claude_desktop_config.json  # Claude Desktop 配置示例
├── test_mcp_server.py          # 测试脚本
├── common/
│   └── tools/
│       └── browser/
│           └── browser.py      # 浏览器工具
└── logger/
    └── __init__.py            # 日志配置
```

## 技术架构

- **MCP 协议**: 基于 Model Context Protocol 1.0+
- **浏览器自动化**: Selenium + Chrome WebDriver
- **HTML 解析**: BeautifulSoup4 + lxml
- **异步处理**: Python asyncio
- **传输支持**: stdio、SSE、WebSocket

## 配置说明

### 传输方式选择

1. **stdio** (推荐)
   - 适用于大多数 MCP 客户端
   - 配置简单，性能稳定
   - 通过命令行参数启动

2. **SSE (Server-Sent Events)**
   - 适用于 Web 应用集成
   - 单向数据流，服务器推送
   - 需要 HTTP 服务器支持

3. **WebSocket**
   - 适用于实时双向通信
   - 低延迟，高性能
   - 需要 WebSocket 服务器支持

### 环境变量

可以通过环境变量配置服务器行为：

```bash
export PYTHONPATH="/path/to/google-patents-crawler"
export CHROMEDRIVER_PATH="/path/to/chromedriver"
export MCP_SERVER_PORT="8080"
```

## 注意事项

1. **ChromeDriver 版本**: 确保 ChromeDriver 版本与系统 Chrome 浏览器版本兼容
2. **网络连接**: 需要稳定的网络连接访问 Google Patents
3. **请求频率**: 建议控制请求频率，避免被反爬虫机制限制
4. **内存使用**: 大量搜索时注意内存使用情况

## 故障排除

### 常见问题

1. **ChromeDriver 错误**
   ```bash
   # 检查 ChromeDriver 是否安装
   which chromedriver
   
   # 安装 ChromeDriver (macOS)
   brew install chromedriver
   ```

2. **依赖缺失**
   ```bash
   pip install -r requirements.txt
   ```

3. **权限问题**
   ```bash
   chmod +x start_mcp_server.py
   ```

4. **端口占用**
   ```bash
   # 检查端口使用情况
   lsof -i :8080
   
   # 使用不同端口
   python start_mcp_server.py --transport sse --port 8081
   ```

### 调试模式

启用调试模式获取详细日志：

```bash
python start_mcp_server.py --debug
```

## 开发说明

### 测试

运行测试脚本验证功能：

```bash
python test_mcp_server.py
```

### 扩展功能

可以通过修改 `mcp_server.py` 添加新的工具和功能：

1. 在 `list_tools()` 中添加新工具定义
2. 在 `call_tool()` 中添加新工具的处理逻辑
3. 实现具体的功能函数

### 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 许可证

MIT License