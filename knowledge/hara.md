# はら — ナレッジ記録

## 担当案件
- 高木さんオンライン秘書講座（全6章・23セクション）のコンテンツ＋スライド制作

## 使用ツール・API
- Google Slides API（SA: start-llc-automatio@start-llc.iam.gserviceaccount.com）
- Google Sheets API（SA: lec-invoice@lec-invoice.iam.gserviceaccount.com）
- Google Drive API（OAuth2: video-text-editor/backend/token.json）
- python-pptx（PPTXファイル操作。デザインが壊れやすいため非推奨）
- SAキーの保存場所: ~/Desktop/start-llc/start-llc/start-llc-sa-key.json

## スライド制作で学んだこと

### 翔伍さんがOKを出したデザインを絶対に壊すな
- 確定版を新規コピーで作り直して壊した
- python-pptxでPPTX結合→再アップロードしたら全壊した
- 対策: 確定版ファイルは変更禁止。python-pptxでの結合は禁止

### テンプレートのデザインは最小限の変更で
- テンプレートを丸ごとコピー→replaceAllTextでテキストだけ置換が正解
- フォント・配置・スタイルを手動で上書きするとテーマ設定が壊れる
- python-pptxのph.text=で上書きするとテーマ継承が切れる

### contentAlignment問題
- テンプレートのCENTERED_TITLEはcontentAlignment=BOTTOM
- 英語→日本語でテキストが短くなると上に大きな余白ができる
- 対策: contentAlignmentをMIDDLEに変更する

### フォントサイズは箱に収まるかで決める
- テンプレートの65ptは英語26文字用。日本語10文字では改行される
- テキストボックスの幅を変えるのではなく、フォントサイズを調整する

### createSlideで新規スライドを作るとデザインが壊れる
- レイアウトを指定してcreateSlideしても、テンプレートのスライドとは別物になる
- テンプレートのスライドをそのまま使い、テキストだけ置換するのが正解

### 1つのファイルにスライドを増やしていく
- テンプレートコピー時に使いたいスライドだけ残して他を削除する方式

### 作る前に完成イメージを見せる
- 言葉で説明しても伝わらない。実物のリンクを見せる
- OKが出るまで実行に移らない

### 日本語フォントはNoto Serif JPが最適
- Googleスライドで使える明朝体。こうさんのテンプレートでも採用

## こうさんのスライドテンプレート（2026-04-07確定）
- URL: templates/SLIDE_TEMPLATE.html
- 3パターン: タイトル（ダーク#1a1a1f）、コンテンツ（ライト#faf9f7）、2カラム比較
- フォント: Noto Serif JP + Cormorant Garamond
- アクセント: #9c8455
- テキスト: #2a2a2a
- 変更禁止

## 確定版スライド
- 2枚確定（タイトル＋コンテンツ）
- URL: https://docs.google.com/presentation/d/1B6uA1ZUSI2wh-jaSGRVS6tqSz4TgNVNW4lxFmI0fj8M/edit
- こうさんのテンプレートに合わせて作り直す予定

## 制作ペースの実績
- 2026-04-06: 1日でスライド2枚（大半がテンプレート試行錯誤）
- まだ安定した制作ペースが確立できていない

## 3つの必須ルール（こうさん通達 2026-04-07）
1. 伝達ボードへの記録（作業開始・完了・ブロッカー時に必ず）
2. ファイル編集前のバックアップ（progress.mdに記録）
3. 翔伍さん確認済み事項をprogress.mdに即記録（同じ質問禁止）
