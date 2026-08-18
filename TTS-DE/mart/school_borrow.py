from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
-- 1. TỐI ƯU TỐC ĐỘ: Tạo Index hỗ trợ JOIN giữa fact_borrow và dim_school
CREATE INDEX IF NOT EXISTS idx_fact_school_key 
ON library_dw.fact_borrow (
    school_key,
    borrow_ticket_id
);

CREATE TABLE IF NOT EXISTS mart.school_borrow (
    school_id INT,
    school_name VARCHAR(255),
    borrow_count INT,
    PRIMARY KEY (school_id)
);

TRUNCATE TABLE mart.school_borrow;

INSERT INTO mart.school_borrow(
    school_id,
    school_name,
    borrow_count
)

SELECT
    s.school_id,
    s.school_name,
    COUNT(DISTINCT f.borrow_ticket_id) AS borrow_count
FROM library_dw.fact_borrow f

JOIN library_dw.dim_school s
    ON f.school_key = s.school_key
GROUP BY
    s.school_id,
    s.school_name;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("✅ Updated mart.school_borrow successfully!")