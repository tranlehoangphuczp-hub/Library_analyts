from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("LÀM SẠCH DỮ LIỆU - LIBRARY_BORROW_TICKET")
print("=" * 60)

sql = r"""
-- 1. Tăng RAM tạm thời cho session này để Sort / DISTINCT siêu nhanh trên RAM
SET work_mem = '64MB';

-- 2. Tạo bảng UNLOGGED (Bỏ qua ghi WAL log, tăng tốc ghi 200-300%)
CREATE UNLOGGED TABLE IF NOT EXISTS clean_data.library_borrow_ticket (
    id INT PRIMARY KEY,
    school_id INT,
    user_id INT,
    total_book INT,
    actual_borrow_date TIMESTAMPTZ,
    actual_return_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

-- 3. Xóa Index cũ (nếu có) để chuẩn bị cho việc Bulk Insert siêu tốc
DROP INDEX IF EXISTS clean_data.idx_clean_bt_borrow_date;
DROP INDEX IF EXISTS clean_data.idx_clean_bt_school;
DROP INDEX IF EXISTS clean_data.idx_clean_bt_user;

-- 4. Truncate dữ liệu cũ
TRUNCATE TABLE clean_data.library_borrow_ticket;

-- 5. Bơm dữ liệu (Lấy bản ghi mới nhất theo updated_at nếu bị trùng id)
INSERT INTO clean_data.library_borrow_ticket (
    id, school_id, user_id, total_book, actual_borrow_date, actual_return_date, created_at, updated_at
)
SELECT DISTINCT ON (id)
    id,
    COALESCE(school_id, 0),
    COALESCE(user_id, 0),
    COALESCE(total_book, 0),
    actual_borrow_date,
    actual_return_date,
    created_at,
    updated_at
FROM staging.library_borrow_ticket
WHERE id IS NOT NULL
ORDER BY id, updated_at DESC NULLS LAST;

-- 6. Đánh lại Index SAU KHI đã bơm xong toàn bộ dữ liệu
CREATE INDEX idx_clean_bt_borrow_date ON clean_data.library_borrow_ticket(actual_borrow_date);
CREATE INDEX idx_clean_bt_school ON clean_data.library_borrow_ticket(school_id);
CREATE INDEX idx_clean_bt_user ON clean_data.library_borrow_ticket(user_id);
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("=" * 60)
print("✅ ĐÃ XỬ LÝ VÀ LƯU THÀNH CÔNG VÀO clean_data.library_borrow_ticket")
print("=" * 60)