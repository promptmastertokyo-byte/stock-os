#!/usr/bin/env python3
"""Stock OS analysis Markdown linter (standard library only)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "## 1. 投資仮説",
    "## 2. スコア",
    "## 10. 反証条件",
    "## 12. 未確認項目",
    "## 13. 判断",
    "## 14. 別エージェント／別モデルによるレビュー",
    "## 15. 出典",
    "## 16. 変更履歴",
]
SCORE_LIMITS = {
    "業績・成長性": 20,
    "財務健全性・CF": 15,
    "収益性": 10,
    "事業品質・MOAT": 15,
    "経営・資本配分": 10,
    "バリュエーション": 15,
    "リスク耐性": 10,
    "タイミング・需給": 5,
}
PRIVATE_PATTERNS = {
    "保有数量": re.compile(r"(?:保有数量|保有株数)\s*[：:]\s*\d"),
    "平均取得単価": re.compile(r"平均取得単価\s*[：:]\s*[¥￥]?\d"),
    "総資産額": re.compile(r"総資産額\s*[：:]\s*[¥￥]?\d"),
    "口座番号": re.compile(r"口座番号\s*[：:]\s*\d"),
}


def inspect(path: Path) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"必須見出しがありません: {heading}")

    for label in ("分析日", "データ取得日"):
        match = re.search(rf"^- {label}：(\d{{4}}-\d{{2}}-\d{{2}})$", text, re.MULTILINE)
        if not match:
            errors.append(f"{label}はYYYY-MM-DDで記載してください")

    scores: dict[str, int] = {}
    for name, limit in SCORE_LIMITS.items():
        match = re.search(rf"^\|{re.escape(name)}\|(\d+)/(\d+)\|", text, re.MULTILINE)
        if not match:
            errors.append(f"スコア行を解析できません: {name}")
            continue
        value, stated_limit = map(int, match.groups())
        if stated_limit != limit:
            errors.append(f"{name}の上限が不正です: {stated_limit}（正: {limit}）")
        if value > limit:
            errors.append(f"{name}が上限超過です: {value}/{limit}")
        scores[name] = value

    total_match = re.search(r"^\|\*\*合計\*\*\|\*\*(\d+)/100\*\*\|", text, re.MULTILINE)
    if total_match and len(scores) == len(SCORE_LIMITS):
        stated_total = int(total_match.group(1))
        calculated = sum(scores.values())
        if stated_total != calculated:
            errors.append(f"合計点が不一致です: 記載{stated_total} / 計算{calculated}")
    elif not total_match:
        errors.append("合計スコアを解析できません")

    source_section = text.split("## 15. 出典", 1)[-1].split("## 16.", 1)[0]
    if "http://" not in source_section and "https://" not in source_section:
        warnings.append("出典欄にURLがありません")

    for label, pattern in PRIVATE_PATTERNS.items():
        if pattern.search(text):
            errors.append(f"公開禁止情報の可能性があります: {label}")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="analysis")
    parser.add_argument("--strict", action="store_true", help="警告も失敗にする")
    args = parser.parse_args()
    root = Path(args.path)
    files = sorted(root.glob("*.md")) if root.is_dir() else [root]
    files = [path for path in files if path.name != "README.md"]
    failed = False

    for path in files:
        errors, warnings = inspect(path)
        status = "FAIL" if errors or (args.strict and warnings) else "OK"
        print(f"[{status}] {path}")
        for message in errors:
            print(f"  ERROR: {message}")
        for message in warnings:
            print(f"  WARN: {message}")
        failed |= bool(errors or (args.strict and warnings))

    print(f"Checked {len(files)} file(s).")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
