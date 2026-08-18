from sqlalchemy import create_engine, text
from config import TARGET
engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)
print("=" * 60)
print("XÂY DỰNG DIM_BOOK (TỐI ƯU PURE SQL)")
print("=" * 60)
# Dùng Raw String (r""") để tránh Cảnh báo SyntaxWarning (\s+) của Python
sql = r"""
-- 1. Tạo khung bảng Dim nếu chưa có
CREATE TABLE IF NOT EXISTS library_dw.dim_book (
    book_key INT PRIMARY KEY,
    book_id INT NOT NULL,
    title VARCHAR(500),
    subject_key INT,
    school_key INT,
    year_publish INT,
    author_id INT,
    publisher_id INT,

    CONSTRAINT fk_book_subject
    FOREIGN KEY(subject_key)
    REFERENCES library_dw.dim_subject(subject_key),

    CONSTRAINT fk_book_school
    FOREIGN KEY(school_key)
    REFERENCES library_dw.dim_school(school_key)
);
-- Index
CREATE INDEX IF NOT EXISTS idx_dim_book_id
ON library_dw.dim_book(book_id);

-- Xóa dữ liệu cũ
TRUNCATE TABLE library_dw.dim_book CASCADE;

-- Unknown Row
INSERT INTO library_dw.dim_book (
    book_key,
    book_id,
    title,
    subject_key,
    school_key,
    year_publish,
    author_id,
    publisher_id
)
VALUES ( 0, 0,
    'Không xác định', 0, 0, NULL, 0, 0
);
    
-- Load dữ liệu
INSERT INTO library_dw.dim_book (
    book_key,
    book_id,
    title,
    subject_key,
    school_key,
    year_publish,
    author_id,
    publisher_id
)

WITH clean_books AS (
    SELECT DISTINCT ON (b.id)
        b.id AS book_id,
        COALESCE(
            NULLIF(
                TRIM(REGEXP_REPLACE(b.title,'\s+',' ','g')),'')
                    ,'Không xác định') AS title,
        COALESCE(ds.subject_key,0) AS subject_key,
        COALESCE(dsc.school_key,0) AS school_key, b.year_publish AS year_publish,
        COALESCE(b.author_id,0) AS author_id,
        COALESCE(b.publisher_id,0) AS publisher_id
    FROM clean_data.library_book b
    LEFT JOIN library_dw.dim_subject ds
        ON b.subject_id = ds.subject_id
    LEFT JOIN library_dw.dim_school dsc
        ON b.school_id = dsc.school_id
    ORDER BY b.id
)

SELECT
    ROW_NUMBER() OVER(ORDER BY book_id) AS book_key,
    book_id,
    title,
    subject_key,
    school_key,
    year_publish,
    author_id,
    publisher_id
FROM clean_books;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("=" * 60)
print("✅ ĐÃ XÂY DỰNG DIM_BOOK THÀNH CÔNG ")
print("=" * 60)