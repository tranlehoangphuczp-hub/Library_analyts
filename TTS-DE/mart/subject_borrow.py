from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
-- 1. TỐI ƯU TỐC ĐỘ: Tạo Index hỗ trợ JOIN và GROUP BY theo môn/chủ đề sách
CREATE INDEX IF NOT EXISTS idx_fact_school_subject 
ON library_dw.fact_borrow (
    school_key,
    subject_key
);

CREATE TABLE IF NOT EXISTS mart.subject_borrow (
    school_id INT,
    subject_name VARCHAR(255),
    borrow_count INT,
    PRIMARY KEY (school_id, subject_name)
);

TRUNCATE TABLE mart.subject_borrow;

INSERT INTO mart.subject_borrow(
    school_id,
    subject_name,
    borrow_count
)

SELECT
    sc.school_id,
    s.subject_name,
    SUM(f.book_count) AS borrow_count
FROM library_dw.fact_borrow f

JOIN library_dw.dim_subject s
    ON f.subject_key = s.subject_key
JOIN library_dw.dim_school sc
    ON f.school_key = sc.school_key
GROUP BY
    sc.school_id,
    s.subject_name;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("✅ Updated mart.subject_borrow successfully!")