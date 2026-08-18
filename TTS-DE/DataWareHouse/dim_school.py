from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("XÂY DỰNG DIM_SCHOOL (TỐI ƯU PURE SQL)")
print("=" * 60)

sql = r"""
-- 1. Tạo bảng Dim nếu chưa có
CREATE TABLE IF NOT EXISTS library_dw.dim_school (
    school_key INT PRIMARY KEY,
    school_id INT NOT NULL,
    school_name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(100),
    address VARCHAR(500),
    website VARCHAR(255),
    province_id INT
);

-- 2. Tạo Index
CREATE INDEX IF NOT EXISTS idx_dim_school_id ON library_dw.dim_school (school_id);

-- 3. Xóa dữ liệu cũ
TRUNCATE TABLE library_dw.dim_school CASCADE;

-- 4. Bơm dòng mặc định (key = 0)
INSERT INTO library_dw.dim_school (school_key, school_id, school_name, phone, email, address, website, province_id)
VALUES (0, 0, 'Không xác định', '', '', '', '', 0);

-- 5. Bơm dữ liệu trường học có mượn sách 1 năm gần nhất (Dùng school_id làm school_key)
INSERT INTO library_dw.dim_school (
    school_key, school_id, school_name, phone, email, address, website, province_id
)
WITH clean_school AS (
    SELECT DISTINCT ON (s.id)
        s.id AS school_id,
        COALESCE( NULLIF(TRIM(REGEXP_REPLACE(s.name,'\s+',' ','g')), ''),'Không xác định') AS school_name,       
        TRIM(COALESCE(s.phone, '')) AS phone,
        TRIM(COALESCE(s.email, '')) AS email,
        TRIM(COALESCE(s.address, '')) AS address,
        TRIM(COALESCE(s.website, '')) AS website,
        COALESCE(s.province_id, 0) AS province_id
    FROM clean_data.school s
    INNER JOIN clean_data.library_borrow_ticket bt ON s.id = bt.school_id
    WHERE s.id IS NOT NULL
      AND bt.actual_borrow_date >= CURRENT_DATE - INTERVAL '1 year'
    ORDER BY s.id
)
SELECT
    school_id AS school_key, -- 👈 Dùng chính school_id làm school_key (6, 39, 55...)
    school_id, 
    school_name, 
    phone, 
    email, 
    address, 
    website, 
    province_id
FROM clean_school;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("=" * 60)
print("✅ ĐÃ XÂY DỰNG DIM_SCHOOL THÀNH CÔNG")
print("=" * 60)