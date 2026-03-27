#!/usr/bin/env python3
"""
Update free models list by querying local OpenCode Desktop API.
Run this script locally whenever you want to refresh the models list.

Usage:
    python3 scripts/update_models.py
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

OPENCODE_URL = "http://localhost:8888"
MODELS_JSON  = Path(__file__).parent.parent / "models.json"
README_EN    = Path(__file__).parent.parent / "README.md"
README_ZH    = Path(__file__).parent.parent / "README.zh-CN.md"


def fetch_free_models():
    try:
        req = urllib.request.Request(f"{OPENCODE_URL}/provider")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"❌ Cannot connect to OpenCode Desktop at {OPENCODE_URL}: {e}")
        print("   Please make sure OpenCode Desktop is running.")
        sys.exit(1)

    free_models = []
    for provider in data.get("all", []):
        if provider.get("id") != "opencode":
            continue
        for model_id, model in (provider.get("models") or {}).items():
            cost = model.get("cost", {})
            if cost.get("input", 1) == 0 and cost.get("output", 1) == 0:
                caps = model.get("capabilities", {})
                inp  = caps.get("input", {})
                free_models.append({
                    "id":        f"opencode/{model_id}",
                    "name":      model.get("name", model_id),
                    "context":   model.get("limit", {}).get("context", 0),
                    "output":    model.get("limit", {}).get("output", 0),
                    "vision":    inp.get("image", False) or inp.get("video", False),
                    "reasoning": caps.get("reasoning", False),
                    "toolcall":  caps.get("toolcall", False),
                })

    free_models.sort(key=lambda x: x["context"], reverse=True)
    return free_models


def fmt_tokens(n):
    if n >= 1_000_000:
        v = n / 1_000_000
        return f"{int(v)}M" if v == int(v) else f"{v:.1f}M"
    if n >= 1_000:
        v = n / 1_000
        return f"{int(v)}K" if v == int(v) else f"{v:.1f}K"
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
    lines.append("> All models support tool calling. "
                 "Models are provided by [OpenCode Zen](https://opencode.ai) "
                 "and are subject to change.")
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
    lines.append("> 所有模型均支持工具调用。"
                 "模型由 [OpenCode Zen](https://opencode.ai) 提供，可能随时更新。")
    return "\n".join(lines)


def update_readme(filepath, new_table, lang="en"):
    content = filepath.read_text(encoding="utf-8")

    if lang == "en":
        pattern = (r"\| Model ID \| Name \|.*?\n"
                   r"(?:\|.*?\n)+"
                   r"\n> All models support tool calling\..*?\n")
    else:
        pattern = (r"\| 模型 ID \| 名称 \|.*?\n"
                   r"(?:\|.*?\n)+"
                   r"\n> 所有模型均支持工具调用。.*?\n")

    new_content = re.sub(pattern, new_table + "\n", content, flags=re.DOTALL)
    if new_content == content:
        print(f"  ⚠️  {filepath.name}: no changes")
        return False

    filepath.write_text(new_content, encoding="utf-8")
    print(f"  ✅ {filepath.name}: updated")
    return True


if __name__ == "__main__":
    print("🔍 Fetching free models from local OpenCode Desktop...")
    models = fetch_free_models()

    print(f"✓ Found {len(models)} free models:")
    for m in models:
        print(f"  - {m['id']} ({m['name']}) "
              f"ctx={fmt_tokens(m['context'])} out={fmt_tokens(m['output'])}")

    # Save to models.json
    MODELS_JSON.write_text(json.dumps(models, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(f"\n💾 Saved to {MODELS_JSON.name}")

    # Update README files
    print("\n📝 Updating README files...")
    update_readme(README_EN, build_en_table(models), lang="en")
    update_readme(README_ZH, build_zh_table(models), lang="zh")

    print("\n✅ Done! Run the following to publish:")
    print("   git add models.json README.md README.zh-CN.md")
    print('   git commit -m "chore: update free models list"')
    print("   git push")
