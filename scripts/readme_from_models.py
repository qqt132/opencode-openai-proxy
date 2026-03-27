#!/usr/bin/env python3
"""
Read models.json and update README files.
Called by GitHub Actions - no external dependencies required.
"""

import json
import re
from pathlib import Path

ROOT      = Path(__file__).parent.parent
MODELS    = json.loads((ROOT / "models.json").read_text(encoding="utf-8"))
README_EN = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"


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
        return
    filepath.write_text(new_content, encoding="utf-8")
    print(f"  ✅ {filepath.name}: updated")


if __name__ == "__main__":
    print(f"📖 Reading {len(MODELS)} models from models.json")
    update_readme(README_EN, build_en_table(MODELS), lang="en")
    update_readme(README_ZH, build_zh_table(MODELS), lang="zh")
    print("✅ Done")
