from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("LÀM SẠCH DỮ LIỆU - LIBRARY_BORROW_BOOK (PURE SQL TỐI ƯU)")
print("=" * 60)

sql = r"""
-- 1. Cấp thêm bộ nhớ RAM cho session để lọc trùng và sắp xếp siêu nhanh
SET work_mem = '64MB';

-- 2. Tạo bảng UNLOGGED để tăng tốc độ ghi dữ liệu gấp 2 - 3 lần
CREATE UNLOGGED TABLE IF NOT EXISTS clean_data.library_borrow_book (
    id INT PRIMARY KEY,
    borrow_ticket_id INT,
    dang_ki_ca_biet_id INT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- 3. Xóa Index cũ (nếu có) để chuẩn bị Bulk Insert
DROP INDEX IF EXISTS clean_data.idx_clean_lbb_ticket_id;
DROP INDEX IF EXISTS clean_data.idx_clean_lbb_dkcb_id;

-- 4. Xóa sạch dữ liệu cũ
TRUNCATE TABLE clean_data.library_borrow_book;

-- 5. Bơm và làm sạch dữ liệu trực tiếp trong Database
INSERT INTO clean_data.library_borrow_book (
    id,
    borrow_ticket_id,
    dang_ki_ca_biet_id,
    created_at,
    updated_at,
    deleted_at
)
SELECT DISTINCT ON (id)
    id,
    borrow_ticket_id,
    dang_ki_ca_biet_id,
    created_at,
    updated_at,
    deleted_at
FROM staging.library_borrow_book
WHERE id IS NOT NULL
  AND borrow_ticket_id IS NOT NULL      -- Loại bỏ bản ghi mồ côi (thiếu mã phiếu)
  AND dang_ki_ca_biet_id IS NOT NULL    -- Loại bỏ bản ghi mồ côi (thiếu mã sách)
ORDER BY id, updated_at DESC NULLS LAST;

-- 6. ĐÁNH INDEX SAU KHI INSERT (Rất quan trọng cho file fact_borrow.py JOIN vào)
CREATE INDEX idx_clean_lbb_ticket_id ON clean_data.library_borrow_book(borrow_ticket_id);
CREATE INDEX idx_clean_lbb_dkcb_id ON clean_data.library_borrow_book(dang_ki_ca_biet_id);
"""

with engine.begin() as conn:
    conn.execute(text(sql))
    print("✅ Đã làm sạch và lưu thành công vào clean_data.library_borrow_book")

print("=" * 60)