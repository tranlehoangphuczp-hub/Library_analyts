from sqlalchemy import create_engine, text
from config import TARGET, TARGET_SCHOOL_ID

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
-- Tạo Materialized View tổng quan nếu chưa tồn tại
CREATE MATERIALIZED VIEW IF NOT EXISTS mart.mv_borrow_overview AS
WITH borrow_ticket AS (
    SELECT
        school_key,
        borrow_ticket_id,
        user_key,
        SUM(book_count) AS total_book,
        MAX(
            CASE
                WHEN return_date_key = 0 THEN 1
                ELSE 0
            END) AS has_unreturned
    FROM library_dw.fact_borrow
    GROUP BY
        school_key,
        borrow_ticket_id,
        user_key
)
SELECT
    school_key,
    SUM(total_book) AS total_book,
    COUNT(*) AS total_borrow,
    COUNT(DISTINCT user_key) AS total_reader,
    COUNT(CASE WHEN has_unreturned = 0 THEN 1 END) AS completed_return,
    COUNT(CASE WHEN has_unreturned = 1 THEN 1 END) AS not_return
FROM borrow_ticket
GROUP BY school_key;

-- Tạo Unique Index
CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_borrow_overview 
ON mart.mv_borrow_overview(school_key);

"""

with engine.begin() as conn:
    conn.execute(text(sql), {"school_key": TARGET_SCHOOL_ID})
print("✅ Đã tạo và cập nhật mv_borrow_overview thành công!")