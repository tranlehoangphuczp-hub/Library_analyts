from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
-- 1. Tạo Materialized View cho thống kê mượn theo môn học
CREATE MATERIALIZED VIEW IF NOT EXISTS mart.mv_subject_borrow AS
SELECT
    school_id AS school_key,  -- Đổi tên school_id thành school_key để đồng bộ chuẩn chung
    subject_name,
    borrow_count
FROM mart.subject_borrow;

-- 2. Tạo Unique Index đúng với các cột thực tế trong bảng
CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_subject_borrow 
ON mart.mv_subject_borrow(school_key, subject_name);

"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("✅ Đã tạo và cập nhật mv_subject_borrow thành công!")