# OpenCode OpenAI 代理

为 [OpenCode](https://opencode.ai) 提供 OpenAI 兼容的 API 代理，让你可以使用 OpenCode 的免费模型（如 `mimo-v2-pro-free`）配合任何 OpenAI 兼容的客户端。

**🎉 完全免费 | 无需 API Key | 开箱即用**

[English](README.md) | 简体中文

## 特性

- ✅ **完全免费** - 使用 OpenCode 免费模型，无需任何 API key，真正的零成本
- ✅ **OpenAI 兼容 API** - 完全兼容 OpenAI API，无缝替换现有代码
- ✅ **开机自启** - 支持 macOS LaunchAgent，开机自动启动
- ✅ **自动启动 OpenCode** - 如果 OpenCode Desktop 未运行，自动启动
- ✅ **会话缓存** - 复用会话实现多轮对话
- ✅ **流式支持** - 实时 SSE 流式响应
- ✅ **Token 计数** - 通过 tiktoken 精确统计 token 使用量
- ✅ **生产就绪** - 并发限制、错误处理、健康检查
- ✅ **配额重置** - 内置 project.id 重置工具，绕过免费配额限制

## 快速开始

### 前置要求

- Python 3.10+
- 已安装 [OpenCode CLI](https://opencode.ai)（`npm install -g opencode-ai`）

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/opencode-openai-proxy.git
cd opencode-openai-proxy

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 使用

#### 方式 1：手动启动

```bash
# 启动代理（如果需要会自动启动 OpenCode Desktop）
./start.sh

# 或直接运行
python opencode_openai_proxy_v2.py
```

#### 方式 2：开机自启（推荐 - macOS）

```bash
# 安装 LaunchAgent（仅需一次）
cp com.opencode.proxy.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.opencode.proxy.plist

# 管理服务
launchctl unload ~/Library/LaunchAgents/com.opencode.proxy.plist  # 停止
launchctl load ~/Library/LaunchAgents/com.opencode.proxy.plist    # 启动
```

代理将在 `http://localhost:8000` 启动，并自动：
1. 检查 OpenCode Desktop 是否运行
2. 如果未运行则启动 OpenCode Desktop
3. 等待其就绪
4. 开始接受请求

**💡 提示：开机自启模式下，服务会在崩溃时自动重启，无需手动干预。**

### 配置

环境变量（可选）：

```bash
export OPENCODE_URL="http://localhost:8888"  # OpenCode Desktop URL
export OPENCODE_USERNAME="opencode"          # Basic auth 用户名（如需要）
export OPENCODE_PASSWORD=""                  # Basic auth 密码（如需要）
export PORT="8000"                           # 代理端口
```

## API 使用

### Python (OpenAI SDK)

```python
from openai import OpenAI

# 🎉 无需 API Key！随便填一个字符串即可
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # 任意字符串，完全免费
)
)

# 流式响应
stream = client.chat.completions.create(
    model="opencode/mimo-v2-pro-free",
    messages=[{"role": "user", "content": "你好！"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# 非流式响应
response = client.chat.completions.create(
    model="opencode/mimo-v2-pro-free",
    messages=[{"role": "user", "content": "2+2等于几？"}],
    stream=False
)

print(response.choices[0].message.content)
```

### cURL

```bash
# 流式响应
curl -N http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "opencode/mimo-v2-pro-free",
    "messages": [{"role": "user", "content": "你好！"}],
    "stream": true
  }'

# 非流式响应
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "opencode/mimo-v2-pro-free",
    "messages": [{"role": "user", "content": "2+2等于几？"}],
    "stream": false
  }'
```

### 会话连续性

使用 `X-Session-Id` 请求头保持对话上下文：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: my-conversation" \
  -d '{
    "model": "opencode/mimo-v2-pro-free",
    "messages": [{"role": "user", "content": "记住：我叫小明"}]
  }'

# 稍后，在同一对话中
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: my-conversation" \
  -d '{
    "model": "opencode/mimo-v2-pro-free",
    "messages": [{"role": "user", "content": "我叫什么名字？"}]
  }'
