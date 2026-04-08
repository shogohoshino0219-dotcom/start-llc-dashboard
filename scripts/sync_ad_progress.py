"""
広告経由進捗（26年2月以降）タブ自動更新スクリプト

■ 技術スタック
- google-auth + googleapiclient（うなさんが作ったroi_phase1.pyと同じ構成）
- gspreadは使わない

■ 概要
ミラーシート・ROIシートから3つのデータソースを読み取り、
広告経由進捗タブのC列・D列にKPI数値を書き込む。

■ 実行
cd ~/roi-sync && python3 sync_ad_progress.py
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import os

# ============================================================
# 設定
# ============================================================

ROI_SHEET_ID = "19Bbpkyl5oG0D_dBSM2u7c3o0qKTuxXFufG8-GvkIeME"
MIRROR_SHEET_ID = "1-RPiGC8eoCV2ojGwrDM-oaKDY71BGerMt-H2m-sYtZ8"

SERVICE_ACCOUNT_KEY = os.environ.get(
    "GOOGLE_SERVICE_ACCOUNT_KEY_PATH",
    os.path.join(os.path.dirname(__file__), "service-account-key.json")
)

CUTOFF_DATE = datetime(2026, 2, 1)

# ============================================================
# 認証（うなさんのroi_phase1.pyと同じ方式）
# ============================================================

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)


# ============================================================
# ヘルパー
# ============================================================

def read_sheet(service, sheet_id, range_str):
    """シートからデータを読み取る"""
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_str
    ).execute()
    return result.get("values", [])


def write_sheet(service, sheet_id, range_str, values):
    """シートにデータを書き込む"""
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_str,
        valueInputOption="RAW",
        body={"values": values}
    ).execute()


def parse_number(val):
    """数値文字列をintに変換"""
    if not val:
        return 0
    try:
        return int(float(str(val).replace(",", "").replace("¥", "").replace("円", "").strip()))
    except (ValueError, TypeError):
        return 0


def is_after_cutoff(date_str):
    """日付文字列が2026年2月以降かどうか"""
    if not date_str:
        return False
    for fmt in ["%Y/%m/%d", "%Y-%m-%d", "%Y年%m月%d日", "%Y年%m月"]:
        try:
            return datetime.strptime(date_str.strip(), fmt) >= CUTOFF_DATE
        except ValueError:
            continue
    if "2026" in str(date_str):
        for m in ["2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]:
            if m in str(date_str):
                return True
    return False


# ============================================================
# データ取得1: ミラーシート > utage個別審査_raw
# ============================================================

def get_shinsa_data(service):
    """utage個別審査_rawから審査関連KPIを集計"""
    rows = read_sheet(service, MIRROR_SHEET_ID, "'utage個別審査_raw'!A1:Z")

    if len(rows) < 2:
        print("[WARN] utage個別審査_rawにデータがありません")
        return {k: 0 for k in ["shinsa_apply", "shinsa_pass", "mendan_wait", "shiharai_wait", "mendan_ochi", "line_unreg"]}

    # ヘッダー確認（デバッグ用）
    header = rows[0]
    print(f"  ヘッダー: {header[:10]}")
    data_rows = rows[1:]

    # E列(idx=4)=審査結果、F列(idx=5)=ステータス
    counts = {"shinsa_apply": 0, "shinsa_pass": 0, "mendan_wait": 0,
              "shiharai_wait": 0, "mendan_ochi": 0, "line_unreg": 0}

    for row in data_rows:
        if not row or len(row) < 2:
            continue

        counts["shinsa_apply"] += 1

        e_val = row[4].strip() if len(row) > 4 else ""
        f_val = row[5].strip() if len(row) > 5 else ""

        if e_val == "審査通過":
            counts["shinsa_pass"] += 1
        if f_val == "面談待ち":
            counts["mendan_wait"] += 1
        if "支払い待ち" in f_val:
            counts["shiharai_wait"] += 1
        if f_val == "不成約":
            counts["mendan_ochi"] += 1
        if "LINE" in f_val:
            counts["line_unreg"] += 1

    return counts


# ============================================================
# データ取得2: ROIシート > マーケ講座（広告経由）
# ============================================================

def get_seiyaku_data(service):
    """マーケ講座（広告経由）タブから成約数・売上を集計"""
    rows = read_sheet(service, ROI_SHEET_ID, "'マーケ講座（広告経由）'!A1:U")

    if len(rows) < 2:
        return {"seiyaku_count": 0, "total_sales": 0}

    header = rows[0]
    print(f"  ヘッダー: {header[:10]}")
    data_rows = rows[1:]

    # D列(idx=3)=契約月
    seiyaku_count = 0
    total_sales = 0

    for row in data_rows:
        if not row or len(row) < 4:
            continue

        contract_month = row[3].strip() if len(row) > 3 else ""
        if is_after_cutoff(contract_month):
            seiyaku_count += 1
            # 売上金額列はヘッダーから特定する
            # TODO: ヘッダーを見て金額列を自動検出する
            for idx in range(4, min(len(row), 20)):
                cell = row[idx]
                if cell and ("円" in str(cell) or str(cell).replace(",", "").isdigit()):
                    amount = parse_number(cell)
                    if amount > 10000:  # 売上っぽい金額（1万円以上）
                        total_sales += amount
                        break

    return {"seiyaku_count": seiyaku_count, "total_sales": total_sales}


# ============================================================
# データ取得3: ミラーシート > FB日別タブ
# ============================================================

def get_fb_daily_data(service):
    """FB日別タブから広告消化額・CV数・ウェビナー参加数を取得"""
    # ミラーシートのタブ一覧を取得
    meta = service.spreadsheets().get(spreadsheetId=MIRROR_SHEET_ID).execute()
    fb_tabs = [s["properties"]["title"] for s in meta["sheets"]
               if "FB" in s["properties"]["title"] and "日別" in s["properties"]["title"]]

    print(f"  FB日別タブ: {fb_tabs}")

    total_ad_cost = 0
    total_cv = 0
    total_webinar = 0

    for tab_name in fb_tabs:
        try:
            # H7=広告消化額合計、I7=CV数、S6=ウェビナー参加数
            cells = read_sheet(service, MIRROR_SHEET_ID, f"'{tab_name}'!H6:S7")
            if len(cells) >= 2:
                # H7 is cells[1][0] (row 7, col H)
                h7 = cells[1][0] if len(cells[1]) > 0 else "0"
                total_ad_cost += parse_number(h7)

                # I7 is cells[1][1] (row 7, col I)
                i7 = cells[1][1] if len(cells[1]) > 1 else "0"
                total_cv += parse_number(i7)

            if len(cells) >= 1:
                # S6 is cells[0][11] (row 6, col S = H+11)
                s6 = cells[0][11] if len(cells[0]) > 11 else "0"
                total_webinar += parse_number(s6)

            print(f"    {tab_name}: 広告費={h7}, CV={i7}, ウェビナー={s6}")

        except Exception as e:
            print(f"  [WARN] {tab_name}: {e}")

    return {"total_ad_cost": total_ad_cost, "total_cv": total_cv, "total_webinar": total_webinar}


# ============================================================
# 書き込み: 広告経由進捗タブ
# ============================================================

def write_progress(service, shinsa, seiyaku, fb):
    """広告経由進捗タブのC列・D列に書き込み"""

    # CPA算出
    opt_cpa = round(fb["total_ad_cost"] / fb["total_cv"]) if fb["total_cv"] > 0 else 0
    seminar_cpa = round(fb["total_ad_cost"] / fb["total_webinar"]) if fb["total_webinar"] > 0 else 0

    # 書き込みデータ: (行番号, C列の値, D列のデータ出どころ)
    write_data = [
        (3,  shinsa["shinsa_apply"],     "ミラーシート｜utage個別審査_raw｜2026年2月以降の行数"),
        (4,  shinsa["shinsa_pass"],      "ミラーシート｜utage個別審査_raw｜E列=「審査通過」の行数"),
        (9,  shinsa["mendan_wait"],      "ミラーシート｜utage個別審査_raw｜F列=「面談待ち」の行数"),
        (10, seiyaku["seiyaku_count"],   "ROIシート｜マーケ講座（広告経由）｜D列が2026年2月以降の行数"),
        (11, shinsa["shiharai_wait"],    "ミラーシート｜utage個別審査_raw｜F列に「支払い待ち」を含む行数"),
        (12, shinsa["mendan_ochi"],      "ミラーシート｜utage個別審査_raw｜F列=「不成約」の行数"),
        (13, shinsa["line_unreg"],       "ミラーシート｜utage個別審査_raw｜F列に「LINE」を含む行数"),
        (18, fb["total_ad_cost"],        "ミラーシート｜FB日別タブ（2月以降）｜H7セルの合計"),
        (19, f'{opt_cpa}({fb["total_cv"]})',          "ミラーシート｜FB日別タブ｜広告費÷CV数（I7セル）"),
        (20, f'{seminar_cpa}({fb["total_webinar"]})', "ミラーシート｜FB日別タブ｜広告費÷ウェビナー参加数（S6セル）"),
    ]

    # 書き込み前にクリア
    clear_rows = [2, 3, 4, 8, 9, 10, 11, 12, 13, 17, 18, 19, 20]
    clear_values = [["", ""] for _ in clear_rows]
    for i, r in enumerate(clear_rows):
        write_sheet(service, ROI_SHEET_ID, f"'広告経由進捗（26年2月以降）'!C{r}:D{r}", [["", ""]])

    # D2にヘッダー
    write_sheet(service, ROI_SHEET_ID, "'広告経由進捗（26年2月以降）'!D2", [["データ出どころ（自動更新）"]])

    # データ書き込み
    for row_num, c_val, d_val in write_data:
        write_sheet(service, ROI_SHEET_ID,
                    f"'広告経由進捗（26年2月以降）'!C{row_num}:D{row_num}",
                    [[c_val, d_val]])

    print(f"\n[OK] 広告経由進捗タブ更新完了（{len(write_data)}項目）")


# ============================================================
# メイン
# ============================================================

def main():
    print("=" * 50)
    print("広告経由進捗タブ自動更新")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    service = get_service()

    print("\n[1/3] ミラーシート > utage個別審査_raw 読み取り中...")
    shinsa = get_shinsa_data(service)
    print(f"  → 申込:{shinsa['shinsa_apply']} 通過:{shinsa['shinsa_pass']} "
          f"面談待ち:{shinsa['mendan_wait']} 支払待ち:{shinsa['shiharai_wait']} "
          f"面談落ち:{shinsa['mendan_ochi']} LINE未登録:{shinsa['line_unreg']}")

    print("\n[2/3] ROIシート > マーケ講座（広告経由）読み取り中...")
    seiyaku = get_seiyaku_data(service)
    print(f"  → 成約:{seiyaku['seiyaku_count']}件 売上:{seiyaku['total_sales']:,}円")

    print("\n[3/3] ミラーシート > FB日別タブ 読み取り中...")
    fb = get_fb_daily_data(service)
    print(f"  → 広告費:{fb['total_ad_cost']:,}円 CV:{fb['total_cv']} ウェビナー:{fb['total_webinar']}")

    print("\n[書き込み] 広告経由進捗タブに反映中...")
    write_progress(service, shinsa, seiyaku, fb)

    # サマリー表示
    opt_cpa = round(fb["total_ad_cost"] / fb["total_cv"]) if fb["total_cv"] > 0 else 0
    seminar_cpa = round(fb["total_ad_cost"] / fb["total_webinar"]) if fb["total_webinar"] > 0 else 0
    print(f"\n{'=' * 50}")
    print(f"審査申込: {shinsa['shinsa_apply']}名")
    print(f"審査通過: {shinsa['shinsa_pass']}名")
    print(f"成約: {seiyaku['seiyaku_count']}件 / 売上: {seiyaku['total_sales']:,}円")
    print(f"広告費: {fb['total_ad_cost']:,}円")
    print(f"オプトCPA: {opt_cpa:,}円 / セミナーCPA: {seminar_cpa:,}円")
    print(f"{'=' * 50}")
    print("✅ 完了")


if __name__ == "__main__":
    main()
