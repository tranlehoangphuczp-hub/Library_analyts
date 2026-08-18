from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

sql ="""-- 1. TỐI ƯU TỐC ĐỘ: Tạo Index phủ đúng 3 cột dùng trong GROUP BY bên dưới
CREATE INDEX IF NOT EXISTS idx_fact_overview
ON library_dw.fact_borrow(
    school_key,
    borrow_ticket_id,
    user_key
);

CREATE TABLE IF NOT EXISTS mart.borrow_overview(
    school_key INT PRIMARY KEY,
    total_book INT,
    total_borrow INT,
    total_reader INT,
    returned INT,
    not_return INT
);

TRUNCATE TABLE mart.borrow_overview;

INSERT INTO mart.borrow_overview(
    school_key,
    total_book,
    total_borrow,
    total_reader,
    returned,
    not_return
)

WITH borrow_ticket AS(
    SELECT
        school_key,
        borrow_ticket_id,
        user_key,
        SUM(book_count) AS total_book,
        MAX(
            CASE 
                WHEN return_date_key = 0 THEN 1
                ELSE 0
            END
) AS has_unreturned
    FROM library_dw.fact_borrow
    GROUP BY
        school_key,
        borrow_ticket_id,
        user_key
)

SELECT
    school_key,
    SUM(total_book),
    COUNT(*) AS total_borrow,
    COUNT(DISTINCT user_key)as total_reader,
    COUNT(
        CASE 
            WHEN has_unreturned = 0 
            THEN 1
        END
    ) AS completed_return,
    -- Phiếu chưa trả đủ sách
    COUNT(
        CASE 
            WHEN has_unreturned = 1 
            THEN 1
        END
    ) AS not_return
FROM borrow_ticket
GROUP BY school_key;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("✅ Updated mart.borrow_overview successfully!")