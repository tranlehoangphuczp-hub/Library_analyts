from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("LÀM SẠCH DỮ LIỆU - LIBRARY_BOOK_COPY (PURE SQL TỐI ƯU)")
print("=" * 60)

sql = r"""
-- 1. Cấp thêm RAM tạm thời cho session để sắp xếp / lọc trùng cực nhanh
SET work_mem = '64MB';

-- 2. Tạo bảng clean với Primary Key & cấu trúc chuẩn (UNLOGGED để tăng tốc ghi)
CREATE UNLOGGED TABLE IF NOT EXISTS clean_data.library_book_copy (
    id INT PRIMARY KEY,
    book_id INT,
    school_id INT,
    barcode VARCHAR(100),
    price NUMERIC(15, 2) DEFAULT 0,
    quantity INT DEFAULT 0,
    quantity_available INT DEFAULT 0,
    borrow_count INT DEFAULT 0,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- Xóa Index cũ (nếu có) để chuẩn bị Bulk Insert
DROP INDEX IF EXISTS clean_data.idx_clean_lbc_book_id;
DROP INDEX IF EXISTS clean_data.idx_clean_lbc_school_id;

-- 3. Xóa sạch dữ liệu cũ trong bảng clean
TRUNCATE TABLE clean_data.library_book_copy;

-- 4. Bơm & Làm sạch dữ liệu trực tiếp trong Database
INSERT INTO clean_data.library_book_copy (
    id, 
    book_id, 
    school_id, 
    barcode, 
    price, 
    quantity, 
    quantity_available, 
    borrow_count, 
    created_at, 
    updated_at, 
    deleted_at
)
SELECT DISTINCT ON (id)
    id,
    COALESCE(book_id, 0),
    COALESCE(school_id, 0),
    TRIM(barcode),
    -- Chuẩn hóa dữ liệu số: NULL hoặc lỗi -> 0 (thay cho pd.to_numeric + fillna(0))
    COALESCE(price, 0),
    COALESCE(quantity, 0),
    COALESCE(quantity_available, 0),
    COALESCE(borrow_count, 0),
    -- Chuẩn hóa dữ liệu ngày: Chuyển về TIMESTAMPTZ
    created_at,
    updated_at,
    deleted_at
FROM staging.library_book_copy
WHERE id IS NOT NULL
ORDER BY id, updated_at DESC NULLS LAST;

-- 5. Tạo Index SAU KHI đã bơm dữ liệu xong (giúp JOIN / Query DW cực nhanh)
CREATE INDEX idx_clean_lbc_book_id ON clean_data.library_book_copy(book_id);
CREATE INDEX idx_clean_lbc_school_id ON clean_data.library_book_copy(school_id);
"""

with engine.begin() as conn:
    conn.execute(text(sql))
    print("✅ Đã làm sạch và lưu clean_data.library_book_copy")

print("=" * 60)