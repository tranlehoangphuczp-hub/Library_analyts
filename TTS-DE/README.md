# TTS-DE — School Library Data Pipeline

Pipeline ETL bằng Python và PostgreSQL để chuyển dữ liệu vận hành thư viện trường học thành **Data Warehouse**, **Data Mart** và **Materialized View** phục vụ báo cáo/BI.

## Tổng quan

```text
Smart School (PostgreSQL nguồn)
        │
        ▼
 staging ──► clean_data ──► library_dw ──► mart ──► materialized views
```

- **Extract:** đọc dữ liệu sách, phiếu mượn, người dùng, vai trò… từ cơ sở dữ liệu nguồn.
- **Clean:** chuẩn hoá dữ liệu, loại trùng lặp, xử lý giá trị thiếu và tạo index hỗ trợ truy vấn.
- **Data Warehouse:** mô hình sao gồm các bảng chiều và `fact_borrow`.
- **Data Mart:** các bảng tổng hợp về hoạt động mượn/trả sách.
- **Materialized View:** lớp dữ liệu tối ưu cho công cụ BI.

## Công nghệ

- Python 3.8+
- PostgreSQL 12+
- pandas
- SQLAlchemy
- psycopg2-binary

## Cài đặt

```bash
git clone <repository-url>
cd TTS-DE
python -m venv .venv
```

Kích hoạt môi trường ảo:

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Cài các thư viện cần thiết:

```bash
pip install pandas sqlalchemy psycopg2-binary
```

## Cấu hình và bảo mật

Tạo file `config.py` ở thư mục gốc (file này **không nên được commit**):

```python
SOURCE = {
    "host": "source-host",
    "port": "5432",
    "database": "source_database",
    "username": "source_user",
    "password": "source_password",
}

TARGET = {
    "host": "localhost",
    "port": "5432",
    "database": "library_dw_database",
    "username": "postgres",
    "password": "target_password",
}

TARGET_SCHOOL_ID = 39
```

Trước khi chạy, tạo các schema trên database đích:

```sql
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS clean_data;
CREATE SCHEMA IF NOT EXISTS library_dw;
CREATE SCHEMA IF NOT EXISTS mart;
```

Kiểm tra kết nối:

```bash
python test_connect.py
```

> Lưu ý bảo mật: nếu `config.py` đã từng được đẩy lên GitHub, hãy đổi ngay mật khẩu nguồn/đích, xoá thông tin đó khỏi lịch sử Git và thêm `config.py` vào `.gitignore`.

## Chạy pipeline

Chạy lần lượt từ thư mục gốc để tạo đầy đủ dữ liệu:

```bash
python school.py
python extract.py

python clean_data/clean_library_book.py
python clean_data/clean_library_book_copy.py
python clean_data/clean_library_borrow_ticket.py
python clean_data/clean_library_borrow_book.py
python clean_data/clean_library_dang_ki_ca_biet.py
python clean_data/clean_library_subject.py
python clean_data/clean_school.py
python clean_data/clean_users.py
python clean_data/clean_role.py
python clean_data/clean_user_role.py

python DataWareHouse/dim_date.py
python DataWareHouse/dim_school.py
python DataWareHouse/dim_subject.py
python DataWareHouse/dim_role.py
python DataWareHouse/dim_user.py
python DataWareHouse/dim_book.py
python DataWareHouse/fact_borrow.py

python mart/borrow_overview.py
python mart/monthly_borrow.py
python mart/role_borrow.py
python mart/book_return_status.py
python mart/subject_borrow.py
python mart/top_book.py
python mart/school_borrow.py
```

Tạo Materialized Views, sau đó làm mới dữ liệu khi cần:

```bash
python materialized_view/runall.py
# hoặc chỉ làm mới các view đã có
python materialized_view/refresh_mv.py
```

`pipeline.py` là script điều phối các bước chính. Danh sách lệnh ở trên bao gồm cả các bảng phụ thuộc hiện chưa được `pipeline.py` gọi trực tiếp, nên phù hợp cho lần chạy đầy đủ đầu tiên.

## Mô hình dữ liệu

### Data Warehouse (`library_dw`)

| Nhóm | Bảng |
| --- | --- |
| Dimensions | `dim_date`, `dim_school`, `dim_subject`, `dim_role`, `dim_user`, `dim_book` |
| Fact | `fact_borrow` |

`fact_borrow` ghi nhận từng lượt mượn sách và liên kết đến người dùng, vai trò, trường, sách, môn học, ngày mượn và ngày trả.

### Data Marts (`mart`)

- `borrow_overview` — tổng quan lượt mượn.
- `monthly_borrow` — thống kê mượn theo tháng.
- `role_borrow` — phân tích theo vai trò.
- `school_borrow` — phân tích theo trường.
- `book_return_status` — trạng thái trả sách.
- `subject_borrow` — phân tích theo môn học.
- `top_book` — sách được mượn nhiều nhất.

## Cấu trúc thư mục

```text
TTS-DE/
├── extract.py                 # Trích xuất dữ liệu nguồn vào staging
├── school.py                  # Trích xuất dữ liệu trường học
├── pipeline.py                # Điều phối pipeline
├── test_connect.py            # Kiểm tra kết nối PostgreSQL
├── clean_data/                # Chuẩn hoá dữ liệu staging
├── DataWareHouse/             # Tạo dimension và fact table
├── mart/                      # Tạo bảng dữ liệu phân tích
└── materialized_view/         # Tạo/làm mới materialized views
```

## Ví dụ truy vấn

```sql
-- 10 sách được mượn nhiều nhất
SELECT *
FROM mart.top_book
ORDER BY borrow_count DESC
LIMIT 10;

-- Số lượt mượn theo tháng
SELECT *
FROM mart.monthly_borrow
ORDER BY year, month;
```

## Lưu ý vận hành

- Các bảng đích được nạp lại bằng `TRUNCATE`/`INSERT`; nên chạy trong môi trường đã sao lưu hoặc database phân tích riêng.
- `fact_borrow` hiện lấy dữ liệu có ngày mượn trong vòng một năm gần nhất.
- Nên lên lịch chạy ETL và refresh Materialized Views sau khi dữ liệu nguồn được cập nhật.

## License

Chưa có license. Có thể thêm file `LICENSE` (ví dụ: MIT) trước khi phát hành công khai.
