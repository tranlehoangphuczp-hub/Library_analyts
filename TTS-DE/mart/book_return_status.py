from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
-- 1. TỐI ƯU TỐC ĐỘ: Tạo Index hỗ trợ GROUP BY theo school_id và trạng thái trả sách
CREATE INDEX IF NOT EXISTS idx_fact_school_return 
ON library_dw.fact_borrow(
    school_key,
    return_date_key
);

CREATE TABLE IF NOT EXISTS mart.book_return_status(
    school_key INT,
    status VARCHAR(50),
    quantity INT,
    PRIMARY KEY (school_key, status)
);

TRUNCATE TABLE mart.book_return_status;

INSERT INTO mart.book_return_status(
    school_key,
    status,
    quantity
)
SELECT
    school_key,
    CASE
        WHEN return_date_key = 0 
        THEN 'Chưa trả'
        ELSE 'Đã trả'
    END AS status,
    COUNT(*) AS quantity
FROM library_dw.fact_borrow
GROUP BY
    school_key,
    CASE
        WHEN return_date_key = 0 
        THEN 'Chưa trả'
        ELSE 'Đã trả'
    END;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("✅ Updated mart.return_status successfully!")