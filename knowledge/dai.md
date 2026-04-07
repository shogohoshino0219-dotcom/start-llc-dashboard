# ダイのナレッジ記録

## 担当案件

### 1. エージェント間調整・伝達ボード管理
- 状況: 伝達ボード（board.md）のGitHub読み書きが安定稼働中
- 全エージェントの状況把握・翔伍さんへの報告が主業務

### 2. NotebookLM連携（Drive自動保存）
- 状況: スクリプト完成・cron稼働中（30分ごと）。NotebookLMへのソース追加は翔伍さんが手動対応
- スクリプトパス: `/Users/hoshinoshougo/roi-sync/notebook_sync.py`
- 保存先Drive: `https://drive.google.com/drive/folders/1-sA2kaLYqtCpScrQgSN7hBn4NrmtzBSl`（AIフォルダ）

### 3. START合同会社HP制作
- 状況: デザイン方向性は確定（ダークモダン×ブルーアクセント×パーティクル背景、ryden.co.jp参考）。翔伍さん最終承認待ち
- フォント: 英語=Cormorant Garamond（セリフ）、日本語=Noto Sans JP（ゴシック）
- ヒーロー: AIパーティクル背景アニメーション
- Service: 横並び3カード、ホバーでブルー光彩
- ツール: STUDIO（ブラウザベース）

### 4. ReC経営会議 議事録
- 状況: 完成・Googleドキュメント化済み。修正対応中
- Googleドキュメント: `https://docs.google.com/document/d/1W7q6O-NU9Ty86aVJO8K5_mJ_N1KyjidU0MfGo0BTIlI/edit`
- ローカル: `~/Desktop/start-llc/start-llc/ログ/2026-04-06_Zoom経営会議_議事録.md`

## 学んだこと

### Google Drive API
- サービスアカウントにはストレージ容量がない → ファイルアップロードは403エラーになる
- OAuth認証（token.json）を使えばアップロード可能
- token.jsonの場所: `~/Desktop/start-llc/start-llc/_旧体制/CDO_技術/動画編集自動化/video-text-editor/backend/token.json`
- スコープは `https://www.googleapis.com/auth/drive` のみ。Documents APIスコープは含まれていない
- mdファイルをGoogleドキュメントに変換してアップロード可能（mimeType指定）

### Whisper（音声文字起こし）
- openai-whisperとfaster-whisperが両方インストール済み
- faster-whisperはPython 3.9でmatmulオーバーフローエラーが発生 → 使えない
- openai-whisperのコマンドパス: `/Users/hoshinoshougo/Library/Python/3.9/bin/whisper`
- バックグラウンド実行時はフルパスが必要（PATHが通っていない）
- 91分の音声をCPUで処理する場合:
  - 10分割して順番処理が安定
  - smallモデル: 1パート約5分、tinyモデル: 1パート約1.5分
  - 並列実行は10個同時だとCPU飽和して遅くなる → 順番処理が結果的に速い
  - mediumモデルはCPUでは非常に遅い（非推奨）
- 文字起こし精度: 固有名詞（地名・人名）は誤認識が多い → 翔伍さんに確認必須

### GitHub API（伝達ボード書き込み）
- `gh api` コマンドで読み書き可能
- 書き込み時はSHAが必要 → 取得と書き込みの間に他のエージェントが書き込むとSHA不一致で409エラー → 最新SHA再取得して再実行
- base64エンコードして送信: `CONTENT=$(base64 -i ファイルパス)`
- 認証: `gh auth status` で確認。keyring経由でPAT管理

### notebooklm-py
- NotebookLMにCLIからソースを追加するツール
- Python 3.11が必要（3.9では型ヒントエラー）
- インストール: `/opt/homebrew/bin/python3.11 -m pip install "notebooklm-py[browser]"`
- ログイン時にブラウザ表示が必要だが、CLIからの自動化は不安定
- SIDクッキーが取得できず認証失敗する問題あり → 現時点では実用困難

### Playwright
- `/Users/hoshinoshougo/.claude/plugins/marketplaces/playwright-skill/skills/playwright-skill` にインストール済み
- at homeなどBot対策が厳しいサイトではブロックされる
- セットアップ: `cd $SKILL_DIR && npm run setup`

## やらかしたこと＋対策

### 1. 伝達ボードの時刻を間違えた
- 事象: うなさんの書き込み時刻(23:00)をそのまま鵜呑みにした。実際は午前中だった
- 対策: 時刻・日付・数値を見たとき、現在の状況と矛盾がないか必ずチェックする

### 2. 「あと数分」と言って30分以上かかった
- 事象: Whisperの処理時間を過小見積もりして翔伍さんに嘘の時間を伝えた
- 対策: 処理時間の見積もりは正直に出す。わからなければ「わからない」と言う

### 3. NotebookLMへの自動追加ができると言ったのにできなかった
- 事象: notebooklm-pyの認証問題を事前に検証せずに「できます」と言った
- 対策: 1.6ルール（着手前アウトプットルール）に従い、不安な点を先に伝える

### 4. Driveにファイルを置いただけでNotebookLMへのソース追加を忘れた
- 事象: 「完了」と報告したが、実際はNotebookLMにソースを追加する作業が残っていた
- 対策: 完了の定義を明確にして、全工程が終わるまで完了と言わない

### 5. サービスアカウントでDriveフォルダを作成してしまった
- 事象: OAuthで見えないフォルダが作成され、翔伍さんの画面で空に見えた
- 対策: Drive操作はOAuth認証（翔伍さんのアカウント）で統一する

## 翔伍さんの好み・判断基準

### コミュニケーション
- 情報が多すぎると思考が止まる → 「次にやること1つ」を常に明確に
- 選択肢は最大3つ。おすすめに★をつける
- 「どうしましょう？」は禁止。必ず提案型
- 時間の見積もりは正直に。嘘をつかない
- 小難しい用語は例え話を添える

### 成果物
- 議事録の人名は正確に（文字起こしの誤認識を鵜呑みにしない）
- 肩書きは不要（「代表」等は書かない）
- 参加者の順番は翔伍さんの指定通りに
- 数字は月換算も併記
- 決定事項は「誰が・何を・どこまで・いつまでに」を具体的に

### デザイン（HP）
- ryden.co.jp（ダークモダン）が好み → 前回のshumoku59.com（白基調・高級感）から方向転換
- アクセントカラー: ブルー系（信頼感・堅実さ）
- ヒーロー: 背景アニメーション（AIパーティクル）が好み
- フォント: 英語はセリフ体（高級感ミックス）

## 未解決の課題

1. **NotebookLMへのAPI自動追加** — notebooklm-pyの認証問題。Python環境の問題かブラウザ表示の問題。後日対応
2. **START合同会社HP** — デザイン案の翔伍さん最終承認待ち。承認後にSTUDIOで制作
3. **議事録の「石橋」→「当知4丁目」** — 堀尾さんに正しい物件名を確認待ち
4. **議事録の「のりさん」** — 不動産業界の人脈紹介ネットワークの関係者。詳細不明
5. **cron実行のPython 3.9問題** — FutureWarningが大量に出る。Python 3.11への移行を検討すべき
