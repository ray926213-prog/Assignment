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

def add_expense():
    """新增一筆支出記錄到資料庫"""
    print("\n--- 新增支出記錄 ---")
    
    # 1. 日期輸入與驗證
    date_str = input("請輸入日期 (格式 YYYY-MM-DD，直接按 Enter 預設為今天): ").strip()
    if not date_str:
        date_str = datetime.today().strftime('%Y-%m-%d')
    else:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(" 日期格式錯誤！將自動使用今天的日期。")
            date_str = datetime.today().strftime('%Y-%m-%d')

    # 2. 金額輸入與驗證
    while True:
        try:
            amount = float(input("請輸入金額: "))
            if amount <= 0:
                print(" 金額必須大於 0，請重新輸入。")
                continue
            break
        except ValueError:
            print(" 請輸入有效的數字！")

    # 3. 分類輸入 (支援中文)
    category = input("請輸入分類 (例如: 食物, 交通, 娛樂): ").strip()
    if not category:
        category = "其他"

    # 4. 備註輸入 (選填，支援中文)
    notes = input("請輸入備註 (選填，可直接略過): ").strip()

    # 寫入 SQLite 資料庫
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO expenses (date, amount, category, notes)
        VALUES (?, ?, ?, ?)
    ''', (date_str, amount, category, notes))
    
    conn.commit()
    conn.close()
    
    print(f" 成功新增：[{category}] ${amount} ({date_str}) 備註: {notes if notes else '無'}")

if __name__ == "__main__":
    # 初始化資料庫
    init_db()
    
    # 互動式選單
    while True:
        add_expense()
        cont = input("\n是否繼續新增支出？(y/n): ").strip().lower()
        if cont != 'y':
            print("\n 輸入結束！資料已成功儲存至 SQLite 資料庫：", DB_FILE)
            break