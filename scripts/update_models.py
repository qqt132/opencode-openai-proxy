#!/usr/bin/env python3
"""
Update free models list in README files by querying OpenCode public API.
Runs on GitHub Actions without requiring local OpenCode Desktop.
"""

import json
import re
import sys
import urllib.request

OPENCODE_ZEN_URL = "https://opencode.ai/zen/v1/models"

# Known free model metadata (context/output limits not exposed by public API)
# Updated manually when new models are added
MODEL_METADATA = {
    "mimo-v2-pro-free":        {"context": 1_048_576, "output": 64_000,  "vision": False, "reasoning": True},
    "mimo-v2-omni-free":       {"context": 262_144,   "output": 64_000,  "vision": True,  "reasoning": True},
    "mimo-v2-flash-free":      {"context": 131_072,   "output": 32_000,  "vision": False, "reasoning": True},
    "gpt-5-nano":              {"context": 400_000,   "output": 128_000, "vision": True,  "reasoning": True},
    "nemotron-3-super-free":   {"context": 1_000_000, "output": 128_000, "vision": False, "reasoning": True},
    "minimax-m2.5-free":       {"context": 204_800,   "output": 131_072, "vision": False, "reasoning": True},
    "trinity-large-preview-free": {"context": 128_000, "output": 32_000, "vision": False, "reasoning": True},
    "big-pickle":              {"context": 200_000,   "output": 128_000, "vision": False, "reasoning": True},
}


def fetch_free_models():
    try:
        req = urllib.request.Request(
            OPENCODE_ZEN_URL,
            headers={
                "Authorization": "Bearer anonymous",
                "User-Agent": "Mozilla/5.0 (compatible; opencode-proxy-updater/1.0)"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"❌ Failed to fetch models from {OPENCODE_ZEN_URL}: {e}")
        sys.exit(1)

    free_models = []
    for model in data.get("data", []):
        model_id = model.get("id", "")
        # Free models have "-free" suffix or are known free models
        if not (model_id.endswith("-free") or model_id in MODEL_METADATA):
            continue
        meta = MODEL_METADATA.get(model_id, {
            "context": 0, "output": 0, "vision": False, "reasoning": False
        })
        free_models.append({
            "id": f"opencode/{model_id}",
            "name": to_display_name(model_id),
            **meta,
        })

    # Sort by context window size descending
    free_models.sort(key=lambda x: x["context"], reverse=True)
    return free_models


def to_display_name(model_id: str) -> str:
    """Convert model ID to display name."""
    known = {
        "mimo-v2-pro-free":           "MiMo V2 Pro Free",
        "mimo-v2-omni-free":          "MiMo V2 Omni Free",
        "mimo-v2-flash-free":         "MiMo V2 Flash Free",
        "gpt-5-nano":                 "GPT-5 Nano",
        "nemotron-3-super-free":      "Nemotron 3 Super Free",
        "minimax-m2.5-free":          "MiniMax M2.5 Free",
        "trinity-large-preview-free": "Trinity Large Preview Free",
        "big-pickle":                 "Big Pickle",
    }
    return known.get(model_id, model_id)


def fmt_tokens(n):
    if n >= 1_000_000:
        v = n / 1_000_000
        return f"{v:.0f}M" if v == int(v) else f"{v:.1f}M"
    if n >= 1_000:
        v = n / 1_000
        return f"{v:.0f}K" if v == int(v) else f"{v:.1f}K"
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
            r"(\| Model ID \| Name \| Context.*?\n"
            r"\|[-| ]+\|\n"
            r"(?:\|.*?\n)+"
            r"\n> All models support tool calling.*?\n)"
        )
    else:
        pattern = (
            r"(\| 模型 ID \| 名称 \| 上下文.*?\n"
            r"\|[-| ]+\|\n"
            r"(?:\|.*?\n)+"
            r"\n> 所有模型均支持工具调用.*?\n)"
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
    print(f"🔍 Fetching free models from {OPENCODE_ZEN_URL}...")
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
