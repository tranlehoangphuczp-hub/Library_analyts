from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql = """
CREATE INDEX IF NOT EXISTS idx_fact_school_role 
ON library_dw.fact_borrow(
    school_key,
    role_key
);

CREATE TABLE IF NOT EXISTS mart.role_borrow(
    school_key INT,
    role_name VARCHAR(100),
    borrow_count INT,

    PRIMARY KEY (school_key, role_name)
);

TRUNCATE TABLE mart.role_borrow;

INSERT INTO mart.role_borrow(
    school_key,
    role_name,
    borrow_count
)

SELECT
    f.school_key,
    r.role_name,
    COUNT(DISTINCT f.borrow_ticket_id) AS borrow_count
FROM library_dw.fact_borrow f

JOIN library_dw.dim_role r
    ON f.role_key = r.role_key
GROUP BY
    f.school_key,
    r.role_name;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("✅ Updated mart.role_borrow successfully!")