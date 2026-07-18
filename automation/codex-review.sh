#!/usr/bin/env bash
# ローカル実行用: Codex CLIで分析ファイルの別モデルレビュー（workflow step 8）を行う。
# クラウドRoutine（平日9:00 JSTに分析をpush）の後に実行する想定。
#
# 前提: codex CLIインストール済み・認証済み（codex login または OPENAI_API_KEY）
# 使い方:
#   ./automation/codex-review.sh              # 全分析ファイルのうち未レビューのものをレビュー
#   ./automation/codex-review.sh analysis/6758-sony-group.md   # 指定ファイルのみ
# 出力: reviews/model-reviews/<basename>-<YYYYMMDD>.codex.md
# 反映: 出力を確認のうえ、各分析ファイルの「14. 別エージェント／別モデルによるレビュー」欄へ
#       要点を転記してコミットする（ローカルのClaude Codeに任せてもよい）。

set -euo pipefail
cd "$(dirname "$0")/.."

git pull --ff-only origin main

mkdir -p reviews/model-reviews
DATE=$(date +%Y%m%d)

review_one() {
  local f="$1"
  local base out
  base=$(basename "$f" .md)
  out="reviews/model-reviews/${base}-${DATE}.codex.md"
  # 「14.」節に既にレビュー実施者が記入済みならスキップ
  if grep -A2 "別エージェント" "$f" | grep -q "未実施"; then
    echo "== Codex review: $f -> $out"
    codex exec "あなたは独立レビュアーです。AGENTS.md の Review policy と rules/scoring-rules.md に従い、
${f} をレビューしてください。確認観点: (1)数値と出典の一致・出典種別の妥当性 (2)前期/今期/来期の期間混同
(3)一時利益・会計変更の扱い (4)希薄化・増資 (5)営業CFと利益の乖離 (6)集中・為替・規制リスクの網羅
(7)競争優位性の定量・定性両面 (8)反証条件と売却条件の明記 (9)各区分の段階評価と換算の妥当性
(10)業種補正の適用の適切さ。指摘は重要度順に、修正提案付きで簡潔に。" > "$out"
    echo "レビュー実施者: codex-cli ($(codex --version 2>/dev/null || echo unknown))" >> "$out"
  else
    echo "-- skip (レビュー済み): $f"
  fi
}

if [ $# -ge 1 ]; then
  review_one "$1"
else
  for f in analysis/*.md; do
    [ "$(basename "$f")" = "README.md" ] && continue
    review_one "$f"
  done
fi

echo ""
echo "完了。reviews/model-reviews/ の内容を確認し、各分析ファイルの14節へ要点を転記後、"
echo "git add -A && git commit && git push でクラウド側に共有してください。"
