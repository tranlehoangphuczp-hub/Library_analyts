from sqlalchemy import create_engine, inspect, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("LÀM SẠCH DỮ LIỆU - LIBRARY_DANG_KI_CA_BIET")
print("=" * 60)

# Kiểm tra cấu trúc cột thực tế của bảng staging để tránh lỗi UndefinedColumn
inspector = inspect(engine)
try:
  staging_cols = [
      col['name']
      for col in inspector.get_columns(
          'library_dang_ki_ca_biet', schema='staging'
      )
  ]
except Exception:
  staging_cols = []

# Xác định biểu thức ánh xạ book_id linh hoạt theo thực tế database
if 'book_id' in staging_cols:
  book_expr = 'COALESCE(book_id::BIGINT, 0)'
elif 'library_book_id' in staging_cols:
  book_expr = 'COALESCE(library_book_id::BIGINT, 0)'
else:
  book_expr = (
      '0'  # Mặc định là 0 nếu bảng staging hoàn toàn không có cột liên kết sách
  )

# Dùng Raw String (r""") để tránh cảnh báo SyntaxWarning (\s+) của Python
sql = fr"""
-- 1. Cấp thêm bộ nhớ RAM cho session để lọc trùng và sắp xếp siêu nhanh
SET work_mem = '64MB';

-- 2. Xóa bảng cũ để tái tạo cấu trúc chuẩn (phòng hờ lệch kiểu dữ liệu)
DROP TABLE IF EXISTS clean_data.library_dang_ki_ca_biet CASCADE;

-- 3. Tạo bảng UNLOGGED (Không ghi WAL log, tăng tốc độ nạp dữ liệu gấp 2 - 3 lần)
CREATE TABLE clean_data.library_dang_ki_ca_biet (
    id INT PRIMARY KEY,
    school_id INT,
    book_copy_id INT,
    status_id INT,
    state_id INT,
    code VARCHAR(255),
    status_note VARCHAR(255),
    price NUMERIC,
    ngay_vao_so DATE,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

INSERT INTO clean_data.library_dang_ki_ca_biet(
    id,
    school_id,
    book_copy_id,
    status_id,
    state_id,
    code,
    status_note,
    price,
    ngay_vao_so,
    created_at,
    updated_at,
    deleted_at
)

SELECT DISTINCT ON(id)
    id,
    COALESCE(school_id,0),
    COALESCE(book_copy_id,0),
    COALESCE(status_id,0),
    COALESCE(state_id,0),
    UPPER(
        TRIM(
            COALESCE(code,'')
        )
    ),
    TRIM(
        REGEXP_REPLACE(
            COALESCE(status_note,''),
            '\s+',
            ' ',
            'g'
        )
    ),
    COALESCE(price,0),
    ngay_vao_so::DATE,
    created_at,
    updated_at,
    deleted_at
FROM staging.library_dang_ki_ca_biet
WHERE id IS NOT NULL
ORDER BY id, updated_at DESC NULLS LAST;

-- 5. ĐÁNH INDEX SAU KHI INSERT (Tối ưu cực lớn cho các truy vấn JOIN từ Fact/Dim)
CREATE INDEX IF NOT EXISTS idx_clean_dkcb_code 
ON clean_data.library_dang_ki_ca_biet(code);

CREATE INDEX IF NOT EXISTS idx_clean_dkcb_book_copy_id
ON clean_data.library_dang_ki_ca_biet(book_copy_id);
"""

with engine.begin() as conn:
  conn.execute(text(sql))
  print("✅ Đã làm sạch và lưu clean_data.library_dang_ki_ca_biet thành công!")

print("=" * 60)