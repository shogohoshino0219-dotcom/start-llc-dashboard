# ゆうさんナレッジ記録（2026-04-04〜04-07）

## 1. ROIシート関連

### スプレッドシートID一覧
| 用途 | ID |
|------|-----|
| ROIシート | `19Bbpkyl5oG0D_dBSM2u7c3o0qKTuxXFufG8-GvkIeME` |
| ミラーシート | `1-RPiGC8eoCV2ojGwrDM-oaKDY71BGerMt-H2m-sYtZ8` |
| ソースシート（広告データ） | `1glp8Xv1lXHSPO_TPwRsisN9Y9sqm6gS4SNSS4m1GJWw` |
| 決済者リスト | `1SU-gzKfyjWhm-yNQmzeCioOWqETv17jS14KztPfWiiA` |
| 受講生管理 | `1THYUzatsPTNSaHIjjVwkrmS5DS6hukJ9aHBq_AZnIys` |
| 経路一覧 | `1Uk9wr199YJGFQi-fYbOGXTMsAD2PouZa25rbc5MD49I` |
| 料金表 | `1B4NEvKIaHdGlYP0Ym0ihqm7cY_9LCyZw_l3QvTnzpbI` |
| 参考シート（広告KPI） | `1B875SEyZN5Fis2SD0TbmrmWWhEeuqjJp-HyTWzBLbC4` |

### ミラーシートの仕組み
- ソースシート（1glp8Xv...）→ ミラーシート（1-RPiG...）へのコピー
- utage個別審査_rawのA〜D列はIMPORTRANGEで接続されている（触るな！）
- E列（審査）・F列（面談）は値コピーで同期
- FBタブ（月別）は書式ごとコピー（copyTo方式）
- 自動同期: ~/roi-sync/mirror_sync.py（cron 30分ごと）

### 広告経由進捗タブの計算ロジック
- 審査申込数: ミラーのutage個別審査_raw 2月以降の行数
- 審査通過数: E列=「審査通過」の行数（2月以降）
- 面談待ち: E列=審査通過 かつ F列=日程or空欄
- 成約: F列=「成約」
- 支払い待ち: 成約・見送り・キャンセル・面談待ち以外
- 面談落ち: F列に「見送り」を含む
- 広告消化額: FBタブの合計行H列（2月は行15、3月以降は行5）
- 着金額: マーケ講座（広告経由）タブのT列合計
- 売上: 同タブのU列合計
- 利益: 着金 - 広告消化額
- 松尾さん報酬: 着金 × 15%
- 純利益: 利益 - 松尾さん報酬

### 経費タブの構造
- カラム: No./請求日/請求月/取引先/項目名/金額/大ジャンル/小ジャンル/請求書リンク
- ヘッダー行に合計・イベント経費残高あり
- 大ジャンル: 12種類（オーガニック/広告経由/代理店/イベント/ブートキャンプ/AI講座/レベシェア/オーディオBC/顧問生/JV/顧問グループ塾）
- 小ジャンル: オーガニックのみ必須（YouTube/Instagram/TikTok/Twitter/アメブロ/FaceBook/HP/LINE・UTAGE/講座運営/デザイン/マーケディレクション/経理・法務）

### 商品構成（LEC）
- マーケ講座 = メイン商品。流入経路でタブが分かれる
  - オーガニック/広告経由/代理店/イベント/25年ブートキャンプ
- 別商品: AI講座/顧問生/顧問グループ塾/物販/レベシェア/JV/オーディオBC

## 2. 自動化スクリプト

### ファイル配置（~/roi-sync/）
| ファイル | 機能 | cron |
|---------|------|------|
| mirror_sync.py | ミラーシート同期（FBタブ+utage審査E/F列） | */30 * * * * |
| expense_sync.py | 経費フォルダスキャン→経費タブ追記 | 5,35 * * * * |
| update_ad_progress.py | 広告経由進捗タブ全No.更新+F〜H列 | 10,40 * * * * |
| line_webhook_server.py | LINE Webhook受信（経費ジャンル選択+freeeサイン連携） | 常時起動（FastAPI+ngrok） |
| sync_roi.py | ROIシート同期（共通ライブラリ） | - |
| service-account-key.json | Google APIサービスアカウント | - |
| freee_sign_token.json | freeeサイン OAuthトークン | - |

### 重要な注意点
- cronからはDesktopフォルダにアクセスできない（macOSセキュリティ）→ ~/roi-sync/に配置
- pdftextはフルパス指定必須（/opt/homebrew/bin/pdftotext）
- PDF読み取り失敗時は経費追加しない（誤追加防止）
- ngrok無料版はMac起動中のみ動作

## 3. LINE連携

### おさるさん経理法務LINE
- アクセストークン: .envに格納
- 機能①: 経費追加時にジャンル選択ボタン送信→ボタン押下でシート更新
- 機能②: freeeサイン契約締結→カテゴリ選択→シート記入
- 機能③: 流入経路の自動取得（経路一覧シート連携）
- 機能④: 支払い方法3パターン（振込/振込＋ユニヴァ/ユニヴァ）
- 機能⑤: 料金表連携（分割回数に応じた金額自動計算）

### freeeサイン連携
- OAuth2クライアント: Claude連携（l_XwRC...）
- Webhook URL: ngrokのURL/freee-sign-webhook
- 締結時の流れ: Webhook受信→署名者情報API取得→LINE通知→カテゴリ選択→追加質問（支払い方法→分割回数）→シート記入

## 4. 失敗と学び

### IMPORTRANGEの破壊（4/4）
- ミラーシートのタブを削除→コピーしたらIMPORTRANGE接続が壊れた
- 対処: 変更履歴から復元
- 教訓: タブ削除前にIMPORTRANGEの依存関係を確認すること

### expense_sync.pyの誤追加（4/6〜4/7）
- cronでpdftotext未検出→PDF中身の判定ができず→LECが出した請求書も含めて27件追加
- 対処: No.959-985を削除、pdftextフルパス指定、読み取り失敗時は追加しないガード追加
- 教訓: cronの環境はターミナルと違う。フルパス指定必須

### GASトリガーの全削除
- setupAllTriggers()は全トリガーを削除するだけで新規作成しない
- 教訓: GASの関数名だけで判断せず、中身を必ず読むこと

## 5. 取引先→ジャンル対応メモ
- 中野雅仁 → AI講座
- 藤﨑龍 → マーケ講座（オーガニック）/ビジネス_YouTube_マーケターおさる が多い
- START(同) → 業務内容ごとにジャンルが変わる（月額報酬=オーガニック、AI業務=AI講座等）
