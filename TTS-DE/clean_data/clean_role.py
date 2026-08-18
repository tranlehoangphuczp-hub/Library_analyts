from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("LÀM SẠCH DỮ LIỆU - ROLE (PURE SQL TỐI ƯU)")
print("=" * 60)

# Dùng Raw String (r""") để tránh cảnh báo SyntaxWarning (\s+) của Python
sql = r"""
-- 1. Cấp thêm RAM tạm thời cho session để lọc trùng và sắp xếp
SET work_mem = '64MB';

-- 2. Tạo bảng UNLOGGED (Không ghi WAL log để tăng tốc tối đa)
CREATE UNLOGGED TABLE IF NOT EXISTS clean_data.role (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role_code VARCHAR(100),
    school_id BIGINT DEFAULT 0,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- 3. Xóa Index cũ (nếu có)
DROP INDEX IF EXISTS clean_data.idx_clean_role_code;

-- 4. Xóa sạch dữ liệu cũ trong bảng clean
TRUNCATE TABLE clean_data.role;

-- 5. Bơm và làm sạch dữ liệu trực tiếp bằng SQL
INSERT INTO clean_data.role (
    id,
    name,
    role_code,
    school_id,
    is_admin,
    created_at,
    updated_at,
    deleted_at
)
SELECT DISTINCT ON (id)
    id::BIGINT,

    -- Chuẩn hóa Tên Role: Xóa khoảng trắng thừa + Loại bỏ NULL
    TRIM(REGEXP_REPLACE(name, '\s+', ' ', 'g')) AS name,

    -- Chuẩn hóa Mã Role: Viết hoa + Xóa khoảng trắng + Xử lý NULL
    UPPER(TRIM(COALESCE(role_code, ''))),

    -- Chuẩn hóa School ID và Is Admin (nếu có trong staging)
    COALESCE(school_id::BIGINT, 0),
    COALESCE(is_admin, FALSE),

    -- Chuẩn hóa Ngày tháng
    created_at::TIMESTAMPTZ,
    updated_at::TIMESTAMPTZ,
    deleted_at::TIMESTAMPTZ
FROM staging.role
WHERE id IS NOT NULL
  AND name IS NOT NULL               -- Loại bỏ bản ghi thiếu tên role
  AND TRIM(name) != ''              -- Loại bỏ tên role bị rỗng
ORDER BY id, updated_at DESC NULLS LAST;

-- 6. ĐÁNH INDEX SAU KHI INSERT (Hỗ trợ tra cứu nhanh theo role_code)
CREATE INDEX IF NOT EXISTS idx_clean_role_code ON clean_data.role(role_code);
"""

with engine.begin() as conn:
    conn.execute(text(sql))
    print("✅ Đã làm sạch và lưu thành công vào clean_data.role")

print("=" * 60)