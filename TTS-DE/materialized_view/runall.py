import sys
import subprocess

PYTHON_EXEC = sys.executable

def run_step(script_path):
    """Bắt lỗi dừng chương trình ngay nếu có script con bị ngắt giữa chừng"""
    subprocess.run([PYTHON_EXEC, script_path], check=True)

try:
    print("===== create MATERIALIZED VIEWS =====")
    run_step("mv_borrow_overview.py")
    run_step("mv_monthly_borrow.py")
    run_step("mv_book_return_status.py")
    run_step("mv_role_borrow.py")
    run_step("mv_subject_borrow.py")
    run_step("mv_top_book.py")

    print("===== REFRESH MATERIALIZED VIEWS =====")
    # Gọi file riêng chuyên refresh toàn bộ MV
    run_step("refresh_mv.py")
except subprocess.CalledProcessError as e:
    print(f"\n❌ PIPELINE BỊ LỖI TẠI BƯỚC: {e.cmd[1]}")