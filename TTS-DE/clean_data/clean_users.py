from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("LÀM SẠCH DỮ LIỆU - USERS")
print("=" * 60)

sql = r"""
CREATE TABLE IF NOT EXISTS clean_data.users (
    id INT PRIMARY KEY,
    full_name VARCHAR(255),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

TRUNCATE TABLE clean_data.users;

INSERT INTO clean_data.users (id, full_name, created_at, updated_at)
SELECT DISTINCT ON (id)
    id,
    COALESCE(TRIM(REGEXP_REPLACE(full_name, '\s+', ' ', 'g')), 'Không xác định') AS full_name,
    created_at,
    updated_at
FROM staging.users
WHERE id IS NOT NULL
ORDER BY id;
"""

with engine.begin() as conn:
    conn.execute(text(sql))
    print("✅ Đã xử lý và lưu clean_data.users")

print("=" * 60)