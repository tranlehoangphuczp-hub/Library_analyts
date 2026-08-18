from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("LÀM SẠCH DỮ LIỆU - LIBRARY_BOOK")
print("=" * 60)

sql = r"""
-- 1. Tạo bảng clean nếu chưa có (Có Primary Key & Index)
CREATE TABLE IF NOT EXISTS clean_data.library_book (
    id INT PRIMARY KEY,
    title VARCHAR(500),
    subject_id INT,
    school_id INT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_clean_book_subject ON clean_data.library_book(subject_id);
CREATE INDEX IF NOT EXISTS idx_clean_book_school ON clean_data.library_book(school_id);

-- 2. Xóa dữ liệu cũ trong clean_data
TRUNCATE TABLE clean_data.library_book;

-- 3. Bơm dữ liệu đã làm sạch trực tiếp trong Postgres
INSERT INTO clean_data.library_book (id, title, subject_id, school_id, created_at, updated_at)
SELECT DISTINCT ON (id)
    id,
    TRIM(REGEXP_REPLACE(title, '\s+', ' ', 'g')) AS title,
    COALESCE(subject_id, 0),
    COALESCE(school_id, 0),
    created_at,
    updated_at
FROM staging.library_book
WHERE id IS NOT NULL 
  AND title IS NOT NULL 
  AND TRIM(title) <> ''
ORDER BY id;
"""

with engine.begin() as conn:
    res = conn.execute(text(sql))
    print(f"✅ Đã xử lý và lưu clean_data.library_book")

print("=" * 60)