```

## 可用模型

代理支持所有 OpenCode 模型。列出可用模型：

```bash
curl http://localhost:8000/v1/models
```

### 免费模型（无需 API Key）

| 模型 ID | 名称 | 上下文 | 最大输出 | 视觉 | 推理 |
|---------|------|--------|----------|------|------|
| `opencode/mimo-v2-pro-free` | MiMo V2 Pro Free | 1.0M | 64K | ❌ | ✅ |
| `opencode/nemotron-3-super-free` | Nemotron 3 Super Free | 1M | 128K | ❌ | ✅ |
| `opencode/gpt-5-nano` | GPT-5 Nano | 400K | 128K | ✅ | ✅ |
| `opencode/mimo-v2-omni-free` | MiMo V2 Omni Free | 262.1K | 64K | ✅ | ✅ |
| `opencode/minimax-m2.5-free` | MiniMax M2.5 Free | 204.8K | 131.1K | ❌ | ✅ |
| `opencode/big-pickle` | Big Pickle | 200K | 128K | ❌ | ✅ |

> 所有模型均支持工具调用。模型由 [OpenCode Zen](https://opencode.ai) 提供，可能随时更新。
> ⚠️ = 预览/暂不可用

## 健康检查

```bash
curl http://localhost:8000/health
```

响应：
```json
{
  "status": "healthy",
  "opencode": "connected",
  "cache": 5
}
```

## 架构

```
OpenAI 客户端
    ↓ (HTTP)
OpenCode 代理 (Python FastAPI)
    ↓ (HTTP REST API)
OpenCode Desktop (localhost:8888)
    ↓ (AI 提供商 API)
OpenCode Zen / OpenAI / Anthropic / 等
```

## 配置选项

编辑 `opencode_openai_proxy_v2.py` 自定义：

- `PORT` - 代理监听端口（默认：8000）
- `OPENCODE_URL` - OpenCode Desktop URL（默认：http://localhost:8888）
- `SESSION_CACHE_SIZE` - 最大缓存会话数（默认：128）
- `SESSION_TTL_SEC` - 会话 TTL 秒数（默认：3600）
- `MAX_CONCURRENT` - 最大并发请求数（默认：20）

## 故障排除

### OpenCode Desktop 无法启动

如果自动启动失败，手动启动 OpenCode：

```bash
opencode serve --port 8888
```

### 连接被拒绝

检查 OpenCode Desktop 是否运行：

```bash
curl http://localhost:8888/global/health
```

### 会话错误

重启代理清除会话缓存。

## 开发

### 运行测试

```bash
# 测试流式响应
curl -N http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "opencode/mimo-v2-pro-free", "messages": [{"role": "user", "content": "测试"}], "stream": true}'

# 测试非流式响应
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "opencode/mimo-v2-pro-free", "messages": [{"role": "user", "content": "测试"}], "stream": false}'
```

### 日志

日志写入同目录下的 `proxy.log` 文件。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- [OpenCode](https://opencode.ai) - AI 编码助手
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架
- [tiktoken](https://github.com/openai/tiktoken) - Token 计数

## 支持

- GitHub Issues: [报告 bug 或请求功能](https://github.com/yourusername/opencode-openai-proxy/issues)
- OpenCode Discord: [加入社区](https://discord.gg/opencode)

---

**注意**：这是一个非官方代理。OpenCode 是其各自所有者的商标。

## 配额重置工具

OpenCode 通过本地数据库中的 `project.id` 追踪免费配额。当提示"免费余额用完，需要等待 XX 小时"时，可以使用重置工具绕过限制。

### 使用方法

```bash
# 重置 project.id（会自动备份数据库）
python3 reset_project_id.py

# 重启 opencode 后会生成新的 project.id
```

### 工作原理

1. 自动备份 `~/.local/share/opencode/opencode.db`（带时间戳）
2. 删除 `project` 表中的 `global` 记录
3. 下次启动 opencode 时自动生成新的 project.id
4. 服务端无法识别新 ID，配额重新计算

### 注意事项

- ✅ 会保留所有会话历史和配置
- ✅ 仅删除 project 标识符
- ✅ 自动创建带时间戳的备份文件
- ⚠️ 可能违反 OpenCode 服务条款
- ⚠️ 仅供学习研究使用

### 恢复备份

如果需要恢复到重置前的状态：

```bash
# 查看备份文件
ls -lh ~/.local/share/opencode/opencode.db.backup_*

# 恢复指定备份
cp ~/.local/share/opencode/opencode.db.backup_20260328_140000 ~/.local/share/opencode/opencode.db
```

