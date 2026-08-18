from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("LÀM SẠCH DỮ LIỆU - USER_ROLE")
print("=" * 60)

sql = r"""
-- 1. Cấp thêm RAM tạm thời cho session
SET work_mem = '64MB';

-- 2. Tạo bảng UNLOGGED
CREATE UNLOGGED TABLE IF NOT EXISTS clean_data.user_role (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- 3. Xóa Index cũ (nếu có)
DROP INDEX IF EXISTS clean_data.idx_clean_ur_user_role;
DROP INDEX IF EXISTS clean_data.idx_clean_ur_role_id;

-- 4. Xóa sạch dữ liệu cũ
TRUNCATE TABLE clean_data.user_role;

-- 5. Bơm và làm sạch dữ liệu trực tiếp bằng SQL
INSERT INTO clean_data.user_role (
    id,
    user_id,
    role_id,
    is_active,
    created_at,
    updated_at,
    deleted_at
)
SELECT DISTINCT ON (id)
    id::BIGINT,
    user_id::BIGINT,
    role_id::BIGINT,

    -- Chuẩn hóa trạng thái active (NULL -> False)
    COALESCE(is_active, FALSE) AS is_active,

    -- Chuẩn hóa Ngày tháng
    created_at::TIMESTAMPTZ,
    updated_at::TIMESTAMPTZ,
    deleted_at::TIMESTAMPTZ
FROM staging.user_role
WHERE id IS NOT NULL
  AND user_id IS NOT NULL  -- Loại bỏ bản ghi mồ côi (thiếu ID người dùng)
  AND role_id IS NOT NULL  -- Loại bỏ bản ghi mồ côi (thiếu ID vai trò)
ORDER BY id, updated_at DESC NULLS LAST;

-- 6. ĐÁNH INDEX SAU KHI INSERT (Siêu quan trọng cho các phép JOIN giữa User và Role)
CREATE INDEX IF NOT EXISTS idx_clean_ur_user_role ON clean_data.user_role(user_id, role_id);
CREATE INDEX IF NOT EXISTS idx_clean_ur_role_id ON clean_data.user_role(role_id);
"""

with engine.begin() as conn:
    conn.execute(text(sql))
    print("✅ Đã làm sạch và lưu clean_data.user_role")

print("=" * 60)