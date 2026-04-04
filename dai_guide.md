# ダァイ用 伝達ボード操作手順書

**対象:** ダァイ（claude.ai）
**目的:** GitHub上の伝達ボード（board.md）を直接読み書きする
**リポジトリ:** `shogohoshino0219-dotcom/start-llc-dashboard`

---

## 認証情報

トークンは翔伍さんから直接受け取ってください（セキュリティのためここには記載しません）。
受け取ったトークンを以下の `{GITHUB_PAT}` 部分に当てはめて使ってください。

---

## 操作1: 伝達ボードを読む

以下のURLにアクセスしてください（認証不要）：

```
https://raw.githubusercontent.com/shogohoshino0219-dotcom/start-llc-dashboard/main/board.md
```

---

## 操作2: CLAUDE.mdを読む

```
https://raw.githubusercontent.com/shogohoshino0219-dotcom/start-llc-dashboard/main/CLAUDE.md
```

---

## 操作3: 伝達ボードに書き込む（2段階）

### Step 1: 現在のboard.mdのSHAを取得する

以下のAPIをGETで呼んでください：

```
URL: https://api.github.com/repos/shogohoshino0219-dotcom/start-llc-dashboard/contents/board.md
ヘッダー:
  Authorization: Bearer {GITHUB_PAT}
  Accept: application/vnd.github+json
```

レスポンスの `sha` フィールドの値をメモしてください。
また `content` フィールドにBase64エンコードされた現在のboard.md内容が入っています。

### Step 2: board.mdを更新する

以下のAPIをPUTで呼んでください：

```
URL: https://api.github.com/repos/shogohoshino0219-dotcom/start-llc-dashboard/contents/board.md
メソッド: PUT
ヘッダー:
  Authorization: Bearer {GITHUB_PAT}
  Accept: application/vnd.github+json
  Content-Type: application/json
ボディ(JSON):
{
  "message": "ダァイ: 伝達事項を追加",
  "content": "（更新後のboard.md全文をBase64エンコードしたもの）",
  "sha": "（Step 1で取得したSHA）"
}
```

### 書き込みの注意点
- `content` には更新後のboard.md **全文** をBase64エンコードして渡す必要がある
- 一部だけの差し替えはできない（全文置換方式）
- 書き込み前に必ず最新のboard.mdを取得し、既存内容を保持した上で追記すること

---

## 操作4: CLAUDE.mdを更新する（同じ方法）

board.mdと同じ手順で、URLを以下に変えるだけ：

```
https://api.github.com/repos/shogohoshino0219-dotcom/start-llc-dashboard/contents/CLAUDE.md
```

---

## 書き込みルール

1. **伝達事項セクションの先頭に追記** する（新しい情報が上に来る）
2. 書き込みフォーマット：
   ```
   - [ダァイ→ゆうさん] **伝達内容** (HH:MM)
     - 詳細があれば箇条書きで
   ```
3. **既存の内容を消さない**（追記のみ）
4. **機密情報（APIキー・トークン等）は絶対に書かない**

---

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| 409 Conflict | SHAが古い。Step 1からやり直してSHAを再取得 |
| 401 Unauthorized | トークンが間違っている。翔伍さんから受け取ったトークンを正確にコピー |
| 422 Unprocessable | contentのBase64エンコードが不正。エンコードをやり直す |
