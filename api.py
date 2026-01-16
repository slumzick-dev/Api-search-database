from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
import sqlite3, os
from typing import Optional, List
import re

DB_DIR = "db_shards"
MAX_LIMIT = 50000  # ป้องกันโหลดหนักเกินไป

# ✅ หลาย API Key
API_KEYS = {
    "dinoshopkey_dna9s",
    "dinoshopkey_dgh9s",
    "dinoshopkey_dhj9k",
    "dinoshopkey_dna99",
    "dinoshopkey_dn9js",
    "dinoshopkey_dns8s",
    "dinoshopkey_vvip"
}

app = FastAPI(title="Logs API", version="3.6 (fix JSON ensure_ascii)")


# ===== Utility =====
def sanitize_filename(name: str) -> str:
    name = name.replace(" ", "_")
    return re.sub(r'[^A-Za-z0-9ก-ฮะ-์ _-]', "_", name)


def search_one_db(db_path: str, keyword: str, table: str, limit: Optional[int]):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    safe_kw = f'"{keyword}"'
    query = f"SELECT url, username, password FROM {table} WHERE url MATCH ?"
    params = [safe_kw]

    if limit is not None:
        query += f" LIMIT {limit}"

    try:
        rows = c.execute(query, params).fetchall()
    except Exception as e:
        print(f"❌ Error in {db_path}: {e}")
        rows = []

    conn.close()
    return [dict(r) for r in rows]


def search_all_dbs(keyword: str, mode: str, limit: Optional[int]):
    table = "logs_clean" if mode == "clean" else "logs_raw"
    results: List[dict] = []
    db_files = sorted([os.path.join(DB_DIR, f) for f in os.listdir(DB_DIR) if f.endswith(".db")])

    for db_path in db_files:
        rows = search_one_db(db_path, keyword, table, limit)
        results.extend(rows)

        if limit and len(results) >= limit:
            return results[:limit]

    return results


# ===== API (เหมือน dump.php) =====
@app.get("/dump.php")
def dump(
    q: str = Query("", description="คำค้นหา เช่น facebook.com"),
    t: int = Query(1, description="0=user:pass, 1=url:user:pass"),
    k: str = Query("", description="API Key"),
    mode: str = Query("clean", description="เลือกตาราง: clean หรือ raw"),
    limit: Optional[int] = Query(None, description=f"จำนวนผลลัพธ์สูงสุด (ไม่ใส่=ดึงทั้งหมด, สูงสุด {MAX_LIMIT})"),
):
    # ถ้าไม่มี q หรือ k → redirect
    if q == "" or k == "":
        return RedirectResponse(url="/log/")

    # ตรวจสอบ API Key
    if k not in API_KEYS:
        return JSONResponse(status_code=403, content={"status": "error", "message": "Invalid API key"})

    # enforce max_limit
    if limit is not None and limit > MAX_LIMIT:
        limit = MAX_LIMIT

    results = search_all_dbs(q, mode, limit)

    if not results:
        return JSONResponse(status_code=404, content={"status": "error", "message": "ยังไม่มีข้อมูล"})

    # format output
    if t == 0:
        formatted = [f"{r['username']}:{r['password']}" for r in results]
    else:
        formatted = [f"{r['url']}:{r['username']}:{r['password']}" for r in results]

    safe_name = sanitize_filename(q) + ".txt"
    lines = len(formatted)

    response = {
        "status": "success",
        "query": q,
        "type": t,
        "file": safe_name,
        "lines": lines,
        "data": "\n".join(formatted)
    }

    # ✅ ใช้ jsonable_encoder + ไม่ต้อง ensure_ascii
    return JSONResponse(content=jsonable_encoder(response), media_type="application/json")