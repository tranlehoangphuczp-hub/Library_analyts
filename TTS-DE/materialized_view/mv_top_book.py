from sqlalchemy import create_engine, text
from config import TARGET, TARGET_SCHOOL_ID

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
CREATE MATERIALIZED VIEW IF NOT EXISTS mart.mv_top_book AS
WITH book_rank AS
(
    SELECT
        f.school_key,
        b.title,
        SUM(f.book_count) AS borrow_count,
        ROW_NUMBER() OVER(
            PARTITION BY f.school_key
            ORDER BY SUM(f.book_count) DESC
        ) AS rank
    FROM library_dw.fact_borrow f
    JOIN library_dw.dim_book b
        ON f.book_key = b.book_key
    GROUP BY
        f.school_key,
        b.title
)
SELECT
    school_key,
    title,
    borrow_count
FROM book_rank
WHERE rank <= 10;
    
-- Unique Index hỗ trợ REFRESH CONCURRENTLY
CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_top_book 
ON mart.mv_top_book(school_key, title);
"""

with engine.begin() as conn:
    conn.execute(text(sql), {"school_key": TARGET_SCHOOL_ID})

print("✅Đã tạo mv_top_book thành công!")