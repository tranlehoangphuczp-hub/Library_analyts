from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
-- 1. TỐI ƯU TỐC ĐỘ: Tạo Index hỗ trợ JOIN và GROUP BY theo sách mượn
CREATE INDEX IF NOT EXISTS idx_fact_school_book 
ON library_dw.fact_borrow
(
    school_key,
    book_key
);

CREATE TABLE IF NOT EXISTS mart.top_book (
    school_id INT,
    title VARCHAR(500),
    borrow_count INT,
    PRIMARY KEY (school_id, title)
);

TRUNCATE TABLE mart.top_book;

INSERT INTO mart.top_book
(
    school_id,
    title,
    borrow_count
)

SELECT
    sc.school_id,
    b.title,
    SUM(f.book_count) AS borrow_count
FROM library_dw.fact_borrow f

JOIN library_dw.dim_book b
    ON f.book_key = b.book_key

JOIN library_dw.dim_school sc
    ON f.school_key = sc.school_key

GROUP BY
    sc.school_id,
    b.title;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("✅ Updated mart.top_book successfully!")