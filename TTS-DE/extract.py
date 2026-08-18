import pandas as pd
from sqlalchemy import create_engine
from config import SOURCE, TARGET

# ==========================
# Kết nối database
# ==========================

source_engine = create_engine(
    f"postgresql+psycopg2://{SOURCE['username']}:{SOURCE['password']}@"
    f"{SOURCE['host']}:{SOURCE['port']}/{SOURCE['database']}"
)

target_engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

# ==========================
# Danh sách bảng
# ==========================

tables = [
    "library_book",
    "library_book_borrower",
    "library_borrow_book",
    "library_borrow_ticket",
    "library_subject",
    "library_dang_ki_ca_biet",
    "library_book_copy",
    "users",
    "user_role",
    "role"
]

# ==========================
# Extract
# ==========================

for table in tables:

    print("=" * 60)
    print(f"Đang trích xuất bảng: {table}")

    if table == "users":
        query = """
        SELECT
            id,
            full_name,
            created_at,
            updated_at,
            deleted_at
        FROM readonly.users
        """
    else:
        query = f"SELECT * FROM public.{table}"

    df = pd.read_sql(query, source_engine)

    print(f"Số bản ghi: {len(df)}")

    df.to_sql(
        name=table,
        con=target_engine,
        schema="staging",
        if_exists="replace",
        index=False
    )

    print(f"Đã lưu vào staging.{table}")

print("=" * 60)
print("HOÀN THÀNH EXTRACT")