# build_index_v3.py
import sqlite3, os, re
from normalize import parse_line
from tqdm import tqdm   # pip install tqdm

DB_FILE = "logs.db"
TEXT_DIR = "txt_files"
BATCH_SIZE = 20000   # จำนวน insert ต่อรอบ (ปรับได้ตาม RAM/CPU)

# ========= ฟิลเตอร์ user/pass =========
def is_valid_user(u: str):
    """เช็คว่า user น่าจะเป็น email หรือเบอร์โทร"""
    if not u:
        return False
    if re.match(r"^[\w\.-]+@[\w\.-]+$", u):   # email
        return True
    if re.match(r"^\d{6,15}$", u):            # phone (6–15 ตัวเลข)
        return True
    if len(u) >= 4:                           # username ปกติ
        return True
    return False

def is_valid_pass(p: str):
    """เช็คว่า password ไม่น้อยกว่า 6 ตัว"""
    return p is not None and len(p) >= 6

# ========= สร้าง DB =========
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # speed tuning
    c.execute("PRAGMA synchronous = OFF;")
    c.execute("PRAGMA journal_mode = MEMORY;")
    c.execute("PRAGMA temp_store = MEMORY;")
    c.execute("PRAGMA cache_size = 100000;")

    # ตาราง clean
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS logs_clean
                 USING fts5(url, username, password)""")
    # ตาราง raw
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS logs_raw
                 USING fts5(url, username, password)""")
    conn.commit()
    return conn, c

# ========= import ไฟล์ =========
def import_txt_files():
    conn, c = init_db()

    for root, _, files in os.walk(TEXT_DIR):
        for fname in files:
            if not fname.endswith(".txt"):
                continue
            path = os.path.join(root, fname)

            # นับบรรทัดก่อน
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                total_lines = sum(1 for _ in f)

            print(f"\n📂 Import {fname} ({total_lines:,} lines)")

            clean_batch, raw_batch = [], []

            with open(path, "r", encoding="utf-8", errors="ignore") as f, tqdm(total=total_lines, unit=" lines") as pbar:
                for line in f:
                    parsed = parse_line(line)
                    if parsed:
                        url, user, pw = parsed
                        if is_valid_user(user) and is_valid_pass(pw):
                            clean_batch.append((url, user, pw))
                        else:
                            raw_batch.append((url, user, pw))

                    if len(clean_batch) >= BATCH_SIZE:
                        c.executemany("INSERT INTO logs_clean (url, username, password) VALUES (?,?,?)", clean_batch)
                        clean_batch.clear()

                    if len(raw_batch) >= BATCH_SIZE:
                        c.executemany("INSERT INTO logs_raw (url, username, password) VALUES (?,?,?)", raw_batch)
                        raw_batch.clear()

                    pbar.update(1)

            # flush ค่าที่เหลือ
            if clean_batch:
                c.executemany("INSERT INTO logs_clean (url, username, password) VALUES (?,?,?)", clean_batch)
            if raw_batch:
                c.executemany("INSERT INTO logs_raw (url, username, password) VALUES (?,?,?)", raw_batch)

            conn.commit()
            print(f"✅ Done {fname}")

    # optimize index
    c.execute("PRAGMA optimize;")
    conn.close()

if __name__ == "__main__":
    if not os.path.exists(TEXT_DIR):
        os.makedirs(TEXT_DIR)
        print(f"⚠️ สร้างโฟลเดอร์ {TEXT_DIR} แล้ว - กรุณาใส่ไฟล์ .txt ข้างใน")
    else:
        import_txt_files()
        print(f"\n📦 Import เสร็จ -> {DB_FILE} พร้อมใช้งานแล้ว")
