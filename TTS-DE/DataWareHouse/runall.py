import sys
import subprocess

PYTHON_EXEC = sys.executable

def run_step(script_path):
    """Bắt lỗi dừng chương trình ngay nếu có script con bị ngắt giữa chừng"""
    subprocess.run([PYTHON_EXEC, script_path], check=True)

try:
    print("===== 3. BUILD DW =====")
    run_step("dim_date.py")
    run_step("dim_school.py")
    run_step("dim_subject.py")
    run_step("dim_role.py")
    run_step("dim_user.py")
    run_step("dim_book.py")
    run_step("fact_borrow.py")

except subprocess.CalledProcessError as e:
    print(f"\n❌ PIPELINE BỊ LỖI TẠI BƯỚC: {e.cmd[1]}")