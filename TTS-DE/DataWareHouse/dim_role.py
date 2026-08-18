from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("XÂY DỰNG DIM_ROLE (TỐI ƯU PURE SQL)")
print("=" * 60)

sql = r"""
-- 1. Tạo bảng Dim nếu chưa có
CREATE TABLE IF NOT EXISTS library_dw.dim_role (
    role_key INT PRIMARY KEY,
    role_id INT,
    role_name VARCHAR(255),
    role_code VARCHAR(100),
    school_key INT,
    CONSTRAINT fk_role_school
    FOREIGN KEY(school_key)
    REFERENCES library_dw.dim_school(school_key)
);

CREATE INDEX IF NOT EXISTS idx_dim_role_id
ON library_dw.dim_role(role_id);
TRUNCATE TABLE library_dw.dim_role CASCADE;
INSERT INTO library_dw.dim_role (
    role_key,
    role_id,
    role_name,
    role_code,
    school_key
)
VALUES (
    0,
    0,
    'Không xác định',
    '',
    0
);

INSERT INTO library_dw.dim_role (
    role_key,
    role_id,
    role_name,
    role_code,
    school_key
)
WITH clean_role AS (
    SELECT DISTINCT ON (r.id) 
        r.id AS role_id,
        COALESCE( NULLIF(TRIM(REGEXP_REPLACE(r.name,'\s+',' ','g')),''),'Không xác định') AS role_name,
        UPPER(TRIM(COALESCE(r.role_code,''))) AS role_code,
        COALESCE(ds.school_key,0) AS school_key
    FROM clean_data.role r
    LEFT JOIN library_dw.dim_school ds
           ON r.school_id = ds.school_id
    WHERE r.id IS NOT NULL
    ORDER BY r.id
)

SELECT
    ROW_NUMBER() OVER (ORDER BY role_id) AS role_key,
    role_id,
    role_name,
    role_code,
    school_key
FROM clean_role;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("=" * 60)
print("✅ ĐÃ XÂY DỰNG DIM_ROLE THÀNH CÔNG")
print("=" * 60)