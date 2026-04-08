# 進捗ファイル（ゆうさん）— 2026-04-08 セッション引き継ぎ

## 完了済みタスク
- [x] CLAUDE.md配置・GitHubリポジトリ更新
- [x] 伝達ボード整理（旧体制→新体制）
- [x] ダァイ↔ゆうさんの伝達ボード連携（GitHub PAT）
- [x] GitHub Actions通知（board.md変更→Chatwork通知）
- [x] ミラーシート復旧（utage審査E/F列＋FBタブ6個＋自動同期cron）
- [x] 広告経由進捗タブ全No.更新＋F〜H列おさるさんフォーマット自動更新
- [x] マーケ講座（広告経由）タブ3名追加＋面談日記入
- [x] 経費タブ4月分11件＋3月分54件書き込み
- [x] 経費タブ大ジャンル全件記入完了
- [x] 経費タブ小ジャンルプルダウン設定（37選択肢）
- [x] 経費タブ日付順並べ替え
- [x] 経費タブからLEC発行請求書をレベシェア・JVタブに移動（合計69件）
- [x] 大分類別サマリーにROI列4つ追加（総計・12月・1月・2月）
- [x] freeeサイン連携（OAuth認証＋LINE通知＋カテゴリ選択＋シート記入）
- [x] 流入経路自動取得（経路一覧シート連携）
- [x] 支払い方法3パターン＋料金表連携＋分割回数
- [x] expense_sync.pyバグ修正（pdftextフルパス＋読み取り失敗時スキップ）
- [x] knowledgeフォルダにナレッジ記録
- [x] gcloud CLI インストール＋Sheets API有効化（start-llcプロジェクト）
- [x] G列大ジャンルを通常プルダウンに変更（データ破損なし確認済み）
- [x] H列小ジャンルを通常プルダウンに変更

## 未完了タスク（次セッションで着手）
- [ ] 経費タブの経費列にSUMIFS関数を入れる（大分類別サマリー・総計の経費が全て0円）
- [ ] roi_phase1.py の作成・実行（翔伍さんからスクリプト内容を受け取る必要あり）
- [ ] freeeサイン連携のオーガニックフロー最終テスト
- [ ] expense_sync.pyのcron復旧後の動作確認
- [ ] Mac再起動時のFastAPI+ngrokサーバー自動起動設定
- [ ] G列→H列の連動プルダウン（GASなしでは実現不可。保留）

## 自動化スクリプト（~/roi-sync/）
| ファイル | 機能 | cron |
|---------|------|------|
| mirror_sync.py | ミラーシート同期（FBタブ+utage審査E/F列） | */30 * * * * |
| expense_sync.py | 経費フォルダスキャン→経費タブ追記 | 5,35 * * * * |
| update_ad_progress.py | 広告経由進捗タブ全No.更新+F〜H列 | 10,40 * * * * |
| line_webhook_server.py | LINE Webhook受信（経費ジャンル選択+freeeサイン連携） | 常時起動（FastAPI+ngrok） |
| sync_roi.py | ROIシート同期（共通ライブラリ） | - |
| service-account-key.json | lec-invoice SA | - |
| freee_sign_token.json | freeeサイン OAuthトークン | - |

## 重要な注意事項
- **既存データは翔伍さんから連絡があるまで一切触らない（削除も上書きも禁止）**
- cronからはDesktopフォルダにアクセスできない → ~/roi-sync/に配置
- pdftextはフルパス指定必須（/opt/homebrew/bin/pdftotext）
- start-llcの正しいSA: start-llc-automatio@start-llc.iam.gserviceaccount.com（キー: ~/Desktop/start-llc/start-llc/start-llc-sa-key.json）
- lec-invoice SAは旧SA。ただし現在のスクリプトは全てこれで動いている

## 翔伍さんからの確認済み事項
- 松尾さん報酬 = 着金額 × 15%
- 純利益 = 利益 - 松尾さん報酬（利益 = 着金 - 広告消化額）
- 着金額 = マーケ講座（広告経由）タブのT列合計
- 支払い方法: 振込 / 振込＋ユニヴァ / ユニヴァ の3パターン
- 花岡圭輔税理士事務所 → 大ジャンル「税理」（新規追加）
- 中野雅仁 → AI講座
- 経費タブはLECが請求されたもの（支払ったもの）のみ
- LECが出した請求書はレベシェアまたはJVタブに移動
- JV判定: 件名に「JVキャンパス」を含むもの。それ以外はレベシェア
