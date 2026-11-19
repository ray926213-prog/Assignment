import sys
import io
import sqlite3
from datetime import datetime

# ==========================================
# 強制設定標準輸出為 UTF-8，徹底解決終端機中文亂碼問題
# ==========================================
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 定義 SQLite 資料庫檔案名稱
DB_FILE = "expenses.db"

def init_db():
    """初始化資料庫與資料表"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 建立支出資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            notes TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# ==========================================
# 1. 新增功能 (Create)
# ==========================================
def add_expense():
    """新增一筆支出記錄到資料庫"""
    print("\n--- 新增支出記錄 ---")
    
    # 日期輸入與驗證
    date_str = input("請輸入日期 (格式 YYYY-MM-DD，直接按 Enter 預設為今天): ").strip()
    if not date_str:
        date_str = datetime.today().strftime('%Y-%m-%d')
    else:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print("⚠️ 日期格式錯誤！將自動使用今天的日期。")
            date_str = datetime.today().strftime('%Y-%m-%d')

    # 金額輸入與驗證
    while True:
        try:
            amount = float(input("請輸入金額: "))
            if amount <= 0:
                print("⚠️ 金額必須大於 0，請重新輸入。")
                continue
            break
        except ValueError:
            print("⚠️ 請輸入有效的數字！")

    # 分類輸入
    category = input("請輸入分類 (例如: 食物, 交通, 娛樂): ").strip()
    if not category:
        category = "其他"

    # 備註輸入
    notes = input("請輸入備註 (選填，可直接按 Enter 略過): ").strip()

    # 寫入 SQLite 資料庫
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (date, amount, category, notes)
        VALUES (?, ?, ?, ?)
    ''', (date_str, amount, category, notes))
    conn.commit()
    conn.close()
    
    print(f"✅ 成功新增：[{category}] ${amount} ({date_str}) 備註: {notes if notes else '無'}")

# ==========================================
# 2. 查詢功能 (Read)
# ==========================================
def query_expenses():
    """從資料庫查詢並顯示支出記錄"""
    print("\n--- 查詢支出記錄 ---")
    print("1. 顯示全部記錄")
    print("2. 依「分類」查詢")
    print("3. 依「日期」查詢 (例如 2026-11 或 2026-11-17)")
    choice = input("請選擇查詢方式 (1/2/3，直接按 Enter 預設顯示全部): ").strip()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if choice == '2':
        cat = input("請輸入要查詢的分類名稱: ").strip()
        cursor.execute("SELECT id, date, amount, category, notes FROM expenses WHERE category LIKE ? ORDER BY date DESC, id DESC", (f"%{cat}%",))
    elif choice == '3':
        dt = input("請輸入日期關鍵字 (YYYY-MM 或 YYYY-MM-DD): ").strip()
        cursor.execute("SELECT id, date, amount, category, notes FROM expenses WHERE date LIKE ? ORDER BY date DESC, id DESC", (f"{dt}%",))
    else:
        cursor.execute("SELECT id, date, amount, category, notes FROM expenses ORDER BY date DESC, id DESC")

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("📭 查無符合的支出記錄。")
        return False

    print("\n" + "=" * 65)
    print(f"{'ID':<5} | {'日期':<12} | {'分類':<8} | {'金額':<10} | {'備註'}")
    print("-" * 65)
    total = 0
    for row in rows:
        exp_id, date_str, amount, category, notes = row
        notes_display = notes if notes else ""
        print(f"{exp_id:<5} | {date_str:<12} | {category:<8} | ${amount:<9.2f} | {notes_display}")
        total += amount
    print("=" * 65)
    print(f"💰 共 {len(rows)} 筆記錄，總計金額: ${total:.2f}\n")
    return True

def show_all_simple():
    """快速列出所有資料供修改與刪除時對照 ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, amount, category, notes FROM expenses ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("📭 目前資料庫中沒有任何支出記錄。")
        return False

    print("\n--- 目前資料庫中的記錄 ---")
    print(f"{'ID':<5} | {'日期':<12} | {'分類':<8} | {'金額':<10} | {'備註'}")
    print("-" * 60)
    for row in rows:
        exp_id, date_str, amount, category, notes = row
        print(f"{exp_id:<5} | {date_str:<12} | {category:<8} | ${amount:<9.2f} | {notes if notes else ''}")
    print("-" * 60)
    return True

