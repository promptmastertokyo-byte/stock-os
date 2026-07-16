# automation/

データ取得・定期レビューなどの自動化を管理する。

## 現在の構成

- `data-contract.md`: Yahoo!ファイナンスと企業IRから取得する項目、優先順位、欠損時の扱い
- `architecture.md`: MCPにする機能と通常スクリプトにする機能の境界
- `review-schedule.md`: 決算・IR監視と半年後／1年後レビューの起票設計
- `validate_analysis.py`: 分析Markdownの構造、日付、配点、プライバシーを静的検査

## 検証

```bash
python3 automation/validate_analysis.py analysis
```

警告も失敗として扱う場合は `--strict` を付ける。既存ファイルの移行中は通常モード、
新規分析を追加するPRではstrictモードを推奨する。
