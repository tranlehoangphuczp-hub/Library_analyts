import sys
import subprocess

PYTHON_EXEC = sys.executable

def run_step(script_path):
    """Bắt lỗi dừng chương trình ngay nếu có script con bị ngắt giữa chừng"""
    subprocess.run([PYTHON_EXEC, script_path], check=True)

try:
    print("===== 4. BUILD MART =====")
    run_step("borrow_overview.py")
    run_step("monthly_borrow.py")
    run_step("role_borrow.py")
    run_step("book_return_status.py")
    run_step("subject_borrow.py")
    run_step("top_book.py")
except subprocess.CalledProcessError as e:
    print(f"\n❌ PIPELINE BỊ LỖI TẠI BƯỚC: {e.cmd[1]}")