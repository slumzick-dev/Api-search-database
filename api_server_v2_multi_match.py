from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, JSONResponse
import sqlite3, io, os
from typing import Optional, List

DB_DIR = "db_shards"
MAX_LIMIT = 50000  # ป้องกันโหลดหนักเกินไป

app = FastAPI(title="Logs API", version="3.4 (multi-DB + MATCH + max_limit)")


# ===== Utility =====
def search_one_db(db_path: str, keyword: str, table: str, limit: Optional[int]):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # wrap keyword ถ้ามี . หรือ @
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

    # sort เพื่อให้ผลลัพธ์ deterministic
    db_files = sorted([os.path.join(DB_DIR, f) for f in os.listdir(DB_DIR) if f.endswith(".db")])

    for db_path in db_files:
        rows = search_one_db(db_path, keyword, table, limit)
        results.extend(rows)

        if limit and len(results) >= limit:
            return results[:limit]

    return results


# ===== API =====
@app.get("/search")
def search(
    q: str = Query(..., description="คำค้นหา เช่น facebook.com"),
    mode: str = Query("clean", description="เลือกตาราง: clean หรือ raw"),
    limit: Optional[int] = Query(
        default=None,
        description=f"จำนวนผลลัพธ์สูงสุด (ไม่ใส่ = ดึงทั้งหมด, สูงสุด {MAX_LIMIT})"
    ),
    d: int = Query(1, description="รูปแบบผลลัพธ์: 0=user:pass, 1=url:user:pass"),
):
    # enforce max_limit
    if limit is not None and limit > MAX_LIMIT:
        limit = MAX_LIMIT

    results = search_all_dbs(q, mode, limit)

    if d == 0:
        formatted = [f"{r['username']}:{r['password']}" for r in results]
    else:
        formatted = [f"{r['url']}:{r['username']}:{r['password']}" for r in results]

    return JSONResponse(
        content={
            "keyword": q,
            "mode": mode,
            "count": len(results),
            "results": formatted,
        }
    )


@app.get("/export")
def export(
    q: str = Query(..., description="คำค้นหา เช่น facebook.com"),
    mode: str = Query("clean", description="เลือกตาราง: clean หรือ raw"),
    limit: Optional[int] = Query(
        default=None,
        description=f"จำนวนผลลัพธ์สูงสุด (ไม่ใส่ = ดึงทั้งหมด, สูงสุด {MAX_LIMIT})"
    ),
    d: int = Query(1, description="รูปแบบผลลัพธ์: 0=user:pass, 1=url:user:pass"),
):
    if limit is not None and limit > MAX_LIMIT:
        limit = MAX_LIMIT

    results = search_all_dbs(q, mode, limit)

    output = io.StringIO()
    for row in results:
        if d == 0:
            line = f"{row['username']}:{row['password']}\n"
        else:
            line = f"{row['url']}:{row['username']}:{row['password']}\n"
        output.write(line)

    output.seek(0)
    headers = {"Content-Disposition": f'attachment; filename="{mode}_{q}.txt"'}
    return StreamingResponse(iter([output.getvalue()]), media_type="text/plain", headers=headers)
