from sqlalchemy import create_engine, text
from config import TARGET, TARGET_SCHOOL_ID

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
CREATE MATERIALIZED VIEW IF NOT EXISTS mart.mv_book_return_status AS
SELECT
    school_key,
    status,
    quantity
FROM mart.book_return_status;

-- Tạo Unique Index đúng tên bảng để dùng REFRESH CONCURRENTLY sau này không bị khóa bảng
CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_book_return_status 
ON mart.mv_book_return_status(school_key, status);
"""

with engine.begin() as conn:
    conn.execute(text(sql), {"school_key": TARGET_SCHOOL_ID})

print("✅Đã tạo mv_book_return_status")