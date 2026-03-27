# OpenCode OpenAI Proxy

OpenAI-compatible API proxy for [OpenCode](https://opencode.ai), enabling you to use OpenCode's free models (like `mimo-v2-pro-free`) with any OpenAI-compatible client.

English | [简体中文](README.zh-CN.md)

## Features

- ✅ **OpenAI-compatible API** - Drop-in replacement for OpenAI API
- ✅ **Auto-start OpenCode** - Automatically starts OpenCode Desktop if not running
- ✅ **Session caching** - Reuses sessions for multi-turn conversations
- ✅ **Streaming support** - Real-time SSE streaming responses
- ✅ **Token counting** - Accurate token usage via tiktoken
- ✅ **Free models** - Use OpenCode's free models without API keys
- ✅ **Production ready** - Concurrency limiting, error handling, health checks

## Quick Start

### Prerequisites

- Python 3.10+
- [OpenCode CLI](https://opencode.ai) installed (`npm install -g opencode-ai`)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/opencode-openai-proxy.git
cd opencode-openai-proxy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Start the proxy (will auto-start OpenCode Desktop if needed)
./start.sh

# Or run directly
python opencode_openai_proxy_v2.py
```

The proxy will start on `http://localhost:8000` and automatically:
1. Check if OpenCode Desktop is running
2. Start OpenCode Desktop if not running
3. Wait for it to be ready
4. Start accepting requests

### Configuration

Environment variables (optional):

```bash
export OPENCODE_URL="http://localhost:8888"  # OpenCode Desktop URL
export OPENCODE_USERNAME="opencode"          # Basic auth username (if needed)
export OPENCODE_PASSWORD=""                  # Basic auth password (if needed)
export PORT="8000"                           # Proxy port
```

## API Usage

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # Any string works
)

# Streaming
stream = client.chat.completions.create(
    model="opencode/mimo-v2-pro-free",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# Non-streaming
response = client.chat.completions.create(
    model="opencode/mimo-v2-pro-free",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    stream=False
)

print(response.choices[0].message.content)
```

### cURL

```bash
# Streaming
curl -N http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "opencode/mimo-v2-pro-free",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'

# Non-streaming
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "opencode/mimo-v2-pro-free",
    "messages": [{"role": "user", "content": "What is 2+2?"}],
    "stream": false
  }'
```

### Session Continuity

Use the `X-Session-Id` header to maintain conversation context:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: my-conversation" \
  -d '{
    "model": "opencode/mimo-v2-pro-free",
    "messages": [{"role": "user", "content": "Remember this: my name is Alice"}]
  }'

# Later, in the same conversation
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: my-conversation" \
  -d '{
    "model": "opencode/mimo-v2-pro-free",
    "messages": [{"role": "user", "content": "What is my name?"}]
  }'
```

## Available Models

The proxy supports all OpenCode models. To list available models:

```bash
curl http://localhost:8000/v1/models
```

### Free Models (No API Key Required)

| Model ID | Name | Context | Max Output | Vision | Reasoning |
|----------|------|---------|------------|--------|-----------|
| `opencode/mimo-v2-pro-free` | MiMo V2 Pro Free | 1M | 64K | ❌ | ✅ |
| `opencode/nemotron-3-super-free` | Nemotron 3 Super Free | 1M | 128K | ❌ | ✅ |
| `opencode/gpt-5-nano` | GPT-5 Nano | 400K | 128K | ✅ | ✅ |
| `opencode/mimo-v2-omni-free` | MiMo V2 Omni Free | 262K | 64K | ✅ | ✅ |
| `opencode/minimax-m2.5-free` | MiniMax M2.5 Free | 204K | 131K | ❌ | ✅ |
| `opencode/big-pickle` | Big Pickle | 200K | 128K | ❌ | ✅ |

> All models support tool calling. Models are provided by [OpenCode Zen](https://opencode.ai) and are subject to change.

## Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "opencode": "connected",
  "cache": 5
}
```

## Architecture

```
OpenAI Client
    ↓ (HTTP)
OpenCode Proxy (Python FastAPI)
    ↓ (HTTP REST API)
OpenCode Desktop (localhost:8888)
    ↓ (AI Provider APIs)
OpenCode Zen / OpenAI / Anthropic / etc.
```

## Configuration Options

Edit `opencode_openai_proxy_v2.py` to customize:

- `PORT` - Proxy listening port (default: 8000)
- `OPENCODE_URL` - OpenCode Desktop URL (default: http://localhost:8888)
- `SESSION_CACHE_SIZE` - Max cached sessions (default: 128)
- `SESSION_TTL_SEC` - Session TTL in seconds (default: 3600)
- `MAX_CONCURRENT` - Max concurrent requests (default: 20)

## Troubleshooting

### OpenCode Desktop not starting

If auto-start fails, manually start OpenCode:

```bash
opencode serve --port 8888
```

### Connection refused

Check if OpenCode Desktop is running:

```bash
curl http://localhost:8888/global/health
```

### Session errors

Clear the session cache by restarting the proxy.

## Development

### Running tests

```bash
# Test streaming
curl -N http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "opencode/mimo-v2-pro-free", "messages": [{"role": "user", "content": "Test"}], "stream": true}'

# Test non-streaming
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "opencode/mimo-v2-pro-free", "messages": [{"role": "user", "content": "Test"}], "stream": false}'
```

### Logs

Logs are written to `proxy.log` in the same directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenCode](https://opencode.ai) - The AI coding assistant
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [tiktoken](https://github.com/openai/tiktoken) - Token counting

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/yourusername/opencode-openai-proxy/issues)
- OpenCode Discord: [Join the community](https://discord.gg/opencode)

---

**Note**: This is an unofficial proxy. OpenCode is a trademark of its respective owners.
