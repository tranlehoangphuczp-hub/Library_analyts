from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("XÂY DỰNG DIM_SUBJECT (TỐI ƯU PURE SQL)")
print("=" * 60)

sql = r"""
-- 1. Tạo bảng Dim nếu chưa có
CREATE TABLE IF NOT EXISTS library_dw.dim_subject (
    subject_key INT PRIMARY KEY,
    subject_id INT NOT NULL,
    subject_name VARCHAR(255),
    code VARCHAR(100)
);

-- 2. Tạo Index
CREATE INDEX IF NOT EXISTS idx_dim_subject_id ON library_dw.dim_subject (subject_id);

-- 3. Xóa dữ liệu cũ
TRUNCATE TABLE library_dw.dim_subject CASCADE;

-- 4. Bơm dòng mặc định (key = 0)
INSERT INTO library_dw.dim_subject (subject_key, subject_id, subject_name, code)
VALUES (0, 0, 'Không xác định', '');

-- 5. Bơm dữ liệu chuẩn hóa
INSERT INTO library_dw.dim_subject (
    subject_key, subject_id, subject_name, code
)
WITH clean_subject AS (
    SELECT DISTINCT ON (id)
        id AS subject_id,
        COALESCE( NULLIF(TRIM(REGEXP_REPLACE(name, '\s+', ' ', 'g')), ''),'Không xác định') AS subject_name,
        UPPER(TRIM(COALESCE(code, ''))) AS code
    FROM clean_data.library_subject
    WHERE id IS NOT NULL
    ORDER BY id
)
SELECT
    ROW_NUMBER() OVER (ORDER BY subject_id) AS subject_key,
    subject_id, subject_name, code
FROM clean_subject;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("=" * 60)
print("✅ ĐÃ XÂY DỰNG DIM_SUBJECT THÀNH CÔNG")
print("=" * 60)