from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("LÀM SẠCH DỮ LIỆU - LIBRARY_SUBJECT")
print("=" * 60)

# Dùng Raw String (r""") để tránh cảnh báo SyntaxWarning (\s+) của Python
sql = r"""
-- 1. Cấp thêm RAM tạm thời cho session
SET work_mem = '64MB';

-- 2. Tạo bảng UNLOGGED (Không ghi WAL log để tăng tốc tối đa)
CREATE UNLOGGED TABLE IF NOT EXISTS clean_data.library_subject (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100),
    description TEXT,
    borrow_count INT DEFAULT 0,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- 3. Xóa Index cũ (nếu có)
DROP INDEX IF EXISTS clean_data.idx_clean_subject_code;

-- 4. Xóa sạch dữ liệu cũ trong bảng clean
TRUNCATE TABLE clean_data.library_subject;

-- 5. Bơm và làm sạch dữ liệu trực tiếp bằng SQL
INSERT INTO clean_data.library_subject (
    id,
    name,
    code,
    description,
    borrow_count,
    created_at,
    updated_at,
    deleted_at
)
SELECT DISTINCT ON (id)
    id::BIGINT,

    -- Chuẩn hóa Tên chủ đề: Xóa khoảng trắng thừa + Loại bỏ NULL
    TRIM(REGEXP_REPLACE(name, '\s+', ' ', 'g')) AS name,

    -- Chuẩn hóa Mã chủ đề: Viết hoa + Xóa khoảng trắng + Xử lý NULL
    UPPER(TRIM(COALESCE(code, ''))),

    -- Chuẩn hóa Mô tả: Xóa khoảng trắng thừa + Xử lý NULL
    TRIM(COALESCE(description, '')),

    -- Chuẩn hóa Lượt mượn: Ép kiểu số, NULL -> 0
    COALESCE(borrow_count, 0),

    -- Chuẩn hóa Ngày tháng
    created_at::TIMESTAMPTZ,
    updated_at::TIMESTAMPTZ,
    deleted_at::TIMESTAMPTZ
FROM staging.library_subject
WHERE id IS NOT NULL
  AND name IS NOT NULL               -- Loại bỏ bản ghi thiếu tên chủ đề
  AND TRIM(name) != ''              -- Loại bỏ tên chủ đề bị rỗng
ORDER BY id, updated_at DESC NULLS LAST;

-- 6. ĐÁNH INDEX SAU KHI INSERT (Tối ưu cho JOIN sang dim_subject)
CREATE INDEX IF NOT EXISTS idx_clean_subject_code ON clean_data.library_subject(code);
"""

with engine.begin() as conn:
    conn.execute(text(sql))
    print("✅ Đã làm sạch và lưu clean_data.library_subject")

print("=" * 60)