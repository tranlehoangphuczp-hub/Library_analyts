import sys
import subprocess

PYTHON_EXEC = sys.executable

def run_step(script_path):
    """Bắt lỗi dừng chương trình ngay nếu có script con bị ngắt giữa chừng"""
    subprocess.run([PYTHON_EXEC, script_path], check=True)

try:
    print("===== 1. EXTRACT =====")
    run_step("extract.py")

    print("===== 2. CLEAN =====")
    run_step("clean_data/clean_library_book.py")
    run_step("clean_data/clean_library_borrow_ticket.py")
    run_step("clean_data/clean_library_borrow_book.py")
    run_step("clean_data/clean_library_dang_ki_ca_biet.py")
    run_step("clean_data/clean_school.py")
    run_step("clean_data/clean_users.py")
    run_step("clean_data/clean_role.py")

    print("===== 3. BUILD DW =====")
    run_step("DataWareHouse/dim_date.py")
    run_step("DataWareHouse/dim_school.py")
    run_step("DataWareHouse/dim_subject.py")
    run_step("DataWareHouse/dim_role.py")
    run_step("DataWareHouse/dim_user.py")
    run_step("DataWareHouse/dim_book.py")
    run_step("DataWareHouse/fact_borrow.py")

    print("===== 4. BUILD MART =====")
    run_step("mart/borrow_overview.py")
    run_step("mart/monthly_borrow.py")
    run_step("mart/role_borrow.py")
    run_step("mart/book_return_status.py")
    run_step("mart/subject_borrow.py")
    run_step("mart/top_book.py")

    print("===== 5. ENSURE MATERIALIZED VIEWS EXIST =====")
    # Lần đầu sẽ tạo, các lần sau có IF NOT EXISTS nên tự bỏ qua
    run_step("materialized_view/mv_borrow_overview.py")
    run_step("materialized_view/mv_monthly_borrow.py")
    run_step("materialized_view/mv_book_return_status.py")
    run_step("materialized_view/mv_role_borrow.py")
    run_step("materialized_view/mv_subject_borrow.py")
    run_step("materialized_view/mv_top_book.py")

    print("===== 6. REFRESH MATERIALIZED VIEWS =====")
    # Gọi file riêng chuyên refresh toàn bộ MV
    run_step("materialized_view/refresh_mv.py")

    print("\n✅ ===== PIPELINE FINISHED SUCCESSFULLY! =====")

except subprocess.CalledProcessError as e:
    print(f"\n❌ PIPELINE BỊ LỖI TẠI BƯỚC: {e.cmd[1]}")