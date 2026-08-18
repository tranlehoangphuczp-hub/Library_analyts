from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
-- 1. TỐI ƯU TỐC ĐỘ: Tạo Index hỗ trợ JOIN và GROUP BY theo ngày/tháng mượn
CREATE INDEX IF NOT EXISTS idx_fact_school_date 
ON library_dw.fact_borrow (
    school_key,
    borrow_date_key
);

CREATE TABLE IF NOT EXISTS mart.monthly_borrow(
    school_key INT,
    year INT,
    month INT,
    month_name VARCHAR(20),
    borrow_count INT,
    PRIMARY KEY (school_key, year, month)
);

TRUNCATE TABLE mart.monthly_borrow;

INSERT INTO mart.monthly_borrow(
    school_key,
    year,
    month,
    month_name,
    borrow_count
)

SELECT
    f.school_key,
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.borrow_ticket_id) AS borrow_count
FROM library_dw.fact_borrow f

JOIN library_dw.dim_date d
    ON f.borrow_date_key = d.date_key
GROUP BY

    f.school_key,
    d.year,
    d.month,
    d.month_name;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("✅ Updated mart.monthly_borrow successfully!")