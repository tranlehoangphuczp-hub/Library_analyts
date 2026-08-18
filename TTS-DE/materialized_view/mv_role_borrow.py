from sqlalchemy import create_engine, text
from config import TARGET, TARGET_SCHOOL_ID

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
CREATE MATERIALIZED VIEW IF NOT EXISTS mart.mv_role_borrow AS

SELECT
    f.school_key,
    r.role_name,
    COUNT(DISTINCT f.borrow_ticket_id) AS borrow_count
FROM library_dw.fact_borrow f
JOIN library_dw.dim_role r
    ON f.role_key = r.role_key
WHERE f.school_key = :school_key
GROUP BY
    f.school_key,
    r.role_name;

-- Unique Index để hỗ trợ REFRESH CONCURRENTLY
CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_role_borrow 
ON mart.mv_role_borrow(school_key, role_name);
"""

with engine.begin() as conn:
    conn.execute(text(sql), {"school_key": TARGET_SCHOOL_ID})

print("✅Đã tạo mv_role_borrow thành công!")