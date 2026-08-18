from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("LÀM SẠCH DỮ LIỆU - SCHOOL")
print("=" * 60)

sql = r"""
-- 1. Cấp thêm RAM tạm thời cho session
SET work_mem = '64MB';

-- 2. Tạo bảng UNLOGGED
CREATE UNLOGGED TABLE IF NOT EXISTS clean_data.school (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) DEFAULT '',
    email VARCHAR(100) DEFAULT '',
    address TEXT DEFAULT '',
    website VARCHAR(255) DEFAULT '',
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- 3. Xóa sạch dữ liệu cũ
TRUNCATE TABLE clean_data.school;

-- 4. Bơm và làm sạch dữ liệu trực tiếp bằng SQL
INSERT INTO clean_data.school (
    id,
    name,
    phone,
    email,
    address,
    website,
    created_at,
    updated_at,
    deleted_at
)
SELECT DISTINCT ON (id)
    id::BIGINT,

    -- Chuẩn hóa Tên trường: Xóa khoảng trắng thừa + NULL -> 'Không xác định'
    COALESCE(TRIM(REGEXP_REPLACE(name, '\s+', ' ', 'g')), 'Không xác định') AS name,

    -- Chuẩn hóa thông tin liên hệ: Xóa khoảng trắng + NULL -> ''
    TRIM(COALESCE(phone, '')) AS phone,
    TRIM(COALESCE(email, '')) AS email,
    TRIM(COALESCE(address, '')) AS address,
    TRIM(COALESCE(website, '')) AS website,

    -- Chuẩn hóa Ngày tháng
    created_at::TIMESTAMPTZ,
    updated_at::TIMESTAMPTZ,
    deleted_at::TIMESTAMPTZ
FROM staging.school
WHERE id IS NOT NULL
ORDER BY id, updated_at DESC NULLS LAST;
"""

with engine.begin() as conn:
    conn.execute(text(sql))
    print("✅ Đã làm sạch và lưu clean_data.school")

print("=" * 60)