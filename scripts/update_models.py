#!/usr/bin/env python3
"""
Update free models list in README files by querying OpenCode API.
Used by GitHub Actions to keep documentation up to date.
"""

import json
import re
import sys
import urllib.request
import urllib.error

OPENCODE_URL = "http://localhost:8888"


def fetch_free_models():
    try:
        req = urllib.request.Request(f"{OPENCODE_URL}/provider")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"❌ Failed to connect to OpenCode Desktop: {e}")
        print("   Make sure OpenCode Desktop is running on port 8888")
        sys.exit(1)

    free_models = []
    for provider in data.get("all", []):
        if provider.get("id") != "opencode":
            continue
        for model_id, model in (provider.get("models") or {}).items():
            cost = model.get("cost", {})
            if cost.get("input", 1) == 0 and cost.get("output", 1) == 0:
                caps = model.get("capabilities", {})
                inp = caps.get("input", {})
                free_models.append({
                    "id": f"opencode/{model_id}",
                    "name": model.get("name", model_id),
                    "context": model.get("limit", {}).get("context", 0),
                    "output": model.get("limit", {}).get("output", 0),
                    "vision": inp.get("image", False) or inp.get("video", False),
                    "reasoning": caps.get("reasoning", False),
                    "toolcall": caps.get("toolcall", False),
                })

    # Sort by context window size descending
    free_models.sort(key=lambda x: x["context"], reverse=True)
    return free_models


def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n // 1_000_000}M"
    if n >= 1_000:
        return f"{n // 1_000}K"
    return str(n)


def build_en_table(models):
    lines = [
        "| Model ID | Name | Context | Max Output | Vision | Reasoning |",
        "|----------|------|---------|------------|--------|-----------|",
    ]
    for m in models:
        lines.append(
            f"| `{m['id']}` | {m['name']} | {fmt_tokens(m['context'])} "
            f"| {fmt_tokens(m['output'])} | {'✅' if m['vision'] else '❌'} "
            f"| {'✅' if m['reasoning'] else '❌'} |"
        )
    lines.append("")
    lines.append("> All models support tool calling. Models are provided by [OpenCode Zen](https://opencode.ai) and are subject to change.")
    return "\n".join(lines)


def build_zh_table(models):
    lines = [
        "| 模型 ID | 名称 | 上下文 | 最大输出 | 视觉 | 推理 |",
        "|---------|------|--------|----------|------|------|",
    ]
    for m in models:
        lines.append(
            f"| `{m['id']}` | {m['name']} | {fmt_tokens(m['context'])} "
            f"| {fmt_tokens(m['output'])} | {'✅' if m['vision'] else '❌'} "
            f"| {'✅' if m['reasoning'] else '❌'} |"
        )
    lines.append("")
    lines.append("> 所有模型均支持工具调用。模型由 [OpenCode Zen](https://opencode.ai) 提供，可能随时更新。")
    return "\n".join(lines)


def update_readme(filepath, new_table, lang="en"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if lang == "en":
        pattern = (
            r"(\| Model ID \| Name \| Context.*?)"
            r"(> All models support tool calling.*?\n)"
        )
    else:
        pattern = (
            r"(\| 模型 ID \| 名称 \| 上下文.*?)"
            r"(> 所有模型均支持工具调用.*?\n)"
        )

    new_content = re.sub(pattern, new_table + "\n", content, flags=re.DOTALL)

    if new_content == content:
        print(f"⚠️  {filepath}: No changes detected")
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ {filepath}: Updated")
    return True


if __name__ == "__main__":
    print("🔍 Fetching free models from OpenCode...")
    models = fetch_free_models()
    print(f"✓ Found {len(models)} free models:")
    for m in models:
        print(f"  - {m['id']} ({m['name']}) ctx={fmt_tokens(m['context'])}")

    print("\n📝 Updating README files...")
    changed = False
    changed |= update_readme("README.md", build_en_table(models), lang="en")
    changed |= update_readme("README.zh-CN.md", build_zh_table(models), lang="zh")

    if changed:
        print("\n✅ README files updated successfully!")
    else:
        print("\n✅ README files are already up to date.")
