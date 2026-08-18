from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

# Danh sách 6 Materialized View cần refresh
views = [
    "mart.mv_borrow_overview",
    "mart.mv_monthly_borrow",
    "mart.mv_book_return_status",
    "mart.mv_role_borrow",
    "mart.mv_subject_borrow",
    "mart.mv_top_book",
]


def refresh_single_view(view_name: str):
    """
    Refresh 1 View trong chế độ AUTOCOMMIT để dùng được CONCURRENTLY
    """
    # BẮT BUỘC dùng execution_options(isolation_level="AUTOCOMMIT")
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view_name};"))
    return f"✅ Refreshed {view_name} successfully!"


if __name__ == "__main__":
    print("🚀 Bắt đầu Refresh các Materialized View song song...")

    # Chạy song song tối đa 3-4 Thread cùng lúc
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(refresh_single_view, views))

    for res in results:
        print(res)