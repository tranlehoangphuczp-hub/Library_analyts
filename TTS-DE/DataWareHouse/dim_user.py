from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("XÂY DỰNG DIM_USER (TỐI ƯU PURE SQL)")
print("=" * 60)

sql = r"""
-- 1. Tạo bảng Dim nếu chưa có
CREATE TABLE IF NOT EXISTS library_dw.dim_user (
    user_key INT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(255),
    role_key INT,
    school_key INT,
    CONSTRAINT fk_user_role
    FOREIGN KEY(role_key)
    REFERENCES library_dw.dim_role(role_key),

    CONSTRAINT fk_user_school
    FOREIGN KEY(school_key)
    REFERENCES library_dw.dim_school(school_key)
);

-- 2. Tạo Index
CREATE INDEX IF NOT EXISTS idx_dim_user_id ON library_dw.dim_user (user_id);

-- 3. Xóa dữ liệu cũ
TRUNCATE TABLE library_dw.dim_user CASCADE;

-- 4. Bơm dòng mặc định (key = 0)
INSERT INTO library_dw.dim_user (user_key, user_id, full_name, role_key, school_key)
VALUES (0, 0, 'Không xác định', 0, 0);

-- 5. Bơm dữ liệu và Map trực tiếp khóa Dim Role & Dim School bằng SQL
INSERT INTO library_dw.dim_user (
    user_key, user_id, full_name, role_key, school_key
)
WITH clean_user AS (
    SELECT DISTINCT ON (u.id)
        u.id AS user_id,
        COALESCE(NULLIF(TRIM(REGEXP_REPLACE(u.full_name, '\s+', ' ', 'g')), ''),'Không xác định') AS full_name,
        COALESCE(dr.role_key, 0) AS role_key,
        COALESCE(ds.school_key, 0) AS school_key
    FROM clean_data.users u
    LEFT JOIN clean_data.user_role ur 
           ON u.id = ur.user_id
    LEFT JOIN library_dw.dim_role dr 
           ON ur.role_id = dr.role_id
    LEFT JOIN library_dw.dim_school ds 
           ON ur.school_id = ds.school_id
    WHERE u.id IS NOT NULL
    ORDER BY u.id
)
SELECT
    ROW_NUMBER() OVER (ORDER BY user_id) AS user_key,
    user_id,
    full_name,
    role_key,
    school_key
FROM clean_user;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("=" * 60)
print("✅ ĐÃ XÂY DỰNG DIM_USER THÀNH CÔNG")
print("=" * 60)