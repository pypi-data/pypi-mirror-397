# 要件定義書  
## EN16931 CI Validation Tool（MVP）

---

## 1. 背景・目的

EU標準電子請求書規格 **EN16931** は継続的に更新されており、
実装企業・サービスプロバイダは以下の課題を抱えている。

- 規格更新時に **どのルールが変わり、何が壊れるか分からない**
- 無料validatorは存在するが、**CIでの回帰テストや差分検証に弱い**
- 検証エラーが仕様寄りで、**開発者が直しにくい**
- 請求書データを外部SaaSに送信できないケースが多い

本プロダクトはこれらを解決し、  
**「EN16931対応をCIで安全に運用するための品質ゲート」** を提供する。

---

## 2. スコープ（重要）

### 2.1 対象範囲（MVP）

- 規格：EN16931
- 構文：
  - UBL
  - CII
- 検証：
  - 公式 Validation Artefacts（XSD / Schematron）
- 実行環境：
  - ローカルCLI
  - CI（GitHub Actions 等）

### 2.2 明示的に対象外とするもの

- 国別CIUS
- Peppol BIS Billing
- 税務・会計上の正しさ保証
- Web UI
- ERP固有マッピング支援
- 相手システムでの処理保証

---

## 3. 非機能要件

### 3.1 セキュリティ

- 請求書XMLは **外部サーバーに送信しない**
- デフォルトは完全ローカル実行
- SaaS連携（将来）は検証結果のみ送信可能な設計

### 3.2 再現性

- 使用する validation artefacts の **バージョンを明示指定可能**
- 同一入力 + 同一バージョンで結果が常に一致すること

### 3.3 CI適合性

- 非対話的に実行可能
- JSON形式で機械可読な出力
- exit code による PASS / FAIL 判定

---

## 4. システム構成（論理）

```
[CLI]
  ├─ Validation Engine (Python)
  │    ├─ XSD Validation
  │    └─ Schematron Validation
  ├─ Artifact Manager
  │    ├─ Download
  │    └─ Cache
  ├─ Diff Engine（有料）
  └─ Report Formatter
```

---

## 5. 機能要件

### 5.1 validate コマンド（無料）

#### コマンド仕様

```bash
invoice-lint validate   --standard EN16931   --syntax UBL   --artifact 1.3.15   invoice.xml
```

#### 入力

- XMLファイル（UBL または CII）
- validation artefacts バージョン

#### 出力（JSON）

```json
{
  "artifact": "EN16931-1.3.15",
  "syntax": "UBL",
  "result": "FAIL",
  "errors": [
    {
      "rule_id": "BR-CO-10",
      "severity": "FATAL",
      "xpath": "/Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount",
      "message": "Total payable amount is incorrect",
      "human_fix": "PayableAmount must equal TaxInclusiveAmount minus PrepaidAmount.",
      "spec_ref": "EN16931 §7.20"
    }
  ],
  "warnings": []
}
```

#### 要件

- XSD / Schematron 両方を実行
- rule_id を必ず含める
- 人間が理解できる修正指針（human_fix）を返す
- FAIL時は exit code != 0

---

### 5.2 diff コマンド（有料）

#### コマンド仕様

```bash
invoice-lint diff   --from 1.3.14.2   --to 1.3.15   ./invoices/
```

#### 機能

- validation artefacts の差分解析
- 追加 / 削除 / 変更されたルールの抽出
- 実データを用いた影響分析

#### 出力例

```json
{
  "from": "1.3.14.2",
  "to": "1.3.15",
  "rule_changes": {
    "added": ["BR-NEW-05"],
    "removed": ["BR-OLD-02"],
    "modified": ["BR-CO-10"]
  },
  "impact_analysis": {
    "failing_files": [
      {
        "file": "invoice_001.xml",
        "rule": "BR-CO-10",
        "reason": "Calculation formula tightened"
      }
    ]
  }
}
```

---

## 6. Artifact Manager 要件

- 公式配布元からのみ artefacts を取得
- ローカルキャッシュを使用
- プロダクトに artefacts を再配布・同梱しない
- バージョン一覧取得機能

---

## 7. エラー翻訳（重要な差別化要件）

- Schematronエラーを以下にマッピング：
  - ルールID
  - 対象XPath
  - 仕様的意味
  - 修正指針（文章）
- 翻訳ルールは辞書として管理し、継続的に拡張可能

---

## 8. CI連携要件

### GitHub Actions

- 専用 Action を提供
- PRでの自動実行
- 結果をコメントとして投稿可能

```yaml
- uses: invoice-lint/action@v1
  with:
    artifact: 1.3.15
    syntax: UBL
    path: ./invoices
```

---

## 9. ライセンス・法務方針

- validation artefacts は公式配布物をそのまま使用
- 仕様本文の再配布は行わない
- プロダクトコードは独自ライセンス
- OSS / Open-core 構成を想定

---

## 10. 成功指標（MVP）

- CI導入まで 10分以内
- 規格更新時の破壊点を事前検知できる
- 有料ユーザーが diff 機能を継続利用する

---

## 11. 将来拡張（MVP外）

- Peppol BIS Billing
- 国別CIUS
- Web UI / ダッシュボード
- SaaS通知機能