# ==========================================
# 3. 修改功能 (Update)
# ==========================================
def update_expense():
    """修改資料庫中的指定支出記錄"""
    print("\n--- 修改支出記錄 ---")
    if not show_all_simple():
        return

    target_id = input("請輸入要修改的記錄 ID (按 Enter 取消): ").strip()
    if not target_id.isdigit():
        print("已取消或 ID 格式不正確。")
        return

    exp_id = int(target_id)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT date, amount, category, notes FROM expenses WHERE id = ?", (exp_id,))
    row = cursor.fetchone()

    if not row:
        print(f"❌ 找不到 ID 為 {exp_id} 的記錄！")
        conn.close()
        return

    old_date, old_amount, old_category, old_notes = row
    print(f"\n正在修改 ID [{exp_id}] 的資料（若該項不修改，直接按 Enter 即可保留原值）：")

    # 1. 修改日期
    new_date = input(f"日期 (原值: {old_date}): ").strip()
    if not new_date:
        new_date = old_date
    else:
        try:
            datetime.strptime(new_date, '%Y-%m-%d')
        except ValueError:
            print("⚠️ 日期格式錯誤，將保留原日期。")
            new_date = old_date

    # 2. 修改金額
    new_amount_str = input(f"金額 (原值: {old_amount}): ").strip()
    if not new_amount_str:
        new_amount = old_amount
    else:
        try:
            val = float(new_amount_str)
            if val > 0:
                new_amount = val
            else:
                print("⚠️ 金額必須大於 0，將保留原金額。")
                new_amount = old_amount
        except ValueError:
            print("⚠️ 數字格式錯誤，將保留原金額。")
            new_amount = old_amount

    # 3. 修改分類
    new_category = input(f"分類 (原值: {old_category}): ").strip()
    if not new_category:
        new_category = old_category

    # 4. 修改備註
    new_notes = input(f"備註 (原值: {old_notes if old_notes else '無'}，輸入 'clear' 可清空備註): ").strip()
    if new_notes.lower() == 'clear':
        new_notes = ""
    elif not new_notes:
        new_notes = old_notes

    # 寫入修改至資料庫
    cursor.execute('''
        UPDATE expenses
        SET date = ?, amount = ?, category = ?, notes = ?
        WHERE id = ?
    ''', (new_date, new_amount, new_category, new_notes, exp_id))
    
    conn.commit()
    conn.close()
    print(f"✅ ID [{exp_id}] 的記錄已成功更新並儲存至 {DB_FILE}！")

# ==========================================
# 4. 刪除功能 (Delete)
# ==========================================
def delete_expense():
    """從資料庫刪除指定的支出記錄"""
    print("\n--- 刪除支出記錄 ---")
    if not show_all_simple():
        return

    target_id = input("請輸入要刪除的記錄 ID (按 Enter 取消): ").strip()
    if not target_id.isdigit():
        print("已取消或 ID 格式不正確。")
        return

    exp_id = int(target_id)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT date, amount, category, notes FROM expenses WHERE id = ?", (exp_id,))
    row = cursor.fetchone()

    if not row:
        print(f"❌ 找不到 ID 為 {exp_id} 的記錄！")
        conn.close()
        return

    confirm = input(f"⚠️ 確定要刪除 ID [{exp_id}] ({row[0]} [{row[2]}] ${row[1]}) 嗎？(y/n): ").strip().lower()
    if confirm == 'y':
        cursor.execute("DELETE FROM expenses WHERE id = ?", (exp_id,))
        conn.commit()
        print(f"🗑️ ID [{exp_id}] 的記錄已成功從資料庫刪除！")
    else:
        print("已取消刪除操作。")
    
    conn.close()

# ==========================================
# 主程式與互動式選單
# ==========================================
def main():
    init_db()
    while True:
        print("\n==============================")
        print("      個人支出管理系統")
        print("==============================")
        print("1. 新增支出 (Add)")
        print("2. 查詢支出 (Query)")
        print("3. 修改支出 (Update)")
        print("4. 刪除支出 (Delete)")
        print("5. 離開系統 (Exit)")
        print("==============================")
        
        choice = input("請輸入功能編號 (1-5): ").strip()
        
        if choice == '1':
            add_expense()
        elif choice == '2':
            query_expenses()
        elif choice == '3':
            update_expense()
        elif choice == '4':
            delete_expense()
        elif choice == '5':
            print(f"\n👋 感謝使用！所有資料變更皆已同步儲存至：{DB_FILE}")
            break
        else:
            print("⚠️ 無效的選項，請輸入 1 到 5 之間的數字。")

if __name__ == "__main__":
    main()