import sys
import subprocess

PYTHON_EXEC = sys.executable

def run_step(script_path):
    """Bắt lỗi dừng chương trình ngay nếu có script con bị ngắt giữa chừng"""
    subprocess.run([PYTHON_EXEC, script_path], check=True)

try:
    print("===== 2. CLEAN =====")
    run_step("clean_library_book.py")
    run_step("clean_library_borrow_ticket.py")
    run_step("clean_library_borrow_book.py")
    run_step("clean_library_dang_ki_ca_biet.py")
    run_step("clean_school.py")
    run_step("clean_users.py")
    run_step("clean_role.py")

except subprocess.CalledProcessError as e:
    print(f"\n❌ PIPELINE BỊ LỖI TẠI BƯỚC: {e.cmd[1]}")