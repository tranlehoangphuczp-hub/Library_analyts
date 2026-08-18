from sqlalchemy import create_engine, text
from config import TARGET, TARGET_SCHOOL_ID

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

#2. Lọc theo school_id từ bảng mart.monthly_borrow
sql = """
CREATE MATERIALIZED VIEW IF NOT EXISTS mart.mv_monthly_borrow AS
SELECT
    f.school_key,
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.borrow_ticket_id) AS borrow_count
FROM library_dw.fact_borrow f
JOIN library_dw.dim_date d
    ON f.borrow_date_key = d.date_key
WHERE f.school_key = :school_key

GROUP BY
    f.school_key,
    d.year,
    d.month,
    d.month_name;

-- 3. Tạo UNIQUE INDEX trên các cột định danh (school_key + năm/tháng)
CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_monthly_borrow 
ON mart.mv_monthly_borrow(school_key, year, month);
"""

with engine.begin() as conn:
    # 👈 4. Truyền tham số school_id vào đây
    conn.execute(text(sql), {"school_key": TARGET_SCHOOL_ID})

print("✅Đã tạo mv_monthly_borrow thành công!")