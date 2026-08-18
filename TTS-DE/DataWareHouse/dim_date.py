from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("XÂY DỰNG DIM_DATE (TỐI ƯU PURE SQL)")
print("=" * 60)

sql = r"""
-- 1. Tạo khung bảng Dim Date chuẩn DW nếu chưa có (Có PRIMARY KEY)
CREATE TABLE IF NOT EXISTS library_dw.dim_date (
    date_key INT PRIMARY KEY,         -- Định dạng YYYYMMDD (vd: 20260728)
    full_date DATE,
    day INT,
    month INT,
    quarter INT,
    year INT,
    weekday VARCHAR(20),
    month_name VARCHAR(20)
);

-- 2. Xóa dữ liệu cũ (Dùng TRUNCATE giữ nguyên Khóa chính và cấu trúc)
TRUNCATE TABLE library_dw.dim_date CASCADE;

-- 3. Bơm dòng mặc định (date_key = 0 dùng cho các phiếu chưa trả / ngày NULL)
INSERT INTO library_dw.dim_date (
    date_key, full_date, day, month, quarter, year, weekday, month_name
)
VALUES (
    0, '1900-01-01', 0, 0, 0, 1900, 'Không xác định', 'Không xác định'
);

-- 4. Bơm dữ liệu ngày tháng thực tế (Sinh date_key chuẩn YYYYMMDD bằng Pure SQL)
INSERT INTO library_dw.dim_date (
    date_key,
    full_date,
    day,
    month,
    quarter,
    year,
    weekday,
    month_name
)
SELECT
    -- Chuyển YYYY-MM-DD thành số INT YYYYMMDD (Vd: 2026-07-28 -> 20260728)
    CAST(TO_CHAR(d.full_date, 'YYYYMMDD') AS INT) AS date_key,
    d.full_date,
    EXTRACT(DAY FROM d.full_date)::INT AS day,
    EXTRACT(MONTH FROM d.full_date)::INT AS month,
    EXTRACT(QUARTER FROM d.full_date)::INT AS quarter,
    EXTRACT(YEAR FROM d.full_date)::INT AS year,
    TO_CHAR(d.full_date, 'FMDay') AS weekday,
    TO_CHAR(d.full_date, 'FMMonth') AS month_name

FROM (
    SELECT DISTINCT DATE(actual_borrow_date) AS full_date
    FROM clean_data.library_borrow_ticket
    WHERE actual_borrow_date IS NOT NULL
      AND actual_borrow_date >= CURRENT_DATE - INTERVAL '1 year'
) d
ORDER BY d.full_date;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("=" * 60)
print("✅ ĐÃ XÂY DỰNG DIM_DATE THÀNH CÔNG")
print("=" * 60)